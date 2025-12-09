from datetime import datetime
from models.vendas import Pedido, ItemPedido, Carrinho
from models.entidades import Cliente
from models.transacoes import Frete, Cupom
from repositories.dados import carregar_dados_loja, salvar_dados_loja
import repositories.cliente_repository as cliente_repository
from typing import Dict, Any, List

def _converter_pedido_to_dict(pedido: Pedido) -> Dict[str, Any]:
    itens_data = []
    for item in pedido._itens:
        itens_data.append({
            'sku': item._sku,
            'nome': item._nome,
            'preco_na_data': item._preco_na_data,
            'quantidade': item._quantidade
        })
        
    return {
        'codigo_pedido': pedido._codigo_pedido,
        'data_criacao': pedido._data_criacao.isoformat(),
        'cpf_cliente': pedido._cliente.cpf,
        'estado': pedido._estado,
        'frete_valor': pedido._frete.valor,
        'cupom_codigo': pedido._cupom.codigo if pedido._cupom else None,
        'subtotal': pedido._subtotal,
        'desconto': pedido._desconto,
        'total': pedido._total,
        'itens': itens_data
    }

def _converter_dict_to_pedido(data: Dict[str, Any], cliente: Cliente) -> Pedido:
    
    # Recria Frete e Cupom (os valores de Frete e Desconto já estão congelados no JSON)
    frete_dummy = Frete(cep_origem="00000000", cep_destino="00000000", valor=data.get('frete_valor', 0.0))
    cupom_codigo = data.get('cupom_codigo')
    cupom_dummy = Cupom(cupom_codigo) if cupom_codigo else None

    # Recria o Pedido com objetos dummy para satisfazer o __init__
    pedido = Pedido(
        cliente=cliente,
        carrinho=Carrinho(), 
        frete=frete_dummy, 
        cupom=cupom_dummy
    )
    
    # Sobrescreve atributos internos com dados congelados do JSON
    pedido._codigo_pedido = data['codigo_pedido']
    pedido._data_criacao = datetime.fromisoformat(data['data_criacao'])
    pedido._estado = data['estado']
    pedido._subtotal = data['subtotal']
    pedido._desconto = data['desconto']
    pedido._total = data['total']
    
    # Reconstroi os ItemPedido
    itens: List[ItemPedido] = []
    for item_data in data['itens']:
        item = ItemPedido(
            sku=item_data['sku'],
            nome=item_data['nome'],
            preco_na_data=item_data['preco_na_data'],
            quantidade=item_data['quantidade']
        )
        itens.append(item)
    pedido._itens = itens
    
    return pedido

def buscar_por_codigo(codigo: str) -> Pedido | None:
    dados = carregar_dados_loja()
    pedido_dict = next((p for p in dados['pedidos'] if p['codigo_pedido'] == codigo), None)
    
    if pedido_dict:
        cpf = pedido_dict['cpf_cliente']
        # Busca o objeto Cliente atual no cliente_repository
        cliente = cliente_repository.buscar_por_cpf(cpf)
        
        if cliente:
            return _converter_dict_to_pedido(pedido_dict, cliente)
    return None

def salvar(pedido: Pedido):
    dados = carregar_dados_loja()
    
    pedido_dict = _converter_pedido_to_dict(pedido)
    
    # Remove o pedido antigo se existir (para atualização de status)
    dados['pedidos'] = [p for p in dados['pedidos'] if p['codigo_pedido'] != pedido._codigo_pedido]
    
    # Adiciona o pedido atualizado/novo
    dados['pedidos'].append(pedido_dict)
    
    salvar_dados_loja(dados)

def carregar_todos() -> List[Pedido]:
    # Para relatórios, exige a desserialização de todos os clientes para linkar o Pedido.
    # Esta é uma implementação avançada, vamos mantê-la simples por enquanto.
    dados = carregar_dados_loja()
    pedidos_data = dados.get('pedidos', [])
    
    pedidos = []
    for pedido_dict in pedidos_data:
        cpf = pedido_dict['cpf_cliente']
        cliente = cliente_repository.buscar_por_cpf(cpf)
        if cliente:
             pedidos.append(_converter_dict_to_pedido(pedido_dict, cliente))
             
    return pedidos
import json
import os
from typing import List, Optional, Dict, Any
from datetime import datetime
from models.vendas import Pedido, Carrinho, ItemCarrinho
from models.entidades import Cliente, Produto, ProdutoFisico, Endereco
from models.transacoes import Frete, Cupom, Pagamento, PagamentoCartao, PagamentoBoleto
from models.exceptions import EntidadeNaoEncontradaError

# Constantes e Funções Auxiliares (Duplicação intencional)

NOME_ARQUIVO = 'loja.json'

def _get_file_path() -> str:
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_dir, 'data', NOME_ARQUIVO)

def _carregar_dados() -> Dict[str, Any]:
    caminho = _get_file_path()
    estrutura_base = {'clientes': [], 'produtos': [], 'pedidos': [], 'cupons': []}
    
    if not os.path.exists(caminho):
        os.makedirs(os.path.dirname(caminho), exist_ok=True)
        with open(caminho, 'w', encoding='utf-8') as f:
            json.dump(estrutura_base, f, indent=4, ensure_ascii=False)
        return estrutura_base
        
    try:
        with open(caminho, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        print(f"⚠️ Aviso: Arquivo {NOME_ARQUIVO} corrompido ou vazio. Recriando...")
        _salvar_dados(estrutura_base)
        return estrutura_base

def _salvar_dados(dados: Dict[str, Any]):
    caminho = _get_file_path()
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    with open(caminho, 'w', encoding='utf-8') as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)

# Funções de Desserialização
# Nota: Essas funções dependem dos repositórios de Entidades estarem carregados (simulação simples)

def _deserializar_produto_from_item(dados_item: Dict[str, Any]) -> Produto:
    """Simula a recriação do objeto Produto, necessário para o ItemCarrinho."""
    # Importação local para evitar dependência circular
    import repositories.produto_repository as produto_repository
    produto = produto_repository.buscar_por_sku(dados_item['produto_sku'])
    
    if produto:
        return produto
    
    # Fallback caso o produto original seja deletado
    return Produto(
        sku=dados_item['produto_sku'],
        nome=f"Produto Desconhecido (SKU: {dados_item['produto_sku']})",
        categoria="N/A",
        preco_unitario=dados_item['preco_unitario'],
        estoque=0,
        is_ativo=False
    )

def _deserializar_item_carrinho(dados_item: Dict[str, Any]) -> ItemCarrinho:
    """Converte dados de ItemCarrinho em objeto."""
    produto = _deserializar_produto_from_item(dados_item)
    item = ItemCarrinho(produto=produto, quantidade=dados_item['quantidade'])
    # Garante que o preço unitário do item seja o preço no momento da compra, 
    # ignorando o preço atualizado do produto no repositório.
    item._preco_unitario = dados_item['preco_unitario'] 
    return item

def _deserializar_carrinho(dados_carrinho: Dict[str, Any]) -> Carrinho:
    """Converte dados de Carrinho em objeto (usado no Pedido)."""
    
    itens = [_deserializar_item_carrinho(i) for i in dados_carrinho.get('itens', [])]
    
    carrinho = Carrinho(itens=itens) 
    return carrinho

def _deserializar_frete(dados_frete: Dict[str, Any]) -> Frete:
    """Converte dados de Frete em objeto."""
    return Frete(
        cep_origem=dados_frete['cep_origem'],
        cep_destino=dados_frete['cep_destino'],
        valor=dados_frete['valor'],
        prazo_dias=dados_frete['prazo_dias']
    )
    
def _deserializar_cupom(dados_cupom: Dict[str, Any]) -> Cupom:
    """Converte dados de Cupom em objeto."""
    validade = datetime.fromisoformat(dados_cupom['validade']) if dados_cupom.get('validade') else None
    return Cupom(
        codigo=dados_cupom['codigo'],
        valor=dados_cupom['valor'],
        is_percentual=dados_cupom['is_percentual'],
        validade=validade
    )
    
def _deserializar_pagamento(dados_pagamento: Dict[str, Any]) -> Pagamento:
    """Converte dados de Pagamento (e subclasses) em objeto."""
    tipo = dados_pagamento.get('tipo', 'Pagamento')
    
    # Campos base
    valor = dados_pagamento['valor']
    status = dados_pagamento['status']
    data_pagamento = datetime.fromisoformat(dados_pagamento['data_pagamento']) \
        if dados_pagamento.get('data_pagamento') else None

    if tipo == 'PagamentoCartao':
        return PagamentoCartao(
            valor=valor, status=status, data_pagamento=data_pagamento,
            bandeira=dados_pagamento.get('bandeira', 'DESCONHECIDA')
        )
    elif tipo == 'PagamentoBoleto':
        return PagamentoBoleto(
            valor=valor, status=status, 
            codigo_barras=dados_pagamento['codigo_barras'],
            data_vencimento=datetime.fromisoformat(dados_pagamento['data_vencimento'])
        )
    else:
        return Pagamento(valor=valor, status=status, data_pagamento=data_pagamento)

def _deserializar_pedido(dados_pedido: Dict[str, Any]) -> Pedido:
    """Converte um dicionário de dados em um objeto Pedido."""
    
    import repositories.cliente_repository as cliente_repository
    
    # Requisito 1: Cliente
    cliente = cliente_repository.buscar_por_cpf(dados_pedido['cliente_cpf'])
    if not cliente:
        # Cria um cliente placeholder se o original foi deletado
        cliente = Cliente(cpf=dados_pedido['cliente_cpf'], nome="Cliente Deletado", email="N/A") 
    
    # Requisito 2: Carrinho (desserializado como referência)
    carrinho = _deserializar_carrinho(dados_pedido['carrinho'])
    carrinho.cliente = cliente # Associa o cliente ao carrinho 
    
    # Requisito 3: Frete
    frete = _deserializar_frete(dados_pedido['frete'])
    
    # Requisito 4: Cupom
    cupom = _deserializar_cupom(dados_pedido['cupom']) if dados_pedido.get('cupom') else None
    
    # Cria o Pedido (aqui o Pedido re-calcula os totais, mas vamos injetar o estado persistido)
    pedido = Pedido(
        cliente=cliente, 
        carrinho=carrinho, 
        frete=frete, 
        cupom=cupom,
        codigo_pedido=dados_pedido['codigo_pedido']
    )
    
    # Injeta o estado e os valores calculados no momento da compra
    pedido._estado = dados_pedido['estado']
    pedido._total = dados_pedido['total']
    pedido._subtotal = dados_pedido['subtotal']
    pedido._desconto = dados_pedido['desconto']
    pedido._data_criacao = datetime.fromisoformat(dados_pedido['data_criacao'])
    
    # Injeta Pagamento, se existir
    if dados_pedido.get('pagamento'):
        pedido.pagamento = _deserializar_pagamento(dados_pedido['pagamento'])

    return pedido

# Funções de Repositório

def salvar(pedido: Pedido):
    """Salva ou atualiza um pedido."""
    dados = _carregar_dados()
    
    lista_pedidos = dados.get('pedidos', [])
    
    # Procura o índice do pedido pelo código
    try:
        idx = next(i for i, p in enumerate(lista_pedidos) if p['codigo_pedido'] == pedido.codigo_pedido)
        # Pedido encontrado: Substitui o registro existente
        lista_pedidos[idx] = pedido.to_dict()
    except StopIteration:
        # Pedido não encontrado: Adiciona novo registro
        lista_pedidos.append(pedido.to_dict())
        
    dados['pedidos'] = lista_pedidos
    _salvar_dados(dados)


def buscar_por_codigo(codigo: str) -> Optional[Pedido]:
    """Busca um pedido pelo código (completo ou prefixo)."""
    codigo = codigo.strip().upper()
    dados = _carregar_dados()
    
    for p in dados.get('pedidos', []):
        # Busca por código exato OU por prefixo
        if p['codigo_pedido'] == codigo or p['codigo_pedido'].startswith(codigo):
            return _deserializar_pedido(p)
            
    return None

def carregar_todos() -> List[Pedido]:
    """Retorna a lista completa de todos os pedidos."""
    dados = _carregar_dados()
    return [_deserializar_pedido(p) for p in dados.get('pedidos', [])]

def carregar_todos_pedidos_raw() -> List[Dict[str, Any]]:
    """Retorna a lista de pedidos como dicionários brutos (para relatórios rápidos)."""
    dados = _carregar_dados()
    return dados.get('pedidos', [])
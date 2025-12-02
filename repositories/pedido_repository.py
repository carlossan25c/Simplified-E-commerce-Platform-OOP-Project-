from models.vendas import Pedido
from repositories.dados import carregar_dados_loja, salvar_dados_loja 
from typing import List, Dict, Any

PEDIDOS_KEY = 'pedidos'


def _pedido_to_dict(pedido: Pedido) -> Dict[str, Any]:
    """Converte objeto Pedido para dicionário (Serialização)."""
    return {
        'codigo_pedido': pedido._codigo_pedido,
        'data_criacao': pedido._data_criacao.isoformat(), 
        'cpf_cliente': pedido._cliente.cpf, 
        'estado': pedido._estado,
        'subtotal': pedido._subtotal,
        'desconto': pedido._desconto,
        'total': pedido._total,
        # Serializa os itens do pedido
        'itens': [{
            'sku': item._sku,
            'nome': item._nome,
            'preco_na_data': item._preco_na_data,
            'quantidade': item._quantidade
        } for item in pedido._itens],
        # Serializa Frete e Cupom
        'frete_valor': pedido._frete.valor,
        'cupom_codigo': pedido._cupom._codigo if pedido._cupom else None
    }

def carregar_todos_pedidos_raw() -> List[Dict[str, Any]]:
    """Carrega apenas os dados brutos dos pedidos para o relatório."""
    dados_completos = carregar_dados_loja()
    return dados_completos.get(PEDIDOS_KEY, [])

def salvar_pedido(pedido: Pedido):
    """Salva um novo pedido (criação) no arquivo loja.json."""
    
    dados_completos = carregar_dados_loja()
    pedidos = dados_completos.get(PEDIDOS_KEY, [])
    
    pedido_dict = _pedido_to_dict(pedido)
    pedidos.append(pedido_dict) 

    dados_completos[PEDIDOS_KEY] = pedidos
    salvar_dados_loja(dados_completos)
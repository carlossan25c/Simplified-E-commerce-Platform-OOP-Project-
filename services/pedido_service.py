# Arquivo: services/pedido_service.py

import repositories.pedido_repository as pedido_repository
from models.vendas import Pedido
from models.exceptions import ValorInvalidoError
from typing import Literal

# Definindo os Status Válidos para o Pedido
StatusPedido = Literal["CRIADO", "PAGO", "SEPARACAO", "ENVIADO", "ENTREGUE", "CANCELADO"]

TRANSICOES_VALIDAS = {
    # De: Status Atual | Para: Statuses Permitidos
    "CRIADO": ["PAGO", "CANCELADO"],
    "PAGO": ["SEPARACAO", "CANCELADO"],
    "SEPARACAO": ["ENVIADO", "CANCELADO"],
    "ENVIADO": ["ENTREGUE"],
    "ENTREGUE": [], # Estado final (não pode mais mudar)
    "CANCELADO": [] # Estado final (não pode mais mudar)
}

def avancar_status(codigo_pedido: str, novo_status: StatusPedido):
    pedido = pedido_repository.buscar_por_codigo(codigo_pedido)
    
    if not pedido:
        raise ValorInvalidoError(f"Pedido com código '{codigo_pedido}' não encontrado.")
    
    status_atual = pedido._estado
    novo_status = novo_status.upper()
    
    if novo_status not in TRANSICOES_VALIDAS.keys():
        raise ValorInvalidoError(f"Status '{novo_status}' não é um status válido.")

    # 1. Checa se a transição é permitida usando o dicionário TRANSICOES_VALIDAS
    if novo_status not in TRANSICOES_VALIDAS.get(status_atual, []):
        raise ValorInvalidoError(
            f"Transição inválida: Não é possível mudar de '{status_atual}' para '{novo_status}'."
        )

    # 2. Atualiza o estado na entidade e persiste no repositório
    pedido._estado = novo_status
    pedido_repository.salvar(pedido)
    
    return pedido
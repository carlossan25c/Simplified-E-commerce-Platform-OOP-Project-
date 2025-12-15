from models.vendas import Carrinho, Pedido
from models.transacoes import Frete, Cupom, Pagamento, PagamentoCartao, PagamentoBoleto
from models.entidades import Cliente
from models.exceptions import ValorInvalidoError, EntidadeNaoEncontradaError
from services.estoque_service import EstoqueService 
from repositories import pedido_repository
from typing import Optional, Dict, Any

class PedidoService:
    """Orquestra o processo de checkout, criação, pagamento e gestão de Pedidos."""

    @staticmethod
    def finalizar_compra(
        carrinho: Carrinho, 
        frete: Frete, 
        metodo_pagamento: str, 
        info_pagamento: Dict[str, Any], 
        cupom: Optional[Cupom] = None
    ) -> Pedido:
        """
        Finaliza a compra, cria o Pedido, tenta processar o pagamento e realiza 
        a baixa de estoque se o pagamento for bem-sucedido.
        """
        if not carrinho.itens:
            raise ValorInvalidoError("O carrinho não pode estar vazio para finalizar a compra.")
        if not carrinho.cliente:
             raise EntidadeNaoEncontradaError("Cliente deve ser associado ao carrinho.")
        
        # 1. Validação de Estoque (Regra de Negócio de Segurança)
        EstoqueService.validar_baixa_estoque(carrinho.itens)
        
        # 2. Criação do Objeto Pedido
        pedido = Pedido(
            cliente=carrinho.cliente,
            carrinho=carrinho,
            frete=frete,
            cupom=cupom
        )
        
        # 3. Processamento do Pagamento
        pagamento = PedidoService._processar_pagamento(
            pedido.cliente, 
            pedido._total, 
            metodo_pagamento, 
            info_pagamento
        )
        
        # 4. Associa o Pagamento e Atualiza o Estado
        pedido.pagamento = pagamento # Usa o setter do Pedido
        
        if pagamento.is_aprovado:
            # Baixa de estoque e atualização de status
            pedido.estado = "PAGO" # Usa o setter de estado
            EstoqueService.realizar_baixa_estoque(carrinho.itens)
        else:
            # Define o status baseado no pagamento. Se for boleto, é PENDENTE. Se falhou, é CANCELADO.
            pedido.estado = "PENDENTE" if metodo_pagamento.lower() == 'boleto' else "CANCELADO" 
            
        # 5. Persiste o Pedido
        pedido_repository.salvar(pedido)
        return pedido


    @staticmethod
    def _processar_pagamento(
        cliente: Cliente, 
        valor_total: float, 
        metodo: str, 
        info: Dict[str, Any]
    ) -> Pagamento:
        """Simula o processamento real do pagamento."""
        
        metodo = metodo.lower()
        status = "APROVADO" # Assumimos sucesso na simulação
        
        if valor_total < 5.00: 
            status = "FALHOU" 
            
        if metodo == 'cartao':
            bandeira = info.get('bandeira', 'VISA')
            # Simulação: Cartão Master Card sempre falha
            if bandeira.lower() == 'master card':
                 status = "FALHOU"

            return PagamentoCartao(
                valor=valor_total,
                status=status,
                bandeira=bandeira
            )
        
        elif metodo == 'boleto':
            # Boletos são sempre pendentes na criação
            codigo_barras = "34191.09003 00000.000008 00000.000009 5 88880000123456" 
            status = "PENDENTE" 
            return PagamentoBoleto(
                valor=valor_total,
                status=status,
                codigo_barras=codigo_barras
            )

        raise ValorInvalidoError(f"Método de pagamento '{metodo}' inválido.")

    @staticmethod
    def atualizar_estado_pedido(codigo_pedido: str, novo_estado: str) -> Pedido:
        """Atualiza o estado de um pedido persistido."""
        pedido = pedido_repository.buscar_por_codigo(codigo_pedido)
        if not pedido:
            raise EntidadeNaoEncontradaError(f"Pedido com código {codigo_pedido} não encontrado.")
            
        pedido.estado = novo_estado # Usa o setter de estado
        pedido_repository.salvar(pedido)
        return pedido
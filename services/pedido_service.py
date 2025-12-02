from models.vendas import Carrinho, Pedido
from models.entidades import Cliente
from models.transacoes import Frete, Cupom
from repositories import produto_repository, pedido_repository
from models.exceptions import ValorInvalidoError 

class PedidoService:
    """Gerencia a lógica de fechamento de pedido, estoque e persistência."""

    @staticmethod
    def fechar_pedido_a_partir_do_carrinho(cliente: Cliente, carrinho: Carrinho, frete: Frete, cupom: Cupom = None) -> Pedido:
        """
        Orquestra a criação do pedido, validação de estoque, ajuste de estoque e persistência.
        """
        
        if not carrinho._itens:
            raise ValorInvalidoError("O carrinho não pode estar vazio.")
            
        # 1. VALIDAÇÃO DE ESTOQUE
        for item in carrinho._itens:
            produto_em_estoque = produto_repository.buscar_por_sku(item.produto._sku)
            if not produto_em_estoque or produto_em_estoque.estoque < item.quantidade:
                raise ValorInvalidoError(f"Estoque insuficiente para {item.produto._nome}.")
                
        # 2. CRIAÇÃO DO PEDIDO
        pedido = Pedido(cliente, carrinho, frete, cupom)
        
        # 3. ATUALIZAÇÃO DE ESTOQUE (Baixa)
        for item in carrinho._itens:
            produto_em_estoque = produto_repository.buscar_por_sku(item.produto._sku)
            if produto_em_estoque:
                produto_em_estoque.ajustar_estoque(-item.quantidade) 
                produto_repository.salvar_produto(produto_em_estoque)
                
        # 4. PERSISTÊNCIA
        pedido_repository.salvar_pedido(pedido)
        
        # 5. Esvaziar o Carrinho após sucesso
        carrinho._itens = [] 
        
        return pedido
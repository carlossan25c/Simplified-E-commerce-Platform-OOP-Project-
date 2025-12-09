from repositories import produto_repository, settings_repository
from models.exceptions import ValorInvalidoError
from models.vendas import ItemCarrinho

class EstoqueService:
    """Gerencia regras de estoque, como limites de segurança."""

    @staticmethod
    def validar_baixa_estoque(itens_carrinho: list[ItemCarrinho]):
        """
        Valida se a baixa de estoque é possível, respeitando o limite de segurança.
        Levanta ValorInvalidoError se a regra for violada.
        """
        settings = settings_repository.carregar_settings()
        limite_seguranca = settings['regra_estoque']['limite_seguranca']
        
        for item in itens_carrinho:
            produto_em_estoque = produto_repository.buscar_por_sku(item.produto._sku)
            
            if not produto_em_estoque or produto_em_estoque.estoque < item.quantidade:
                raise ValorInvalidoError(f"Estoque insuficiente para {item.produto._nome}.")
            
            # Cálculo da regra de negócio avançada (Entrega 4)
            estoque_apos_compra = produto_em_estoque.estoque - item.quantidade
            
            if estoque_apos_compra < limite_seguranca:
                raise ValorInvalidoError(
                    f"Não é possível vender {item.produto._nome}. A compra excederia o limite de segurança de {limite_seguranca} unidades. Estoque atual: {produto_em_estoque.estoque}."
                )

    @staticmethod
    def realizar_baixa_estoque(itens_carrinho: list[ItemCarrinho]):
        """Realiza a baixa de estoque e persiste as alterações."""
        for item in itens_carrinho:
            produto_em_estoque = produto_repository.buscar_por_sku(item.produto._sku)
            if produto_em_estoque:
                produto_em_estoque.ajustar_estoque(-item.quantidade) 
                produto_repository.salvar_produto(produto_em_estoque)
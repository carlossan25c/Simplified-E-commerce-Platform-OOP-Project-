from repositories import produto_repository, settings_repository
from models.exceptions import ValorInvalidoError
from models.vendas import ItemCarrinho
from models.entidades import ProdutoFisico 

class EstoqueService:
    """Gerencia regras de estoque, como limites de segurança e baixa."""

    @staticmethod
    def validar_baixa_estoque(itens_carrinho: list[ItemCarrinho]):
        """
        Valida se a baixa de estoque é possível, respeitando o limite de segurança
        e a disponibilidade de estoque para Produtos Físicos.
        """
        settings = settings_repository.carregar_settings()
        limite_seguranca = settings['regra_estoque']['limite_seguranca']
        
        for item in itens_carrinho:
            # CORREÇÃO: Usando a propriedade pública 'sku' e 'nome'
            sku = item.produto.sku
            nome = item.produto.nome
            
            produto_em_estoque = produto_repository.buscar_por_sku(sku)
            
            # Checa apenas Produtos Físicos (ou aqueles que têm estoque gerenciável)
            if isinstance(produto_em_estoque, ProdutoFisico):
                
                # 1. Validação Simples de Estoque
                if not produto_em_estoque or produto_em_estoque.estoque < item.quantidade:
                    raise ValorInvalidoError(f"Estoque insuficiente para {nome}. Disponível: {produto_em_estoque.estoque}")
                
                # 2. Regra de Limite de Segurança
                estoque_apos_compra = produto_em_estoque.estoque - item.quantidade
                
                if estoque_apos_compra < limite_seguranca:
                    raise ValorInvalidoError(
                        f"Não é possível vender {nome}. A compra excederia o limite de segurança de {limite_seguranca} unidades. Estoque atual: {produto_em_estoque.estoque}."
                    )

    @staticmethod
    def realizar_baixa_estoque(itens_carrinho: list[ItemCarrinho]):
        """Realiza a baixa de estoque e persiste as alterações."""
        
        for item in itens_carrinho:
            # CORREÇÃO: Usando a propriedade pública 'sku'
            sku = item.produto.sku
            
            produto_em_estoque = produto_repository.buscar_por_sku(sku)
            
            # Só realiza a baixa se for um Produto Físico (ou gerenciável)
            if isinstance(produto_em_estoque, ProdutoFisico) and produto_em_estoque:
                
                # Ajusta o estoque (método deve existir na classe Produto/ProdutoFisico)
                produto_em_estoque.ajustar_estoque(-item.quantidade) 
                
                # CORREÇÃO: Usando a função correta do repositório
                produto_repository.salvar(produto_em_estoque)
from models.vendas import Carrinho, Pedido
from models.entidades import Cliente
from models.transacoes import Frete, Cupom
from repositories import pedido_repository
from services.estoque_service import EstoqueService # Importamos o novo Service
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
            
        
        EstoqueService.validar_baixa_estoque(carrinho._itens)
                
        pedido = Pedido(cliente, carrinho, frete, cupom)
        
        EstoqueService.realizar_baixa_estoque(carrinho._itens)
                
        pedido_repository.salvar_pedido(pedido)
        
        carrinho._itens = [] 
        
        return pedido
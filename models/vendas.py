from models.entidades import Produto, Cliente # Importa as classes necessárias

class ItemCarrinho:
    """
    Representa um produto e sua quantidade dentro de um Carrinho.
    
    Requisitos de POO:
    - Garante o encapsulamento: 'quantidade' deve ser >= 1.
    - Relacionamento 1:1 com a classe Produto.
    """
    def __init__(self, produto: Produto, quantidade: int):
        self._produto = produto
        self._quantidade = quantidade # Será validado via @property

    def calcular_subtotal_item(self) -> float:
        """Calcula o valor total do item (preço unitário * quantidade)."""
        pass
    
    def to_dict(self):
        """Retorna uma representação em dicionário para persistência JSON."""
        pass 


class Carrinho:
    """
    Gerencia a lista de itens selecionados antes de fechar o pedido.
    
    Requisitos de POO:
    - Composição: é composto por uma lista de objetos ItemCarrinho.
    - Deve implementar __len__ (para saber o número total de itens/produtos).
    """
    def __init__(self):
        self._itens: list[ItemCarrinho] = []

    def adicionar_item(self, produto: Produto, quantidade: int):
        """Adiciona ou atualiza a quantidade de um produto no carrinho."""
        pass

    def calcular_subtotal(self) -> float:
        """Soma o subtotal de todos os ItemCarrinho."""
        pass

    # __len__, __iter__ (opcional) virão aqui...


class ItemPedido:
    """
    Representa um produto e sua quantidade dentro de um Pedido, 
    registrando o preço na data da compra.
    """
    def __init__(self, produto: Produto, quantidade: int, preco_na_data: float):
        self._produto = produto
        self._quantidade = quantidade
        self._preco_na_data = preco_na_data

    def to_dict(self):
        """Retorna uma representação em dicionário para persistência JSON."""
        pass 


class Pedido:
    """
    Gerencia o ciclo de vida da transação (estados) e consolida os totais.
    
    Requisitos de POO:
    - Alto nível de Composição: utiliza Cliente, lista de ItemPedido, Frete, Cupom e Pagamento.
    """
    def __init__(self, codigo_pedido: str, cliente: Cliente, itens: list[ItemPedido], estado: str = "CRIADO"):
        self._cliente = cliente
        self._itens = itens
        self._estado = estado # CRIADO, PAGO, ENVIADO, ENTREGUE, CANCELADO
        self._frete = None
        self._desconto = 0.0
        self._total = 0.0
        self._pagamentos = []

    def fechar_pedido(self, carrinho: Carrinho, frete, cupom=None):
        """Orquestra a conversão do carrinho em pedido, aplicação de frete e cupom."""
        pass

    def calcular_total(self):
        """Calcula o total final (subtotal + frete - desconto)."""
        pass
        
    def to_dict(self):
        """Retorna uma representação em dicionário para persistência JSON."""
        pass
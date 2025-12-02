from datetime import datetime
from uuid import uuid4
from typing import List
from models.entidades import Cliente, Produto 
from models.transacoes import Frete, Cupom
from models.exceptions import ValorInvalidoError 
from datetime import datetime
from uuid import uuid4

class ItemCarrinho:
    """Representa um produto e sua quantidade no carrinho."""
    def __init__(self, produto: Produto, quantidade: int):
        if quantidade <= 0:
            raise ValorInvalidoError("A quantidade de itens deve ser maior que zero.")
        
        self.produto = produto
        self.quantidade = quantidade
        
    def calcular_subtotal_item(self) -> float:
        return self.produto.preco_unitario * self.quantidade

class Carrinho:
    """
    Gerencia a lista de ItemCarrinho. 
    Implementa __len__ para contar a quantidade total de itens (Requisito RT).
    """
    def __init__(self):
        self._itens: List[ItemCarrinho] = []

    # Método especial: __len__ (Requisito RT)
    def __len__(self) -> int:
        """Retorna o número de itens diferentes no carrinho."""
        return len(self._itens)

    def adicionar_item(self, produto: Produto, quantidade: int):
        """Adiciona ou atualiza a quantidade de um item no carrinho."""
        for item in self._itens:
            if item.produto == produto: # Usa o __eq__ do Produto
                item.quantidade += quantidade
                return
        self._itens.append(ItemCarrinho(produto, quantidade))
    
    def calcular_subtotal(self) -> float:
        """Calcula a soma dos subtotais de todos os itens."""
        return sum(item.calcular_subtotal_item() for item in self._itens)


class ItemPedido:
    """
    Representa o item no pedido, capturando o preço no momento da criação 
    (dados congelados).
    """
    def __init__(self, sku: str, nome: str, preco_na_data: float, quantidade: int):
        self._sku = sku
        self._nome = nome
        self._preco_na_data = preco_na_data
        self._quantidade = quantidade

    def calcular_subtotal_item(self) -> float:
        return self._preco_na_data * self._quantidade

    def __str__(self):
        return f"{self._nome} (SKU: {self._sku}) x{self._quantidade} @ R$ {self._preco_na_data:.2f}"

class Pedido:
    """
    Gerencia o ciclo de vida da transação. 
    O 'codigo_pedido' é o identificador único.
    """
    ESTADOS = ["CRIADO", "PAGO", "ENVIADO", "ENTREGUE", "CANCELADO"]

    def __init__(self, cliente: Cliente, carrinho: Carrinho, frete: Frete, cupom: Cupom = None):
        self._codigo_pedido = str(uuid4()) 
        self._data_criacao = datetime.now()
        self._cliente = cliente # Agregação (cliente existe fora do pedido)
        self._estado = "CRIADO" 
        self._frete = frete
        self._cupom = cupom
        
        # Composição (itens nascem e morrem com o pedido)
        self._itens: List[ItemPedido] = self._converter_carrinho_para_itens(carrinho)
        
        # Cálculos
        self._subtotal = carrinho.calcular_subtotal()
        self._desconto = self._calcular_desconto()
        self._total = self._calcular_total()
        self._pagamentos = [] 

    def _converter_carrinho_para_itens(self, carrinho: Carrinho) -> List[ItemPedido]:
        """Copia os dados do carrinho para ItemPedido para 'congelar' o preço."""
        itens_pedido = []
        for item_carrinho in carrinho._itens:
            itens_pedido.append(
                ItemPedido(
                    sku=item_carrinho.produto._sku,
                    nome=item_carrinho.produto._nome,
                    preco_na_data=item_carrinho.produto.preco_unitario,
                    quantidade=item_carrinho.quantidade
                )
            )
        return itens_pedido

    def _calcular_desconto(self) -> float:
        """Aplica o desconto do cupom, se houver."""
        if self._cupom:
            return self._cupom.calcular_desconto(self._subtotal)
        return 0.0

    def _calcular_total(self) -> float:
        """Calcula o total final (subtotal - desconto + frete)."""
        total_sem_frete = self._subtotal - self._desconto
        return max(0, total_sem_frete) + self._frete.valor

    @property
    def estado(self) -> str:
        return self._estado
    
    def __str__(self): # Requisito __str__
        return f"Pedido {self._codigo_pedido[:8]}... | Cliente: {self._cliente.nome} | Total: R$ {self._total:.2f} | Status: {self._estado}"
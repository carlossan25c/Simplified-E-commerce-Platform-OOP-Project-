from datetime import datetime
from uuid import uuid4
from typing import List
from .entidades import Cliente, Produto 
from .transacoes import Frete, Cupom
from .exceptions import ValorInvalidoError 


class ItemCarrinho:
    def __init__(self, produto: Produto, quantidade: int):
        if quantidade <= 0:
            raise ValorInvalidoError("A quantidade de itens deve ser maior que zero.")
        
        self._produto = produto
        self._quantidade = quantidade
        
    @property
    def produto(self):
        return self._produto

    @property
    def quantidade(self):
        return self._quantidade
        
    @property
    def subtotal(self) -> float:
        return self._produto.preco_unitario * self._quantidade
        
    def __str__(self):
        return f"{self.produto.nome} (x{self.quantidade}) - Subtotal: R$ {self.subtotal:.2f}"


class Carrinho:
    def __init__(self, cliente: Cliente = None):
        self._cliente = cliente
        self._itens: List[ItemCarrinho] = []

    # PROPRIEDADE ESSENCIAL PARA VISUALIZAÇÃO NO app.py (Opção 2)
    @property
    def itens(self):
        return self._itens.copy()
        
    @property
    def total(self) -> float:
        return sum(item.subtotal for item in self._itens)
    
    def __len__(self) -> int:
        return len(self._itens)

    def adicionar_item(self, produto: Produto, quantidade: int):
        if quantidade <= 0:
            raise ValorInvalidoError("Quantidade deve ser positiva para adicionar.")
            
        for item in self._itens:
            if item.produto == produto:
                # Acessa o atributo interno _quantidade para modificar
                item._quantidade += quantidade 
                return
                
        self._itens.append(ItemCarrinho(produto, quantidade))
    
    def remover_item(self, sku: str):
        self._itens = [item for item in self._itens if item.produto.sku != sku]
        
    def __str__(self):
        if not self._itens:
            return "Carrinho Vazio."
            
        detalhes = [str(item) for item in self._itens]
        return "\n".join(["--- ITENS DO CARRINHO ---"] + detalhes + [f"TOTAL FINAL: R$ {self.total:.2f}"])

class ItemPedido:
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
    ESTADOS = ["CRIADO", "PAGO", "ENVIADO", "ENTREGUE", "CANCELADO"]

    def __init__(self, cliente: Cliente, carrinho: Carrinho, frete: Frete, cupom: Cupom = None):
        self._codigo_pedido = str(uuid4()) 
        self._data_criacao = datetime.now()
        self._cliente = cliente 
        self._estado = "CRIADO" 
        self._frete = frete
        self._cupom = cupom
        
        self._itens: List[ItemPedido] = self._converter_carrinho_para_itens(carrinho)
        
        self._subtotal = carrinho.total # Usa a propriedade 'total' de Carrinho
        self._desconto = self._calcular_desconto()
        self._total = self._calcular_total()
        self._pagamentos = [] 

    def _converter_carrinho_para_itens(self, carrinho: Carrinho) -> List[ItemPedido]:
        itens_pedido = []
        for item_carrinho in carrinho.itens: # Usa a nova property 'itens'
            itens_pedido.append(
                ItemPedido(
                    sku=item_carrinho.produto.sku,
                    nome=item_carrinho.produto.nome,
                    preco_na_data=item_carrinho.produto.preco_unitario,
                    quantidade=item_carrinho.quantidade
                )
            )
        return itens_pedido

    def _calcular_desconto(self) -> float:
        if self._cupom:
            return self._cupom.calcular_desconto(self._subtotal)
        return 0.0

    def _calcular_total(self) -> float:
        total_sem_frete = self._subtotal - self._desconto
        return max(0, total_sem_frete) + self._frete.valor

    @property
    def estado(self) -> str:
        return self._estado
    
    def __str__(self): 
        return f"Pedido {self._codigo_pedido[:8]}... | Cliente: {self._cliente.nome} | Total: R$ {self._total:.2f} | Status: {self._estado}"
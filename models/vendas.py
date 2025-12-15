from datetime import datetime
from typing import List, Optional, Union
from models.entidades import Produto, Cliente, ProdutoFisico
from models.transacoes import Frete, Cupom, Pagamento
from models.exceptions import ValorInvalidoError
import math

class ItemCarrinho:
    def __init__(self, produto: Produto, quantidade: int):
        if quantidade <= 0:
            raise ValorInvalidoError("A quantidade do item deve ser maior que zero.")
        
        self._produto = produto
        self._quantidade = quantidade
        # Salva o preço unitário atual do produto no item (para histórico)
        self._preco_unitario = produto.preco_unitario 

    @property
    def produto(self) -> Produto: return self._produto
    @property
    def quantidade(self) -> int: return self._quantidade
    @property
    def preco_unitario(self) -> float: return self._preco_unitario
    
    @property
    def subtotal(self) -> float:
        return self.preco_unitario * self.quantidade

    def to_dict(self):
        return {
            'produto_sku': self.produto.sku,
            'quantidade': self.quantidade,
            'preco_unitario': self.preco_unitario
        }
        
    def __str__(self):
        return f"{self.produto.nome} (SKU: {self.produto.sku}) - Qtd: {self.quantidade} - Subtotal: R$ {self.subtotal:.2f}"


class Carrinho:
    def __init__(self, cliente: Optional[Cliente] = None, itens: Optional[List[ItemCarrinho]] = None):
        self._cliente = cliente
        self._itens = itens or []

    @property
    def cliente(self) -> Optional[Cliente]: return self._cliente
    
    @cliente.setter
    def cliente(self, cliente: Cliente):
        if not isinstance(cliente, Cliente):
            raise TypeError("O objeto deve ser uma instância de Cliente.")
        self._cliente = cliente

    @property
    def itens(self) -> List[ItemCarrinho]: return self._itens

    @property
    def total(self) -> float:
        """Calcula o subtotal dos itens no carrinho."""
        return sum(item.subtotal for item in self.itens)

    def adicionar_item(self, produto: Produto, quantidade: int):
        """Adiciona ou atualiza a quantidade de um item no carrinho."""
        if not produto.is_ativo:
            raise ValorInvalidoError(f"Produto {produto.nome} está inativo e não pode ser adicionado ao carrinho.")
            
        # 1. Tenta encontrar o item existente
        item_existente = next((item for item in self._itens if item.produto.sku == produto.sku), None)

        if item_existente:
            # 2. Se existe, atualiza a quantidade
            item_existente._quantidade += quantidade # Acessa diretamente para simplicidade na atualização
        else:
            # 3. Se não existe, cria um novo item
            novo_item = ItemCarrinho(produto, quantidade)
            self._itens.append(novo_item)

    def remover_item(self, sku: str):
        """Remove um item completamente do carrinho pelo SKU."""
        self._itens = [item for item in self._itens if item.produto.sku != sku]

    def calcular_peso_total(self) -> float:
        """Calcula o peso total dos itens Físicos no carrinho."""
        peso_total = 0.0
        for item in self.itens:
            # Verifica se o produto é ProdutoFisico ou tem o atributo peso
            if isinstance(item.produto, ProdutoFisico) and hasattr(item.produto, 'peso'):
                peso_total += item.produto.peso * item.quantidade
        return peso_total
        
    def to_dict(self):
        return {
            'cliente_cpf': self.cliente.cpf if self.cliente else None,
            'itens': [item.to_dict() for item in self.itens]
        }
        
    def __str__(self):
        if not self.itens:
            return "🛒 Carrinho vazio."
            
        output = "ITENS NO CARRINHO:\n"
        for item in self.itens:
            output += f" * {item}\n"
        output += f"\nTOTAL (Itens): R$ {self.total:.2f}"
        return output


class Pedido:
    # Estados possíveis para o pedido (usado em PedidoService)
    ESTADOS_VALIDOS = ["NOVO", "AGUARDANDO_PAGAMENTO", "PAGO", "SEPARACAO", "ENVIADO", "ENTREGUE", "CANCELADO"]
    
    def __init__(self, cliente: Cliente, carrinho: Carrinho, frete: Frete, cupom: Optional[Cupom] = None, codigo_pedido: Optional[str] = None):
        
        if not cliente or not carrinho or not frete:
            raise ValorInvalidoError("Cliente, Carrinho e Frete são obrigatórios para criar um Pedido.")

        self._codigo_pedido = codigo_pedido or self._gerar_codigo()
        self._cliente = cliente
        self._data_criacao = datetime.now()
        self._carrinho = carrinho # Mantém a referência ao carrinho (itens e cliente)
        self._frete = frete
        self._cupom = cupom
        self._estado = "NOVO" 
        self._pagamento = None # Objeto Pagamento será anexado após o processamento
        
        # Valores calculados no momento da criação/atualização
        self._subtotal = self._calcular_subtotal()
        self._desconto = self._calcular_desconto()
        self._total = self._calcular_total()
        
    def _gerar_codigo(self) -> str:
        """Gera um código de pedido simples, baseado em data e um hash."""
        # Código simples: P-YYYYMMDDHHMMSS-RANDOM5
        return "P-" + datetime.now().strftime("%Y%m%d%H%M%S") + "-" + str(math.floor(datetime.now().timestamp() * 1000) % 10000)

    def _calcular_subtotal(self) -> float:
        """Calcula o subtotal dos itens (valor antes de frete/desconto)."""
        return self.carrinho.total

    def _calcular_desconto(self) -> float:
        """Calcula o valor do desconto do cupom, limitado ao subtotal dos itens."""
        if self.cupom:
            # Desconto calculado sobre o subtotal, não sobre o total (itens + frete)
            desconto_bruto = self.cupom.calcular_desconto(self._subtotal)
            
            # Regra de Negócio: O desconto não pode ser maior que o subtotal dos itens.
            return min(desconto_bruto, self._subtotal)
        return 0.0

    def _calcular_total(self) -> float:
        """Calcula o total final (subtotal - desconto + frete)."""
        total_itens_com_desconto = self._subtotal - self._desconto
        return total_itens_com_desconto + self.frete.valor

    @property
    def codigo_pedido(self) -> str: return self._codigo_pedido
    @property
    def cliente(self) -> Cliente: return self._cliente
    @property
    def data_criacao(self) -> datetime: return self._data_criacao
    @property
    def carrinho(self) -> Carrinho: return self._carrinho
    @property
    def frete(self) -> Frete: return self._frete
    @property
    def cupom(self) -> Optional[Cupom]: return self._cupom
    @property
    def pagamento(self) -> Optional[Pagamento]: return self._pagamento
    
    # Propriedades de estado e valores (propriedades de leitura)
    @property
    def estado(self) -> str: return self._estado
    @property
    def subtotal(self) -> float: return self._subtotal
    @property
    def desconto(self) -> float: return self._desconto
    @property
    def total(self) -> float: return self._total
    
    # Setters para atributos protegidos (usados apenas pelo serviço)
    @pagamento.setter
    def pagamento(self, pagamento: Pagamento):
         self._pagamento = pagamento

    @estado.setter
    def estado(self, novo_estado: str):
        if novo_estado not in self.ESTADOS_VALIDOS:
            raise ValorInvalidoError(f"Estado '{novo_estado}' inválido.")
        self._estado = novo_estado
        
    def to_dict(self):
        return {
            'codigo_pedido': self.codigo_pedido,
            'cliente_cpf': self.cliente.cpf,
            'data_criacao': self.data_criacao.isoformat(),
            'estado': self.estado,
            'subtotal': self.subtotal,
            'desconto': self.desconto,
            'total': self.total,
            'carrinho': self.carrinho.to_dict(),
            'frete': self.frete.to_dict(),
            'cupom': self.cupom.to_dict() if self.cupom else None,
            'pagamento': self.pagamento.to_dict() if self.pagamento else None
        }
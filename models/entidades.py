class Produto:
    """
    Representa um produto disponível para venda na loja.
    
    Requisitos de POO:
    - O encapsulamento deve ser garantido usando @property para validar
      que 'preco_unitario' é > 0 e 'estoque' é >= 0.
    - Deve implementar __eq__ (para comparação por SKU) e __lt__ 
      (para ordenação por preço ou nome).
    - Métodos para serialização (to_dict) são necessários para persistência JSON.
    """
    def __init__(self, sku: str, nome: str, categoria: str, preco_unitario: float, estoque: int, ativo: bool = True):
        # Utiliza-se '_' para indicar que o acesso deve ser feito via @property (encapsulamento)
        self._sku = sku
        self._nome = nome
        self._categoria = categoria
        self._preco_unitario = preco_unitario 
        self._estoque = estoque             
        self._ativo = ativo

    def ajustar_estoque(self, quantidade: int):
        """Atualiza o estoque do produto. Positivo para entrada, negativo para baixa (faturamento)."""
        pass 

    def to_dict(self):
        """Retorna uma representação em dicionário para persistência JSON."""
        pass 

    # @property para preco_unitario e estoque virão aqui...

# --- Classes de Herança Opcional ---

class ProdutoFisico(Produto):
    """Subclasse de Produto que inclui a característica de peso para cálculo de frete."""
    def __init__(self, sku, nome, categoria, preco_unitario, estoque, peso: float, ativo=True):
        super().__init__(sku, nome, categoria, preco_unitario, estoque, ativo)
        self._peso = peso

# ------------------------------------

class Cliente:
    """
    Representa um cliente da loja.
    
    Requisitos de POO:
    - O encapsulamento deve ser garantido usando @property para validar 
      e formatar o 'email' e o 'cpf'.
    - Gerencia o relacionamento 1:N com a classe Endereco (Composição).
    """
    def __init__(self, id: int, nome: str, email: str, cpf: str):
        self._id = id
        self._nome = nome
        self._email = email     # Será validado via @property
        self._cpf = cpf         # Será validado via @property
        self._enderecos = [] # Lista de objetos Endereco

    def adicionar_endereco(self, endereco):
        """Adiciona um objeto Endereco à lista de endereços do cliente."""
        pass

    def to_dict(self):
        """Retorna uma representação em dicionário para persistência JSON."""
        pass 
    
    # @property para email e cpf virão aqui...


class Endereco:
    """Representa um endereço de entrega ou cobrança."""
    def __init__(self, cep: str, logradouro: str, numero: str, cidade: str, uf: str):
        self._cep = cep
        self._logradouro = logradouro
        self._numero = numero
        self._cidade = cidade
        self._uf = uf

    def to_dict(self):
        """Retorna uma representação em dicionário para persistência JSON."""
        pass
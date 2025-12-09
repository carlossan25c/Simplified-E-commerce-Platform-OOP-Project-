import re # Usado para validações básicas de CPF e Email
from .exceptions import ValorInvalidoError, DocumentoInvalidoError 

class Produto:
    """
    Representa um produto disponível para venda. O SKU é o código único.
    Encapsulamento em 'preco_unitario' e 'estoque' para garantir a validade dos dados.
    """
    def __init__(self, sku: str, nome: str, categoria: str, preco: float, estoque: int, ativo: bool = True):
        # Atributos internos (privados)
        self._sku = sku
        self._nome = nome
        self._categoria = categoria
        self._ativo = ativo
        
        # A atribuição inicial usa os setters para garantir a validação na criação do objeto
        self.preco_unitario = preco
        self.estoque = estoque      

    @property
    def preco_unitario(self) -> float:
        """Getter: Retorna o preço unitário do produto."""
        return self._preco_unitario

    @preco_unitario.setter
    def preco_unitario(self, novo_preco: float):
        """Setter: Valida se o preço é maior que zero."""
        if novo_preco <= 0:
            raise ValorInvalidoError("O preço unitário deve ser um valor maior que zero.")
        self._preco_unitario = novo_preco

    @property
    def estoque(self) -> int:
        """Getter: Retorna a quantidade em estoque do produto."""
        return self._estoque

    @estoque.setter
    def estoque(self, nova_quantidade: int):
        """Setter: Valida se o estoque não é negativo (exceto em casos específicos de projeto)."""
        if nova_quantidade < 0:
            raise ValorInvalidoError("O estoque não pode ser negativo no cadastro.")
        self._estoque = nova_quantidade
    
    def __eq__(self, outro):
        """Dois produtos são considerados iguais se possuírem o mesmo SKU (código único)."""
        if isinstance(outro, Produto):
            return self._sku == outro._sku
        return False
    
    def __str__(self):
        """Representação amigável do produto."""
        status = "ATIVO" if self._ativo else "INATIVO"
        return f"[{self._sku}] {self._nome} ({self._categoria}) | R$ {self.preco_unitario:.2f} | Estoque: {self.estoque} ({status})"

    def ajustar_estoque(self, quantidade: int):
        """Ajusta o estoque, usando o setter para garantir a validação."""
        self.estoque += quantidade

class ProdutoFisico(Produto):
    """Subclasse de Produto para itens que exigem cálculo de frete baseado no peso."""
    def __init__(self, sku: str, nome: str, categoria: str, preco: float, estoque: int, peso: float, ativo: bool = True):
        super().__init__(sku, nome, categoria, preco, estoque, ativo)
        
        if peso <= 0:
            raise ValorInvalidoError("O peso deve ser maior que zero para um ProdutoFisico.")
        self._peso = peso
    
    @property
    def peso(self):
        return self._peso

class Endereco:
    def __init__(self, cep: str, logradouro: str, numero: str, cidade: str, uf: str):
        # Encapsulamento
        self._cep = cep
        self._logradouro = logradouro
        self._numero = numero
        self._cidade = cidade
        self._uf = uf

    # Propriedades de leitura pública
    @property
    def cep(self): return self._cep
    @property
    def logradouro(self): return self._logradouro
    @property
    def cidade(self): return self._cidade
    @property
    def uf(self): return self._uf

    def __str__(self):
        return f"{self.logradouro}, {self._numero} - {self.cidade}/{self.uf} ({self.cep})"


class Cliente:
    def __init__(self, cpf: str, nome: str, email: str):
        # 1. Validação de Formato e Atribuição (Não usa Repositório)
        self._cpf = self._validar_cpf(cpf) 
        self._nome = nome
        self._email = self._validar_email(email)
        
        # 2. Inicialização Interna da lista de Endereços (Corrigido)
        self._enderecos = [] 
        
    
    def _validar_cpf(self, cpf: str):
        # Validação: deve ser numérico e ter 11 dígitos.
        # Não faz verificação de existência no JSON/BD.
        if not cpf.isdigit() or len(cpf) != 11:
            raise DocumentoInvalidoError("CPF deve conter 11 dígitos numéricos.")
        return cpf
    
    def _validar_email(self, email: str):
        # Validação simples de email
        if "@" not in email or "." not in email:
            raise ValorInvalidoError("Formato de e-mail inválido.")
        return email
    
    @property
    def cpf(self): return self._cpf
    
    @property
    def nome(self): return self._nome
    
    @property
    def email(self): return self._email
    
    @property
    def enderecos(self): 
        # Retorna uma cópia para proteger a lista interna
        return self._enderecos.copy()

    # --- Métodos de Negócio ---
    
    def adicionar_endereco(self, endereco: Endereco):
        if not isinstance(endereco, Endereco):
            raise TypeError("O objeto deve ser uma instância de Endereco.")
        self._enderecos.append(endereco)
    
    def __eq__(self, other):
        # Permite comparação por CPF
        if isinstance(other, Cliente):
            return self._cpf == other.cpf
        return False
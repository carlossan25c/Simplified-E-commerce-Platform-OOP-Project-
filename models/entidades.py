import re 
from .exceptions import ValorInvalidoError, DocumentoInvalidoError 


class Produto:
    def __init__(self, sku: str, nome: str, categoria: str, preco: float, estoque: int, ativo: bool = True):
        self._sku = sku
        self._nome = nome
        self._categoria = categoria
        self._ativo = ativo
        
        self.preco_unitario = preco
        self.estoque = estoque 
        
    @property
    def sku(self):
        return self._sku
    
    @property
    def nome(self):
        return self._nome

    @property
    def preco_unitario(self) -> float:
        return self._preco_unitario

    @preco_unitario.setter
    def preco_unitario(self, novo_preco: float):
        if novo_preco <= 0:
            raise ValorInvalidoError("O preço unitário deve ser um valor maior que zero.")
        self._preco_unitario = novo_preco

    @property
    def estoque(self) -> int:
        return self._estoque

    @estoque.setter
    def estoque(self, nova_quantidade: int):
        if nova_quantidade < 0:
            raise ValorInvalidoError("O estoque não pode ser negativo no cadastro.")
        self._estoque = nova_quantidade
    
    def ajustar_estoque(self, quantidade: int):
        self.estoque += quantidade

    def __eq__(self, outro):
        if isinstance(outro, Produto):
            return self._sku == outro.sku
        return False
    
    def __str__(self):
        status = "ATIVO" if self._ativo else "INATIVO"
        return f"[{self._sku}] {self._nome} ({self._categoria}) | R$ {self.preco_unitario:.2f} | Estoque: {self.estoque} ({status})"


class ProdutoFisico(Produto):
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
        self._cep = cep
        self._logradouro = logradouro
        self._numero = numero
        self._cidade = cidade
        self._uf = uf

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
        self._cpf = self._validar_cpf(cpf) 
        self._nome = nome
        self._email = self._validar_email(email)
        
        self._enderecos = [] 
        
    def _validar_cpf(self, cpf: str):
        if not cpf.isdigit() or len(cpf) != 11:
            raise DocumentoInvalidoError("CPF deve conter 11 dígitos numéricos.")
        return cpf
    
    def _validar_email(self, email: str):
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
        return self._enderecos.copy()

    def adicionar_endereco(self, endereco: Endereco):
        if not isinstance(endereco, Endereco):
            raise TypeError("O objeto deve ser uma instância de Endereco.")
        self._enderecos.append(endereco)
    
    def __eq__(self, other):
        if isinstance(other, Cliente):
            return self._cpf == other.cpf
        return False
import re
from typing import List, Optional
from datetime import datetime
from models.exceptions import DocumentoInvalidoError, ValorInvalidoError

class Endereco:
    def __init__(self, cep: str, logradouro: str, numero: str, cidade: str, uf: str, complemento: Optional[str] = None):
        if not re.match(r'^\d{8}$', cep):
            raise ValorInvalidoError("CEP deve conter 8 dígitos numéricos.")
        if not logradouro or not numero or not cidade or not uf:
            raise ValorInvalidoError("Logradouro, número, cidade e UF são obrigatórios.")
            
        self._cep = cep
        self._logradouro = logradouro
        self._numero = numero
        self._cidade = cidade
        self._uf = uf.upper()
        self._complemento = complemento

    @property
    def cep(self) -> str: return self._cep
    @property
    def logradouro(self) -> str: return self._logradouro
    @property
    def numero(self) -> str: return self._numero
    @property
    def cidade(self) -> str: return self._cidade
    @property
    def uf(self) -> str: return self._uf
    @property
    def complemento(self) -> Optional[str]: return self._complemento

    def __str__(self):
        comp = f" ({self.complemento})" if self.complemento else ""
        return f"{self.logradouro}, {self.numero}{comp} - {self.cidade}/{self.uf} (CEP: {self.cep})"
        
    def to_dict(self):
        return {
            'cep': self.cep,
            'logradouro': self.logradouro,
            'numero': self.numero,
            'cidade': self.cidade,
            'uf': self.uf,
            'complemento': self.complemento
        }


class Cliente:
    def __init__(self, cpf: str, nome: str, email: str, data_cadastro: Optional[datetime] = None, enderecos: Optional[List[Endereco]] = None):
        if not Cliente.validar_cpf(cpf):
            raise DocumentoInvalidoError(f"CPF '{cpf}' é inválido.")
        if not nome or not email:
            raise ValorInvalidoError("Nome e email são obrigatórios.")

        self._cpf = cpf
        self._nome = nome
        self._email = email
        self._data_cadastro = data_cadastro or datetime.now()
        self._enderecos = enderecos or []

    @staticmethod
    def validar_cpf(cpf: str) -> bool:
        """Simplificação da validação: checa se tem 11 dígitos."""
        cpf_limpo = re.sub(r'\D', '', cpf)
        return len(cpf_limpo) == 11

    @property
    def cpf(self) -> str: return self._cpf
    @property
    def nome(self) -> str: return self._nome
    @property
    def email(self) -> str: return self._email
    @property
    def data_cadastro(self) -> datetime: return self._data_cadastro
    @property
    def enderecos(self) -> List[Endereco]: return self._enderecos

    def adicionar_endereco(self, endereco: Endereco):
        if not isinstance(endereco, Endereco):
            raise TypeError("O objeto deve ser uma instância de Endereco.")
        self._enderecos.append(endereco)
        
    def to_dict(self):
        return {
            'cpf': self.cpf,
            'nome': self.nome,
            'email': self.email,
            'data_cadastro': self.data_cadastro.isoformat(),
            'enderecos': [e.to_dict() for e in self.enderecos]
        }


class Produto:
    def __init__(self, sku: str, nome: str, categoria: str, preco_unitario: float, estoque: int = 0, is_ativo: bool = True):
        if not sku or not nome or preco_unitario <= 0:
            raise ValorInvalidoError("SKU, nome e preço unitário válido são obrigatórios para o Produto.")
        
        self._sku = sku
        self._nome = nome
        self._categoria = categoria
        self._preco_unitario = preco_unitario
        self._estoque = estoque
        self._is_ativo = is_ativo

    @property
    def sku(self) -> str: return self._sku
    @property
    def nome(self) -> str: return self._nome
    @property
    def categoria(self) -> str: return self._categoria
    @property
    def preco_unitario(self) -> float: return self._preco_unitario
    @property
    def is_ativo(self) -> bool: return self._is_ativo
    
    # Propriedade de Estoque (pode ser usado para produtos digitais que têm um estoque virtual)
    @property
    def estoque(self) -> int: return self._estoque

    @estoque.setter
    def estoque(self, novo_valor: int):
        if novo_valor < 0:
             raise ValorInvalidoError("Estoque não pode ser negativo.")
        self._estoque = novo_valor

    def ajustar_estoque(self, quantidade: int):
        """Ajusta o estoque, aceitando valores positivos (entrada) ou negativos (saída)."""
        novo_estoque = self._estoque + quantidade
        self.estoque = novo_estoque # Usa o setter para validação de valor < 0

    def to_dict(self):
        return {
            'sku': self.sku,
            'nome': self.nome,
            'categoria': self.categoria,
            'preco_unitario': self.preco_unitario,
            'estoque': self.estoque,
            'is_ativo': self.is_ativo,
            'tipo': self.__class__.__name__ # Adiciona o tipo para desserialização
        }


class ProdutoFisico(Produto):
    def __init__(self, sku: str, nome: str, categoria: str, preco_unitario: float, estoque: int, peso: float, is_ativo: bool = True):
        super().__init__(sku, nome, categoria, preco_unitario, estoque, is_ativo)
        if peso <= 0:
            raise ValorInvalidoError("Produto Físico deve ter peso positivo.")
        self._peso = peso

    @property
    def peso(self) -> float: return self._peso

    def to_dict(self):
        data = super().to_dict()
        data['peso'] = self.peso
        return data
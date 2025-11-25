import re # Usado para validações básicas de CPF e Email
from .exceptions import ValorInvalidoError, DocumentoInvalidoError 

# CLASSE PRODUTO
# O SKU (código único) é o identificador

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

    # --- ENCAPSULAMENTO PARA PREÇO UNITÁRIO (@property) ---

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

    # --- ENCAPSULAMENTO PARA ESTOQUE (@property) ---

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

    # --- MÉTODOS ESPECIAIS ---
    
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

# --- CLASSE PRODUTO FÍSICO (Herança Opcional) ---

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
    
# CLASSE CLIENTE

class Cliente:
    """
    Representa um cliente da loja. O CPF é o código único e identificador.
    Encapsulamento em 'cpf' e 'email' para validação de formato.
    """
    def __init__(self, nome: str, cpf: str, email: str):
        self._nome = nome
        self._enderecos = [] 
        
        # A atribuição inicial usa os setters
        self.cpf = cpf          
        self.email = email      

    # --- ENCAPSULAMENTO PARA CPF (@property) ---

    @property
    def cpf(self) -> str:
        """Getter: Retorna o CPF limpo (apenas dígitos)."""
        return self._cpf
    
    @cpf.setter
    def cpf(self, novo_cpf: str):
        """Setter: Valida se o CPF é válido e armazena apenas dígitos."""
        cpf_limpo = re.sub(r'[^0-9]', '', novo_cpf)
        
        # Validação básica de formato (11 dígitos)
        if not (len(cpf_limpo) == 11 and cpf_limpo.isdigit()):
            raise DocumentoInvalidoError("CPF deve conter exatamente 11 dígitos.")
        
        self._cpf = cpf_limpo
        
    # --- ENCAPSULAMENTO PARA EMAIL (@property) ---

    @property
    def email(self) -> str:
        """Getter: Retorna o email."""
        return self._email
    
    @email.setter
    def email(self, novo_email: str):
        """Setter: Validação Regex Simples para o formato do email."""
        if not re.match(r"[^@]+@[^@]+\.[^@]+", novo_email):
            raise DocumentoInvalidoError("Formato de email inválido.")
            
        self._email = novo_email

    # --- MÉTODOS CHAVE ---

    def adicionar_endereco(self, endereco):
        """Adiciona um objeto Endereco à lista de endereços do cliente."""
        self._enderecos.append(endereco)

    def __eq__(self, outro):
        """Dois clientes são considerados iguais se tiverem o mesmo CPF (código único)."""
        if isinstance(outro, Cliente):
            return self._cpf == outro._cpf
        return False

    def __str__(self):
        """Representação amigável do cliente."""
        return f"Cliente: {self._nome} (CPF: {self._cpf[:3]}...{self._cpf[-3:]}) | Email: {self.email}"




class Endereco:
    """Representa um endereço de entrega ou cobrança (Objeto de Valor)."""
    def __init__(self, cep: str, logradouro: str, numero: str, cidade: str, uf: str, complemento: str = ""):
        self._cep = re.sub(r'[^0-9]', '', cep)
        self._logradouro = logradouro
        self._numero = numero
        self._cidade = cidade
        self._uf = uf
        self._complemento = complemento

    def __str__(self):
        """Representação completa do endereço."""
        return f"{self._logradouro}, {self._numero}{' ' + self._complemento if self._complemento else ''} - {self._cidade}/{self._uf} (CEP: {self._cep})"

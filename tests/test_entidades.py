import pytest
from models.entidades import Produto, Cliente, Endereco, ValorInvalidoError, DocumentoInvalidoError

# Fixture para Produto Válido
@pytest.fixture
def produto_valido(): 
    """Retorna uma instância válida de Produto."""
    return Produto(sku="P001", nome="Notebook Pro", categoria="Eletronicos", preco=4500.00, estoque=10)

# Fixture para Cliente Válido
@pytest.fixture
def cliente_valido():
    """Retorna uma instância válida de Cliente."""
    # CPF de 11 dígitos para o teste
    return Cliente(nome="João da Silva", cpf="12345678900", email="joao.silva@teste.com")

# TESTES DA CLASSE PRODUTO

def test_produto_criacao_e_atributos(produto_valido):
    """Testa se o produto é criado corretamente e se os atributos estão acessíveis."""
    assert produto_valido._sku == "P001"
    assert produto_valido.nome == "Notebook Pro"
    assert produto_valido.preco_unitario == 4500.00 # Acessando via getter (@property)
    assert produto_valido.estoque == 10            # Acessando via getter (@property)
    assert str(produto_valido).startswith("[P001]")

def test_produto_preco_valido_com_setter(produto_valido):
    """Testa se o setter de preco_unitario funciona corretamente com um valor válido."""
    produto_valido.preco_unitario = 5000.00
    assert produto_valido.preco_unitario == 5000.00

def test_produto_preco_invalido_deve_falhar():
    """Testa se o encapsulamento impede preços <= 0 (teste negativo)."""
    with pytest.raises(ValorInvalidoError) as excinfo:
        Produto(sku="P002", nome="Monitor", categoria="Eletronicos", preco=0.00, estoque=5)
    assert "maior que zero" in str(excinfo.value)
    
    with pytest.raises(ValorInvalidoError):
        Produto(sku="P003", nome="Mouse", categoria="Acessorios", preco=-10.00, estoque=20)

def test_produto_estoque_invalido_deve_falhar(produto_valido):
    """Testa se o encapsulamento impede estoque negativo via setter (teste negativo)."""
    # Testando o setter
    with pytest.raises(ValorInvalidoError) as excinfo:
        produto_valido.estoque = -5 
    assert "não pode ser negativo" in str(excinfo.value)

def test_produto_ajustar_estoque(produto_valido):
    """Testa o método ajustar_estoque para entrada e baixa."""
    produto_valido.ajustar_estoque(5)  # Entrada
    assert produto_valido.estoque == 15
    
    produto_valido.ajustar_estoque(-10) # Baixa
    assert produto_valido.estoque == 5
    
    # Testa se o ajuste de estoque ainda respeita a regra negativa
    with pytest.raises(ValorInvalidoError):
        produto_valido.ajustar_estoque(-10) # Tenta ir para -5

def test_produto_igualdade_por_sku(produto_valido):
    """Testa o método mágico __eq__ (igualdade)."""
    produto_igual = Produto(sku="P001", nome="Notebook Pro (Outra Marca)", categoria="Outro", preco=1.0, estoque=1)
    produto_diferente = Produto(sku="P002", nome="Teclado", categoria="Acessorios", preco=100.0, estoque=5)
    
    assert produto_valido == produto_igual  # Devem ser iguais pelo SKU
    assert produto_valido != produto_diferente # Devem ser diferentes

# TESTES DA CLASSE CLIENTE

def test_cliente_criacao_e_atributos(cliente_valido):
    """Testa se o cliente é criado corretamente e se o CPF está limpo."""
    assert cliente_valido.nome == "João da Silva"
    assert cliente_valido.cpf == "12345678900" # Deve estar limpo (apenas dígitos)
    assert cliente_valido.email == "joao.silva@teste.com"

def test_cliente_cpf_aceita_formatacao_mas_armazena_limpo():
    """Testa se o setter de CPF limpa a string antes de armazenar."""
    cliente = Cliente(nome="Pedro", cpf="987.654.321-00", email="pedro@teste.com")
    assert cliente.cpf == "98765432100"

def test_cliente_cpf_invalido_deve_falhar():
    """Testa se o encapsulamento impede CPFs que não têm 11 dígitos."""
    with pytest.raises(DocumentoInvalidoError) as excinfo:
        Cliente(nome="Mauro", cpf="12345", email="mauro@teste.com")
    assert "11 dígitos" in str(excinfo.value)

def test_cliente_email_invalido_deve_falhar():
    """Testa se o encapsulamento impede emails com formato inválido."""
    with pytest.raises(DocumentoInvalidoError) as excinfo:
        cliente_valido().email = "email_sem_arroba.com"
    assert "Formato de email inválido" in str(excinfo.value)

def test_cliente_adicionar_endereco(cliente_valido):
    """Testa o método adicionar_endereco e o relacionamento de composição."""
    endereco = Endereco(cep="01234-567", logradouro="Rua Teste", numero="100", cidade="São Paulo", uf="SP")
    cliente_valido.adicionar_endereco(endereco)
    
    assert len(cliente_valido._enderecos) == 1
    assert str(cliente_valido._enderecos[0]).startswith("Rua Teste")

def test_cliente_igualdade_por_cpf(cliente_valido):
    """Testa o método mágico __eq__ (igualdade)."""
    # Cliente com mesmo CPF, mas nome diferente
    cliente_igual = Cliente(nome="José da Silva", cpf="123.456.789-00", email="jose@outro.com")
    # Cliente com CPF diferente
    cliente_diferente = Cliente(nome="Maria", cpf="11122233344", email="maria@teste.com")
    
    assert cliente_valido == cliente_igual
    assert cliente_valido != cliente_diferente

# TESTES DA CLASSE ENDERECO

def test_endereco_criacao_e_formatacao():
    """Testa se o endereço é criado corretamente e se o CEP é limpo."""
    endereco = Endereco(cep="12345-678", logradouro="Av. Central", numero="S/N", cidade="Crato", uf="CE")
    
    assert endereco._cep == "12345678" # Deve armazenar sem traço
    assert "Av. Central, S/N - Crato/CE (CEP: 12345678)" in str(endereco)
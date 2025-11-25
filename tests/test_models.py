import pytest
from models.entidades import Produto, Cliente, Endereco, ProdutoFisico
from models.exceptions import ValorInvalidoError, DocumentoInvalidoError


@pytest.fixture
def produto_valido():
    """Retorna uma instância válida de Produto."""
    return Produto(sku="P001", nome="Notebook Pro", categoria="Eletronicos", preco=4500.00, estoque=10)

@pytest.fixture
def cliente_valido():
    """Retorna uma instância válida de Cliente."""
    return Cliente(nome="João da Silva", cpf="12345678900", email="joao.silva@teste.com")


def test_produto_criacao_e_atributos(produto_valido):
    """Testa se o produto é criado corretamente e se os atributos estão acessíveis."""
    assert produto_valido.preco_unitario == 4500.00 # Acessando via getter
    assert produto_valido.estoque == 10            # Acessando via getter

def test_produto_preco_invalido_deve_falhar():
    """Testa se o encapsulamento impede preços <= 0 (teste negativo)."""
    with pytest.raises(ValorInvalidoError) as excinfo:
        Produto(sku="P002", nome="Monitor", categoria="Eletronicos", preco=0.00, estoque=5)
    assert "maior que zero" in str(excinfo.value)

def test_produto_estoque_invalido_deve_falhar(produto_valido):
    """Testa se o encapsulamento impede estoque negativo via setter (teste negativo)."""
    with pytest.raises(ValorInvalidoError) as excinfo:
        produto_valido.estoque = -5 
    assert "não pode ser negativo" in str(excinfo.value)

def test_produto_ajustar_estoque_com_validacao(produto_valido):
    """Testa se o método ajustar_estoque respeita a validação de estoque."""
    produto_valido.ajustar_estoque(-5) # Baixa
    assert produto_valido.estoque == 5
    
    with pytest.raises(ValorInvalidoError):
        produto_valido.ajustar_estoque(-10) # Tenta ir para -5

def test_produto_igualdade_por_sku(produto_valido):
    """Testa o método mágico __eq__ (igualdade) usando o código único SKU."""
    produto_igual = Produto(sku="P001", nome="Notebook Pro (Outra Marca)", categoria="Outro", preco=1.0, estoque=1)
    
    assert produto_valido == produto_igual

def test_produto_fisico_preco_invalido():
    """Testa se o ProdutoFisico herda a validação de preço do Produto."""
    with pytest.raises(ValorInvalidoError):
        ProdutoFisico(sku="PF01", nome="Cadeira", categoria="Móveis", preco=100.0, estoque=5, peso=0.0)
        

def test_cliente_criacao_e_cpf_limpo(cliente_valido):
    """Testa se o cliente é criado corretamente e se o CPF está limpo."""
    cliente_formatado = Cliente(nome="Pedro", cpf="987.654.321-00", email="pedro@teste.com")
    assert cliente_formatado.cpf == "98765432100" # Deve estar limpo

def test_cliente_cpf_invalido_deve_falhar():
    """Testa se o encapsulamento impede CPFs que não têm 11 dígitos."""
    with pytest.raises(DocumentoInvalidoError) as excinfo:
        Cliente(nome="Mauro", cpf="12345", email="mauro@teste.com")
    assert "11 dígitos" in str(excinfo.value)

def test_cliente_email_invalido_deve_falhar(cliente_valido):
    """Testa se o encapsulamento impede emails com formato inválido."""
    with pytest.raises(DocumentoInvalidoError) as excinfo:
        cliente_valido.email = "email_sem_arroba.com"
    assert "Formato de email inválido" in str(excinfo.value)

def test_cliente_igualdade_por_cpf(cliente_valido):
    """Testa o método mágico __eq__ (igualdade) usando o código único CPF."""
    # Cliente com mesmo CPF, mas nome diferente
    cliente_igual = Cliente(nome="José da Silva", cpf="123.456.789-00", email="jose@outro.com")
    
    assert cliente_valido == cliente_igual

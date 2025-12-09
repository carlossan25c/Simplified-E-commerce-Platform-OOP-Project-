from models.entidades import Produto, ProdutoFisico
from repositories.dados import carregar_dados_loja, salvar_dados_loja 
from models.exceptions import DocumentoInvalidoError
from typing import Optional,List, Dict, Any


def _produto_to_dict(produto: Produto) -> Dict[str, Any]:
    """Converte objeto Produto (ou ProdutoFisico) para dicionário."""
    data = {
        'sku': produto._sku,
        'nome': produto._nome,
        'categoria': produto._categoria,
        'preco_unitario': produto.preco_unitario, 
        'estoque': produto.estoque,             
        'ativo': produto._ativo,
        'tipo': produto.__class__.__name__ # Salva o tipo para reconstrução (Herança)
    }
    if isinstance(produto, ProdutoFisico):
        data['peso'] = produto.peso
    return data

PRODUTOS_KEY = 'produtos'

def _dict_to_produto(data: Dict[str, Any]) -> Optional[Produto]:
    """Converte um dicionário JSON em um objeto Produto ou ProdutoFisico."""
    if not data:
        return None
        
    tipo_produto = data.get('tipo', 'Produto')
    
    if tipo_produto == 'ProdutoFisico':
        return ProdutoFisico(
            sku=data['sku'],
            nome=data['nome'],
            categoria=data['categoria'],
            preco=data['preco_unitario'],
            estoque=data['estoque'],
            peso=data['peso'] # Adicionar peso para o ProdutoFisico
        )
    # Produto base (para produtos digitais, etc.)
    return Produto(
        sku=data['sku'],
        nome=data['nome'],
        categoria=data['categoria'],
        preco=data['preco_unitario'],
        estoque=data['estoque']
    )

def carregar_todos() -> List[Produto]:
    """Carrega a lista de produtos (chave 'produtos')."""
    dados_completos = carregar_dados_loja()
    produtos_data = dados_completos.get("produtos", []) 
    return [_dict_to_produto(d) for d in produtos_data]

def buscar_por_sku(sku: str) -> Optional[Produto]:
    """Busca um produto pelo SKU na lista persistida."""
    dados_completos = carregar_dados_loja()
    produtos_data = dados_completos.get(PRODUTOS_KEY, [])
    
    # Encontra o dicionário do produto
    produto_dict = next((d for d in produtos_data if d['sku'] == sku), None)
    
    # Retorna o objeto completo ou None
    return _dict_to_produto(produto_dict)

def salvar_produto(produto: Produto):
    """Salva ou atualiza um produto."""
    
    dados_completos = carregar_dados_loja()
    produtos = dados_completos.get("produtos", [])
    
    # Validação de Unicidade
    for p_data in produtos:
        if p_data['sku'] == produto._sku and p_data['sku'] != produto._sku: 
            raise DocumentoInvalidoError(f"SKU {produto._sku} já cadastrado.")
    
    # Atualiza ou Adiciona
    produto_dict = _produto_to_dict(produto)
    
    encontrado = False
    for i, p_data in enumerate(produtos):
        if p_data['sku'] == produto._sku:
            produtos[i] = produto_dict 
            encontrado = True
            break
            
    if not encontrado:
        produtos.append(produto_dict)
        
    dados_completos["produtos"] = produtos
    salvar_dados_loja(dados_completos)
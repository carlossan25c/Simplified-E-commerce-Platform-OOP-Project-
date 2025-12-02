from models.entidades import Produto, ProdutoFisico
from repositories.dados import carregar_dados_loja, salvar_dados_loja 
from models.exceptions import DocumentoInvalidoError
from typing import List, Dict, Any


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

def _dict_to_produto(data: Dict[str, Any]) -> Produto:
    """Converte dicionário JSON para objeto Produto ou ProdutoFisico."""
    if data.get('tipo') == 'ProdutoFisico':
        return ProdutoFisico(
            sku=data['sku'],
            nome=data['nome'],
            categoria=data['categoria'],
            preco=data['preco_unitario'],
            estoque=data['estoque'],
            peso=data['peso'],
            ativo=data['ativo']
        )
    else:
        return Produto(
            sku=data['sku'],
            nome=data['nome'],
            categoria=data['categoria'],
            preco=data['preco_unitario'],
            estoque=data['estoque'],
            ativo=data['ativo']
        )


def carregar_todos() -> List[Produto]:
    """Carrega a lista de produtos (chave 'produtos')."""
    dados_completos = carregar_dados_loja()
    produtos_data = dados_completos.get("produtos", []) 
    return [_dict_to_produto(d) for d in produtos_data]

def buscar_por_sku(sku: str) -> Produto | None:
    """Busca um produto pelo código único (SKU)."""
    produtos = carregar_todos()
    for produto in produtos:
        if produto._sku == sku:
            return produto
    return None

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
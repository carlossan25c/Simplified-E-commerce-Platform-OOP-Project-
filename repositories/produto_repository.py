from models.entidades import Produto, ProdutoFisico
from repositories.dados import carregar_dados_loja, salvar_dados_loja
from models.exceptions import ValorInvalidoError
from typing import List, Dict, Any


def _produto_to_dict(produto: Produto) -> Dict[str, Any]:
    data = {
        'sku': produto.sku,
        'nome': produto.nome,
        'categoria': produto._categoria,
        'preco_unitario': produto.preco_unitario,
        'estoque': produto.estoque,
        'ativo': produto._ativo,
        # Guarda o tipo para saber qual classe desserializar
        'tipo': 'fisico' if isinstance(produto, ProdutoFisico) else 'simples'
    }
    # Adiciona o atributo 'peso' somente se for ProdutoFisico
    if isinstance(produto, ProdutoFisico):
        data['peso'] = produto.peso
    return data

def _dict_to_produto(data: Dict[str, Any]) -> Produto:
    if data.get('tipo') == 'fisico':
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
    dados_completos = carregar_dados_loja()
    produtos_data = dados_completos.get("produtos", []) 
    return [_dict_to_produto(d) for d in produtos_data]

def buscar_por_sku(sku: str) -> Produto | None:
    produtos = carregar_todos()
    for produto in produtos:
        if produto.sku == sku:
            return produto
    return None

def salvar(produto: Produto):
    dados_completos = carregar_dados_loja()
    produtos = dados_completos.get("produtos", [])
    
    produto_dict = _produto_to_dict(produto)
    
    # Atualiza ou Adiciona
    encontrado = False
    for i, p_data in enumerate(produtos):
        if p_data['sku'] == produto.sku:
            produtos[i] = produto_dict # Atualiza o objeto
            encontrado = True
            break
            
    if not encontrado:
        produtos.append(produto_dict)
        
    dados_completos["produtos"] = produtos
    salvar_dados_loja(dados_completos)
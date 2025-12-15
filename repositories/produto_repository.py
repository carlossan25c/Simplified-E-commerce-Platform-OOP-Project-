import json
import os
from typing import List, Optional, Dict, Any
from models.entidades import Produto, ProdutoFisico
from models.exceptions import EntidadeNaoEncontradaError

# Constantes e Funções Auxiliares de Gerenciamento de Arquivo

NOME_ARQUIVO = 'loja.json'

def _get_file_path() -> str:
    """Gera o caminho completo para o arquivo loja.json na pasta data/."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_dir, 'data', NOME_ARQUIVO)

def _carregar_dados() -> Dict[str, Any]:
    """Carrega todo o conteúdo do arquivo loja.json."""
    caminho = _get_file_path()
    
    # Estrutura base para inicialização
    estrutura_base = {
        'clientes': [], 
        'produtos': [], 
        'pedidos': [],
        'cupons': [] # Incluído para compatibilidade
    }
    
    if not os.path.exists(caminho):
        os.makedirs(os.path.dirname(caminho), exist_ok=True)
        with open(caminho, 'w', encoding='utf-8') as f:
            json.dump(estrutura_base, f, indent=4, ensure_ascii=False)
        return estrutura_base
        
    try:
        with open(caminho, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        # Em caso de erro, retorna a estrutura base e tenta salvar o arquivo novamente
        print(f"⚠️ Aviso: Arquivo {NOME_ARQUIVO} corrompido ou vazio. Recriando...")
        _salvar_dados(estrutura_base)
        return estrutura_base

def _salvar_dados(dados: Dict[str, Any]):
    """Salva todo o conteúdo no arquivo loja.json."""
    caminho = _get_file_path()
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    with open(caminho, 'w', encoding='utf-8') as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)

# Funções de Desserialização

def _deserializar_produto(dados_produto: Dict[str, Any]) -> Produto:
    """Converte um dicionário de dados em um objeto Produto ou ProdutoFisico."""
    
    # Usa o campo 'tipo' para determinar a classe correta
    tipo = dados_produto.get('tipo', 'Produto')
    
    if tipo == 'ProdutoFisico' and 'peso' in dados_produto:
        return ProdutoFisico(
            sku=dados_produto['sku'],
            nome=dados_produto['nome'],
            categoria=dados_produto['categoria'],
            preco_unitario=dados_produto['preco_unitario'],
            estoque=dados_produto.get('estoque', 0),
            peso=dados_produto['peso'],
            is_ativo=dados_produto.get('is_ativo', True)
        )
    else:
        # Produto ou Produto Digital
        return Produto(
            sku=dados_produto['sku'],
            nome=dados_produto['nome'],
            categoria=dados_produto['categoria'],
            preco_unitario=dados_produto['preco_unitario'],
            estoque=dados_produto.get('estoque', 0),
            is_ativo=dados_produto.get('is_ativo', True)
        )

# Funções de Repositório

def salvar(produto: Produto):
    """
    Salva ou atualiza um produto. Se o produto já existir (pelo SKU), 
    ele é substituído. Caso contrário, é adicionado.
    """
    dados = _carregar_dados()
    
    lista_produtos = dados.get('produtos', [])
    
    # Procura o índice do produto pelo SKU
    try:
        idx = next(i for i, p in enumerate(lista_produtos) if p['sku'] == produto.sku)
        # Produto encontrado: Substitui o registro existente
        lista_produtos[idx] = produto.to_dict()
    except StopIteration:
        # Produto não encontrado: Adiciona novo registro
        lista_produtos.append(produto.to_dict())
        
    dados['produtos'] = lista_produtos
    _salvar_dados(dados)

def buscar_por_sku(sku: str) -> Optional[Produto]:
    """Busca um produto pelo SKU."""
    sku = sku.strip().upper()
    dados = _carregar_dados()
    
    for p in dados.get('produtos', []):
        if p['sku'] == sku:
            return _deserializar_produto(p)
            
    return None

def carregar_todos() -> List[Produto]:
    """Retorna a lista completa de todos os produtos."""
    dados = _carregar_dados()
    return [_deserializar_produto(p) for p in dados.get('produtos', [])]
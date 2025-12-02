import json
import os
from models.exceptions import PersistenciaError
from typing import Dict, Any

DATA_FOLDER = 'data'
LOJA_FILE = 'loja.json'

def _get_file_path(nome_arquivo: str = LOJA_FILE) -> str:
    """Gera o caminho completo para o arquivo JSON na pasta data/."""
    # Navega para o root (dois níveis acima)
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_dir, DATA_FOLDER, nome_arquivo)

def carregar_dados_loja() -> Dict[str, Any]:
    """Lê o conteúdo do arquivo loja.json, garantindo a estrutura base."""
    caminho = _get_file_path(LOJA_FILE)
    
    estrutura_base = {"clientes": [], "produtos": [], "pedidos": [], "cupons": []}
    
    if not os.path.exists(caminho) or os.path.getsize(caminho) == 0:
        return estrutura_base
    
    try:
        with open(caminho, 'r', encoding='utf-8') as f:
            dados = json.load(f)
            return {**estrutura_base, **dados}
    except json.JSONDecodeError:
        raise PersistenciaError(f"Erro: O arquivo {LOJA_FILE} está corrompido.")
    except Exception as e:
        raise PersistenciaError(f"Erro ao carregar dados de {LOJA_FILE}: {e}")

def salvar_dados_loja(dados: Dict[str, Any]):
    """Salva o dicionário completo de dados no arquivo loja.json."""
    caminho = _get_file_path(LOJA_FILE)
    
    try:
        os.makedirs(os.path.dirname(caminho), exist_ok=True)
        with open(caminho, 'w', encoding='utf-8') as f:
            json.dump(dados, f, indent=4, ensure_ascii=False)
    except Exception as e:
        raise PersistenciaError(f"Erro ao salvar dados em {LOJA_FILE}: {e}")
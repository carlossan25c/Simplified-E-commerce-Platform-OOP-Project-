import json
import os
from typing import Dict, Any

SETTINGS_FILE = 'settings.json'

def _get_file_path(nome_arquivo: str = SETTINGS_FILE) -> str:
    """Gera o caminho completo para o arquivo settings.json na pasta data/."""
    # Assume que repositories/ está um nível acima de data/
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_dir, 'data', nome_arquivo)

def carregar_settings() -> Dict[str, Any]:
    """Lê o conteúdo do arquivo settings.json."""
    caminho = _get_file_path(SETTINGS_FILE)
    
    # Estrutura base com valores padrão
    estrutura_base = {
        "regra_estoque": {
            "limite_seguranca": 5, 
            "alerta_percentual": 0.15 
        },
        "frete": {
            "valor_padrao": 25.0,
            "prazo_dias": 5
        }
    }
    
    # 1. Tenta criar o arquivo e a estrutura de diretórios se não existir
    if not os.path.exists(caminho):
        try:
            os.makedirs(os.path.dirname(caminho), exist_ok=True)
            with open(caminho, 'w', encoding='utf-8') as f:
                json.dump(estrutura_base, f, indent=4, ensure_ascii=False)
            return estrutura_base
        except:
            # Em caso de falha ao criar/escrever, retorna a estrutura base em memória
            return estrutura_base 
            
    # 2. Tenta ler o arquivo existente
    try:
        with open(caminho, 'r', encoding='utf-8') as f:
            dados = json.load(f)
            # Mescla: garante que valores persistidos (dados) sobrescrevam os padrões (estrutura_base),
            # mas mantém os padrões para chaves que faltam no arquivo.
            return {**estrutura_base, **dados} 
    except:
        # Se houver erro de leitura ou JSONDecodeError, retorna a estrutura base
        return estrutura_base
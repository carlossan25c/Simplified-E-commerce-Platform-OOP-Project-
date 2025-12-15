import json
import os
import re
from typing import List, Optional, Dict, Any
from models.entidades import Cliente, Endereco
from models.exceptions import EntidadeNaoEncontradaError, DocumentoInvalidoError
from datetime import datetime

# Constantes e Funções Auxiliares de Gerenciamento de Arquivo

NOME_ARQUIVO = 'loja.json'

def _get_file_path() -> str:
    """Gera o caminho completo para o arquivo loja.json na pasta data/."""
    # Assume que repositories/ está um nível acima de data/
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
        # Cria o arquivo com a estrutura base se não existir
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
    os.makedirs(os.path.dirname(caminho), exist_ok=True) # Garante que a pasta existe
    with open(caminho, 'w', encoding='utf-8') as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)

# Funções de Desserialização

def _deserializar_cliente(dados_cliente: Dict[str, Any]) -> Cliente:
    """Converte um dicionário de dados em um objeto Cliente."""
    
    enderecos = []
    for end_data in dados_cliente.get('enderecos', []):
        enderecos.append(Endereco(
            cep=end_data['cep'],
            logradouro=end_data['logradouro'],
            numero=end_data['numero'],
            cidade=end_data['cidade'],
            uf=end_data['uf'],
            complemento=end_data.get('complemento')
        ))
        
    data_cadastro = datetime.fromisoformat(dados_cliente['data_cadastro']) \
        if dados_cliente.get('data_cadastro') else None
        
    return Cliente(
        cpf=dados_cliente['cpf'],
        nome=dados_cliente['nome'],
        email=dados_cliente['email'],
        data_cadastro=data_cadastro,
        enderecos=enderecos
    )

# Funções de Repositório

def salvar(cliente: Cliente):
    """
    Salva ou atualiza um cliente. Se o cliente já existir (pelo CPF), 
    ele é substituído. Caso contrário, é adicionado.
    """
    dados = _carregar_dados()
    
    # Limpa CPF para comparação
    cpf_limpo = re.sub(r'\D', '', cliente.cpf)
    
    lista_clientes = dados.get('clientes', [])
    
    # Procura o índice do cliente
    try:
        idx = next(i for i, c in enumerate(lista_clientes) if re.sub(r'\D', '', c['cpf']) == cpf_limpo)
        # Cliente encontrado: Substitui o registro existente
        lista_clientes[idx] = cliente.to_dict()
    except StopIteration:
        # Cliente não encontrado: Adiciona novo registro
        lista_clientes.append(cliente.to_dict())
        
    dados['clientes'] = lista_clientes
    _salvar_dados(dados)

def buscar_por_cpf(cpf: str) -> Optional[Cliente]:
    """Busca um cliente pelo CPF (ignorando formatação)."""
    
    if not Cliente.validar_cpf(cpf):
        raise DocumentoInvalidoError("Formato de CPF inválido.")
        
    cpf_limpo = re.sub(r'\D', '', cpf)
    dados = _carregar_dados()
    
    for c in dados.get('clientes', []):
        if re.sub(r'\D', '', c['cpf']) == cpf_limpo:
            return _deserializar_cliente(c)
            
    return None

def carregar_todos() -> List[Cliente]:
    """Retorna a lista completa de todos os clientes."""
    dados = _carregar_dados()
    return [_deserializar_cliente(c) for c in dados.get('clientes', [])]
from models.entidades import Cliente
from repositories.dados import carregar_dados_loja, salvar_dados_loja 
from models.exceptions import DocumentoInvalidoError
from typing import List, Dict, Any


def _cliente_to_dict(cliente: Cliente) -> Dict[str, Any]:
    """Converte objeto Cliente para dicionário (Serialização)."""
    return {
        'cpf': cliente.cpf,
        'nome': cliente._nome,
        'email': cliente.email,
        # Serializa endereços (para o objeto Endereco ser reconstruído se necessário)
        'enderecos': [{'cep': e._cep, 'logradouro': e._logradouro, 'numero': e._numero, 'cidade': e._cidade, 'uf': e._uf} for e in cliente._enderecos]
    }

def _dict_to_cliente(data: Dict[str, Any]) -> Cliente:
    """Converte dicionário JSON para objeto Cliente (Desserialização)."""
    cliente = Cliente(
        nome=data['nome'],
        cpf=data['cpf'],
        email=data['email']
    )
    # TODO: Reconstruir endereços, se necessário (para a Semana 3, a base já é suficiente)
    return cliente


def carregar_todos() -> List[Cliente]:
    """Carrega a lista de clientes (chave 'clientes')."""
    dados_completos = carregar_dados_loja()
    clientes_data = dados_completos.get("clientes", []) 
    return [_dict_to_cliente(d) for d in clientes_data]

def buscar_por_cpf(cpf: str) -> Cliente | None:
    """Busca um cliente pelo código único (CPF)."""
    clientes = carregar_todos()
    for cliente in clientes:
        if cliente.cpf == cpf:
            return cliente
    return None

def salvar_cliente(cliente: Cliente):
    """Salva ou atualiza um cliente."""
    
    dados_completos = carregar_dados_loja()
    clientes = dados_completos.get("clientes", [])
    
    # Validação de Unicidade
    for c_data in clientes:
        # Verifica se o CPF/Email já existe EM OUTRO CLIENTE
        if c_data['cpf'] == cliente.cpf and c_data['cpf'] != cliente.cpf: 
            raise DocumentoInvalidoError(f"CPF {cliente.cpf} já cadastrado no sistema.")
        if c_data['email'] == cliente.email and c_data['cpf'] != cliente.cpf:
            raise DocumentoInvalidoError(f"Email {cliente.email} já cadastrado no sistema.")
    
    # Atualiza ou Adiciona
    cliente_dict = _cliente_to_dict(cliente)
    
    encontrado = False
    for i, c_data in enumerate(clientes):
        if c_data['cpf'] == cliente.cpf:
            clientes[i] = cliente_dict # Atualiza o objeto
            encontrado = True
            break
            
    if not encontrado:
        clientes.append(cliente_dict)
        
    dados_completos["clientes"] = clientes
    salvar_dados_loja(dados_completos)
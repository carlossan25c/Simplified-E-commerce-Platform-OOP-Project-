from models.entidades import Cliente, Endereco
from repositories.dados import carregar_dados_loja, salvar_dados_loja 
from models.exceptions import DocumentoInvalidoError
from typing import List, Dict, Any


def _cliente_to_dict(cliente: Cliente) -> Dict[str, Any]:
    # Serialização do Cliente e Endereços (acessando atributos privados para JSON)
    enderecos_data = [{'cep': e._cep, 'logradouro': e._logradouro, 'numero': e._numero, 'cidade': e._cidade, 'uf': e._uf} for e in cliente.enderecos]
    
    return {
        'cpf': cliente.cpf,
        'nome': cliente.nome,
        'email': cliente.email,
        'enderecos': enderecos_data
    }

def _dict_to_cliente(data: Dict[str, Any]) -> Cliente:
    # Desserialização para objeto Cliente
    cliente = Cliente(
        nome=data['nome'],
        cpf=data['cpf'],
        email=data['email']
    )
    
    # Reconstrução dos objetos Endereco (necessário para a Opção 7)
    for end_data in data.get('enderecos', []):
        endereco = Endereco(
            cep=end_data['cep'],
            logradouro=end_data['logradouro'],
            numero=end_data['numero'],
            cidade=end_data['cidade'],
            uf=end_data['uf']
        )
        cliente.adicionar_endereco(endereco)
        
    return cliente


def carregar_todos() -> List[Cliente]:
    dados_completos = carregar_dados_loja()
    clientes_data = dados_completos.get("clientes", []) 
    return [_dict_to_cliente(d) for d in clientes_data]

def buscar_por_cpf(cpf: str) -> Cliente | None:
    clientes = carregar_todos()
    for cliente in clientes:
        if cliente.cpf == cpf:
            return cliente
    return None

def salvar(cliente: Cliente):
    dados_completos = carregar_dados_loja()
    clientes = dados_completos.get("clientes", [])
    
    cliente_dict = _cliente_to_dict(cliente)
    
    for c_data in clientes:
        # Se for um cliente diferente (CPF !=)
        if c_data['cpf'] != cliente.cpf:
            if c_data['email'] == cliente.email: 
                raise DocumentoInvalidoError(f"Email {cliente.email} já cadastrado por outro cliente.")
            
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
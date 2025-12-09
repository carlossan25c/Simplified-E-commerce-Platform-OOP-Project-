from datetime import date
from models.entidades import Cliente, ProdutoFisico, Endereco
from models.transacoes import Frete, Cupom
from models.vendas import Carrinho
from repositories import cliente_repository, produto_repository
from services.pedido_service import PedidoService
from services.relatorio_service import RelatorioService
from models.exceptions import DocumentoInvalidoError, ValorInvalidoError, PersistenciaError
from repositories import cliente_repository
from models.entidades import Cliente

CARRINHO_SESSAO = Carrinho()

def inicializar_dados_seed():
    """Garante que pelo menos um cliente e um produto estejam no sistema."""
    try:
        # Cliente de Teste
        if not cliente_repository.buscar_por_cpf("12345678901"):
            cliente1 = Cliente(nome="Alice Silva", cpf="12345678901", email="alice@teste.com")
            cliente1.adicionar_endereco(Endereco(cep="63040440", logradouro="Rua C", numero="100", cidade="Juazeiro", uf="CE"))
            cliente_repository.salvar_cliente(cliente1)

        # Produto de Teste (Estoque baixo para testar a regra de segurança)
        if not produto_repository.buscar_por_sku("LIV-001"):
            produtoA = ProdutoFisico(sku="LIV-001", nome="POO Avançada", categoria="Livros", preco=120.00, estoque=8, peso=0.5)
            produto_repository.salvar_produto(produtoA)
    except Exception as e:
        # Usamos PersistenciaError se a falha for no I/O, mas Exception é um bom fallback
        print(f"\n[ERRO] Falha ao carregar dados iniciais (Verifique o arquivo JSON): {e}")
        
def mostrar_menu():
    print("\n" + "="*30)
    print("      MENU PRINCIPAL")
    print("="*30)
    print("1. Adicionar produto ao carrinho")
    print("2. Visualizar carrinho")
    print("3. Finalizar compra (Checkout)")
    print("4. Cadastrar Cliente") 
    print("9. Gerar Relatório de Vendas")
    print("0. Sair")
    print("="*30)

def listar_produtos():
    print("\n--- PRODUTOS DISPONÍVEIS ---")
    produtos = produto_repository.carregar_todos()
    if not produtos:
        print("Nenhum produto cadastrado.")
        return
        
    for i, p in enumerate(produtos):
        # USANDO PROPRIEDADES PÚBLICAS (sku, nome, estoque)
        print(f"[{p.sku}] {p.nome} | R$ {p.preco_unitario:.2f} | Estoque: {p.estoque}")

# Nova função para Opção 2
def visualizar_carrinho():
    print("\n--- SEU CARRINHO ---")
    if not CARRINHO_SESSAO.itens: # USANDO PROPRIEDADE PÚBLICA DE CARRINHO
        print("Seu carrinho está vazio.")
        return
        
    for item in CARRINHO_SESSAO.itens:
        print(f"-> {item.quantidade}x {item.produto.nome} (R$ {item.calcular_subtotal_item():.2f})")
    
    print("-" * 30)
    print(f"SUBTOTAL GERAL: R$ {CARRINHO_SESSAO.calcular_subtotal():.2f}")


def cadastrar_cliente():
    print("\n--- CADASTRO DE NOVO CLIENTE ---")
    
    cpf = input("Digite o CPF (apenas números): ").strip()
    nome = input("Digite o Nome Completo: ").strip()
    email = input("Digite o E-mail: ").strip()
    
    if not all([cpf, nome, email]):
        print("\nERRO: Todos os campos são obrigatórios.")
        return

    try:
        # 1. Checa se o cliente já existe (Regra de Negócio: CPF único)
        if cliente_repository.buscar_por_cpf(cpf):
             print("\nERRO: Cliente com este CPF já cadastrado.")
             return
             
        # 2. Instancia o objeto Cliente (Corrigido: sem 'enderecos' no construtor)
        novo_cliente = Cliente(
            cpf=cpf, 
            nome=nome, 
            email=email
        )
        
        # 3. COLETA E ADICIONA O ENDEREÇO
        print("\n--- Dados do Endereço Principal ---")
        cep = input("CEP: ").strip()
        logradouro = input("Logradouro (Rua, Av.): ").strip()
        numero = input("Número: ").strip()
        cidade = input("Cidade: ").strip()
        uf = input("UF (Ex: CE): ").strip().upper()
        
        # Cria a instância de Endereco
        novo_endereco = Endereco(cep, logradouro, numero, cidade, uf)
        
        # Usa o método de negócio do Cliente para associar o endereço
        novo_cliente.adicionar_endereco(novo_endereco)
        
        print("✅ Endereço adicionado ao cliente.")
        
        cliente_repository.salvar_cliente(novo_cliente)
        
        print(f"\n✅ SUCESSO! Cliente {nome} cadastrado com sucesso.")
        
    except DocumentoInvalidoError as e:
        print(f"\nERRO NO CADASTRO: {e}")
        print("Verifique o formato do CPF (apenas números) e tente novamente.")
    except ValorInvalidoError as e:
        print(f"\nERRO NO CADASTRO: {e}")
        print("Verifique o formato do Email e tente novamente.")
    except Exception as e:
        print(f"\nERRO INESPERADO AO CADASTRAR: {e}")

def adicionar_ao_carrinho():
    listar_produtos()
    sku = input("Digite o SKU do produto: ").strip()
    try:
        produto = produto_repository.buscar_por_sku(sku)
        if not produto:
            print(f"⚠️ Produto com SKU '{sku}' não encontrado.")
            return

        quantidade = int(input(f"Quantas unidades de '{produto.nome}' deseja adicionar? "))
        
        CARRINHO_SESSAO.adicionar_item(produto, quantidade)
        print(f"✅ {quantidade}x {produto.nome} adicionados ao carrinho!")
        print(f"   Subtotal do Carrinho: R$ {CARRINHO_SESSAO.calcular_subtotal():.2f}")

    except ValueError:
        print("⚠️ Quantidade inválida. Digite um número inteiro.")
    except Exception as e:
        print(f"❌ Erro ao adicionar: {e}")

def fechar_pedido():
    if not CARRINHO_SESSAO.itens: 
        print("⚠️ O carrinho está vazio. Adicione itens antes de fechar o pedido.")
        return

    print("\n--- FECHAMENTO DE PEDIDO ---")
    
    # SOLICITAÇÃO DO CLIENTE (Melhor que CPF fixo)
    cpf_cliente = input("Digite seu CPF cadastrado para continuar: ").strip()
    cliente = cliente_repository.buscar_por_cpf(cpf_cliente)
    
    if not cliente:
        print(f"⚠️ Cliente com CPF {cpf_cliente} não encontrado. Por favor, cadastre-se (Opção 4).")
        return
        
    print(f"Cliente: {cliente.nome} | CPF: {cliente.cpf}")
    
    # 1. Obter Frete e Cupom de Teste (Exemplo)
    frete = Frete(valor=25.0, prazo_dias=5)
    cupom = Cupom(codigo="TESTE10", valor=10.0, is_percentual=True, validade=date(2099, 12, 31))
    
    print(f"Cupom aplicado: {cupom.codigo} | Frete: R$ {frete.valor:.2f}")

    try:
        # 2. Executar o Serviço (Regras de Negócio, Validações, Baixa de Estoque)
        pedido = PedidoService.fechar_pedido_a_partir_do_carrinho(cliente, CARRINHO_SESSAO, frete, cupom)
        
        print(f"\n=========================================")
        print(f"🎉 PEDIDO FECHADO COM SUCESSO! Código: {pedido.codigo_pedido[:8]}...")
        print(f" Total: R$ {pedido.total:.2f}") # USANDO PROPRIEDADE PÚBLICA
        print(f" Estoque atualizado no JSON.")
        print(f"=========================================")
        
        # Limpar o carrinho após sucesso
        CARRINHO_SESSAO.itens.clear() 

    except ValorInvalidoError as e:
        # Tratamento de Exceções de Regra de Negócio (Ex: Estoque de Segurança, Cupom inválido)
        print(f"\n❌ ERRO NA VENDA: {e}")
        print("   O carrinho não foi finalizado. Verifique estoque ou regras.")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")

def visualizar_relatorio():
    print("\n--- RELATÓRIO DE FATURAMENTO (OCUPAÇÃO) ---")
    try:
        # Chamada do Serviço
        relatorio = RelatorioService.relatorio_ocupacao_por_periodo(periodo='dia')
        
        if not relatorio:
            print("Nenhum pedido encontrado para o relatório.")
            return

        for dia, total in relatorio.items():
            print(f"🗓️ {dia}: R$ {total:.2f}")

    except Exception as e:
        print(f"❌ Erro ao gerar relatório: {e}")

def main():
    inicializar_dados_seed()
    
    while True:
        mostrar_menu() # Nome da função corrigido (não era exibir_menu_principal)
        
        escolha = input("Selecione uma opção: ").strip()
        
        # O mapeamento do menu foi corrigido para bater com a função mostrar_menu()
        if escolha == '1':
            adicionar_ao_carrinho() # Menu 1: Adiciona ao carrinho
        elif escolha == '2':
            visualizar_carrinho() # Menu 2: Visualiza o carrinho (Função nova)
        elif escolha == '3':
            fechar_pedido() # Menu 3: Checkout
        elif escolha == '4':
            cadastrar_cliente() # Menu 4: Cadastra Cliente
        elif escolha == '9':
            visualizar_relatorio() # Menu 9: Relatório
        elif escolha == '0':
            print("Saindo do CLI. Até logo!")
            break
        else:
            print("Opção inválida. Tente novamente.")

if __name__ == "__main__":
    main()
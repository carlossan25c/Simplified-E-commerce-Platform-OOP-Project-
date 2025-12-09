from datetime import date
from models.entidades import Cliente, ProdutoFisico, Endereco
from models.transacoes import Frete, Cupom
from models.vendas import Carrinho
from repositories import cliente_repository, produto_repository
from services.pedido_service import PedidoService
from services.relatorio_service import RelatorioService
from models.exceptions import DocumentoInvalidoError, ValorInvalidoError

CARRINHO_SESSAO = Carrinho()

def inicializar_dados_seed():
    """Garante que pelo menos um cliente e um produto estejam no sistema."""
    
    # Cliente (garante que o cliente de teste exista)
    try:
        if not cliente_repository.buscar_por_cpf("12345678901"):
            cliente1 = Cliente(nome="Alice Silva", cpf="12345678901", email="alice@teste.com")
            cliente1.adicionar_endereco(Endereco(cep="63040440", logradouro="Rua C", numero="100", cidade="Juazeiro", uf="CE"))
            cliente_repository.salvar_cliente(cliente1)

        # Produto (garante que o produto com estoque baixo exista)
        if not produto_repository.buscar_por_sku("LIV-001"):
            # Estoque baixo para testar a regra de segurança (limite 5)
            produtoA = ProdutoFisico(sku="LIV-001", nome="POO Avançada", categoria="Livros", preco=120.00, estoque=8, peso=0.5)
            produto_repository.salvar_produto(produtoA)
    except Exception as e:
        print(f"\n[ERRO] Falha ao carregar dados iniciais: {e}")
        

def exibir_menu_principal():
    print("\n=========================================")
    print("💻 CLI DE VENDAS")
    print("=========================================")
    print("1. Listar Produtos em Estoque")
    print("2. Adicionar Produto ao Carrinho")
    print("3. Fechar Pedido")
    print("4. Visualizar Relatório de Faturamento (Ocupação)")
    print("0. Sair")
    print(f"🛒 Itens no Carrinho: {len(CARRINHO_SESSAO)}")
    print("-----------------------------------------")

def listar_produtos():
    print("\n--- PRODUTOS DISPONÍVEIS ---")
    produtos = produto_repository.carregar_todos()
    if not produtos:
        print("Nenhum produto cadastrado.")
        return
        
    for i, p in enumerate(produtos):
        print(f"[{p._sku}] {p._nome} | R$ {p.preco_unitario:.2f} | Estoque: {p.estoque}")

def adicionar_ao_carrinho():
    listar_produtos()
    sku = input("Digite o SKU do produto: ").strip()
    try:
        produto = produto_repository.buscar_por_sku(sku)
        if not produto:
            print(f"⚠️ Produto com SKU '{sku}' não encontrado.")
            return

        quantidade = int(input(f"Quantas unidades de '{produto._nome}' deseja adicionar? "))
        
        CARRINHO_SESSAO.adicionar_item(produto, quantidade)
        print(f"✅ {quantidade}x {produto._nome} adicionados ao carrinho!")
        print(f"   Subtotal do Carrinho: R$ {CARRINHO_SESSAO.calcular_subtotal():.2f}")

    except ValueError:
        print("⚠️ Quantidade inválida.")
    except Exception as e:
        print(f"❌ Erro ao adicionar: {e}")

def fechar_pedido():
    if not CARRINHO_SESSAO._itens:
        print("⚠️ O carrinho está vazio. Adicione itens antes de fechar o pedido.")
        return

    print("\n--- FECHAMENTO DE PEDIDO ---")
    # Para simplificar, usamos o cliente de teste
    cliente = cliente_repository.buscar_por_cpf("12345678901")
    
    if not cliente:
        print("⚠️ Cliente de teste (12345678901) não encontrado. Reinicie o sistema.")
        return
        
    print(f"Cliente: {cliente._nome}")
    print(f"Subtotal: R$ {CARRINHO_SESSAO.calcular_subtotal():.2f}")
    
    # 1. Obter Frete e Cupom de Teste
    frete = Frete(valor=25.0, prazo_dias=5)
    cupom = Cupom(codigo="TESTE10", valor=10.0, is_percentual=True, validade=date(2099, 12, 31))
    
    print(f"Cupom aplicado: {cupom._codigo} | Frete: R$ {frete.valor:.2f}")

    try:
        # 2. Executar o Serviço (Aqui as Regras de Negócio e Validações Disparam)
        pedido = PedidoService.fechar_pedido_a_partir_do_carrinho(cliente, CARRINHO_SESSAO, frete, cupom)
        
        print(f"\n=========================================")
        print(f"🎉 PEDIDO FECHADO COM SUCESSO! Código: {pedido._codigo_pedido[:8]}...")
        print(f" Total: R$ {pedido._total:.2f}")
        print(f" Estoque atualizado no JSON.")
        print(f"=========================================")

    except ValorInvalidoError as e:
        # 3. Tratamento de Exceções de Regra de Negócio
        print(f"\n❌ ERRO NA VENDA: {e}")
        print("   O carrinho não foi finalizado. Verifique estoque ou regras.")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")

def visualizar_relatorio():
    print("\n--- RELATÓRIO DE FATURAMENTO (OCUPAÇÃO) ---")
    try:
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
        exibir_menu_principal()
        
        escolha = input("Selecione uma opção: ").strip()
        
        if escolha == '1':
            listar_produtos()
        elif escolha == '2':
            adicionar_ao_carrinho()
        elif escolha == '3':
            fechar_pedido()
        elif escolha == '4':
            visualizar_relatorio()
        elif escolha == '0':
            print("Saindo do CLI. Até logo!")
            break
        else:
            print("Opção inválida. Tente novamente.")

if __name__ == "__main__":
    main()
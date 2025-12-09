from models.entidades import Cliente, Produto, Endereco, ProdutoFisico
from models.vendas import Carrinho, Pedido 
from models.exceptions import ValorInvalidoError, DocumentoInvalidoError
from datetime import datetime
from models.transacoes import Frete, Cupom
import repositories.cliente_repository as cliente_repository
import repositories.produto_repository as produto_repository
import repositories.pedido_repository as pedido_repository
import services.pedido_service as pedido_service

# Variável Global de Sessão
CARRINHO_SESSAO = Carrinho() 

def mostrar_menu():
    print("\n" + "="*35)
    print("      SISTEMA SIMPLIFICADO E-COMMERCE")
    print("="*35)
    
    print("1. Adicionar produto ao carrinho")
    print("2. Visualizar carrinho")
    print("3. Finalizar compra (Checkout)")
    print("4. Cadastrar Cliente") 
    print("5. Visualizar Status do Pedido")
    print("6. Gestão de Produtos (Cadastro, Alterar Estoque)")
    print("7. Gerenciar Endereços de Cliente")
    print("8. Avançar Status do Pedido (Mudar para PAGO, ENVIADO, etc.)")
    print("9. Gerar Relatório de Vendas")
    print("0. Sair")
    print("="*35)

def listar_produtos():
    print("\n--- PRODUTOS DISPONÍVEIS ---")
    
    try:
        produtos = produto_repository.carregar_todos() 
    except AttributeError:
        produtos = [
            ProdutoFisico("SKU001", "Livro POO Python", "Educação", 59.90, 10, 0.8),
            Produto("SKU002", "Ebook PyTest", "Digital", 29.90, 999, 1),
        ]

    if not produtos:
        print("Nenhum produto cadastrado.")
        return []

    for p in produtos:
        print(f"[{p.sku}] {p.nome} | R$ {p.preco_unitario:.2f} | Estoque: {p.estoque}")
    return produtos


def adicionar_ao_carrinho():
    produtos = listar_produtos()
    if not produtos:
        return

    print("\n--- ADICIONAR AO CARRINHO ---")
    sku = input("Digite o SKU do produto: ").strip().upper()
    
    produto_selecionado = next((p for p in produtos if p.sku == sku), None)

    if not produto_selecionado:
        print("⚠️ SKU não encontrado.")
        return

    try:
        quantidade = int(input("Digite a quantidade: "))
        if quantidade <= 0:
             raise ValorInvalidoError("A quantidade deve ser positiva.")
        
        if quantidade > produto_selecionado.estoque:
             print(f"❌ Erro: Estoque insuficiente. Máximo disponível: {produto_selecionado.estoque}")
             return

        CARRINHO_SESSAO.adicionar_item(produto_selecionado, quantidade)
        print(f"✅ Adicionado: {quantidade}x {produto_selecionado.nome} ao carrinho.")

    except ValueError:
        print("❌ Quantidade inválida. Digite um número.")
    except ValorInvalidoError as e:
        print(f"❌ Erro: {e}")
        

def visualizar_carrinho():
    print("\n--- SEU CARRINHO ---")
    
    if not CARRINHO_SESSAO.itens: 
        print("🛒 O carrinho está vazio.")
        return

    print(CARRINHO_SESSAO)


def cadastrar_cliente():
    print("\n--- CADASTRO DE CLIENTE ---")
    
    nome = input("Nome completo: ").strip()
    cpf = input("CPF (somente números): ").strip()
    email = input("E-mail: ").strip()
    
    try:
        novo_cliente = Cliente(cpf=cpf, nome=nome, email=email)
        
        print("Simulando salvamento no Repositório...")
        # cliente_repository.salvar(novo_cliente) 
        
        print(f"\n✅ Cliente cadastrado com sucesso:")
        print(f"Nome: {novo_cliente.nome}, CPF: {novo_cliente.cpf}")

    except (ValorInvalidoError, DocumentoInvalidoError) as e:
        print(f"❌ Erro de validação: {e}")
    except Exception as e:
        print(f"❌ Erro inesperado ao cadastrar: {e}")


def visualizar_status_pedido():
    print("\n--- CONSULTAR STATUS DO PEDIDO ---")
    codigo = input("Digite o código do pedido (completo): ").strip()
    
    try:
        pedido = pedido_repository.buscar_por_codigo(codigo)
        
        if not pedido:
            print(f"⚠️ Pedido com código '{codigo}' não encontrado.")
            return

        # Exibição Detalhada do Status
        print("\n" + "="*40)
        print(f"PEDIDO: {pedido._codigo_pedido}")
        print(f"CLIENTE: {pedido._cliente.nome} (CPF: {pedido._cliente.cpf})")
        print(f"DATA CRIAÇÃO: {pedido._data_criacao.strftime('%d/%m/%Y %H:%M')}")
        print(f"STATUS ATUAL: **{pedido._estado}**")
        print("---")
        
        # Exibir Itens (apenas para referência)
        print("ITENS:")
        for item in pedido._itens:
            print(f"  - {item}")
            
        print("---")
        print(f"SUBTOTAL: R$ {pedido._subtotal:.2f}")
        print(f"DESCONTO: R$ {pedido._desconto:.2f}")
        print(f"FRETE:    R$ {pedido._frete.valor:.2f}")
        print(f"TOTAL GERAL: R$ {pedido._total:.2f}")
        print("="*40)

    except Exception as e:
        print(f"❌ Erro ao buscar pedido: {e}")
    
def fechar_pedido():
    global CARRINHO_SESSAO

    print("\n--- FINALIZAR COMPRA (CHECKOUT) ---")
    
    # 1. Checagem do Carrinho
    if not CARRINHO_SESSAO.itens:
        print("❌ Não é possível finalizar. O carrinho está vazio.")
        return

    # 2. Identificação do Cliente (Busca no Repositório)
    cpf = input("Digite seu CPF para finalizar a compra: ").strip()
    cliente = cliente_repository.buscar_por_cpf(cpf)
    
    if not cliente:
        print("⚠️ Cliente não encontrado. Por favor, cadastre-se (Opção 4) ou digite um CPF válido.")
        return
        
    # 3. Simulação de Frete e Cupom
    
    # IMPORTANTE: Em um projeto real, aqui você chamaria carrinho_service.calcular_frete()
    frete_simulado = Frete(cep_origem="00000000", cep_destino="00000000", valor=15.00)
    
    # Simulação de cupom (Se você tiver a entidade Cupom implementada)
    cupom_aplicado = None # Supondo que não há cupom aplicado por padrão
    # Exemplo: cupom_aplicado = Cupom(codigo="DESCONTO10") 
    
    print(f"\nDetalhes do Pedido para {cliente.nome}:")
    print(f"Subtotal dos Itens: R$ {CARRINHO_SESSAO.total:.2f}")
    print(f"Frete: R$ {frete_simulado.valor:.2f}")

    try:
        # 4. Criar a Entidade Pedido (Congelamento dos dados da transação)
        novo_pedido = Pedido(
            cliente=cliente,
            carrinho=CARRINHO_SESSAO,
            frete=frete_simulado,
            cupom=cupom_aplicado
        )
        
        # 5. Salvar o Pedido no Repositório
        pedido_repository.salvar(novo_pedido)
        
        # 6. Limpar o Carrinho de Sessão após o sucesso
        CARRINHO_SESSAO = Carrinho() 
        
        print("\n========================================")
        print(f"✅ PEDIDO FINALIZADO COM SUCESSO!")
        print(f"CÓDIGO: {novo_pedido._codigo_pedido}")
        print(f"TOTAL A PAGAR: R$ {novo_pedido._total:.2f}")
        print("========================================")
        print("Seu pedido está no status 'CRIADO'. Use a Opção 5 para monitorá-lo.")

    except Exception as e:
        print(f"❌ Erro ao finalizar o pedido: {e}")

def gerenciar_produtos():
    while True:
        print("\n--- GESTÃO DE PRODUTOS ---")
        print("1. Cadastrar Novo Produto")
        print("2. Ajustar Estoque de Produto Existente")
        print("0. Voltar ao Menu Principal")
        
        escolha = input("Selecione uma opção: ").strip()
        
        if escolha == '1':
            cadastrar_produto()
        elif escolha == '2':
            ajustar_estoque()
        elif escolha == '0':
            break
        else:
            print("Opção inválida.")

def gerenciar_enderecos():
    print("\n--- GERENCIAR ENDEREÇOS DO CLIENTE ---")
    cpf = input("Digite o CPF do cliente (somente números): ").strip()

    try:
        cliente = cliente_repository.buscar_por_cpf(cpf)
        
        if not cliente:
            print(f"⚠️ Cliente com CPF {cpf} não encontrado.")
            return

        print(f"\nCliente Selecionado: {cliente.nome}")
        
        if cliente.enderecos:
            print("\nEndereços Atuais:")
            for i, end in enumerate(cliente.enderecos):
                print(f"  [{i+1}] {end}")
        else:
            print("Nenhum endereço cadastrado.")
            
        print("\n--- NOVO ENDEREÇO ---")
        cep = input("CEP: ").strip()
        logradouro = input("Logradouro (Rua, Av.): ").strip()
        numero = input("Número: ").strip()
        cidade = input("Cidade: ").strip()
        uf = input("UF (Ex: SP): ").strip().upper()

        novo_endereco = Endereco(
            cep=cep,
            logradouro=logradouro,
            numero=numero,
            cidade=cidade,
            uf=uf
        )
        cliente.adicionar_endereco(novo_endereco)
        
        cliente_repository.salvar(cliente)
        
        print("\n✅ Endereço adicionado e cliente salvo com sucesso!")
        print(f"Novo Total de Endereços: {len(cliente.enderecos)}")
        
    except ValorInvalidoError as e:
        print(f"❌ Erro de Validação: {e}")
    except Exception as e:
        print(f"❌ Erro ao gerenciar endereços: {e}")
    
def avancar_status_pedido():
    print("\n--- AVANÇAR STATUS DO PEDIDO ---")
    codigo = input("Digite o código do pedido a ser atualizado: ").strip()
    
    # 1. Exibir Statuses Válidos
    print("\nStatus Disponíveis (Exemplos de entrada):")
    print("PAGO | SEPARACAO | ENVIADO | ENTREGUE | CANCELADO")
    
    novo_status = input("Digite o NOVO status: ").strip().upper()

    try:
        # Busca o pedido apenas para mostrar o status atual antes de mudar
        pedido_atual = pedido_repository.buscar_por_codigo(codigo)
        
        if not pedido_atual:
             print(f"⚠️ Pedido com código '{codigo}' não encontrado.")
             return
             
        print(f"Status Atual: **{pedido_atual._estado}**")
        
        # 2. Chama a lógica de serviço para realizar a transição
        # O serviço valida a transição e salva
        pedido_atualizado = pedido_service.avancar_status(codigo, novo_status)
        
        print("\n✅ STATUS ATUALIZADO COM SUCESSO!")
        print(f"Pedido: {pedido_atualizado._codigo_pedido}")
        print(f"De: {pedido_atual._estado} -> Para: **{pedido_atualizado._estado}**")

    except ValorInvalidoError as e:
        # Captura erros de pedido não encontrado ou transição inválida
        print(f"❌ Erro de transição: {e}")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
    
def visualizar_relatorio():
    print("\n--- RELATÓRIO DE VENDAS (Em desenvolvimento) ---")
    pass

def cadastrar_produto():
    print("\n--- CADASTRO DE NOVO PRODUTO ---")
    sku = input("SKU (Código Único): ").strip().upper()
    nome = input("Nome do Produto: ").strip()
    categoria = input("Categoria: ").strip()
    
    if produto_repository.buscar_por_sku(sku):
        print(f"❌ Erro: Produto com SKU '{sku}' já existe.")
        return

    try:
        preco = float(input("Preço Unitário: "))
        estoque = int(input("Estoque Inicial: "))
        tipo = input("Produto Físico? (s/n): ").strip().lower()
        
        peso = 0.0
        if tipo == 's':
            peso = float(input("Peso (kg): "))
            
        if tipo == 's':
            novo_produto = ProdutoFisico(sku, nome, categoria, preco, estoque, peso)
        else:
            novo_produto = Produto(sku, nome, categoria, preco, estoque)
            
        produto_repository.salvar(novo_produto)
        print(f"✅ Produto '{novo_produto.nome}' cadastrado com sucesso e salvo no JSON.")

    except ValueError:
        print("❌ Entrada inválida para preço/estoque/peso.")
    except ValorInvalidoError as e:
        print(f"❌ Erro de validação: {e}")
    except Exception as e:
        print(f"❌ Erro inesperado ao cadastrar produto: {e}")


def ajustar_estoque():
    print("\n--- AJUSTAR ESTOQUE ---")
    listar_produtos()
    sku = input("\nDigite o SKU do produto a ser ajustado: ").strip().upper()
    
    produto = produto_repository.buscar_por_sku(sku)
    
    if not produto:
        print(f"⚠️ Produto com SKU '{sku}' não encontrado.")
        return

    try:
        ajuste = int(input(f"Ajuste de estoque (+ ou -). Estoque atual: {produto.estoque}: "))
        
        novo_estoque = produto.estoque + ajuste
        
        if novo_estoque < 0:
            print("❌ Aviso: Ação cancelada. O estoque final não pode ser negativo.")
            return

        # Ajusta o estoque na entidade (usa o setter, se houver lógica)
        produto.estoque = novo_estoque
        
        # Salva o produto atualizado
        produto_repository.salvar(produto)
        
        print(f"✅ Estoque de '{produto.nome}' atualizado. Novo estoque: {produto.estoque}")
        
    except ValueError:
        print("❌ Quantidade de ajuste inválida. Digite um número inteiro.")
    except Exception as e:
        print(f"❌ Erro ao ajustar estoque: {e}")

def main():
    print("\n[Inicialização]: Carregando dados da loja...")
    
    while True:
        try:
            mostrar_menu() 
            escolha = input("Selecione uma opção: ").strip()
            
            if escolha == '1':
                adicionar_ao_carrinho()
            elif escolha == '2':
                visualizar_carrinho()
            elif escolha == '3':
                fechar_pedido()
            elif escolha == '4':
                cadastrar_cliente()
            elif escolha == '5':
                visualizar_status_pedido()
            elif escolha == '6':
                gerenciar_produtos()
            elif escolha == '7':
                gerenciar_enderecos()
            elif escolha == '8':
                avancar_status_pedido()
            elif escolha == '9':
                visualizar_relatorio()
            elif escolha == '0':
                print("Saindo do CLI. Até logo!")
                break
            else:
                print("Opção inválida. Tente novamente.")
        
        except Exception as e:
            print(f"\n❌ Ocorreu um erro fatal na aplicação: {e}")


if __name__ == '__main__':
    main()
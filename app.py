from models.entidades import Cliente, Produto, Endereco, ProdutoFisico
from models.vendas import Carrinho, Pedido 
from models.exceptions import ValorInvalidoError, DocumentoInvalidoError, EntidadeNaoEncontradaError
from datetime import datetime
from models.transacoes import Frete, Cupom
import repositories.cliente_repository as cliente_repository
import repositories.produto_repository as produto_repository
import repositories.pedido_repository as pedido_repository
import services.pedido_service as pedido_service
import services.relatorio_service as relatorio_service 
import services.carrinho_service as carrinho_service
from services.estoque_service import EstoqueService


CARRINHO_SESSAO = Carrinho() 


def cadastrar_produto():
    """Função auxiliar para a Opção 6."""
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
        print(f"✅ Produto '{novo_produto.nome}' cadastrado com sucesso.")

    except ValueError:
        print("❌ Entrada inválida para preço/estoque/peso.")
    except Exception as e:
        print(f"❌ Erro inesperado ao cadastrar produto: {e}")


def ajustar_estoque():
    """Função auxiliar para a Opção 6."""
    print("\n--- AJUSTAR ESTOQUE ---")
    listar_produtos()
    sku = input("\nDigite o SKU do produto a ser ajustado: ").strip().upper()
    
    produto = produto_repository.buscar_por_sku(sku)
    
    if not produto:
        print(f"⚠️ Produto com SKU '{sku}' não encontrado.")
        return
        
    if not hasattr(produto, 'estoque'):
        print(f"⚠️ O produto '{produto.nome}' não gerencia estoque. Ajuste cancelado.")
        return


    try:
        ajuste = int(input(f"Ajuste de estoque (+ ou -). Estoque atual: {produto.estoque}: "))
        
        # Usando o método ajustar_estoque da entidade para encapsulamento
        produto.ajustar_estoque(ajuste) 
        
        produto_repository.salvar(produto)
        
        print(f"✅ Estoque de '{produto.nome}' atualizado. Novo estoque: {produto.estoque}")
        
    except ValueError:
        print("❌ Quantidade de ajuste inválida. Digite um número inteiro.")
    except ValorInvalidoError as e:
         print(f"❌ Erro de Validação: {e}")
    except Exception as e:
        print(f"❌ Erro ao ajustar estoque: {e}")


def mostrar_menu():
    print("\n" + "="*35)
    print("      SISTEMA SIMPLIFICADO E-COMMERCE")
    print("="*35)
    
    # Exibe o status do carrinho
    print(f"🛒 Carrinho Atual: {len(CARRINHO_SESSAO.itens)} item(s)")
    if CARRINHO_SESSAO.cliente:
         print(f"👤 Cliente Associado: {CARRINHO_SESSAO.cliente.nome}")
    print("-----------------------------------")
    
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
    """Lista produtos, incluindo um fallback se o repositório falhar."""
    print("\n--- PRODUTOS DISPONÍVEIS ---")
    
    try:
        produtos = produto_repository.carregar_todos() 
    except Exception:
        # Fallback de simulação
        produtos = [
            ProdutoFisico("SKU001", "Livro POO Python", "Educação", 59.90, 10, 0.8),
            Produto("SKU002", "Ebook PyTest", "Digital", 29.90, 999), 
        ]

    if not produtos:
        print("Nenhum produto cadastrado.")
        return []

    for p in produtos:
        estoque_info = f"Estoque: {p.estoque}" if hasattr(p, 'estoque') else "Estoque: N/A"
        print(f"[{p.sku}] {p.nome} | R$ {p.preco_unitario:.2f} | {estoque_info}")
    return produtos


def adicionar_ao_carrinho():
    """Opção 1: Adicionar item ao carrinho."""
    produtos = listar_produtos()
    if not produtos:
        return

    print("\n--- ADICIONAR AO CARRINHO ---")
    sku = input("Digite o SKU do produto: ").strip().upper()
    
    produto_selecionado = produto_repository.buscar_por_sku(sku)

    if not produto_selecionado:
        print("⚠️ SKU não encontrado.")
        return

    try:
        quantidade = int(input("Digite a quantidade: "))
        
        # Chama a lógica de serviço/validação
        carrinho_service.adicionar_item_ao_carrinho(CARRINHO_SESSAO, sku, quantidade)
        
        # Pergunta se deseja associar um cliente
        if not CARRINHO_SESSAO.cliente:
            associar = input("Deseja associar um cliente (necessário para checkout)? (s/n): ").strip().lower()
            if associar == 's':
                 cpf = input("Digite o CPF do cliente: ").strip()
                 cliente = cliente_repository.buscar_por_cpf(cpf)
                 if cliente:
                     CARRINHO_SESSAO.cliente = cliente
                     print(f"✅ Cliente {cliente.nome} associado ao carrinho.")
                 else:
                      print("❌ Cliente não encontrado. Cadastre-se na Opção 4.")

        print(f"✅ Adicionado: {quantidade}x {produto_selecionado.nome} ao carrinho.")

    except ValueError:
        print("❌ Quantidade inválida. Digite um número.")
    except ValorInvalidoError as e:
        print(f"❌ Erro: {e}")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        

def visualizar_carrinho():
    """Opção 2: Visualizar itens do carrinho."""
    print("\n--- SEU CARRINHO ---")
    
    if not CARRINHO_SESSAO.itens: 
        print("🛒 O carrinho está vazio.")
        return

    print(CARRINHO_SESSAO)


def finalizar_compra():
    """Opção 3: Inicia o checkout chamando o PedidoService completo."""
    global CARRINHO_SESSAO
    
    if not CARRINHO_SESSAO.itens:
        print("❌ O carrinho está vazio. Adicione itens antes de finalizar a compra.")
        return
        
    # Associa o cliente se ainda não estiver
    if not CARRINHO_SESSAO.cliente:
        cpf_cliente = input("Digite o CPF do cliente para checkout: ").strip()
        try:
            cliente = cliente_repository.buscar_por_cpf(cpf_cliente)
            if not cliente:
                 print("❌ Cliente não encontrado. Por favor, cadastre-se (Opção 4).")
                 return
            CARRINHO_SESSAO.cliente = cliente
        except (DocumentoInvalidoError, EntidadeNaoEncontradaError) as e:
            print(f"❌ Erro: {e}")
            return


    print("\n--- FINALIZAR COMPRA (CHECKOUT) ---")
    
    cliente = CARRINHO_SESSAO.cliente
    
    if not cliente.enderecos:
        print("❌ Cliente sem endereço cadastrado. Use a Opção 7 para adicionar um endereço.")
        return

    cep_destino = cliente.enderecos[0].cep 
    frete = carrinho_service.calcular_frete(CARRINHO_SESSAO, cep_destino)
    
    # Simulação de cupom para teste
    cupom = None
    cupom_codigo = input("Digite o código do cupom (opcional): ").strip()
    if cupom_codigo:
        try:
             cupom = carrinho_service.buscar_cupom(cupom_codigo)
             if cupom:
                 print(f"✅ Cupom '{cupom.codigo}' aplicado! Desconto será calculado no total.")
             else:
                 print(f"⚠️ Cupom '{cupom_codigo}' inválido/não encontrado.")
        except Exception as e:
             print(f"⚠️ Erro ao buscar cupom: {e}")
             
    
    # Exibição de Resumo (cria um pedido temporário para simular)
    pedido_simulado = Pedido(cliente, CARRINHO_SESSAO, frete, cupom)
    
    print(f"\nDetalhes do Pedido para {cliente.nome}:")
    # Acessando atributos protegidos para exibição simples no CLI
    print(f"Subtotal dos Itens: R$ {pedido_simulado._subtotal:.2f}")
    print(f"Desconto do Cupom: R$ {pedido_simulado._desconto:.2f}")
    print(f"Frete: R$ {frete.valor:.2f} (Prazo: {frete.prazo_dias} dias)")
    print(f"TOTAL FINAL: R$ {pedido_simulado._total:.2f}")

    print("\n--- INFORMAÇÕES DE PAGAMENTO ---")
    metodo = input("Método de pagamento (cartao/boleto): ").strip().lower()
    
    info_pagamento = {}
    if metodo == 'cartao':
        info_pagamento['bandeira'] = input("Bandeira do Cartão (Ex: VISA, Master Card): ").strip()

    
    try:
        # CHAMADA CRUCIAL: Finaliza a compra usando o PedidoService
        pedido_final = pedido_service.PedidoService.finalizar_compra(
            carrinho=CARRINHO_SESSAO, 
            frete=frete, 
            metodo_pagamento=metodo, 
            info_pagamento=info_pagamento, 
            cupom=cupom
        )
        
        print("\n" + "="*40)
        print(f"✅ PEDIDO **{pedido_final._codigo_pedido}** CONCLUÍDO!")
        print(f"Status do Pagamento: **{pedido_final._estado}**")
        print(f"TOTAL COBRADO: R$ {pedido_final._total:.2f}")
        print("🔑 Anote o código do pedido para consulta futura.")
        print("="*40)
        
        # LIMPAR CARRINHO
        CARRINHO_SESSAO = Carrinho() 

    except (DocumentoInvalidoError, ValorInvalidoError, EntidadeNaoEncontradaError) as e:
        print(f"❌ Erro de Validação/Checkout: {e}")
    except Exception as e:
        print(f"❌ Ocorreu um erro fatal ao finalizar o pedido: {e}")


def cadastrar_cliente():
    """Opção 4: Cadastro simples de cliente."""
    print("\n--- CADASTRO DE CLIENTE ---")
    
    nome = input("Nome completo: ").strip()
    cpf = input("CPF (somente números): ").strip()
    email = input("E-mail: ").strip()
    
    try:
        # Cria e salva o cliente
        novo_cliente = Cliente(cpf=cpf, nome=nome, email=email)
        cliente_repository.salvar(novo_cliente) 
        
        print(f"\n✅ Cliente '{novo_cliente.nome}' cadastrado com sucesso! Use a Opção 7 para adicionar endereço.")

    except (ValorInvalidoError, DocumentoInvalidoError) as e:
        print(f"❌ Erro de validação: {e}")
    except Exception as e:
        print(f"❌ Erro inesperado ao cadastrar: {e}")


def visualizar_status_pedido():
    """Opção 5: Consulta o status do pedido."""
    print("\n--- CONSULTAR STATUS DO PEDIDO ---")
    codigo = input("Digite o código do pedido (completo/prefixo): ").strip()
    
    try:
        # Busca o pedido (repositório deve lidar com prefixo)
        pedido = pedido_repository.buscar_por_codigo(codigo)
        
        if not pedido:
            print(f"⚠️ Pedido com código '{codigo}' não encontrado.")
            return

        # Acessa os atributos protegidos (assumindo que não há propriedades públicas)
        print("\n" + "="*40)
        print(f"PEDIDO: {pedido._codigo_pedido}")
        print(f"CLIENTE: {pedido.cliente.nome} (CPF: {pedido.cliente.cpf})")
        print(f"STATUS ATUAL: **{pedido._estado}**")
        print("---")
        
        # Exibir Itens
        print("ITENS:")
        for item in pedido.carrinho.itens:
            print(f"  - {item.produto.nome} (SKU: {item.produto.sku}) x{item.quantidade} | R$ {item.preco_unitario:.2f}") 
            
        print("---")
        # Acessa os atributos protegidos
        print(f"SUBTOTAL: R$ {pedido._subtotal:.2f}")
        print(f"DESCONTO: R$ {pedido._desconto:.2f}")
        print(f"FRETE:    R$ {pedido.frete.valor:.2f}")
        print(f"TOTAL GERAL: R$ {pedido._total:.2f}")
        print("="*40)

    except Exception as e:
        print(f"❌ Erro ao buscar pedido: {e}")


def gerenciar_produtos():
    """Opção 6: Menu de gestão de produtos."""
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
    """Opção 7: Adiciona endereço a cliente existente."""
    print("\n--- GERENCIAR ENDEREÇOS DO CLIENTE ---")
    cpf = input("Digite o CPF do cliente: ").strip()

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
        
    except ValorInvalidoError as e:
        print(f"❌ Erro de Validação: {e}")
    except Exception as e:
        print(f"❌ Erro ao gerenciar endereços: {e}")


def avancar_status_pedido():
    """Opção 8: Avança o status do pedido (ADMIN)."""
    print("\n--- AVANÇAR STATUS DO PEDIDO ---")
    codigo = input("Digite o código do pedido a ser atualizado: ").strip()
    
    print("\nStatus Disponíveis (Exemplos de entrada):")
    print("PAGO | SEPARACAO | ENVIADO | ENTREGUE | CANCELADO")
    
    novo_status = input("Digite o NOVO status: ").strip().upper()

    try:
        # Busca o pedido para referência
        pedido_anterior = pedido_repository.buscar_por_codigo(codigo)
        
        if not pedido_anterior:
            raise EntidadeNaoEncontradaError(f"Pedido com código '{codigo}' não encontrado.")
            
        print(f"Status Atual: **{pedido_anterior._estado}**")
        
        # CORREÇÃO: Chama o método correto do PedidoService
        pedido_atualizado = pedido_service.PedidoService.atualizar_estado_pedido(codigo, novo_status)

        print("\n✅ STATUS ATUALIZADO COM SUCESSO!")
        print(f"Pedido: {pedido_atualizado._codigo_pedido}")
        print(f"De: {pedido_anterior._estado} -> Para: **{pedido_atualizado._estado}**")

    except (ValorInvalidoError, EntidadeNaoEncontradaError) as e:
        print(f"❌ Erro de transição: {e}")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")


def visualizar_relatorio():
    """Opção 9: Menu de relatórios."""
    print("\n--- OPÇÕES DE RELATÓRIO ---")
    print("1. Clientes Cadastrados (Listagem)")
    print("2. Produtos e Estoque (Listagem)")
    print("3. Pedidos e Vendas (Listagem)")
    print("4. Faturamento por Período (Ocupação)")
    print("0. Voltar ao Menu Principal")
    
    escolha = input("Selecione o relatório: ").strip()
    
    # Chama os métodos estáticos do serviço de relatório
    if escolha == '1':
        print(relatorio_service.RelatorioService.relatorio_clientes())
    elif escolha == '2':
        print(relatorio_service.RelatorioService.relatorio_produtos())
    elif escolha == '3':
        print(relatorio_service.RelatorioService.relatorio_pedidos())
    elif escolha == '4':
        periodo = input("Agrupar por 'dia' ou 'mes'? (Padrão: dia): ").strip().lower()
        if periodo not in ['dia', 'mes']:
            periodo = 'dia'
            
        dados = relatorio_service.RelatorioService.relatorio_ocupacao_por_periodo(periodo)
        
        print(f"\n--- FATURAMENTO POR {periodo.upper()} ---")
        if not dados:
            print("Nenhum dado de venda encontrado.")
            return

        total_geral = sum(dados.values())
        for chave, valor in dados.items():
            print(f"[{chave}]: R$ {valor:.2f}")
            
        print(f"\nTOTAL GERAL: R$ {total_geral:.2f}")

    elif escolha == '0':
        return
    else:
        print("Opção inválida.")


# --- MAIN ---

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
                finalizar_compra()
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
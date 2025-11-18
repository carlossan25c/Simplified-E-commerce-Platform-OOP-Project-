# 🛍️ Simplified E-commerce Platform (OOP Project)

This project is a **Simplified Virtual Store System** developed in Python, focusing on **Object-Oriented Programming (OOP)** principles like encapsulation, inheritance, and composition. It features core e-commerce functionalities, including product/customer management, cart/order processing, and basic persistence using JSON.

# Descrição
Este projeto visa desenvolver um Sistema Simplificado de Loja Virtual.

A implementação, vai ser feita em Python e vai contar com uma Interface de Linha de Comando (CLI) como principal meio de interação e uma API mínima — usando framework Flask. O projeto todo envolve as funcionalidades essenciais de um e-commerce:


* Gestão de Entidades: Cadastro (CRUD) de Produtos e Clientes.    
* Fluxo de Vendas: Criação do Carrinho de Compras e Finalização dos Pedidos.    
* Transações: Registro de Pagamentos, Aplicação de Cupons de Desconto, e também o Cálculo de Frete.    
* Expedição e Status: Gerenciamento dos estados dos pedidos, tipo CRIADO, PAGO, ENVIADO, ENTREGUE, e CANCELADO.    
* Relatórios: Geração de relatórios de gestão sobre vendas e faturamento.   

A persistência dos dados será implementada de maneira bem simples usando JSON, dispensando um ORM complexo. 

# Propósito do Projeto

O objetivo primordial deste trabalho é aplicar e exibir maestria nos princípios da Programação Orientada a Objetos POO com ênfase nestes requerimentos técnicos: Modelagem e Herança Modelar classes, tipo Produto, Cliente, Pedido etc. e usar herança, por exemplo, subclasses opcionais de Produto como ProdutoDigital ou ProdutoFisico. 

* Encapsulamento e Validações: Certificar a integridade dos dados, com @property para validar atributos como preço $>0$, estoque $\ge 0$, email/CPF válidos.     
* Composição Empregar: composição para estruturar objetos complexos como Carrinho com ItemCarrinho; Cliente com Endereços.     
* Regras de Negócio: Implementar com cuidado as regras de negócio cruciais, tipo controle de estoque na baixa e estorno validação de cupons e as transições de estado do pedido.     
* Testes Desenvolver: testes unitários pytest abrangendo tanto os "casos de sucesso" quanto os cenários de erro e transições de estado.    

# 💡 Estrutura de Classes (UML Textual)

## 1. Entidades Básicas (Modelagem do Domínio)    
Classe| Atributos e Propriedades Chave| Métodos Principais| Relacionamentos
------|-------------------------------|-------------------|-----------------
Produto| `sku: str` (PK, único), `nome: str`, `preco_unitario: float` (>0, `@property`), `estoque: int` (>=0, `@property`), `ativo: bool`| `ajustar_estoque(quantidade), __str__(), __eq__(sku), __lt__(preco_nome)`| ItemCarrinho (1:N), ItemPedido (1:N)
ProdutoFisico| `peso: float`| (Herda de Produto)| Herda de Produto.
ProdutoDigital| `link_download: str`| (Herda de Produto)| Herda de Produto.
Cliente| `cpf: str, nome: str, email: str` (único, válido, `@property`), `cpf: str` (único, válido, `@property),enderecos: list[Endereco]`| `adicionar_endereco(endereco), __eq__(cpf_email)`| Endereco (1:N), Pedido (1:N)| 
Endereco| `cep: str, cidade: str, uf: str, logradouro: str`|` __str__()`| Cliente (N:1)

## 2. Fluxo de Vendas (Carrinho e Pedido)    
Classe| Atributos e Propriedades Chave| Métodos Principais| Relacionamentos
------|-------------------------------|-------------------|-----------------
Carrinho| `itens: list[ItemCarrinho]`| `adicionar_item(produto, quantidade), remover_item(sku), alterar_quantidade(sku, qtd), calcular_subtotal(), __len__`| ItemCarrinho (1:N)
ItemCarrinho| `produto: Produto, quantidade: int` (>=1, `@property`)| `calcular_subtotal_item()`| Produto (1:1), Carrinho (N:1)
Pedido| `codigo_pedido: str, cliente: Cliente, itens: list[ItemPedido], estado: str, frete: Frete, desconto: float, total: float`| `fechar_pedido(...), calcular_total(), gerar_resumo_nota(), cancelar(), __str__`| Cliente (1:1), ItemPedido (1:N), Pagamento (1:N), Cupom (0:1), Frete (1:1)
ItemPedido| `produto: Produto, quantidade: int, preco_na_data: float`| `calcular_subtotal_item()`| Produto (1:1), Pedido (N:1)

## 3. Transações e Regras de Negócio    
Classe| Atributos e Propriedades Chave| Métodos Principais| Relacionamentos
------|-------------------------------|-------------------|-----------------
Cupom| `codigo: str, tipo: str` (VALOR/PERCENTUAL), `valor_margem: float, data_validade: datetime, uso_maximo: int`| `validar(carrinho), aplicar_desconto(subtotal)`| Não permitir desconto que torne total $< 0.$| 
Pagamento| `data: datetime, forma: str, valor: float`| `registrar_pagamento(pedido), validar_total(pedido)`| Total pago $\ge$ total do pedido.| 
Frete| `valor: float, prazo_estimado_dias: int`| `calcular_frete(cep, uf) `(Baseado em `settings.json`)| Obrigatório antes do pagamento. Produtos digitais não somam frete.
# 📁 Estruturas de classes 
```
. (root)    
├── README.md    
├── app.py     
├── requirements.txt    
│    
├── data/    
│   └── loja.json    
│   └── settings.json    
|    
├── models/    
│   ├── __init__.py     
│   ├── entidades.py    # Cliente, Produto, Endereco    
│   ├── vendas.py       # Carrinho, Pedido, Item...    
│   └── transacoes.py   # Pagamento, Cupom, Frete    
|    
├── repositories/    
│   ├── __init__.py    
│   ├── produto_repository.py    
│   ├── cliente_repository.py    
│   └── pedido_repository.py    
|    
├── services/    
│   ├── __init__.py    
│   ├── estoque_service.py    
│   ├── carrinho_service.py    
│   ├── pedido_service.py    
│   └── relatorio_service.py    
│    
└── tests/    
    ├── __init__.py    
    ├── test_models.py    
    ├── test_services.py     
    └── test_regras_negocio.py
```
# 🛠️Decisões de Framework

## 1. Escolha do Framework: Flask

Framework Web| Flask (Micro-framework Python) será utilizado para implementar a API Mínima  como interface de interação do sistema.
-------------|---------------------------------------------------------------------------------------------------------------------
Justificativa| O Flask é leve e flexível, ideal para o escopo do projeto que requer apenas endpoints equivalentes aos comandos CLI (ex: `/clientes/cadastrar, /pedidos/fechar`). Isso permite focar na lógica de POO, que é o objetivo principal do trabalho.
Alternativa| Embora a especificação também mencione a Interface de Linha de Comando (CLI), a API mínima com Flask oferece uma estrutura modular (utilizando os `Services` e `Models`) mais clara e escalável.

## 2. Estrutura da API Mínima com Flask

|GET /produtos/         -> | Lista todos os produtos (via Repositories)
---------------------------|--------------------------------------------
POST /pedidos/fechar   -> | Chama o PedidoService para fechar o pedido
POST /pedidos/`<id>`/pagar -> | Chama o PagamentoService para registrar o pagamento

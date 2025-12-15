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

## 1. Camada de Modelagem e POO (`models/`)

Esta camada define as entidades, o encapsulamento, a herança e os relacionamentos do domínio de vendas.

| Arquivo | Classe | Princípio POO e Finalidade |
| :--- | :--- | :--- |
| **`entidades.py`** | `Produto` | Classe base. Encapsulamento e validação de preço/estoque. |
| | `ProdutoFisico` | **Herança** de `Produto`. Adiciona e valida o atributo `_peso`. |
| | `Cliente` | Encapsulamento. Validação de formato de CPF. |
| | `Endereco` | Objeto de Valor (Composição em `Cliente`). |
| **`vendas.py`** | `Carrinho` | **Agregação**. Implementa o método mágico `__len__`. |
| | `Pedido` | **Composição** (contém `ItemPedido`). Lógica de cálculo de total. |
| | `ItemCarrinho` | Item temporário de venda. |
| **`transacoes.py`** | `Cupom` | Objeto de Valor. Implementa a **Regra de Negócio Avançada** (limite de 50% de desconto). |
| | `Frete` | Objeto de Valor. |
| **`exceptions.py`** | `ValorInvalidoError` | Exceção customizada (erros de valor). |


## 2. Camada de Persistência e Configuração (`repositories/`)

Esta camada isola a lógica de I/O, gerenciando os arquivos `loja.json` (dados) e `settings.json` (configurações).

| Arquivo | Entidade Gerenciada | Função no Projeto (I/O Isolation) |
| :--- | :--- | :--- |
| **`dados.py`** | Dados Brutos (`loja.json`) | Módulo utilitário central. Faz o I/O do arquivo `loja.json`. |
| **`settings_repository.py`** | Configurações (`settings.json`) | Leitura de constantes de sistema e **Regras de Negócio Globais** (ex: `limite_seguranca`). |
| **`produto_repository.py`** | `Produto` / `ProdutoFisico` | CRUD específico. Lida com a serialização/desserialização e a lógica de **herança**. |
| **`cliente_repository.py`** | `Cliente` | CRUD específico. |
| **`pedido_repository.py`** | `Pedido` | CRUD específico. |

## 3. Camada de Regras de Negócio e Serviços (`services/`)

A camada de "inteligência" do sistema, responsável por executar a lógica complexa e as Regras de Negócio.

| Arquivo | Classe | Responsabilidade Principal (Separação de Preocupações) |
| :--- | :--- | :--- |
| **`pedido_service.py`** | `PedidoService` | **Orquestrador Central:** Gerencia o fluxo completo de venda (validação, criação do pedido e persistência). |
| **`estoque_service.py`** | `EstoqueService` | **Regra de Negócio:** Implementa a lógica de **Validação de Estoque de Segurança** (lendo a regra do `settings.json`). |
| **`relatorio_service.py`** | `RelatorioService` | **Relatórios:** Processa a lista de pedidos para gerar o Relatório de Faturamento por Período. |
| **`carrinho_service.py`** | `CarrinhoService` | *Esqueleto* — Reservado para lógica futura. |


# 📁 Estruturas de classes 
```
Simplified-E-commerce-Platform-OOP-Project/
├── app.py
├── data/
│   ├── loja.json          <-- Arquivo principal de persistência (dados da loja)
│   └── settings.json
|
├── models/
│   ├── __init__.py
│   ├── entidades.py
│   ├── exceptions.py
│   ├── transacoes.py
│   └── vendas.py
|
├── repositories/
│   ├── __init__.py
│   ├── dados.py          
│   ├── cliente_repository.py
│   ├── produto_repository.py
│   └── pedido_repository.py
|
└── services/
    ├── __init__.py
    ├── carrinho_service.py
    ├── pedido_service.py
    ├── relatorio_service.py
    └── estoque_service.py
```

# Requesitos de execução 

### Execução projeto

* Python 3.1 

### Clonagem do repositório

* git clone `https://github.com/carlossan25c/Simplified-E-commerce-Platform-OOP-Project-` 

### Execução via CLI

* `python app.py`

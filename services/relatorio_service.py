from repositories import pedido_repository, cliente_repository, produto_repository
from datetime import datetime
from collections import defaultdict
from typing import Dict, Any
from models.vendas import Pedido 

class RelatorioService:
    """Gera relatórios de vendas e métricas."""

    @staticmethod
    def relatorio_ocupacao_por_periodo(periodo: str = 'dia') -> Dict[str, float]:
        """ Relatório de Faturamento Agrupado (Ocupação por Período). """
        
        # Usa dados RAW para eficiência
        dados_pedidos = pedido_repository.carregar_todos_pedidos_raw()
        faturamento_por_periodo = defaultdict(float)
        
        formato_data = '%Y-%m-%d'
        if periodo.lower() == 'mes':
            formato_data = '%Y-%m'

        for pedido_data in dados_pedidos:
            try:
                # Acessa diretamente os dados do dicionário (RAW)
                total_pedido = pedido_data['total']
                data_pedido = datetime.fromisoformat(pedido_data['data_criacao'])
                chave_periodo = data_pedido.strftime(formato_data)
                faturamento_por_periodo[chave_periodo] += total_pedido
            except (ValueError, KeyError):
                continue 

        return dict(sorted(faturamento_por_periodo.items()))

    @staticmethod
    def relatorio_clientes() -> str:
        clientes = cliente_repository.carregar_todos()
        if not clientes:
            return "Nenhum cliente cadastrado."
            
        output = "--- RELATÓRIO DE CLIENTES ---\n"
        output += f"Total de Clientes: {len(clientes)}\n"
        output += "--------------------------------------\n"
        
        for cliente in clientes:
            output += f"CPF: {cliente.cpf}\n"
            output += f"Nome: {cliente.nome}\n"
            output += f"Email: {cliente.email}\n"
            output += f"Endereços: {len(cliente.enderecos)}\n"
            output += "--------------------------------------\n"
            
        return output

    @staticmethod
    def relatorio_produtos() -> str:
        produtos = produto_repository.carregar_todos()
        if not produtos:
            return "Nenhum produto cadastrado."
            
        output = "--- RELATÓRIO DE ESTOQUE E PRODUTOS ---\n"
        output += f"Total de Produtos Distintos: {len(produtos)}\n"
        output += "--------------------------------------\n"
        
        for p in produtos:
            ativo_status = "ATIVO" if p.is_ativo else "INATIVO"
            output += f"SKU: {p.sku} ({ativo_status})\n"
            output += f"Nome: {p.nome}\n"
            output += f"Preço: R$ {p.preco_unitario:.2f}\n"
            
            # Checa se o produto tem a propriedade estoque (ProdutoFisico e Produto)
            estoque_info = f"Estoque: {p.estoque} unidades" if hasattr(p, 'estoque') else "Estoque: N/A"
            output += estoque_info + "\n"
            
            if hasattr(p, 'peso'):
                output += f"Peso: {p.peso:.2f} kg\n"
            output += "--------------------------------------\n"
            
        return output

    @staticmethod
    def relatorio_pedidos() -> str:
        pedidos = pedido_repository.carregar_todos()
        if not pedidos:
            return "Nenhum pedido registrado."
            
        output = "--- RELATÓRIO DE PEDIDOS / VENDAS ---\n"
        output += f"Total de Pedidos: {len(pedidos)}\n"
        output += "--------------------------------------\n"
        
        total_vendido = 0.0
        
        for p in pedidos:
            # Usando atributos protegidos para valores calculados e estados
            total_vendido += p._total 
            
            output += f"CÓDIGO: {p._codigo_pedido} | Status: {p._estado}\n" 
            output += f"Cliente: {p.cliente.nome} (CPF: {p.cliente.cpf})\n"
            
            output += f"Total: R$ {p._total:.2f} (Itens: R$ {p._subtotal:.2f} + Frete: R$ {p.frete.valor:.2f})\n" 
            output += "--------------------------------------\n"

        output += f"\nTOTAL BRUTO VENDIDO (todos os pedidos): R$ {total_vendido:.2f}\n"
        return output
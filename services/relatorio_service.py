from repositories import pedido_repository
from datetime import datetime
from collections import defaultdict
from typing import Dict

class RelatorioService:
    """Gera relatórios de vendas e métricas."""

    @staticmethod
    def relatorio_ocupacao_por_periodo(periodo: str = 'dia') -> Dict[str, float]:
        """
        Relatório de Faturamento Agrupado (Ocupação por Período).
        Agrupa o total das vendas por dia ('%Y-%m-%d') ou por mês ('%Y-%m').
        """
        
        dados_pedidos = pedido_repository.carregar_todos_pedidos_raw()
        faturamento_por_periodo = defaultdict(float)
        
        formato_data = '%Y-%m-%d'
        if periodo.lower() == 'mes':
            formato_data = '%Y-%m'

        for pedido_data in dados_pedidos:
            try:
                # O total do pedido é usado para o faturamento
                total_pedido = pedido_data['total']
                
                # Converte a string ISO da data para objeto datetime
                data_pedido = datetime.fromisoformat(pedido_data['data_criacao'])
                
                # Formata a chave de agrupamento
                chave_periodo = data_pedido.strftime(formato_data)
                
                faturamento_por_periodo[chave_periodo] += total_pedido
            except (ValueError, KeyError):
                # Ignora pedidos com dados de data ou total inválidos
                continue 

        # Ordena o resultado pela chave de período (data)
        return dict(sorted(faturamento_por_periodo.items()))
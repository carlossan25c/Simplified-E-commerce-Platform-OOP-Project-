from models.vendas import Carrinho
from models.transacoes import Frete, Cupom 
from models.exceptions import ValorInvalidoError
import repositories.produto_repository as produto_repository
import math
from typing import Optional 

def adicionar_item_ao_carrinho(carrinho: Carrinho, sku: str, quantidade: int):
    produto = produto_repository.buscar_por_sku(sku)
    
    if not produto or not produto.is_ativo:
        raise ValorInvalidoError(f"Produto com SKU '{sku}' não encontrado ou inativo.")
        
    if quantidade <= 0:
        raise ValorInvalidoError("A quantidade deve ser maior que zero.")
        
    # Busca a quantidade atual do produto no carrinho
    quantidade_atual = 0
    for item in carrinho.itens:
        if item.produto.sku == sku:
            quantidade_atual = item.quantidade
            break
            
    nova_quantidade_total = quantidade_atual + quantidade
    
    # Verifica o estoque total (apenas para ProdutoFisico que tem estoque)
    if hasattr(produto, 'estoque'):
        if produto.estoque < nova_quantidade_total:
            # CORREÇÃO: Informa o total disponível
            raise ValorInvalidoError(
                f"Estoque insuficiente. Disponível: {produto.estoque}. Você já tem {quantidade_atual} no carrinho."
            )
            
    carrinho.adicionar_item(produto, quantidade)
    
    
def calcular_frete(carrinho: Carrinho, cep_destino: str) -> Frete:
    """
    Simula o cálculo do frete baseado no peso total do carrinho.
    """
    
    # Simulação de CEP de Origem
    CEP_ORIGEM_SIMULADO = "00000000"
    
    if not carrinho.itens:
        # Retorna frete zero
        return Frete(cep_origem=CEP_ORIGEM_SIMULADO, cep_destino=cep_destino, valor=0.0, prazo_dias=0)

    # Assume que calcular_peso_total() existe em models/vendas.py (Classe Carrinho)
    peso_total_kg = carrinho.calcular_peso_total()
    
    # Simulação de custo: R$ 5.00 base + R$ 10.00 por quilo
    valor_frete = 5.00 + (peso_total_kg * 10.00)
    
    # Limita o valor mínimo do frete
    valor_frete = max(15.00, valor_frete)

    # Arredonda o valor do frete para duas casas decimais, arredondando para cima (ceil)
    valor_frete = math.ceil(valor_frete * 100) / 100

    # Simulação de Prazo: 3 dias base + 1 dia por 5kg de peso. Mínimo de 5 dias.
    prazo_dias = 3 + int(peso_total_kg / 5) 
    prazo_dias = max(5, prazo_dias) 
    
    # Cria e retorna o objeto Frete completo
    return Frete(
        cep_origem=CEP_ORIGEM_SIMULADO,
        cep_destino=cep_destino, 
        valor=valor_frete,
        prazo_dias=prazo_dias 
    )

def buscar_cupom(cupom_codigo: str) -> Optional[Cupom]:
    """
    Simula a busca de um cupom.
    """
    
    cupom_codigo = cupom_codigo.upper()
    
    if cupom_codigo == "PRIMEIRA10":
        return Cupom(
            codigo="PRIMEIRA10",
            valor=0.10, # 10%
            is_percentual=True,
            validade=None # Sem validade
        )
    elif cupom_codigo == "FRETEZERO":
        # Simulação de cupom que zera o frete.
        return Cupom(
            codigo="FRETEZERO",
            valor=100.00, # Valor fixo alto (limitado pelo Pedido)
            is_percentual=False,
            validade=None
        )
    else:
        return None


def calcular_desconto_cupom(carrinho: Carrinho, cupom: Cupom) -> float:
    """
    Calcula o valor do desconto de um cupom válido no subtotal do carrinho.
    """
    if not cupom.is_valido():
        raise ValorInvalidoError(f"Cupom '{cupom.codigo}' expirado.")
        
    return cupom.calcular_desconto(carrinho.total)
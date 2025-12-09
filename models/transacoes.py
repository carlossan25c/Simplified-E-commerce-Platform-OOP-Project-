from datetime import date, datetime
from .exceptions import ValorInvalidoError
from datetime import date, datetime 

class Frete:
    """Representa o valor e o prazo de entrega."""
    def __init__(self, valor: float, prazo_dias: int, transportadora: str = "Correios"):
        if valor < 0:
            raise ValorInvalidoError("O valor do frete não pode ser negativo.")
        self._valor = valor
        self._prazo_dias = prazo_dias
        self._transportadora = transportadora

    @property
    def valor(self):
        return self._valor
    
    def __str__(self):
        return f"Frete {self._transportadora}: R$ {self._valor:.2f} ({self._prazo_dias} dias)"



class Cupom:
    """Cupom de desconto com validação básica de validade."""
    def __init__(self, codigo: str, valor: float, is_percentual: bool, validade: date):
        self._codigo = codigo.upper()
        self._valor = valor
        self._is_percentual = is_percentual
        self._validade = validade

    def is_valido(self) -> bool:
        """Verifica se o cupom não expirou."""
        return self._validade >= date.today()

    def calcular_desconto(self, subtotal: float) -> float:
        """Calcula o valor de desconto."""
        if not self.is_valido():
            return 0.0

        if self._is_percentual:
            desconto = subtotal * (self._valor / 100)
            return min(desconto, subtotal) 
        else:
            return min(self._valor, subtotal) 

    def __str__(self):
        tipo = f"{self._valor:.2f}%" if self._is_percentual else f"R$ {self._valor:.2f}"
        return f"CUPOM {self._codigo} ({tipo})"


class Pagamento:
    """Classe base para métodos de pagamento."""
    def __init__(self, valor: float):
        if valor <= 0:
            raise ValorInvalidoError("O valor do pagamento deve ser positivo.")
        self._valor = valor
        self._data_pagamento = datetime.now()
        
    def processar_pagamento(self) -> bool:
        """Método polimórfico (Requisito RT)."""
        raise NotImplementedError("Método 'processar_pagamento' deve ser implementado na subclasse.")
        
    def __str__(self):
        return f"Pagamento de R$ {self._valor:.2f}"

class PagamentoCartao(Pagamento):
    """Pagamento via Cartão de Crédito/Débito."""
    def __init__(self, valor: float, bandeira: str, parcelas: int):
        super().__init__(valor)
        self._bandeira = bandeira
        self._parcelas = parcelas

    def processar_pagamento(self) -> bool:
        # Simula processamento
        return True 
    
    def __str__(self):
        return f"{super().__str__()} (Cartão {self._bandeira}, {self._parcelas}x)"

class PagamentoBoleto(Pagamento):
    """Pagamento via Boleto Bancário."""
    def __init__(self, valor: float, vencimento: date):
        super().__init__(valor)
        self._vencimento = vencimento
        
    def processar_pagamento(self) -> bool:
        # Simula emissão
        return True 

    def __str__(self):
        return f"{super().__str__()} (Boleto, Vencimento: {self._vencimento.strftime('%d/%m/%Y')})"
    

class Cupom:
    # ... (métodos __init__, is_valido)

    def calcular_desconto(self, subtotal: float) -> float:
        """Calcula o valor de desconto a ser aplicado ao subtotal, limitado a 50%."""
        if not self.is_valido():
            return 0.0

        # Regra de Negócio: Limitar o desconto a 50% do subtotal
        limite_desconto = subtotal * 0.50
        
        if self._is_percentual:
            desconto_bruto = subtotal * (self._valor / 100)
        else:
            desconto_bruto = self._valor

        
        desconto_aplicavel = min(desconto_bruto, limite_desconto)
        
        return min(desconto_aplicavel, subtotal)
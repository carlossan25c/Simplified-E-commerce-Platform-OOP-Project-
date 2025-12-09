from datetime import date, datetime
from models.exceptions import ValorInvalidoError

class Frete:
    def __init__(self, cep_origem: str, cep_destino: str, valor: float, prazo_dias: int = 5, transportadora: str = "Correios"):
        if valor < 0:
            raise ValorInvalidoError("O valor do frete não pode ser negativo.")
            
        self._cep_origem = cep_origem
        self._cep_destino = cep_destino
        self._valor = valor
        self._prazo_dias = prazo_dias
        self._transportadora = transportadora

    @property
    def valor(self):
        return self._valor
    
    @property
    def cep_destino(self):
        return self._cep_destino
    
    def __str__(self):
        return f"Frete {self._transportadora}: R$ {self._valor:.2f} ({self._prazo_dias} dias)"

class Cupom:

    def __init__(self, codigo: str, valor: float, is_percentual: bool, validade: date):
        if valor <= 0:
            raise ValorInvalidoError("Valor do cupom deve ser positivo.")
            
        self._codigo = codigo
        self._valor = valor
        self._is_percentual = is_percentual
        self._validade = validade
    
    @property
    def codigo(self):
        return self._codigo

    def is_valido(self) -> bool:
        return self._validade >= date.today()

    def calcular_desconto(self, subtotal: float) -> float:
        if not self.is_valido():
            return 0.0

        limite_desconto = subtotal * 0.50
        
        if self._is_percentual:
            desconto_bruto = subtotal * (self._valor / 100)
        else:
            desconto_bruto = self._valor
        
        desconto_aplicavel = min(desconto_bruto, limite_desconto)
        
        return min(desconto_aplicavel, subtotal) 

    def __str__(self):
        tipo = "%" if self._is_percentual else "R$"
        return f"CUPOM {self._codigo} ({self._valor}{tipo})"

class Pagamento:
    def __init__(self, valor: float):
        if valor <= 0:
            raise ValorInvalidoError("O valor do pagamento deve ser positivo.")
        self._valor = valor
        self._data_pagamento = datetime.now()
        
    def processar_pagamento(self) -> bool:
        raise NotImplementedError("Método 'processar_pagamento' deve ser implementado na subclasse.")
        
    def __str__(self):
        return f"Pagamento de R$ {self._valor:.2f}"

class PagamentoCartao(Pagamento):
    def __init__(self, valor: float, bandeira: str, parcelas: int):
        super().__init__(valor)
        self._bandeira = bandeira
        self._parcelas = parcelas

    def processar_pagamento(self) -> bool:
        return True 
    
    def __str__(self):
        return f"{super().__str__()} (Cartão {self._bandeira}, {self._parcelas}x)"

class PagamentoBoleto(Pagamento):
    def __init__(self, valor: float, vencimento: date):
        super().__init__(valor)
        self._vencimento = vencimento
        
    def processar_pagamento(self) -> bool:
        return True 

    def __str__(self):
        return f"{super().__str__()} (Boleto, Vencimento: {self._vencimento.strftime('%d/%m/%Y')})"
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from models.exceptions import ValorInvalidoError

class Cupom:
    def __init__(self, codigo: str, valor: float, is_percentual: bool, validade: Optional[datetime] = None):
        if not codigo or valor <= 0:
            raise ValorInvalidoError("Código e valor do cupom devem ser válidos.")
        if is_percentual and valor > 1.0:
            raise ValorInvalidoError("Valor percentual deve ser um decimal entre 0 e 1.")

        self._codigo = codigo.upper()
        self._valor = valor
        self._is_percentual = is_percentual
        self._validade = validade

    @property
    def codigo(self) -> str: return self._codigo
    @property
    def valor(self) -> float: return self._valor
    @property
    def is_percentual(self) -> bool: return self._is_percentual
    @property
    def validade(self) -> Optional[datetime]: return self._validade

    def is_valido(self) -> bool:
        """Verifica se o cupom está dentro do prazo de validade."""
        if self.validade is None:
            return True
        return self.validade >= datetime.now()

    def calcular_desconto(self, valor_total: float) -> float:
        """Calcula o valor real do desconto aplicado ao valor total."""
        if not self.is_valido():
            return 0.0 # Sem desconto se expirado

        if self.is_percentual:
            return valor_total * self.valor
        else:
            # Desconto fixo, limitado pelo valor total para evitar valor negativo.
            return min(self.valor, valor_total) 

    def to_dict(self):
        return {
            'codigo': self.codigo,
            'valor': self.valor,
            'is_percentual': self.is_percentual,
            'validade': self.validade.isoformat() if self.validade else None,
        }


class Frete:
    def __init__(self, cep_origem: str, cep_destino: str, valor: float, prazo_dias: int):
        if valor < 0 or prazo_dias < 0:
            raise ValorInvalidoError("Valor do frete e prazo devem ser não-negativos.")
            
        self._cep_origem = cep_origem
        self._cep_destino = cep_destino
        self._valor = valor
        self._prazo_dias = prazo_dias

    @property
    def cep_origem(self) -> str: return self._cep_origem
    @property
    def cep_destino(self) -> str: return self._cep_destino
    @property
    def valor(self) -> float: return self._valor
    @property
    def prazo_dias(self) -> int: return self._prazo_dias
    
    def to_dict(self):
        return {
            'cep_origem': self.cep_origem,
            'cep_destino': self.cep_destino,
            'valor': self.valor,
            'prazo_dias': self.prazo_dias
        }


class Pagamento:
    STATUS_VALIDOS = ["PENDENTE", "APROVADO", "FALHOU", "CANCELADO"]
    
    def __init__(self, valor: float, status: str, data_pagamento: Optional[datetime] = None):
        if valor <= 0:
            raise ValorInvalidoError("O valor do pagamento deve ser positivo.")
        if status not in self.STATUS_VALIDOS:
            raise ValorInvalidoError(f"Status '{status}' inválido para pagamento.")
            
        self._valor = valor
        self._status = status
        self._data_pagamento = data_pagamento if data_pagamento else (datetime.now() if status == "APROVADO" else None)

    @property
    def valor(self) -> float: return self._valor
    @property
    def status(self) -> str: return self._status
    @property
    def data_pagamento(self) -> Optional[datetime]: return self._data_pagamento

    @property
    def is_aprovado(self) -> bool:
        return self.status == "APROVADO"

    def to_dict(self) -> Dict[str, Any]:
        return {
            'valor': self.valor,
            'status': self.status,
            'data_pagamento': self.data_pagamento.isoformat() if self.data_pagamento else None,
            'tipo': self.__class__.__name__ # Adiciona o tipo para desserialização
        }


class PagamentoCartao(Pagamento):
    def __init__(self, valor: float, status: str, bandeira: str, data_pagamento: Optional[datetime] = None):
        super().__init__(valor, status, data_pagamento)
        self._bandeira = bandeira

    @property
    def bandeira(self) -> str: return self._bandeira
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data['bandeira'] = self.bandeira
        return data


class PagamentoBoleto(Pagamento):
    def __init__(self, valor: float, status: str, codigo_barras: str, data_vencimento: Optional[datetime] = None):
        # Boletos são criados com status PENDENTE
        super().__init__(valor, "PENDENTE", None) 
        self._codigo_barras = codigo_barras
        # Data de vencimento padrão: 3 dias úteis
        self._data_vencimento = data_vencimento or (datetime.now() + timedelta(days=3)) 

    @property
    def codigo_barras(self) -> str: return self._codigo_barras
    @property
    def data_vencimento(self) -> datetime: return self._data_vencimento
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data['codigo_barras'] = self.codigo_barras
        data['data_vencimento'] = self.data_vencimento.isoformat()
        return data
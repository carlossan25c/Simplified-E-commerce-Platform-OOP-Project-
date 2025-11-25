class BaseProjetoError(Exception):
    """Classe base para todas as exceções personalizadas do projeto."""
    pass


class ValorInvalidoError(BaseProjetoError, ValueError):
    """
    Exceção levantada quando um valor numérico (preço, estoque, quantidade)
    é inválido (e.g., menor ou igual a zero, ou negativo onde não é permitido).
    
    Herda de ValueError para manter compatibilidade com erros nativos de valor.
    """
    pass


class DocumentoInvalidoError(BaseProjetoError, ValueError):
    """
    Exceção levantada quando um código (CPF, Email, SKU) falha na validação
    de formato, tamanho ou unicidade.
    """
    pass


class PersistenciaError(BaseProjetoError):
    """
    Exceção para erros ocorridos durante operações de leitura ou escrita
    no arquivo JSON (a ser usado na camada repositories).
    """
    pass

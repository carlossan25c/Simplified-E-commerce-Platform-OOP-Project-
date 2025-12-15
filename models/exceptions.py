class ECommerceBaseError(Exception):
    """Classe base para todas as exceções do sistema."""
    pass

class ValorInvalidoError(ECommerceBaseError):
    """Exceção levantada para valores que violam regras de negócio (e.g., estoque negativo, preço <= 0)."""
    pass

class DocumentoInvalidoError(ECommerceBaseError):
    """Exceção levantada para documentos inválidos (e.g., CPF, CNPJ)."""
    pass

class EntidadeNaoEncontradaError(ECommerceBaseError):
    """Exceção levantada quando uma entidade não é encontrada no repositório."""
    pass
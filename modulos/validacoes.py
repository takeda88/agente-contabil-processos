"""Validacoes de documentos fiscais brasileiros.

Exemplo de uso:
    from modulos.validacoes import validar_cnpj, validar_cpf
    
    if validar_cnpj("11.222.333/0001-81"):
        print("CNPJ valido")
"""

from validate_docbr import CNPJ, CPF
from typing import Union

# Instancias globais dos validadores
_cnpj_validator = CNPJ()
_cpf_validator = CPF()


def validar_cnpj(cnpj: str) -> bool:
    """Valida CNPJ brasileiro.
    
    Args:
        cnpj: CNPJ com ou sem mascara (XX.XXX.XXX/XXXX-XX ou XXXXXXXXXXXXXX)
    
    Returns:
        True se CNPJ for valido, False caso contrario
    
    Example:
        >>> validar_cnpj("11.222.333/0001-81")
        True
        >>> validar_cnpj("00.000.000/0000-00")
        False
    """
    return _cnpj_validator.validate(cnpj)


def validar_cpf(cpf: str) -> bool:
    """Valida CPF brasileiro.
    
    Args:
        cpf: CPF com ou sem mascara (XXX.XXX.XXX-XX ou XXXXXXXXXXX)
    
    Returns:
        True se CPF for valido, False caso contrario
    
    Example:
        >>> validar_cpf("123.456.789-09")
        True
    """
    return _cpf_validator.validate(cpf)


def formatar_cnpj(cnpj: str) -> str:
    """Formata CNPJ com mascara.
    
    Args:
        cnpj: CNPJ sem mascara (14 digitos)
    
    Returns:
        CNPJ formatado (XX.XXX.XXX/XXXX-XX)
    
    Example:
        >>> formatar_cnpj("11222333000181")
        "11.222.333/0001-81"
    """
    return _cnpj_validator.mask(cnpj)


def formatar_cpf(cpf: str) -> str:
    """Formata CPF com mascara.
    
    Args:
        cpf: CPF sem mascara (11 digitos)
    
    Returns:
        CPF formatado (XXX.XXX.XXX-XX)
    
    Example:
        >>> formatar_cpf("12345678909")
        "123.456.789-09"
    """
    return _cpf_validator.mask(cpf)

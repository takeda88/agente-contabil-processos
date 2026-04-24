"""Decorators e utilitarios para metricas de performance.

Exemplo de uso:
    from modulos.metricas import medir_tempo
    
    @medir_tempo
    def processar_lancamentos():
        # ... logica ...
        pass
"""

import time
import logging
from functools import wraps
from typing import Callable, Any


def medir_tempo(func: Callable) -> Callable:
    """Decorator que mede tempo de execucao de funcao.
    
    Args:
        func: Funcao a ser decorada
    
    Returns:
        Funcao decorada com medicao de tempo
    
    Example:
        >>> @medir_tempo
        ... def processar():
        ...     time.sleep(1)
        >>> processar()
        [METRICA] processar executou em 1.001s
    """
    logger = logging.getLogger(func.__module__)
    
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        inicio = time.perf_counter()
        try:
            resultado = func(*args, **kwargs)
            duracao = time.perf_counter() - inicio
            logger.info(
                f"[METRICA] {func.__name__} executou em {duracao:.3f}s",
                extra={
                    "metrica": "tempo_execucao",
                    "funcao": func.__name__,
                    "duracao_segundos": duracao,
                    "sucesso": True
                }
            )
            return resultado
        except Exception as e:
            duracao = time.perf_counter() - inicio
            logger.error(
                f"[METRICA] {func.__name__} falhou apos {duracao:.3f}s: {e}",
                extra={
                    "metrica": "tempo_execucao",
                    "funcao": func.__name__,
                    "duracao_segundos": duracao,
                    "sucesso": False,
                    "erro": str(e)
                }
            )
            raise
    
    return wrapper


class Contador:
    """Contador simples de eventos para metricas."""
    
    def __init__(self):
        self._contadores = {}
    
    def incrementar(self, nome: str, valor: int = 1):
        """Incrementa contador."""
        self._contadores[nome] = self._contadores.get(nome, 0) + valor
    
    def obter(self, nome: str) -> int:
        """Obtem valor do contador."""
        return self._contadores.get(nome, 0)
    
    def resetar(self, nome: str = None):
        """Reseta contador(es)."""
        if nome:
            self._contadores[nome] = 0
        else:
            self._contadores.clear()
    
    def todos(self) -> dict:
        """Retorna todos os contadores."""
        return self._contadores.copy()

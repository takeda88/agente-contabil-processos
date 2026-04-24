"""Configuracao de logs estruturados em JSON.

Este modulo configura o sistema de logging para gerar logs
estruturados em JSON, facilitando analise e monitoramento.

Exemplo de uso:
    from modulos.logs_config import setup_logging
    
    logger = setup_logging(__name__)
    logger.info("Processamento iniciado", extra={"empresa_id": 123})
"""

import logging
import sys
from pathlib import Path
from pythonjsonlogger import jsonlogger


def setup_logging(
    name: str,
    level: int = logging.INFO,
    log_file: str = "dados/logs/agente.jsonl"
) -> logging.Logger:
    """Configura logger com formato JSON.
    
    Args:
        name: Nome do logger (geralmente __name__)
        level: Nivel de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Caminho do arquivo de log
    
    Returns:
        Logger configurado para JSON
    
    Example:
        >>> logger = setup_logging(__name__)
        >>> logger.info("Teste", extra={"user_id": 42})
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Criar diretorio de logs se nao existir
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Handler para arquivo JSON
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    json_formatter = jsonlogger.JsonFormatter(
        "%(asctime)s %(name)s %(levelname)s %(message)s",
        rename_fields={"asctime": "timestamp", "levelname": "level"},
        timestamp=True
    )
    file_handler.setFormatter(json_formatter)
    
    # Handler para console (formato legivel)
    console_handler = logging.StreamHandler(sys.stdout)
    console_formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    console_handler.setFormatter(console_formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

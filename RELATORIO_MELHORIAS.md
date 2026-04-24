# Relatorio de Melhorias — Agente Contabil de Processos

**Data:** 24 de Abril de 2026
**Projeto:** agente-contabil-processos
**Total de linhas analisadas:** 1.563 linhas em 7 modulos principais

---

## Resumo Executivo

Este relatorio mapeia as principais oportunidades de melhoria identificadas na analise tecnica do projeto Agente Contabil. As melhorias estao organizadas por prioridade (Alta, Media, Baixa) e por categoria tecnica, com sugestoes praticas de implementacao.

---

## 1. SEGURANCA — Prioridade ALTA

### 1.1 Protecao de Credenciais
**Problema:** O `config.example.env` expoe os nomes das variaveis sensiveis (DOMINIO_SENHA, ALTERDATA_SENHA). Se o arquivo `.env` real for commitado acidentalmente, credenciais ficam expostas.

**Acoes recomendadas:**
```bash
# Verificar e atualizar .gitignore
echo ".env" >> .gitignore
echo "*.env" >> .gitignore
echo "*.db" >> .gitignore  # opcional: nao versionar o banco SQLite

# Adicionar pre-commit hook para detectar segredos
pip install detect-secrets
detect-secrets scan > .secrets.baseline
```

### 1.2 Validacao de Entradas
**Problema:** Nao ha evidencia de sanitizacao de entradas antes de queries no SQLite (`agente_contabil.db`).

**Acao recomendada:** Garantir uso de parametros preparados em todas as queries:
```python
# Errado
cursor.execute(f"SELECT * FROM lancamentos WHERE id={id}")

# Correto
cursor.execute("SELECT * FROM lancamentos WHERE id=?", (id,))
```

---

## 2. TESTES — Prioridade ALTA

### 2.1 Expandir Cobertura de Testes
**Problema:** Apenas 2 arquivos de teste (test_email.py, test_planilhas.py) para 7 modulos com 1.563 linhas. Cobertura estimada < 15%.

**Meta recomendada:** Atingir minimo de 70% de cobertura.

**Estrutura de testes sugerida:**
```
tests/
├── test_classificador.py     # Testar regras de classificacao contabil
├── test_conciliacao.py       # Testar reconciliacao bancaria
├── test_obrigacoes.py        # Testar verificacao de DCTF, DIRF, RAIS
├── test_relatorios.py        # Testar geracao de Excel
├── test_vencimentos.py       # Testar calculos de datas de vencimento
├── test_scheduler.py         # Testar agendamento de tarefas
├── test_email.py             # Ja existe
└── test_planilhas.py         # Ja existe
```

### 2.2 Configurar pytest e Medicao de Cobertura
```bash
pip install pytest pytest-cov

# Adicionar ao requirements.txt (dev):
# pytest>=7.0
# pytest-cov>=4.0

# Executar com relatorio de cobertura:
pytest --cov=. --cov-report=html tests/
```

**Criar `pyproject.toml` ou `pytest.ini`:**
```ini
[pytest]
testpaths = tests
addopts = --cov=. --cov-report=term-missing
```

---

## 3. QUALIDADE DE CODIGO — Prioridade MEDIA

### 3.1 Eliminar Backups Manuais com Git
**Problema:** `agent_contabil.py.bak` indica uso de backup manual em vez de controle de versao adequado.

**Acoes:**
```bash
# Remover o .bak do repositorio
git rm agente/agent_contabil.py.bak

# Usar branches para desenvolvimento:
git checkout -b feature/nova-funcionalidade
# Trabalhar...
git commit -m "feat: descricao da mudanca"
git merge main
```

### 3.2 Adicionar Linting e Formatacao
**Problema:** Nao ha ferramentas de qualidade de codigo configuradas.

```bash
pip install ruff black mypy

# Configurar ruff (substitui flake8, isort, etc.):
```
```toml
# pyproject.toml
[tool.ruff]
line-length = 88
select = ["E", "F", "I", "N", "W"]

[tool.black]
line-length = 88
target-version = ["py312"]

[tool.mypy]
python_version = "3.12"
warn_return_any = true
```

### 3.3 Definir requirements.txt com Versoes Fixas
**Problema:** Dependencias sem versoes pinadas causam quebras em atualizacoes.

```bash
# Gerar requirements com versoes fixas
pip freeze > requirements.txt

# Ou separar dev de producao:
# requirements.txt        — producao
# requirements-dev.txt   — desenvolvimento e testes
```

### 3.4 Resolver Modulo Incompleto
**Problema:** `modulos/` contem apenas `__pycache__` sem arquivos `.py` visiveis.

**Acao:** Revisar se ha modulos que deveriam estar nessa pasta ou se a pasta pode ser removida para evitar confusao arquitetural.

---

## 4. ARQUITETURA — Prioridade MEDIA

### 4.1 Substituir difflib por Logica Financeira Real na Conciliacao
**Problema:** O modulo `conciliacao.py` importa `difflib` (comparacao textual) e `SequenceMatcher`, que sao ferramentas de comparacao de strings — nao ideais para reconciliacao financeira que exige correspondencia por valor, data e historico.

**Melhoria sugerida:**
```python
# Logica de conciliacao financeira adequada:
from decimal import Decimal
from datetime import date

def conciliar_lancamentos(extrato: list[dict], contabilidade: list[dict]) -> dict:
    """Reconcilia por valor exato + janela de datas (+/- 3 dias)."""
    conciliados = []
    pendentes = []
    for item_extrato in extrato:
        match = encontrar_correspondencia(
            item_extrato,
            contabilidade,
            tolerancia_dias=3
        )
        if match:
            conciliados.append((item_extrato, match))
        else:
            pendentes.append(item_extrato)
    return {"conciliados": conciliados, "pendentes": pendentes}
```

### 4.2 Modularizar o AgenteContabil (Evitar God Class)
**Problema:** O `AgenteContabil` pode se tornar uma "God Class" ao crescer.

**Sugestao:** Implementar padrão Command ou Strategy para as acoes:
```python
from abc import ABC, abstractmethod

class AcaoContabil(ABC):
    @abstractmethod
    def executar(self) -> dict:
        pass

class VerificarObrigacoes(AcaoContabil):
    def executar(self) -> dict:
        # logica especifica
        pass
```

### 4.3 Implementar Fila de Tarefas (Scheduler Robusto)
**Problema:** O `scheduler.py` atual com 189 linhas pode nao ter retry e monitoramento adequados.

**Alternativa mais robusta:**
```bash
pip install apscheduler
```
```python
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore

scheduler = BackgroundScheduler(
    jobstores={"default": SQLAlchemyJobStore(url="sqlite:///dados/agente_contabil.db")},
    job_defaults={"max_instances": 1, "misfire_grace_time": 3600}
)
```

---

## 5. DOCUMENTACAO — Prioridade MEDIA

### 5.1 Adicionar Docstrings Completas
**Padrao recomendado (Google Style):**
```python
def classificar_lancamento(descricao: str, valor: float) -> dict:
    """Classifica um lancamento contabil automaticamente.

    Args:
        descricao: Historico do lancamento bancario.
        valor: Valor monetario do lancamento (positivo = credito).

    Returns:
        Dict com chaves: conta_debito, conta_credito, categoria, confianca.

    Raises:
        ValueError: Se descricao for vazia ou valor for zero.

    Example:
        >>> classificar_lancamento("SALARIO FUNC", 5000.00)
        {"conta_debito": "6.1.1", "conta_credito": "2.1.3", ...}
    """
```

### 5.2 Criar CONTRIBUTING.md
```markdown
# Como Contribuir
1. Fork o repositorio
2. Crie branch: `git checkout -b feature/nome-da-feature`
3. Escreva testes antes do codigo (TDD)
4. Execute: `pytest && ruff check . && black .`
5. Abra Pull Request com descricao clara
```

---

## 6. OBSERVABILIDADE — Prioridade BAIXA

### 6.1 Estruturar Logs em JSON
**Problema:** Logs em formato texto livre sao dificeis de consultar e analisar.

```bash
pip install python-json-logger
```
```python
import logging
from pythonjsonlogger import jsonlogger

handler = logging.FileHandler("dados/logs/agente.jsonl")
handler.setFormatter(jsonlogger.JsonFormatter(
    "%(asctime)s %(name)s %(levelname)s %(message)s"
))
```

### 6.2 Adicionar Metricas de Execucao
```python
import time
from functools import wraps

def medir_tempo(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        inicio = time.perf_counter()
        resultado = func(*args, **kwargs)
        duracao = time.perf_counter() - inicio
        logger.info(f"[METRICA] {func.__name__} executou em {duracao:.3f}s")
        return resultado
    return wrapper
```

---

## 7. INTEGRACAO FISCAL — Prioridade BAIXA

### 7.1 Validacao de CNPJ
Adicionar validacao de CNPJ nas entradas de dados:
```bash
pip install validate-docbr
```
```python
from validate_docbr import CNPJ
cnpj = CNPJ()
assert cnpj.validate("11.222.333/0001-81")
```

### 7.2 Calendarios Fiscais Atualizados
Considerar integracao com calendario oficial da Receita Federal para vencimentos dinamicos, em vez de datas hardcoded.

---

## Plano de Acao Resumido

| # | Acao | Prioridade | Esforco | Impacto |
|---|------|-----------|---------|--------|
| 1 | Atualizar .gitignore + proteger .env | Alta | Baixo | Alto |
| 2 | Criar tests/ para todos os modulos | Alta | Alto | Alto |
| 3 | Configurar pytest + cobertura | Alta | Baixo | Alto |
| 4 | Instalar ruff + black + mypy | Media | Baixo | Medio |
| 5 | Remover .bak, adotar branches Git | Media | Baixo | Medio |
| 6 | Reescrever logica de conciliacao | Media | Medio | Alto |
| 7 | Adicionar docstrings completas | Media | Medio | Medio |
| 8 | Migrar scheduler para APScheduler | Media | Medio | Medio |
| 9 | Logs em JSON estruturado | Baixa | Baixo | Medio |
| 10 | Validacao de CNPJ e docs fiscais | Baixa | Baixo | Baixo |

---

## Dependencias Recomendadas (adicionar ao requirements.txt)

```
# Producao
validate-docbr>=1.9.2
apscheduler>=3.10.0

# Desenvolvimento
pytest>=7.4.0
pytest-cov>=4.1.0
ruff>=0.1.0
black>=23.0.0
mypy>=1.5.0
detect-secrets>=1.4.0
python-json-logger>=2.0.7
```

---

*Relatorio gerado em 24/04/2026 — Baseado em analise estatica do codigo-fonte do projeto agente-contabil-processos.*

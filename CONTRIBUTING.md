# Como Contribuir para o Agente Contabil

Obrigado por considerar contribuir para o projeto! Este documento fornece diretrizes para contribuicoes.

## Processo de Contribuicao

### 1. Fork e Clone
```bash
# Fork no GitHub, depois:
git clone https://github.com/SEU_USUARIO/agente-contabil-processos.git
cd agente-contabil-processos
```

### 2. Criar Branch de Feature
```bash
# Nunca trabalhe direto na main!
git checkout -b feature/nome-da-funcionalidade
# ou
git checkout -b fix/correcao-de-bug
```

### 3. Configurar Ambiente de Desenvolvimento
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### 4. Desenvolver com TDD (Test-Driven Development)
```bash
# 1. Escreva o teste ANTES do codigo
vim tests/test_nova_funcionalidade.py

# 2. Execute o teste (deve falhar)
pytest tests/test_nova_funcionalidade.py

# 3. Implemente o codigo minimo para passar
vim contabilidade/nova_funcionalidade.py

# 4. Execute novamente (deve passar)
pytest tests/test_nova_funcionalidade.py
```

### 5. Verificar Qualidade do Codigo
```bash
# Formatacao automatica
black .

# Linting
ruff check .

# Type checking
mypy .

# Executar todos os testes
pytest

# Verificar cobertura (minimo 70%)
pytest --cov=. --cov-fail-under=70
```

### 6. Commit com Mensagens Semanticas
```bash
# Formato: tipo(escopo): descricao
#
# Tipos:
#   feat: nova funcionalidade
#   fix: correcao de bug
#   docs: apenas documentacao
#   style: formatacao (nao afeta logica)
#   refactor: refatoracao de codigo
#   test: adicionar/corrigir testes
#   chore: tarefas de manutencao

git add .
git commit -m "feat(classificador): adicionar classificacao por ML"
```

### 7. Push e Pull Request
```bash
git push origin feature/nome-da-funcionalidade
```

Depois abra Pull Request no GitHub com:
- Descricao clara do que foi alterado
- Referencia a issues relacionadas (#123)
- Screenshots se aplicavel

## Padroes de Codigo

### Docstrings (Google Style)
```python
def classificar_lancamento(descricao: str, valor: float) -> dict:
    """Classifica um lancamento contabil automaticamente.

    Args:
        descricao: Historico do lancamento bancario.
        valor: Valor monetario (positivo = credito, negativo = debito).

    Returns:
        Dict com chaves:
            - conta_debito: str
            - conta_credito: str
            - categoria: str
            - confianca: float (0.0-1.0)

    Raises:
        ValueError: Se descricao for vazia.

    Example:
        >>> classificar_lancamento("SALARIO", 5000.00)
        {"conta_debito": "1.1.1", "conta_credito": "3.1.1", ...}
    """
```

### Type Hints
```python
from typing import List, Dict, Optional
from decimal import Decimal
from datetime import date

def conciliar(
    extrato: List[Dict[str, any]],
    contabilidade: List[Dict[str, any]],
    tolerancia_dias: int = 3
) -> Dict[str, List[tuple]]:
    ...
```

### Testes
```python
import pytest

class TestClassificador:
    def setup_method(self):
        """Executado antes de cada teste."""
        self.classificador = Classificador()

    def test_classifica_salario(self):
        """Deve classificar salario corretamente."""
        resultado = self.classificador.classificar("SALARIO", 5000.0)
        assert resultado["categoria"] == "Folha de Pagamento"
        assert resultado["confianca"] > 0.8

    @pytest.mark.parametrize("descricao,esperado", [
        ("ALUGUEL", "Despesas com Aluguel"),
        ("ENERGIA", "Despesas com Utilidades"),
    ])
    def test_multiplos_casos(self, descricao, esperado):
        resultado = self.classificador.classificar(descricao, -100.0)
        assert resultado["categoria"] == esperado
```

## Checklist Antes de Submeter PR

- [ ] Testes escritos e passando (`pytest`)
- [ ] Cobertura >= 70% (`pytest --cov`)
- [ ] Codigo formatado (`black .`)
- [ ] Sem erros de linting (`ruff check .`)
- [ ] Type hints adicionados (`mypy .`)
- [ ] Docstrings completas (Google Style)
- [ ] CHANGELOG.md atualizado (se aplicavel)
- [ ] README.md atualizado (se aplicavel)
- [ ] Sem segredos commitados (`detect-secrets scan`)

## Duvidas?

Abra uma issue ou entre em contato com os mantenedores.

---

*Obrigado por contribuir para o Agente Contabil!*

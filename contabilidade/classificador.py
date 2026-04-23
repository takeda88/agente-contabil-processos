"""
Classificador Contabil com IA - Agente Contabil
Classifica e-mails, lancamentos e documentos
usando OpenAI GPT para maxima precisao.
"""

import os
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class ClassificadorContabil:
    """
    Classifica e-mails, lancamentos contabeis e documentos
    usando regras de negocio e IA (OpenAI GPT-4).
    """

    # Palavras-chave para classificacao de e-mails
    KEYWORDS_FISCAL = ['nota fiscal', 'nfe', 'sefaz', 'darf', 'tributo', 'imposto', 'receita federal', 'cnpj', 'irpf', 'irpj']
    KEYWORDS_TRABALHISTA = ['holerite', 'salario', 'fgts', 'inss', 'clt', 'demissao', 'admissao', 'ferias', 'rescisao']
    KEYWORDS_SOCIETARIO = ['contrato social', 'alteracao', 'registro', 'junta comercial', 'cnpj abertura', 'encerramento']
    KEYWORDS_BANCARIO = ['extrato', 'transferencia', 'ted', 'pix', 'boleto', 'cobranca', 'pagamento']
    KEYWORDS_URGENTE = ['urgente', 'prazo', 'vencimento', 'multa', 'autuacao', 'intimacao', 'notificacao']

    # Plano de contas simplificado para classificacao de lancamentos
    PLANO_CONTAS = {
        'RECEITA': ['receita', 'venda', 'faturamento', 'honorario', 'servico prestado'],
        'DESPESA_PESSOAL': ['salario', 'pro-labore', 'inss', 'fgts', 'ferias', 'bonus'],
        'DESPESA_FISCAL': ['darf', 'das', 'iss', 'icms', 'imposto', 'taxa'],
        'DESPESA_OPERACIONAL': ['aluguel', 'energia', 'agua', 'telefone', 'internet', 'material'],
        'DESPESA_FINANCEIRA': ['juros', 'multa', 'tarifa bancaria', 'iof'],
        'ATIVO': ['compra de bem', 'investimento', 'estoque', 'veiculo'],
        'PASSIVO': ['emprestimo', 'financiamento', 'fornecedor a pagar'],
    }

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self._llm = None

    def _get_llm(self):
        """Inicializa o LLM de forma lazy"""
        if self._llm is None:
            try:
                from openai import OpenAI
                self._llm = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
            except Exception as e:
                self.logger.warning(f"OpenAI nao disponivel: {e}. Usando classificacao por regras.")
        return self._llm

    def classificar_email(self, email: Dict) -> str:
        """
        Classifica um e-mail contabil por categoria.

        Args:
            email: Dicionario com dados do e-mail

        Returns:
            Categoria: fiscal, trabalhista, societario, bancario, outros
        """
        texto = f"{email.get('assunto', '')} {email.get('corpo', '')}".lower()

        # Classificacao por palavras-chave (rapida)
        if any(kw in texto for kw in self.KEYWORDS_FISCAL):
            return 'fiscal'
        elif any(kw in texto for kw in self.KEYWORDS_TRABALHISTA):
            return 'trabalhista'
        elif any(kw in texto for kw in self.KEYWORDS_SOCIETARIO):
            return 'societario'
        elif any(kw in texto for kw in self.KEYWORDS_BANCARIO):
            return 'bancario'
        elif any(kw in texto for kw in self.KEYWORDS_URGENTE):
            return 'urgente'
        else:
            # Fallback para IA se OpenAI disponivel
            return self._classificar_com_ia(texto) if self._get_llm() else 'outros'

    def gerar_resposta(self, email: Dict, classificacao: str) -> Dict:
        """
        Gera resposta automatica para um e-mail classificado.

        Args:
            email: Dados do e-mail
            classificacao: Categoria do e-mail

        Returns:
            Dicionario com 'automatica' (bool) e 'texto' (str)
        """
        respostas_padrao = {
            'fiscal': (
                True,
                "Recebemos seu e-mail sobre assunto fiscal. "
                "Nossa equipe esta analisando e retornaremos em breve. "
                "Caso seja urgente, entre em contato pelo telefone do escritorio."
            ),
            'bancario': (
                True,
                "Recebemos seu e-mail sobre movimentacao bancaria. "
                "Verificaremos e confirmaremos o recebimento em breve."
            ),
            'trabalhista': (
                False,  # Requer revisao humana
                "Assunto trabalhista requer revisao manual."
            ),
            'societario': (
                False,  # Requer revisao humana
                "Assunto societario requer revisao manual."
            ),
            'urgente': (
                False,  # Sempre revisao humana
                "Assunto urgente requer revisao manual imediata."
            ),
            'outros': (
                True,
                "Recebemos seu e-mail. Nossa equipe entrara em contato em breve."
            )
        }

        automatica, texto_base = respostas_padrao.get(classificacao, (True, 'Recebemos seu e-mail.'))

        # Tenta gerar resposta personalizada com IA
        if automatica and self._get_llm():
            texto_ia = self._gerar_resposta_ia(email, classificacao)
            if texto_ia:
                texto_base = texto_ia

        return {'automatica': automatica, 'texto': texto_base, 'classificacao': classificacao}

    def classificar_lancamento(self, descricao: str, valor: float) -> Dict:
        """
        Classifica um lancamento contabil automaticamente.

        Args:
            descricao: Descricao do lancamento
            valor: Valor do lancamento (positivo=debito, negativo=credito)

        Returns:
            Dicionario com conta contabil, natureza e centro de custo sugerido
        """
        descricao_lower = descricao.lower()

        # Classifica por plano de contas
        for categoria, keywords in self.PLANO_CONTAS.items():
            if any(kw in descricao_lower for kw in keywords):
                return {
                    'categoria': categoria,
                    'descricao_original': descricao,
                    'valor': valor,
                    'natureza': 'credito' if valor > 0 and categoria == 'RECEITA' else 'debito',
                    'confianca': 'alta',
                    'requer_revisao': False
                }

        # Nao classificado - envia para IA ou revisao manual
        resultado = {
            'categoria': 'NAO_CLASSIFICADO',
            'descricao_original': descricao,
            'valor': valor,
            'natureza': 'indefinida',
            'confianca': 'baixa',
            'requer_revisao': True
        }

        # Tenta classificar com IA
        if self._get_llm():
            categoria_ia = self._classificar_lancamento_ia(descricao, valor)
            if categoria_ia:
                resultado['categoria'] = categoria_ia
                resultado['confianca'] = 'media'
                resultado['requer_revisao'] = False

        return resultado

    def detectar_inconsistencias(self, lancamentos: List[Dict]) -> List[Dict]:
        """
        Detecta inconsistencias em lista de lancamentos.

        Args:
            lancamentos: Lista de lancamentos contabeis

        Returns:
            Lista de inconsistencias encontradas
        """
        inconsistencias = []

        for i, lanc in enumerate(lancamentos):
            # Verifica lancamentos com valor zero
            if lanc.get('valor', 0) == 0:
                inconsistencias.append({
                    'linha': i + 1,
                    'tipo': 'VALOR_ZERO',
                    'descricao': f"Lancamento com valor zero: {lanc.get('descricao', 'N/A')}",
                    'sugestao': 'Verificar e corrigir o valor do lancamento'
                })

            # Verifica data invalida
            from datetime import datetime
            try:
                data = lanc.get('data', '')
                if data:
                    datetime.strptime(str(data), '%Y-%m-%d')
            except ValueError:
                inconsistencias.append({
                    'linha': i + 1,
                    'tipo': 'DATA_INVALIDA',
                    'descricao': f"Data invalida no lancamento: {lanc.get('data', 'N/A')}",
                    'sugestao': 'Corrigir para formato YYYY-MM-DD'
                })

            # Verifica descricao vazia
            if not lanc.get('descricao', '').strip():
                inconsistencias.append({
                    'linha': i + 1,
                    'tipo': 'DESCRICAO_VAZIA',
                    'descricao': 'Lancamento sem descricao',
                    'sugestao': 'Adicionar descricao ao lancamento'
                })

        return inconsistencias

    # ---- Metodos privados com IA ----

    def _classificar_com_ia(self, texto: str) -> str:
        """Classifica texto usando OpenAI GPT"""
        try:
            client = self._get_llm()
            response = client.chat.completions.create(
                model=os.getenv('OPENAI_MODEL', 'gpt-4-turbo'),
                messages=[{
                    'role': 'system',
                    'content': 'Voce e um especialista em contabilidade. Classifique o e-mail em: fiscal, trabalhista, societario, bancario, urgente ou outros. Responda apenas com a categoria.'
                }, {
                    'role': 'user',
                    'content': texto[:500]  # Limita tamanho
                }],
                max_tokens=20
            )
            return response.choices[0].message.content.strip().lower()
        except Exception as e:
            self.logger.warning(f"Erro na classificacao IA: {e}")
            return 'outros'

    def _gerar_resposta_ia(self, email: Dict, classificacao: str) -> Optional[str]:
        """Gera resposta personalizada usando OpenAI GPT"""
        try:
            client = self._get_llm()
            prompt = (
                f"Assunto do e-mail: {email.get('assunto', '')}\n"
                f"Classificacao: {classificacao}\n"
                f"Gere uma resposta profissional e cordial de no maximo 3 linhas "
                f"para um escritorio de contabilidade."
            )
            response = client.chat.completions.create(
                model=os.getenv('OPENAI_MODEL', 'gpt-4-turbo'),
                messages=[{
                    'role': 'system',
                    'content': 'Voce e assistente de um escritorio de contabilidade. Seja profissional e cordial.'
                }, {
                    'role': 'user',
                    'content': prompt
                }],
                max_tokens=150
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            self.logger.warning(f"Erro ao gerar resposta IA: {e}")
            return None

    def _classificar_lancamento_ia(self, descricao: str, valor: float) -> Optional[str]:
        """Classifica lancamento contabil usando OpenAI GPT"""
        try:
            client = self._get_llm()
            categorias = ', '.join(self.PLANO_CONTAS.keys())
            response = client.chat.completions.create(
                model=os.getenv('OPENAI_MODEL', 'gpt-4-turbo'),
                messages=[{
                    'role': 'system',
                    'content': f'Classifique o lancamento contabil em uma dessas categorias: {categorias}. Responda apenas com a categoria.'
                }, {
                    'role': 'user',
                    'content': f'Descricao: {descricao}, Valor: R$ {valor:.2f}'
                }],
                max_tokens=30
            )
            return response.choices[0].message.content.strip().upper()
        except Exception:
            return None

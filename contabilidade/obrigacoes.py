"""
Modulo de Obrigacoes Acessorias.
Gerencia calendario de obrigacoes por regime tributario e gera checklists.
"""

import os
import json
import logging
from typing import Dict, List
from datetime import datetime, timedelta


class ObrigacoesAcessorias:
    """
    Modulo responsavel por obrigacoes acessorias.
    """

    def __init__(self):
        """Inicializa o modulo de obrigacoes."""
        self.logger = logging.getLogger(self.__class__.__name__)
        self.feriados = self._carregar_calendario_feriados()
        self.obrigacoes_db = self._carregar_obrigacoes_base()
        self.logger.info("ObrigacoesAcessorias inicializado")

    def listar_por_regime(self, regime: str, competencia: str) -> List[Dict]:
        """
        Retorna obrigacoes do regime especificado."""
        try:
            regime = regime.upper()
            obrigacoes = []
            
            for obrig in self.obrigacoes_db:
                if regime in obrig.get('regimes', []):
                    obrigacoes.append({
                        'nome': obrig['nome'],
                        'descricao': obrig.get('descricao', ''),
                        'periodicidade': obrig.get('periodicidade', ''),
                        'prazo': self.calcular_prazo(obrig['nome'], competencia)
                    })
            
            self.logger.info(f"{len(obrigacoes)} obrigacoes para {regime}")
            return obrigacoes
        except Exception as e:
            self.logger.error(f"Erro ao listar obrigacoes: {e}")
            return []

    def calcular_prazo(self, obrigacao: str, competencia: str) -> str:
        """
        Calcula data de vencimento real."""
        try:
            ano, mes = competencia.split('-')
            mes_seguinte = int(mes) + 1
            ano_venc = int(ano)
            
            if mes_seguinte > 12:
                mes_seguinte = 1
                ano_venc += 1
            
            if 'DCTF' in obrigacao:
                return self._dias_uteis(f"01/{mes_seguinte}/{ano_venc}", 15)
            elif 'SPED' in obrigacao:
                return f"25/{mes_seguinte}/{ano_venc}"
            elif 'DACON' in obrigacao:
                ultimo_dia = '31/03' if mes in ['12'] else f"30/{mes_seguinte}"
                return f"{ultimo_dia}/{ano_venc}"
            else:
                return f"20/{mes_seguinte}/{ano_venc}"
        except Exception as e:
            self.logger.error(f"Erro ao calcular prazo: {e}")
            return "N/A"

    def verificar_enviadas(self, competencia: str) -> Dict:
        """
        Checa quais obrigacoes ja foram enviadas."""
        try:
            arquivo_controle = f"dados/obrigacoes/{competencia}.json"
            
            if not os.path.exists(arquivo_controle):
                return {}
            
            with open(arquivo_controle, 'r', encoding='utf-8') as f:
                enviadas = json.load(f)
            
            self.logger.info(f"{len(enviadas)} obrigacoes registradas para {competencia}")
            return enviadas
        except Exception as e:
            self.logger.error(f"Erro ao verificar enviadas: {e}")
            return {}

    def gerar_checklist(self, empresa: Dict) -> List[Dict]:
        """
        Gera checklist completo para empresa."""
        try:
            regime = empresa.get('regime', 'SIMPLES')
            hoje = datetime.now()
            competencia = f"{hoje.year}-{hoje.month:02d}"
            
            obrigacoes = self.listar_por_regime(regime, competencia)
            enviadas = self.verificar_enviadas(competencia)
            
            checklist = []
            for obrig in obrigacoes:
                status = 'ENVIADO' if obrig['nome'] in enviadas else 'PENDENTE'
                checklist.append({
                    'obrigacao': obrig['nome'],
                    'prazo': obrig['prazo'],
                    'status': status,
                    'protocolo': enviadas.get(obrig['nome'], {}).get('protocolo')
                })
            
            self.logger.info(f"Checklist gerado: {len(checklist)} itens")
            return checklist
        except Exception as e:
            self.logger.error(f"Erro ao gerar checklist: {e}")
            return []

    def registrar_entrega(self, obrigacao: str, competencia: str, protocolo: str) -> bool:
        """
        Registra entrega e protocolo."""
        try:
            arquivo_controle = f"dados/obrigacoes/{competencia}.json"
            os.makedirs(os.path.dirname(arquivo_controle), exist_ok=True)
            
            enviadas = self.verificar_enviadas(competencia)
            enviadas[obrigacao] = {
                'protocolo': protocolo,
                'data_envio': datetime.now().isoformat()
            }
            
            with open(arquivo_controle, 'w', encoding='utf-8') as f:
                json.dump(enviadas, f, indent=2)
            
            self.logger.info(f"Registrada entrega: {obrigacao} - {protocolo}")
            return True
        except Exception as e:
            self.logger.error(f"Erro ao registrar entrega: {e}")
            return False

    def _dias_uteis(self, data_base: str, n_dias: int) -> str:
        """
        Calcula N dias uteis a partir de uma data."""
        try:
            data = datetime.strptime(data_base, '%d/%m/%Y')
            dias_contados = 0
            
            while dias_contados < n_dias:
                data += timedelta(days=1)
                if data.weekday() < 5 and data.strftime('%d/%m/%Y') not in self.feriados:
                    dias_contados += 1
            
            return data.strftime('%d/%m/%Y')
        except Exception as e:
            self.logger.error(f"Erro ao calcular dias uteis: {e}")
            return data_base

    def _carregar_calendario_feriados(self) -> List[str]:
        """
        Retorna lista de feriados nacionais."""
        ano_atual = datetime.now().year
        feriados = [
            f"01/01/{ano_atual}", f"21/04/{ano_atual}",
            f"01/05/{ano_atual}", f"07/09/{ano_atual}",
            f"12/10/{ano_atual}", f"02/11/{ano_atual}",
            f"15/11/{ano_atual}", f"25/12/{ano_atual}"
        ]
        return feriados

    def _carregar_obrigacoes_base(self) -> List[Dict]:
        """
        Retorna base de conhecimento de obrigacoes."""
        return [
            {'nome': 'PGDAS-D', 'regimes': ['SIMPLES'], 'periodicidade': 'MENSAL'},
            {'nome': 'DEFIS', 'regimes': ['SIMPLES'], 'periodicidade': 'ANUAL'},
            {'nome': 'SPED ECD', 'regimes': ['LUCRO_REAL', 'LUCRO_PRESUMIDO'], 'periodicidade': 'ANUAL'},
            {'nome': 'SPED ECF', 'regimes': ['LUCRO_REAL', 'LUCRO_PRESUMIDO'], 'periodicidade': 'ANUAL'},
            {'nome': 'DCTF', 'regimes': ['LUCRO_REAL', 'LUCRO_PRESUMIDO'], 'periodicidade': 'MENSAL'},
            {'nome': 'EFD ICMS/IPI', 'regimes': ['LUCRO_REAL', 'LUCRO_PRESUMIDO'], 'periodicidade': 'MENSAL'},
            {'nome': 'EFD CONTRIBUICOES', 'regimes': ['LUCRO_REAL'], 'periodicidade': 'MENSAL'},
            {'nome': 'DACON', 'regimes': ['LUCRO_PRESUMIDO'], 'periodicidade': 'MENSAL'},
        ]

"""
Modulo de Relatorios Contabeis.
Gera DRE, Balancete, Fluxo de Caixa e exporta para Excel/PDF.
"""

import os
import logging
from typing import Dict, List
from openpyxl import Workbook
from datetime import datetime


class RelatoriosContabeis:
    """
    Modulo responsavel por geracao de relatorios contabeis.
    """

    def __init__(self, planilhas_module=None):
        self.planilhas = planilhas_module
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info("RelatoriosContabeis inicializado")

    def gerar_dre(self, lancamentos: List[Dict], periodo: str) -> Dict:
        """
        Gera Demonstracao do Resultado do Exercicio."""
        try:
            receitas = sum(l.get('valor', 0) for l in lancamentos if l.get('tipo') == 'RECEITA')
            despesas = sum(l.get('valor', 0) for l in lancamentos if l.get('tipo') == 'DESPESA')
            
            dre = {
                'periodo': periodo,
                'receita_bruta': receitas,
                'total_despesas': despesas,
                'resultado_liquido': receitas - despesas,
                'data_geracao': datetime.now().isoformat()
            }
            
            self.logger.info(f"DRE gerada para {periodo}")
            return dre
        except Exception as e:
            self.logger.error(f"Erro ao gerar DRE: {e}")
            return {'erro': str(e)}

    def gerar_balancete(self, lancamentos: List[Dict], periodo: str) -> Dict:
        """
        Gera balancete de verificacao."""
        try:
            contas = {}
            for lanc in lancamentos:
                conta = lanc.get('conta', 'SEM_CONTA')
                if conta not in contas:
                    contas[conta] = {'debito': 0, 'credito': 0}
                
                if lanc.get('natureza') == 'D':
                    contas[conta]['debito'] += lanc.get('valor', 0)
                else:
                    contas[conta]['credito'] += lanc.get('valor', 0)
            
            balancete = {
                'periodo': periodo,
                'contas': contas,
                'total_debito': sum(c['debito'] for c in contas.values()),
                'total_credito': sum(c['credito'] for c in contas.values())
            }
            
            self.logger.info(f"Balancete gerado para {periodo}")
            return balancete
        except Exception as e:
            self.logger.error(f"Erro ao gerar balancete: {e}")
            return {'erro': str(e)}

    def gerar_fluxo_caixa(self, lancamentos: List[Dict], periodo: str) -> Dict:
        """
        Gera fluxo de caixa do periodo."""
        try:
            entradas = sum(l.get('valor', 0) for l in lancamentos if l.get('valor', 0) > 0)
            saidas = sum(abs(l.get('valor', 0)) for l in lancamentos if l.get('valor', 0) < 0)
            
            fluxo = {
                'periodo': periodo,
                'entradas': entradas,
                'saidas': saidas,
                'saldo_periodo': entradas - saidas
            }
            
            self.logger.info(f"Fluxo de caixa gerado para {periodo}")
            return fluxo
        except Exception as e:
            self.logger.error(f"Erro ao gerar fluxo: {e}")
            return {'erro': str(e)}

    def exportar_excel(self, relatorio: Dict, tipo: str, destino: str) -> bool:
        """
        Exporta relatorio para Excel."""
        try:
            wb = Workbook()
            ws = wb.active
            ws.title = tipo
            
            ws.append([f"Relatorio: {tipo}"])
            ws.append([f"Periodo: {relatorio.get('periodo', 'N/A')}"])
            ws.append([])
            
            for chave, valor in relatorio.items():
                if chave not in ['periodo', 'data_geracao']:
                    ws.append([chave, valor])
            
            os.makedirs(os.path.dirname(destino), exist_ok=True)
            wb.save(destino)
            
            self.logger.info(f"Excel exportado: {destino}")
            return True
        except Exception as e:
            self.logger.error(f"Erro ao exportar Excel: {e}")
            return False

    def exportar_pdf(self, relatorio: Dict, tipo: str, destino: str) -> bool:
        """
        Exporta relatorio como PDF (implementacao basica)."""
        self.logger.warning("exportar_pdf: Funcao nao implementada (requer reportlab)")
        return False

    def gerar_grafico_receitas_despesas(self, lancamentos: List[Dict], destino: str) -> bool:
        """
        Gera grafico de barras (implementacao basica)."""
        self.logger.warning("gerar_grafico: Funcao nao implementada (requer matplotlib)")
        return False

    def _agrupar_por_categoria(self, lancamentos: List[Dict]) -> Dict:
        """
        Agrupa lancamentos por categoria."""
        categorias = {}
        for lanc in lancamentos:
            cat = lanc.get('categoria', 'SEM_CATEGORIA')
            if cat not in categorias:
                categorias[cat] = []
            categorias[cat].append(lanc)
        return categorias

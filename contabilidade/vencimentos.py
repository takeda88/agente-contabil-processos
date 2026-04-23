"""
Controle de Vencimentos - Agente Contabil
Gerencia e monitora todos os vencimentos tributarios,
trabalhistas e previdenciarios do escritorio contabil.
"""

import sqlite3
import logging
import os
from datetime import datetime, date, timedelta
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class ControleVencimentos:
    """
    Controla todos os vencimentos fiscais, trabalhistas e previdenciarios.
    Mantem banco de dados de obrigacoes e alerta com antecedencia configuravel.
    """

    # Calendario fixo de obrigacoes recorrentes
    # (dia_vencimento, descricao, tipo)
    OBRIGACOES_MENSAIS = [
        (7,  'FGTS - Competencia anterior',          'FGTS'),
        (10, 'Simples Nacional - DAS',                'SIMPLES'),
        (15, 'DARF - PIS/COFINS',                    'DARF'),
        (20, 'INSS - GPS',                            'INSS'),
        (20, 'IRRF sobre salarios',                   'IRRF'),
        (25, 'DARF - IRPJ/CSLL Estimativa',          'DARF'),
        (30, 'ISS - Imposto Sobre Servicos',         'ISS'),
    ]

    OBRIGACOES_ANUAIS = [
        (date(datetime.now().year, 3, 31),  'DIRF - Declaracao IR Retido Fonte'),
        (date(datetime.now().year, 4, 30),  'DEFIS - Simples Nacional'),
        (date(datetime.now().year, 6, 30),  'RAIS - Relatorio Anual'),
        (date(datetime.now().year, 7, 31),  'ECF - Escrituracao Contabil Fiscal'),
        (date(datetime.now().year, 9, 30),  'ECD - Escrituracao Contabil Digital'),
    ]

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.db_path = os.getenv('DB_PATH', 'dados/agente_contabil.db')
        self._inicializar_banco()

    def _inicializar_banco(self):
        """Inicializa o banco de dados SQLite"""
        os.makedirs(os.path.dirname(self.db_path) if os.path.dirname(self.db_path) else '.', exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS vencimentos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    empresa TEXT NOT NULL,
                    tipo TEXT NOT NULL,
                    descricao TEXT,
                    data_vencimento TEXT NOT NULL,
                    valor REAL DEFAULT 0,
                    competencia TEXT,
                    status TEXT DEFAULT 'pendente',
                    whatsapp TEXT,
                    email TEXT,
                    criado_em TEXT DEFAULT CURRENT_TIMESTAMP,
                    pago_em TEXT
                )
            """)
            conn.commit()

    def buscar_proximos(self, dias: int = 5) -> List[Dict]:
        """
        Busca vencimentos para os proximos N dias.

        Args:
            dias: Numero de dias para verificar

        Returns:
            Lista de vencimentos proximos
        """
        hoje = date.today()
        limite = hoje + timedelta(days=dias)

        # Gera vencimentos do mes atual automaticamente
        vencimentos_auto = self._gerar_vencimentos_mes(hoje)

        # Busca vencimentos cadastrados no banco
        vencimentos_banco = self._buscar_banco(hoje, limite)

        # Combina e filtra por periodo
        todos = vencimentos_auto + vencimentos_banco
        proximos = [
            v for v in todos
            if hoje <= datetime.strptime(v['data'], '%Y-%m-%d').date() <= limite
            and v.get('status', 'pendente') == 'pendente'
        ]

        self.logger.info(f"{len(proximos)} vencimentos nos proximos {dias} dias")
        return proximos

    def _gerar_vencimentos_mes(self, hoje: date) -> List[Dict]:
        """Gera lista de vencimentos fixos do mes atual"""
        vencimentos = []
        ano, mes = hoje.year, hoje.month

        for dia, descricao, tipo in self.OBRIGACOES_MENSAIS:
            # Ajusta para o ultimo dia do mes se necessario
            try:
                data_vcto = date(ano, mes, dia)
            except ValueError:
                import calendar
                ultimo_dia = calendar.monthrange(ano, mes)[1]
                data_vcto = date(ano, mes, ultimo_dia)

            # Se vencimento cair em fim de semana, prorroga para segunda
            while data_vcto.weekday() >= 5:  # 5=Sabado, 6=Domingo
                data_vcto += timedelta(days=1)

            vencimentos.append({
                'tipo': tipo,
                'descricao': descricao,
                'data': data_vcto.strftime('%Y-%m-%d'),
                'data_formatada': data_vcto.strftime('%d/%m/%Y'),
                'competencia': f"{mes:02d}/{ano}",
                'valor': 0,
                'status': 'pendente',
                'empresa': 'GERAL',
                'dias_restantes': (data_vcto - hoje).days
            })

        return vencimentos

    def _buscar_banco(self, inicio: date, fim: date) -> List[Dict]:
        """Busca vencimentos do banco de dados"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(
                    "SELECT * FROM vencimentos WHERE data_vencimento BETWEEN ? AND ? AND status = 'pendente'",
                    (inicio.strftime('%Y-%m-%d'), fim.strftime('%Y-%m-%d'))
                )
                rows = cursor.fetchall()
                return [
                    {
                        'id': row['id'],
                        'empresa': row['empresa'],
                        'tipo': row['tipo'],
                        'descricao': row['descricao'],
                        'data': row['data_vencimento'],
                        'data_formatada': datetime.strptime(row['data_vencimento'], '%Y-%m-%d').strftime('%d/%m/%Y'),
                        'valor': row['valor'],
                        'competencia': row['competencia'],
                        'status': row['status'],
                        'whatsapp': row['whatsapp'],
                        'email': row['email'],
                        'dias_restantes': (datetime.strptime(row['data_vencimento'], '%Y-%m-%d').date() - date.today()).days
                    }
                    for row in rows
                ]
        except Exception as e:
            self.logger.error(f"Erro ao buscar banco: {e}")
            return []

    def adicionar(self, empresa: str, tipo: str, data_vencimento: str,
                  descricao: str = '', valor: float = 0,
                  competencia: str = '', whatsapp: str = '', email: str = '') -> int:
        """
        Adiciona novo vencimento ao banco de dados.

        Args:
            empresa: Nome da empresa
            tipo: Tipo (DARF, FGTS, INSS, etc.)
            data_vencimento: Data no formato YYYY-MM-DD
            descricao: Descricao detalhada
            valor: Valor em reais
            competencia: Mes/Ano de competencia
            whatsapp: Numero WhatsApp para notificacao
            email: E-mail para notificacao

        Returns:
            ID do registro criado
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    """INSERT INTO vencimentos
                       (empresa, tipo, descricao, data_vencimento, valor, competencia, whatsapp, email)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    (empresa, tipo, descricao, data_vencimento, valor, competencia, whatsapp, email)
                )
                conn.commit()
                self.logger.info(f"Vencimento cadastrado: {tipo} - {empresa} - {data_vencimento}")
                return cursor.lastrowid
        except Exception as e:
            self.logger.error(f"Erro ao adicionar vencimento: {e}")
            return -1

    def marcar_pago(self, id_vencimento: int, data_pagamento: Optional[str] = None):
        """Marca vencimento como pago"""
        if data_pagamento is None:
            data_pagamento = date.today().strftime('%Y-%m-%d')
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "UPDATE vencimentos SET status='pago', pago_em=? WHERE id=?",
                (data_pagamento, id_vencimento)
            )
            conn.commit()
        self.logger.info(f"Vencimento {id_vencimento} marcado como pago")

    def buscar_atrasados(self) -> List[Dict]:
        """Busca vencimentos atrasados (nao pagos apos a data)"""
        hoje = date.today().strftime('%Y-%m-%d')
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(
                    "SELECT * FROM vencimentos WHERE data_vencimento < ? AND status='pendente'",
                    (hoje,)
                )
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            self.logger.error(f"Erro ao buscar atrasados: {e}")
            return []

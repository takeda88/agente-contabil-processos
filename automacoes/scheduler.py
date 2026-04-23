"""
Agendador de Tarefas - Agente Contabil
Gerencia execucao automatica de todas as rotinas
do Departamento de Processos Contabeis.
"""

import logging
import os
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)


class AgendadorTarefas:
    """
    Gerencia o agendamento automatico de todas as tarefas
    do Agente Contabil usando APScheduler.

    Rotinas automaticas:
    - Verificacao de e-mails a cada 30 minutos
    - Alerta de vencimentos diariamente as 08:00
    - Relatorio mensal todo dia 1 do mes
    - Conciliacao bancaria toda segunda-feira
    - Verificacao de obrigacoes SPED semanalmente
    """

    def __init__(self, agente):
        self.agente = agente
        self.logger = logging.getLogger(self.__class__.__name__)
        self._scheduler = None

    def configurar_tarefas(self):
        """Configura todas as tarefas agendadas"""
        from apscheduler.schedulers.background import BackgroundScheduler
        from apscheduler.triggers.cron import CronTrigger
        from apscheduler.triggers.interval import IntervalTrigger

        self._scheduler = BackgroundScheduler(
            job_defaults={'coalesce': False, 'max_instances': 1},
            timezone='America/Sao_Paulo'
        )

        # -----------------------------------------------
        # VERIFICACAO DE E-MAILS - a cada 30 minutos
        # -----------------------------------------------
        self._scheduler.add_job(
            func=self.agente.processar_emails,
            trigger=IntervalTrigger(minutes=30),
            id='verificar_emails',
            name='Verificar e-mails pendentes',
            replace_existing=True
        )

        # -----------------------------------------------
        # ALERTA DE VENCIMENTOS - todos os dias as 08:00
        # -----------------------------------------------
        self._scheduler.add_job(
            func=self.agente.verificar_vencimentos,
            trigger=CronTrigger(hour=8, minute=0),
            id='alertar_vencimentos',
            name='Alertar vencimentos proximos',
            replace_existing=True
        )

        # -----------------------------------------------
        # NOTIFICACOES WHATSAPP - todos os dias as 09:00
        # -----------------------------------------------
        self._scheduler.add_job(
            func=self.agente.enviar_notificacoes_whatsapp,
            trigger=CronTrigger(hour=9, minute=0),
            id='notificacoes_whatsapp',
            name='Enviar notificacoes WhatsApp',
            replace_existing=True
        )

        # -----------------------------------------------
        # RELATORIO MENSAL - dia 1 de cada mes as 07:00
        # -----------------------------------------------
        self._scheduler.add_job(
            func=self._gerar_relatorio_mensal,
            trigger=CronTrigger(day=1, hour=7, minute=0),
            id='relatorio_mensal',
            name='Gerar relatorio mensal',
            replace_existing=True
        )

        # -----------------------------------------------
        # VERIFICACAO SPED/ECF - toda sexta-feira as 17:00
        # -----------------------------------------------
        self._scheduler.add_job(
            func=self.agente.verificar_obrigacoes_sped,
            trigger=CronTrigger(day_of_week='fri', hour=17, minute=0),
            id='verificar_sped',
            name='Verificar obrigacoes SPED/ECF',
            replace_existing=True
        )

        # -----------------------------------------------
        # ORGANIZACAO DE PASTAS - todo dia as 23:00
        # -----------------------------------------------
        self._scheduler.add_job(
            func=self._organizar_pastas,
            trigger=CronTrigger(hour=23, minute=0),
            id='organizar_pastas',
            name='Organizar pastas de documentos',
            replace_existing=True
        )

        self.logger.info(f"{len(self._scheduler.get_jobs())} tarefas agendadas")

    def iniciar(self):
        """Inicia o agendador em modo bloqueante"""
        if self._scheduler is None:
            self.configurar_tarefas()

        self._scheduler.start()
        self.logger.info("Agendador iniciado. Pressione Ctrl+C para parar.")

        import time
        try:
            while True:
                time.sleep(60)
                self._log_proximas_tarefas()
        except KeyboardInterrupt:
            self.parar()

    def parar(self):
        """Para o agendador"""
        if self._scheduler and self._scheduler.running:
            self._scheduler.shutdown()
            self.logger.info("Agendador encerrado")

    def listar_tarefas(self) -> list:
        """Retorna lista de tarefas agendadas"""
        if self._scheduler is None:
            return []
        return [
            {
                'id': job.id,
                'nome': job.name,
                'proxima_execucao': str(job.next_run_time)
            }
            for job in self._scheduler.get_jobs()
        ]

    # ---- Tarefas compostas ----

    def _gerar_relatorio_mensal(self):
        """Gera e envia relatorio mensal completo"""
        try:
            mes = datetime.now().strftime('%B/%Y')
            self.logger.info(f"Gerando relatorio mensal: {mes}")

            # Gera DRE
            relatorio = self.agente.gerar_relatorio('DRE')

            # Envia por e-mail
            destinatarios = os.getenv('EMAIL_ALERTAS', '').split(',')
            caminho = f"dados/relatorios/DRE_{datetime.now().strftime('%Y-%m')}.xlsx"
            self.agente.email.enviar_relatorio_mensal(destinatarios, caminho, mes)

            # Envia resumo por WhatsApp
            numeros = os.getenv('WHATSAPP_ALERTAS', '').split(',')
            for numero in numeros:
                if numero.strip():
                    self.agente.whatsapp.enviar_relatorio_resumido(
                        numero.strip(), relatorio, mes
                    )

            self.logger.info("Relatorio mensal enviado com sucesso")
        except Exception as e:
            self.logger.error(f"Erro ao gerar relatorio mensal: {e}")

    def _organizar_pastas(self):
        """Organiza pastas de documentos automaticamente"""
        try:
            pasta = os.getenv('PASTA_MONITORAMENTO', 'dados/documentos')
            if os.path.exists(pasta):
                self.agente.pastas.organizar_pasta(pasta)
                self.logger.info("Organizacao de pastas concluida")
        except Exception as e:
            self.logger.error(f"Erro ao organizar pastas: {e}")

    def _log_proximas_tarefas(self):
        """Loga proximas execucoes das tarefas"""
        tarefas = self.listar_tarefas()
        for tarefa in tarefas[:3]:  # Mostra as 3 proximas
            self.logger.debug(f"Proxima: {tarefa['nome']} em {tarefa['proxima_execucao']}")

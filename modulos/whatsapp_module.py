"""
Modulo WhatsApp - Agente Contabil
Envio automatico de mensagens, alertas e relatorios
via WhatsApp Business API (Twilio) para clientes e equipe.
"""

import os
import logging
from typing import List, Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class WhatsAppModule:
    """
    Modulo de integracao com WhatsApp via Twilio API.
    Permite envio de mensagens, alertas e relatorios
    para clientes e colaboradores do escritorio contabil.
    """

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.account_sid = os.getenv('TWILIO_ACCOUNT_SID', '')
        self.auth_token = os.getenv('TWILIO_AUTH_TOKEN', '')
        self.from_number = os.getenv('TWILIO_WHATSAPP_FROM', 'whatsapp:+14155238886')
        self._client = None

    def _get_client(self):
        """Inicializa o cliente Twilio de forma lazy"""
        if self._client is None:
            from twilio.rest import Client
            self._client = Client(self.account_sid, self.auth_token)
        return self._client

    def enviar_mensagem(self, numero: str, mensagem: str) -> bool:
        """
        Envia mensagem de texto via WhatsApp.

        Args:
            numero: Numero no formato +5511999999999
            mensagem: Texto da mensagem

        Returns:
            True se enviado com sucesso
        """
        try:
            client = self._get_client()
            numero_formatado = f"whatsapp:{numero}" if not numero.startswith('whatsapp:') else numero

            msg = client.messages.create(
                body=mensagem,
                from_=self.from_number,
                to=numero_formatado
            )
            self.logger.info(f"WhatsApp enviado para {numero}: SID={msg.sid}")
            return True
        except Exception as e:
            self.logger.error(f"Erro ao enviar WhatsApp para {numero}: {e}")
            return False

    def enviar_para_lista(self, numeros: List[str], mensagem: str) -> Dict:
        """
        Envia mensagem para lista de numeros.

        Args:
            numeros: Lista de numeros
            mensagem: Texto da mensagem

        Returns:
            Dicionario com sucesso/falha por numero
        """
        resultados = {'sucesso': [], 'falha': []}
        for numero in numeros:
            if self.enviar_mensagem(numero, mensagem):
                resultados['sucesso'].append(numero)
            else:
                resultados['falha'].append(numero)
        return resultados

    def enviar_alertas_vencimentos(self, vencimentos: List[Dict]):
        """
        Envia alertas de vencimentos via WhatsApp.
        Agrupa por cliente e envia mensagem consolidada.

        Args:
            vencimentos: Lista de dicionarios com dados dos vencimentos
        """
        # Agrupa vencimentos por empresa/cliente
        por_cliente = {}
        for v in vencimentos:
            empresa = v.get('empresa', 'N/A')
            numero = v.get('whatsapp', '')
            if not numero:
                continue
            if empresa not in por_cliente:
                por_cliente[empresa] = {'numero': numero, 'vencimentos': []}
            por_cliente[empresa]['vencimentos'].append(v)

        for empresa, dados in por_cliente.items():
            mensagem = self._formatar_mensagem_vencimentos(empresa, dados['vencimentos'])
            self.enviar_mensagem(dados['numero'], mensagem)

    def enviar_relatorio_resumido(self, numero: str, relatorio: Dict, mes: str):
        """
        Envia resumo do relatorio mensal via WhatsApp.

        Args:
            numero: Numero WhatsApp do destinatario
            relatorio: Dicionario com dados do relatorio
            mes: Mes de referencia
        """
        mensagem = (
            f"*RELATORIO CONTABIL - {mes}*\n"
            f"{'='*30}\n"
            f"Receita Total: R$ {relatorio.get('receita_total', '0,00')}\n"
            f"Despesa Total: R$ {relatorio.get('despesa_total', '0,00')}\n"
            f"Resultado: R$ {relatorio.get('resultado', '0,00')}\n"
            f"{'='*30}\n"
            f"Para o relatorio completo, verifique seu e-mail.\n"
            f"Departamento de Processos Contabeis"
        )
        self.enviar_mensagem(numero, mensagem)

    def enviar_alerta_documento_recebido(self, numero: str, tipo_doc: str, empresa: str):
        """
        Notifica cliente sobre documento recebido e processado.

        Args:
            numero: Numero WhatsApp do cliente
            tipo_doc: Tipo do documento (NF, boleto, contrato)
            empresa: Nome da empresa
        """
        mensagem = (
            f"Ola! Documento recebido com sucesso.\n\n"
            f"*Tipo:* {tipo_doc}\n"
            f"*Empresa:* {empresa}\n"
            f"*Data/Hora:* {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n"
            f"O documento foi classificado e arquivado automaticamente.\n"
            f"Departamento de Processos Contabeis"
        )
        self.enviar_mensagem(numero, mensagem)

    def enviar_alerta_irregularidade(self, numero: str, tipo: str, descricao: str, empresa: str):
        """
        Envia alerta de irregularidade fiscal ou contabil detectada.

        Args:
            numero: Numero WhatsApp
            tipo: Tipo da irregularidade
            descricao: Descricao detalhada
            empresa: Nome da empresa
        """
        mensagem = (
            f"*ALERTA - IRREGULARIDADE DETECTADA*\n"
            f"{'='*30}\n"
            f"*Empresa:* {empresa}\n"
            f"*Tipo:* {tipo}\n"
            f"*Descricao:* {descricao}\n"
            f"*Data:* {datetime.now().strftime('%d/%m/%Y')}\n\n"
            f"Entre em contato com o departamento imediatamente.\n"
            f"Departamento de Processos Contabeis"
        )
        self.enviar_mensagem(numero, mensagem)

    def enviar_holerite_aviso(self, numero: str, funcionario: str, mes: str):
        """
        Avisa funcionario que o holerite esta disponivel.

        Args:
            numero: Numero WhatsApp do funcionario
            funcionario: Nome do funcionario
            mes: Mes de referencia
        """
        mensagem = (
            f"Ola, {funcionario}!\n\n"
            f"Seu holerite referente a *{mes}* ja esta disponivel.\n"
            f"Acesse o sistema ou verifique seu e-mail para visualizar.\n\n"
            f"Departamento Pessoal"
        )
        self.enviar_mensagem(numero, mensagem)

    # ---- Metodos auxiliares ----

    def _formatar_mensagem_vencimentos(self, empresa: str, vencimentos: List[Dict]) -> str:
        """Formata mensagem de vencimentos para WhatsApp"""
        linhas = [
            f"*ALERTAS DE VENCIMENTO - {empresa}*",
            f"Data: {datetime.now().strftime('%d/%m/%Y')}",
            "="*30
        ]
        for v in vencimentos:
            linhas.append(
                f"- *{v['tipo']}*: {v['data']} | R$ {v.get('valor', '0,00')}"
            )
        linhas.extend([
            "="*30,
            "Providencie os pagamentos em dia para evitar multas.",
            "Departamento de Processos Contabeis"
        ])
        return "\n".join(linhas)

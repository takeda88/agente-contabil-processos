"""
Modulo de E-mail - Agente Contabil
Gerencia leitura, envio, resposta e agendamento de e-mails
para o Departamento de Processos Contabeis.
"""

import smtplib
import imaplib
import email
import logging
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from email.header import decode_header
from datetime import datetime
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class EmailModule:
    """
    Modulo completo de integracao com e-mail.
    Suporta Gmail, Outlook, e qualquer servidor SMTP/IMAP.
    """

    def __init__(self):
        self.smtp_host = os.getenv('EMAIL_SMTP', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('EMAIL_SMTP_PORT', '587'))
        self.imap_host = os.getenv('EMAIL_IMAP', 'imap.gmail.com')
        self.usuario = os.getenv('EMAIL_USER', '')
        self.senha = os.getenv('EMAIL_PASSWORD', '')
        self.logger = logging.getLogger(self.__class__.__name__)

    def ler_emails_nao_lidos(self, pasta: str = 'INBOX', limite: int = 50) -> List[Dict]:
        """
        Le e-mails nao lidos da caixa de entrada.

        Args:
            pasta: Pasta IMAP (INBOX, SENT, etc.)
            limite: Numero maximo de e-mails a ler

        Returns:
            Lista de dicionarios com dados dos e-mails
        """
        emails_lidos = []
        try:
            conexao = imaplib.IMAP4_SSL(self.imap_host)
            conexao.login(self.usuario, self.senha)
            conexao.select(pasta)

            _, ids = conexao.search(None, 'UNSEEN')
            ids_lista = ids[0].split()

            # Limita ao numero maximo
            ids_lista = ids_lista[-limite:] if len(ids_lista) > limite else ids_lista

            for id_email in ids_lista:
                _, dados = conexao.fetch(id_email, '(RFC822)')
                msg_raw = dados[0][1]
                msg = email.message_from_bytes(msg_raw)

                assunto = self._decodificar(msg.get('Subject', ''))
                remetente = msg.get('From', '')
                data = msg.get('Date', '')
                corpo = self._extrair_corpo(msg)

                emails_lidos.append({
                    'id': id_email.decode(),
                    'assunto': assunto,
                    'remetente': remetente,
                    'data': data,
                    'corpo': corpo,
                    'anexos': self._listar_anexos(msg)
                })

            conexao.logout()
            self.logger.info(f"{len(emails_lidos)} e-mails nao lidos carregados")

        except Exception as e:
            self.logger.error(f"Erro ao ler e-mails: {e}")

        return emails_lidos

    def enviar(self,
               destinatario: str,
               assunto: str,
               corpo: str,
               html: bool = False,
               anexos: Optional[List[str]] = None,
               cc: Optional[List[str]] = None):
        """
        Envia e-mail com suporte a HTML, CC e anexos.

        Args:
            destinatario: E-mail do destinatario
            assunto: Assunto do e-mail
            corpo: Corpo do e-mail (texto ou HTML)
            html: True para envio em HTML
            anexos: Lista de caminhos de arquivos para anexar
            cc: Lista de e-mails em copia
        """
        try:
            msg = MIMEMultipart()
            msg['From'] = self.usuario
            msg['To'] = destinatario
            msg['Subject'] = assunto

            if cc:
                msg['Cc'] = ', '.join(cc)

            tipo_mime = 'html' if html else 'plain'
            msg.attach(MIMEText(corpo, tipo_mime, 'utf-8'))

            # Adiciona anexos
            if anexos:
                for caminho in anexos:
                    self._adicionar_anexo(msg, caminho)

            todos_destinatarios = [destinatario] + (cc or [])

            with smtplib.SMTP(self.smtp_host, self.smtp_port) as servidor:
                servidor.ehlo()
                servidor.starttls()
                servidor.login(self.usuario, self.senha)
                servidor.sendmail(self.usuario, todos_destinatarios, msg.as_string())

            self.logger.info(f"E-mail enviado para {destinatario}: {assunto}")
            return True

        except Exception as e:
            self.logger.error(f"Erro ao enviar e-mail: {e}")
            return False

    def enviar_relatorio_mensal(self, destinatarios: List[str], relatorio_path: str, mes: str):
        """
        Envia relatorio mensal contabil por e-mail.

        Args:
            destinatarios: Lista de e-mails destinatarios
            relatorio_path: Caminho do arquivo de relatorio
            mes: Mes de referencia (ex: 'Janeiro/2026')
        """
        assunto = f"Relatorio Contabil - {mes}"
        corpo_html = f"""
        <html><body>
        <h2>Relatorio Contabil - {mes}</h2>
        <p>Segue em anexo o relatorio contabil referente ao mes de <strong>{mes}</strong>.</p>
        <p>Caso tenha duvidas, entre em contato com o Departamento de Processos.</p>
        <br>
        <p>Atenciosamente,<br>
        <strong>Agente Contabil - Departamento de Processos</strong></p>
        </body></html>
        """

        for dest in destinatarios:
            self.enviar(
                destinatario=dest,
                assunto=assunto,
                corpo=corpo_html,
                html=True,
                anexos=[relatorio_path] if os.path.exists(relatorio_path) else None
            )

    def enviar_alerta_vencimento(self, destinatario: str, vencimento: Dict):
        """
        Envia alerta de vencimento proximo.

        Args:
            destinatario: E-mail do destinatario
            vencimento: Dicionario com dados do vencimento
        """
        assunto = f"ALERTA: Vencimento {vencimento['tipo']} - {vencimento['data']}"
        corpo_html = f"""
        <html><body>
        <h2 style='color:red;'>ALERTA DE VENCIMENTO</h2>
        <table border='1' cellpadding='8' style='border-collapse:collapse;'>
            <tr><td><strong>Obrigacao:</strong></td><td>{vencimento['tipo']}</td></tr>
            <tr><td><strong>Empresa:</strong></td><td>{vencimento.get('empresa','N/A')}</td></tr>
            <tr><td><strong>Data de Vencimento:</strong></td><td style='color:red;'><strong>{vencimento['data']}</strong></td></tr>
            <tr><td><strong>Valor:</strong></td><td>R$ {vencimento.get('valor', '0,00')}</td></tr>
            <tr><td><strong>Competencia:</strong></td><td>{vencimento.get('competencia','N/A')}</td></tr>
        </table>
        <p><strong>Acao necessaria:</strong> Providencie o pagamento antes da data de vencimento para evitar multa e juros.</p>
        <br>
        <p>Agente Contabil - Departamento de Processos</p>
        </body></html>
        """
        self.enviar(destinatario, assunto, corpo_html, html=True)

    def responder(self, email_original: Dict, texto_resposta: str):
        """Responde um e-mail recebido"""
        remetente_original = email_original['remetente']
        assunto_original = email_original['assunto']
        assunto_resposta = f"Re: {assunto_original}"

        corpo_html = f"""
        <html><body>
        <p>{texto_resposta}</p>
        <br><hr>
        <p><em>Em resposta a: {assunto_original}</em></p>
        <p>Agente Contabil - Departamento de Processos</p>
        </body></html>
        """
        self.enviar(remetente_original, assunto_resposta, corpo_html, html=True)

    def marcar_para_revisao(self, email_msg: Dict, classificacao: str):
        """Marca e-mail para revisao humana com tag de classificacao"""
        self.logger.warning(
            f"E-mail marcado para revisao humana | "
            f"Classificacao: {classificacao} | "
            f"Assunto: {email_msg['assunto']} | "
            f"Remetente: {email_msg['remetente']}"
        )
        # Salva em arquivo de pendencias
        import json
        pendencias_path = 'dados/logs/emails_pendentes.json'
        pendencias = []
        if os.path.exists(pendencias_path):
            with open(pendencias_path, 'r', encoding='utf-8') as f:
                pendencias = json.load(f)

        pendencias.append({
            'data': datetime.now().isoformat(),
            'classificacao': classificacao,
            'assunto': email_msg['assunto'],
            'remetente': email_msg['remetente']
        })

        os.makedirs('dados/logs', exist_ok=True)
        with open(pendencias_path, 'w', encoding='utf-8') as f:
            json.dump(pendencias, f, ensure_ascii=False, indent=2)

    # ---- Metodos auxiliares privados ----

    def _decodificar(self, texto: str) -> str:
        """Decodifica textos de cabecalho de e-mail"""
        partes = decode_header(texto)
        resultado = []
        for parte, enc in partes:
            if isinstance(parte, bytes):
                resultado.append(parte.decode(enc or 'utf-8', errors='replace'))
            else:
                resultado.append(str(parte))
        return ''.join(resultado)

    def _extrair_corpo(self, msg) -> str:
        """Extrai o corpo textual do e-mail"""
        corpo = ''
        if msg.is_multipart():
            for part in msg.walk():
                ct = part.get_content_type()
                cd = str(part.get('Content-Disposition', ''))
                if ct == 'text/plain' and 'attachment' not in cd:
                    payload = part.get_payload(decode=True)
                    if payload:
                        corpo = payload.decode('utf-8', errors='replace')
                        break
        else:
            payload = msg.get_payload(decode=True)
            if payload:
                corpo = payload.decode('utf-8', errors='replace')
        return corpo

    def _listar_anexos(self, msg) -> List[str]:
        """Lista os nomes dos anexos do e-mail"""
        anexos = []
        for part in msg.walk():
            if part.get_content_disposition() == 'attachment':
                nome = self._decodificar(part.get_filename() or 'sem_nome')
                anexos.append(nome)
        return anexos

    def _adicionar_anexo(self, msg: MIMEMultipart, caminho: str):
        """Adiciona um arquivo como anexo ao e-mail"""
        with open(caminho, 'rb') as f:
            parte = MIMEBase('application', 'octet-stream')
            parte.set_payload(f.read())
        encoders.encode_base64(parte)
        nome_arquivo = os.path.basename(caminho)
        parte.add_header('Content-Disposition', f'attachment; filename="{nome_arquivo}"')
        msg.attach(parte)

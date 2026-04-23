"""
Modulo de Notificacoes via WhatsApp, Email e outros canais.
Envia alertas, lembretes e notificacoes de vencimentos.
"""

import os
import json
import logging
from typing import Dict, List
from datetime import datetime, timedelta


class NotificacoesModule:
    """
    Modulo responsavel por envio de notificacoes.
    """

    def __init__(self, email_module=None, whatsapp_module=None):
        """Inicializa o modulo de notificacoes."""
        self.email = email_module
        self.whatsapp = whatsapp_module
        self.logger = logging.getLogger(self.__class__.__name__)
        self.log_file = os.getenv('NOTIFICACOES_LOG', 'dados/logs/notificacoes.json')
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
        self.logger.info("NotificacoesModule inicializado")

    def alertar_vencimentos(self, vencimentos: List[Dict]) -> Dict:
        """
        Envia alertas para uma lista de vencimentos.
        """
        try:
            resultados = {
                'total': len(vencimentos),
                'enviados': 0,
                'falhas': 0,
                'detalhes': []
            }

            for vencimento in vencimentos:
                canais = vencimento.get('canais', ['email', 'whatsapp'])
                retorno = self.notificar_vencimento(vencimento, canais)

                sucesso = any(bool(v) for v in retorno.values()) if isinstance(retorno, dict) else False

                resultados['detalhes'].append({
                    'descricao': vencimento.get('descricao', 'Sem descricao'),
                    'resultado': retorno
                })

                if sucesso:
                    resultados['enviados'] += 1
                else:
                    resultados['falhas'] += 1

            self.logger.info(f"{resultados['enviados']} alertas enviados, {resultados['falhas']} falhas")
            return resultados

        except Exception as e:
            self.logger.error(f"Erro ao alertar vencimentos: {e}")
            return {'erro': str(e)}    

    def enviar_whatsapp(self, numero: str, mensagem: str) -> bool:
        """
        Envia mensagem via WhatsApp usando modulo whatsapp_module.

        Args:
            numero: Numero de telefone (formato: 5511999999999)
            mensagem: Texto da mensagem

        Returns:
            True se sucesso, False caso contrario
        """
        try:
            self.logger.info(f"Enviando WhatsApp para {numero}")
            
            # Importa modulo WhatsApp
            try:
                if self.whatsapp:
                    resultado = self.whatsapp.enviar_mensagem(numero, mensagem)
                else:
                    from modulos.whatsapp_module import WhatsAppModule
                    whatsapp = WhatsAppModule()
                    resultado = whatsapp.enviar_mensagem(numero, mensagem)
                                
                self._registrar_notificacao({
                    'tipo': 'whatsapp',
                    'destinatario': numero,
                    'mensagem': mensagem,
                    'sucesso': resultado,
                    'data_hora': datetime.now().isoformat()
                })
                
                return resultado
            
            except ImportError:
                self.logger.warning("WhatsAppModule nao disponivel")
                return False

        except Exception as e:
            self.logger.error(f"Erro ao enviar WhatsApp: {e}")
            return False

    def enviar_email_alerta(self, destinatario: str, assunto: str, corpo: str) -> bool:
        """
        Envia email de alerta usando modulo email_module.

        Args:
            destinatario: Email do destinatario
            assunto: Assunto do email
            corpo: Corpo do email

        Returns:
            True se sucesso, False caso contrario
        """
        try:
            self.logger.info(f"Enviando email para {destinatario}")
            
            try:
                if self.email:
                    resultado = self.email.enviar(
                        destinatario=destinatario,
                        assunto=assunto,
                        corpo=corpo
                    )
                else:
                    from modulos.email_module import EmailModule
                    email_mod = EmailModule()
                    resultado = email_mod.enviar(
                        destinatario=destinatario,
                        assunto=assunto,
                        corpo=corpo
                    )
                
                self._registrar_notificacao({
                    'tipo': 'email',
                    'destinatario': destinatario,
                    'assunto': assunto,
                    'sucesso': resultado,
                    'data_hora': datetime.now().isoformat()
                })
                
                return resultado
            
            except ImportError:
                self.logger.warning("EmailModule nao disponivel")
                return False

        except Exception as e:
            self.logger.error(f"Erro ao enviar email: {e}")
            return False

    def notificar_vencimento(self, vencimento: Dict, canais: List[str]) -> Dict:
        """
        Notifica vencimento em multiplos canais.

        Args:
            vencimento: Dict com dados do vencimento {'descricao', 'data', 'valor', 'contato'}
            canais: Lista de canais ['email', 'whatsapp']

        Returns:
            Dicionario com resultado por canal
        """
        try:
            resultados = {}
            descricao = vencimento.get('descricao', 'Vencimento')
            data_venc = vencimento.get('data', '')
            valor = vencimento.get('valor', '')
            contato = vencimento.get('contato', {})
            
            mensagem = f"ALERTA DE VENCIMENTO\n\n"
            mensagem += f"Descricao: {descricao}\n"
            mensagem += f"Data: {data_venc}\n"
            if valor:
                mensagem += f"Valor: R$ {valor}\n"
            
            self.logger.info(f"Notificando vencimento: {descricao}")
            
            if 'whatsapp' in canais and contato.get('telefone'):
                resultados['whatsapp'] = self.enviar_whatsapp(
                    contato['telefone'],
                    mensagem
                )
            
            if 'email' in canais and contato.get('email'):
                resultados['email'] = self.enviar_email_alerta(
                    contato['email'],
                    f"Alerta: Vencimento - {descricao}",
                    mensagem
                )
            
            return resultados

        except Exception as e:
            self.logger.error(f"Erro ao notificar vencimento: {e}")
            return {'erro': str(e)}

    def notificar_erro_critico(self, descricao: str, responsavel: str) -> bool:
        """
        Envia notificacao urgente de erro critico.

        Args:
            descricao: Descricao do erro
            responsavel: Email/telefone do responsavel

        Returns:
            True se enviado com sucesso
        """
        try:
            self.logger.critical(f"ERRO CRITICO: {descricao}")
            
            mensagem = f"ERRO CRITICO NO SISTEMA\n\n"
            mensagem += f"Descricao: {descricao}\n"
            mensagem += f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n"
            mensagem += f"\nAcao imediata necessaria!"
            
            # Tenta enviar por ambos os canais
            if '@' in responsavel:
                return self.enviar_email_alerta(
                    responsavel,
                    "URGENTE: Erro Critico no Sistema",
                    mensagem
                )
            else:
                return self.enviar_whatsapp(responsavel, mensagem)

        except Exception as e:
            self.logger.error(f"Erro ao notificar erro critico: {e}")
            return False

    def agendar_lembrete(self, vencimento: Dict, dias_antes: List[int] = [7, 3, 1]) -> List[Dict]:
        """
        Cria lembretes programados para vencimento.

        Args:
            vencimento: Dados do vencimento
            dias_antes: Dias antes do vencimento para enviar lembrete

        Returns:
            Lista de lembretes agendados
        """
        try:
            from datetime import datetime
            
            data_venc_str = vencimento.get('data', '')
            data_venc = datetime.strptime(data_venc_str, '%d/%m/%Y')
            
            lembretes = []
            
            for dias in dias_antes:
                data_lembrete = data_venc - timedelta(days=dias)
                
                lembrete = {
                    'id': f"{vencimento.get('id', 'venc')}_{dias}d",
                    'descricao': vencimento.get('descricao'),
                    'data_vencimento': data_venc_str,
                    'data_envio': data_lembrete.strftime('%d/%m/%Y'),
                    'dias_antecedencia': dias,
                    'status': 'pendente'
                }
                
                lembretes.append(lembrete)
            
            self.logger.info(f"{len(lembretes)} lembretes agendados")
            return lembretes

        except Exception as e:
            self.logger.error(f"Erro ao agendar lembretes: {e}")
            return []

    def verificar_pendentes(self) -> List[Dict]:
        """
        Verifica notificacoes pendentes de envio.

        Returns:
            Lista de notificacoes pendentes
        """
        try:
            pendencias_file = os.getenv('NOTIF_PENDENCIAS', 'dados/notificacoes_pendentes.json')
            
            if not os.path.exists(pendencias_file):
                return []
            
            with open(pendencias_file, 'r', encoding='utf-8') as f:
                todas = json.load(f)
            
            hoje = datetime.now().strftime('%d/%m/%Y')
            pendentes = [n for n in todas if n.get('data_envio') == hoje and n.get('status') == 'pendente']
            
            self.logger.info(f"{len(pendentes)} notificacoes pendentes para hoje")
            return pendentes

        except Exception as e:
            self.logger.error(f"Erro ao verificar pendentes: {e}")
            return []

    def _registrar_notificacao(self, dados: Dict) -> None:
        """
        Registra notificacao no arquivo de log.

        Args:
            dados: Dados da notificacao enviada
        """
        try:
            registros = []
            
            if os.path.exists(self.log_file):
                with open(self.log_file, 'r', encoding='utf-8') as f:
                    registros = json.load(f)
            
            registros.append(dados)
            
            # Mantém apenas ultimos 1000 registros
            if len(registros) > 1000:
                registros = registros[-1000:]
            
            with open(self.log_file, 'w', encoding='utf-8') as f:
                json.dump(registros, f, indent=2, ensure_ascii=False)

        except Exception as e:
            self.logger.error(f"Erro ao registrar notificacao: {e}")

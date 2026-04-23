"""
Agente Contabil - Departamento de Processos
Ponto de entrada principal do sistema
"""

import os
import sys
import logging
from dotenv import load_dotenv

# Carrega variaveis de ambiente
load_dotenv()

# Configura logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.FileHandler('dados/logs/agente.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Cria estrutura de diretorios necessaria
os.makedirs('dados/logs', exist_ok=True)
os.makedirs('dados/relatorios', exist_ok=True)
os.makedirs('dados/templates', exist_ok=True)

from agente.agent_contabil import AgenteContabil
from automacoes.scheduler import AgendadorTarefas


def main():
    """Funcao principal - inicializa e executa o agente"""
    logger.info("=" * 60)
    logger.info("AGENTE CONTABIL - DEPARTAMENTO DE PROCESSOS")
    logger.info("=" * 60)

    try:
        # Inicializa o agente principal
        agente = AgenteContabil()
        logger.info("Agente inicializado com sucesso")

        # Inicializa o agendador de tarefas automaticas
        agendador = AgendadorTarefas(agente)
        agendador.configurar_tarefas()

        # Menu interativo para uso manual
        while True:
            print("\n" + "="*50)
            print("AGENTE CONTABIL - MENU PRINCIPAL")
            print("="*50)
            print("1. Processar e-mails pendentes")
            print("2. Verificar vencimentos")
            print("3. Gerar relatorio contabil")
            print("4. Conciliacao bancaria")
            print("5. Monitorar pastas")
            print("6. Enviar notificacoes WhatsApp")
            print("7. Analisar planilha")
            print("8. Gerar documento Word")
            print("9. Web scraping fiscal")
            print("10. Verificar obrigacoes SPED/ECF")
            print("11. Iniciar modo automatico (scheduler)")
            print("0. Sair")
            print("-"*50)

            escolha = input("Escolha uma opcao: ").strip()

            if escolha == "0":
                logger.info("Encerrando o Agente Contabil")
                break
            elif escolha == "1":
                agente.processar_emails()
            elif escolha == "2":
                agente.verificar_vencimentos()
            elif escolha == "3":
                tipo = input("Tipo (DRE/balancete/bp/fluxo_caixa): ")
                agente.gerar_relatorio(tipo)
            elif escolha == "4":
                arquivo = input("Arquivo OFX/CSV do extrato bancario: ")
                agente.conciliacao_bancaria(arquivo)
            elif escolha == "5":
                pasta = input("Pasta a monitorar: ")
                agente.monitorar_pasta(pasta)
            elif escolha == "6":
                agente.enviar_notificacoes_whatsapp()
            elif escolha == "7":
                arquivo = input("Arquivo Excel (.xlsx): ")
                agente.analisar_planilha(arquivo)
            elif escolha == "8":
                template = input("Template Word: ")
                agente.gerar_documento_word(template)
            elif escolha == "9":
                portal = input("Portal (receita/ecac/sefaz/simples): ")
                agente.scraping_fiscal(portal)
            elif escolha == "10":
                agente.verificar_obrigacoes_sped()
            elif escolha == "11":
                logger.info("Iniciando modo automatico...")
                agendador.iniciar()
            else:
                print("Opcao invalida. Tente novamente.")

    except KeyboardInterrupt:
        logger.info("Agente encerrado pelo usuario")
    except Exception as e:
        logger.error(f"Erro critico: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

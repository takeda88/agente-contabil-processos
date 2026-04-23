# Agente Contabil - Departamento de Processos

> Agente de Inteligencia Artificial voltado para a area da Contabilidade, especificamente para o Departamento de Processos. Automatiza, analisa, corrige, sugere melhorias e envia comunicacoes de forma inteligente.

---

## Funcionalidades

### Analise e Integracao de Dados
- **E-mail** - Leitura, classificacao, resposta automatica e envio agendado (SMTP/IMAP/Gmail API/Outlook)
- **WhatsApp** - Envio automatico de mensagens e relatorios via WhatsApp Business API / Twilio
- **Planilhas** - Leitura, escrita, analise e geracao de relatorios em Excel (.xlsx) e Google Sheets
- **Word** - Geracao e preenchimento automatico de documentos .docx com dados contabeis
- **Pastas e Arquivos** - Monitoramento, organizacao, renomeacao e arquivamento automatico
- **Sites** - Web scraping de portais fiscais (Receita Federal, SEFAZ, e-CAC, Simples Nacional)
- **Programas** - Integracao com softwares contabeis (Dominio, Alterdata, Contabilizei, SPED)
- **PDF** - Extracao de dados de notas fiscais, DARF, guias e contratos

### Automacoes Contabeis
- Classificacao automatica de lancamentos contabeis
- Conciliacao bancaria automatizada
- Verificacao de vencimentos (DARF, FGTS, INSS, ISS, ICMS)
- Geracao automatica de guias de pagamento
- Alertas de obrigacoes acessorias (SPED, ECF, EFD, DCTF)
- Analise de DRE, Balancete e Balanco Patrimonial
- Deteccao de inconsistencias e erros lancamentos

### Envios Automaticos
- Relatorios mensais por e-mail/WhatsApp
- Notificacoes de vencimentos para clientes
- Envio de boletos e cobracas automaticas
- Distribuicao de holerites e informes de rendimentos
- Alertas de irregularidades fiscais

---

## Estrutura do Projeto

```
agente-contabil-processos/
|
+-- agente/
|   +-- __init__.py
|   +-- agent_contabil.py        # Orquestrador principal
|   +-- config.py                # Configuracoes globais
|
+-- modulos/
|   +-- __init__.py
|   +-- email_module.py          # Integracao e-mail (SMTP/IMAP/Gmail)
|   +-- whatsapp_module.py       # WhatsApp Business API / Twilio
|   +-- planilhas_module.py      # Excel / Google Sheets
|   +-- word_module.py           # Geracao documentos Word
|   +-- pastas_module.py         # Gestao de arquivos e pastas
|   +-- web_scraping_module.py   # Portais fiscais
|   +-- pdf_module.py            # Extracao de dados PDF
|   +-- sped_module.py           # SPED / EFD / ECF
|   +-- notificacoes_module.py   # Alertas e notificacoes
|
+-- contabilidade/
|   +-- __init__.py
|   +-- classificador.py         # Classificacao de lancamentos
|   +-- conciliacao.py           # Conciliacao bancaria
|   +-- vencimentos.py           # Controle de vencimentos
|   +-- relatorios.py            # DRE, Balancete, BP
|   +-- obrigacoes.py            # DCTF, SPED, ECF, EFD
|
+-- automacoes/
|   +-- __init__.py
|   +-- scheduler.py             # Agendador de tarefas (APScheduler)
|   +-- envio_automatico.py      # Envios automatizados
|   +-- alertas.py               # Sistema de alertas
|
+-- dados/
|   +-- templates/               # Templates Word/Excel
|   +-- relatorios/              # Relatorios gerados
|   +-- logs/                    # Logs do sistema
|
+-- tests/
|   +-- test_email.py
|   +-- test_planilhas.py
|   +-- test_contabilidade.py
|
+-- requirements.txt
+-- config.example.env
+-- main.py
+-- README.md
```

---

## Instalacao

```bash
# 1. Clone o repositorio
git clone https://github.com/takeda88/agente-contabil-processos.git
cd agente-contabil-processos

# 2. Crie o ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 3. Instale as dependencias
pip install -r requirements.txt

# 4. Configure as variaveis de ambiente
cp config.example.env .env
# Edite o arquivo .env com suas credenciais

# 5. Execute o agente
python main.py
```

---

## Configuracao (.env)

```env
# E-mail
EMAIL_USER=seu@email.com
EMAIL_PASSWORD=sua_senha
EMAIL_SMTP=smtp.gmail.com
EMAIL_SMTP_PORT=587
EMAIL_IMAP=imap.gmail.com

# WhatsApp (Twilio)
TWILIO_ACCOUNT_SID=seu_sid
TWILIO_AUTH_TOKEN=seu_token
TWILIO_WHATSAPP_FROM=whatsapp:+14155238886

# OpenAI (LLM)
OPENAI_API_KEY=sua_api_key

# Google Sheets
GOOGLE_CREDENTIALS_FILE=credentials.json

# Banco de Dados
DB_PATH=dados/agente_contabil.db
```

---

## Tecnologias Utilizadas

| Tecnologia | Uso |
|---|---|
| Python 3.11+ | Linguagem principal |
| OpenAI GPT-4 | Motor de IA / analise |
| LangChain | Orquestracao do agente |
| APScheduler | Agendamento de tarefas |
| smtplib / imaplib | Integracao e-mail |
| Twilio | WhatsApp API |
| openpyxl / pandas | Planilhas Excel |
| python-docx | Documentos Word |
| pdfplumber / PyMuPDF | Extracao PDF |
| BeautifulSoup / Selenium | Web scraping |
| gspread | Google Sheets |
| watchdog | Monitoramento de pastas |
| SQLite | Banco de dados local |

---

## Casos de Uso no Departamento de Processos

1. **Abertura de Empresas** - Coleta documentos, preenche formularios, monitora andamento no portal da Receita Federal
2. **Escrituracao Contabil** - Importa extratos bancarios, classifica lancamentos automaticamente
3. **Obrigacoes Fiscais** - Alerta vencimentos, gera DARF, monitora entrega de declaracoes
4. **Atendimento ao Cliente** - Responde e-mails e WhatsApp com informacoes sobre processos em andamento
5. **Relatorios Gerenciais** - Gera DRE, Balancete e Fluxo de Caixa automaticamente
6. **Auditoria Interna** - Detecta inconsistencias e sugere correcoes nos lancamentos

---

## Licenca

MIT License - veja o arquivo LICENSE para detalhes.

---

*Desenvolvido para o Departamento de Processos Contabeis*

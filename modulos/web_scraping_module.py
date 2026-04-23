"""
Modulo de Web Scraping para consultas fiscais e extrações de dados de sites.
Realiza consultas em APIs publicas (Receita Federal, SINTEGRA) e extrai informacoes
de paginas web usando BeautifulSoup.
"""

import os
import re
import time
import logging
from typing import Dict, List, Optional
import requests
from bs4 import BeautifulSoup


class WebScrapingModule:
    """
    Modulo responsavel por web scraping e consultas fiscais online.
    """

    def __init__(self):
        """Inicializa o modulo de web scraping."""
        self.logger = logging.getLogger(self.__class__.__name__)
        self.timeout = int(os.getenv('WEB_TIMEOUT', '30'))
        self.max_retries = int(os.getenv('WEB_MAX_RETRIES', '3'))
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.logger.info("WebScrapingModule inicializado")

    def buscar_cnpj(self, cnpj: str) -> Dict:
        """
        Consulta informacoes de CNPJ na API publica da Receita Federal.

        Args:
            cnpj: CNPJ a ser consultado (com ou sem formatacao)

        Returns:
            Dicionario com dados da empresa ou erro
        """
        try:
            cnpj_limpo = re.sub(r'\D', '', cnpj)
            if len(cnpj_limpo) != 14:
                return {'erro': 'CNPJ invalido'}

            url = f'https://www.receitaws.com.br/v1/cnpj/{cnpj_limpo}'
            self.logger.info(f"Consultando CNPJ: {cnpj_limpo}")

            response = self._fazer_requisicao(url)
            if not response:
                return {'erro': 'Falha na requisicao'}

            import json
            dados = json.loads(response)

            if dados.get('status') == 'ERROR':
                return {'erro': dados.get('message', 'Erro desconhecido')}

            return {
                'cnpj': dados.get('cnpj'),
                'razao_social': dados.get('nome'),
                'nome_fantasia': dados.get('fantasia'),
                'situacao': dados.get('situacao'),
                'data_abertura': dados.get('abertura'),
                'natureza_juridica': dados.get('natureza_juridica'),
                'porte': dados.get('porte'),
                'endereco': {
                    'logradouro': dados.get('logradouro'),
                    'numero': dados.get('numero'),
                    'complemento': dados.get('complemento'),
                    'bairro': dados.get('bairro'),
                    'municipio': dados.get('municipio'),
                    'uf': dados.get('uf'),
                    'cep': dados.get('cep')
                },
                'telefone': dados.get('telefone'),
                'email': dados.get('email'),
                'capital_social': dados.get('capital_social'),
                'atividade_principal': dados.get('atividade_principal', []),
                'atividades_secundarias': dados.get('atividades_secundarias', [])
            }

        except Exception as e:
            self.logger.error(f"Erro ao buscar CNPJ {cnpj}: {e}")
            return {'erro': str(e)}

    def verificar_situacao_fiscal(self, cnpj: str) -> Dict:
        """
        Verifica situacao fiscal: regime tributario, SIMPLES, MEI.

        Args:
            cnpj: CNPJ a ser verificado

        Returns:
            Dicionario com informacoes fiscais
        """
        try:
            dados_cnpj = self.buscar_cnpj(cnpj)
            if 'erro' in dados_cnpj:
                return dados_cnpj

            cnpj_limpo = re.sub(r'\D', '', cnpj)
            situacao_fiscal = {
                'cnpj': cnpj_limpo,
                'razao_social': dados_cnpj.get('razao_social'),
                'situacao_cadastral': dados_cnpj.get('situacao'),
                'regime_tributario': 'Nao identificado',
                'optante_simples': False,
                'mei': False
            }

            # Verifica se e MEI pelo porte
            porte = dados_cnpj.get('porte', '')
            if 'MEI' in porte.upper() or 'MICROEMPREENDEDOR' in porte.upper():
                situacao_fiscal['mei'] = True
                situacao_fiscal['regime_tributario'] = 'MEI - Simples Nacional'

            # Simula consulta ao SIMPLES (em producao usaria API oficial)
            # Aqui apenas estima baseado no porte
            if porte and ('MICRO' in porte.upper() or 'PEQUENO' in porte.upper()):
                situacao_fiscal['optante_simples'] = True
                if not situacao_fiscal['mei']:
                    situacao_fiscal['regime_tributario'] = 'Simples Nacional'
            elif porte and 'DEMAIS' in porte.upper():
                situacao_fiscal['regime_tributario'] = 'Lucro Presumido ou Real'

            self.logger.info(f"Situacao fiscal verificada para {cnpj_limpo}")
            return situacao_fiscal

        except Exception as e:
            self.logger.error(f"Erro ao verificar situacao fiscal {cnpj}: {e}")
            return {'erro': str(e)}

    def baixar_certidao_negativa(self, cnpj: str, destino: str) -> Optional[str]:
        """
        Tenta baixar Certidao Negativa de Debitos Federal.
        NOTA: Esta e uma implementacao simulada. Em producao, seria necessario
        integrar com o e-CAC da Receita Federal com certificado digital.

        Args:
            cnpj: CNPJ da empresa
            destino: Caminho onde salvar o arquivo

        Returns:
            Caminho do arquivo salvo ou None em caso de erro
        """
        try:
            self.logger.warning("baixar_certidao_negativa: Funcao simulada")
            self.logger.info(f"Tentativa de download CND para CNPJ {cnpj}")

            # Em producao, aqui faria:
            # 1. Autenticacao com certificado digital
            # 2. Acesso ao portal e-CAC
            # 3. Download da certidao

            # Simulacao: retorna mensagem
            return None

        except Exception as e:
            self.logger.error(f"Erro ao baixar certidao {cnpj}: {e}")
            return None

    def consultar_sintegra(self, uf: str, ie: str) -> Dict:
        """
        Consulta Inscricao Estadual no SINTEGRA.
        NOTA: Implementacao simulada. Cada estado tem seu proprio portal.

        Args:
            uf: Sigla do estado (ex: 'SP', 'RJ')
            ie: Inscricao Estadual

        Returns:
            Dicionario com dados da IE ou erro
        """
        try:
            uf = uf.upper().strip()
            ie_limpa = re.sub(r'\D', '', ie)

            self.logger.info(f"Consultando IE {ie_limpa} no SINTEGRA {uf}")

            # URLs dos SINTEGRAs estaduais (exemplos)
            urls_sintegra = {
                'SP': 'https://www.fazenda.sp.gov.br/sintegra/',
                'RJ': 'https://www4.fazenda.rj.gov.br/sintegra/',
                'MG': 'https://www2.fazenda.mg.gov.br/sol/',
                'GO': 'http://appagg.sefaz.go.gov.br/Sintegra/'
            }

            if uf not in urls_sintegra:
                return {'erro': f'UF {uf} nao suportada'}

            # Simulacao de retorno (em producao faria scraping real)
            return {
                'uf': uf,
                'ie': ie_limpa,
                'situacao': 'HABILITADO',
                'consulta': 'Simulada - implementar scraping especifico por UF',
                'url_portal': urls_sintegra[uf]
            }

        except Exception as e:
            self.logger.error(f"Erro ao consultar SINTEGRA {uf}/{ie}: {e}")
            return {'erro': str(e)}

    def extrair_dados_site(self, url: str, seletores: Dict) -> Dict:
        """
        Extrai dados de um site usando seletores CSS.

        Args:
            url: URL do site
            seletores: Dicionario com nome_campo: seletor_css

        Returns:
            Dicionario com dados extraidos
        """
        try:
            self.logger.info(f"Extraindo dados de {url}")

            html = self._fazer_requisicao(url)
            if not html:
                return {'erro': 'Falha ao carregar pagina'}

            soup = BeautifulSoup(html, 'html.parser')
            dados = {}

            for campo, seletor in seletores.items():
                try:
                    elemento = soup.select_one(seletor)
                    if elemento:
                        dados[campo] = elemento.get_text(strip=True)
                    else:
                        dados[campo] = None
                        self.logger.warning(f"Seletor '{seletor}' nao encontrado")
                except Exception as e:
                    self.logger.error(f"Erro ao extrair campo {campo}: {e}")
                    dados[campo] = None

            return dados

        except Exception as e:
            self.logger.error(f"Erro ao extrair dados de {url}: {e}")
            return {'erro': str(e)}

    def _fazer_requisicao(self, url: str, headers: Dict = None) -> Optional[str]:
        """
        Faz requisicao HTTP com retry automatico.

        Args:
            url: URL a ser acessada
            headers: Headers adicionais (opcional)

        Returns:
            Conteudo da resposta ou None em caso de erro
        """
        for tentativa in range(1, self.max_retries + 1):
            try:
                self.logger.debug(f"Tentativa {tentativa}/{self.max_retries} - {url}")

                request_headers = self.session.headers.copy()
                if headers:
                    request_headers.update(headers)

                response = self.session.get(
                    url,
                    timeout=self.timeout,
                    headers=request_headers
                )

                if response.status_code == 200:
                    return response.text
                elif response.status_code == 429:  # Rate limit
                    self.logger.warning("Rate limit atingido, aguardando...")
                    time.sleep(5 * tentativa)
                else:
                    self.logger.warning(f"Status {response.status_code} - {url}")

            except requests.Timeout:
                self.logger.warning(f"Timeout na tentativa {tentativa}")
                time.sleep(2 * tentativa)
            except requests.RequestException as e:
                self.logger.error(f"Erro na requisicao {tentativa}: {e}")
                if tentativa < self.max_retries:
                    time.sleep(2 * tentativa)

        self.logger.error(f"Todas as tentativas falharam para {url}")
        return None

    def __del__(self):
        """Fecha a sessao ao destruir o objeto."""
        try:
            self.session.close()
        except:
            pass

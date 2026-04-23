"""
Modulo para leitura e processamento de arquivos PDF.
Extrai textos, notas fiscais, boletos, extratos bancarios e realiza operacoes de PDF.
"""

import os
import re
import logging
from typing import Dict, List, Optional
import fitz  # PyMuPDF


class PdfModule:
    """
    Modulo responsavel por operacoes com arquivos PDF.
    """

    def __init__(self):
        """Inicializa o modulo de PDF."""
        self.logger = logging.getLogger(self.__class__.__name__)
        self.dpi = int(os.getenv('PDF_IMAGE_DPI', '150'))
        self.logger.info("PdfModule inicializado")

    def ler_texto(self, caminho: str) -> str:
        """
        Extrai todo o texto de um arquivo PDF.

        Args:
            caminho: Caminho do arquivo PDF

        Returns:
            Texto completo extraido do PDF
        """
        try:
            if not os.path.exists(caminho):
                self.logger.error(f"Arquivo nao encontrado: {caminho}")
                return ""

            self.logger.info(f"Lendo PDF: {caminho}")
            doc = fitz.open(caminho)
            texto_completo = ""

            for pagina_num in range(len(doc)):
                pagina = doc[pagina_num]
                texto_completo += pagina.get_text()

            doc.close()
            self.logger.info(f"PDF lido com sucesso: {len(doc)} paginas")
            return texto_completo

        except Exception as e:
            self.logger.error(f"Erro ao ler PDF {caminho}: {e}")
            return ""

    def ler_nota_fiscal(self, caminho: str) -> Dict:
        """
        Extrai informacoes de uma nota fiscal em PDF.

        Args:
            caminho: Caminho do arquivo PDF da nota fiscal

        Returns:
            Dicionario com dados da nota fiscal
        """
        try:
            texto = self.ler_texto(caminho)
            if not texto:
                return {'erro': 'Nao foi possivel ler o PDF'}

            texto_limpo = self._limpar_texto(texto)

            # Regex para extrair dados comuns de NF-e
            cnpj_pattern = r'CNPJ[:\s]*(\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2})'
            numero_nf_pattern = r'N[FÚ]MERO[:\s]*(\d+)'
            valor_pattern = r'VALOR TOTAL[:\s]*R?\$?[:\s]*(\d+[.,]\d{2})'
            data_pattern = r'DATA[:\s]*(\d{2}/\d{2}/\d{4})'

            cnpj_match = re.search(cnpj_pattern, texto_limpo, re.IGNORECASE)
            numero_match = re.search(numero_nf_pattern, texto_limpo, re.IGNORECASE)
            valor_match = re.search(valor_pattern, texto_limpo, re.IGNORECASE)
            data_match = re.search(data_pattern, texto_limpo, re.IGNORECASE)

            resultado = {
                'arquivo': os.path.basename(caminho),
                'cnpj': cnpj_match.group(1) if cnpj_match else None,
                'numero': numero_match.group(1) if numero_match else None,
                'valor': valor_match.group(1).replace(',', '.') if valor_match else None,
                'data_emissao': data_match.group(1) if data_match else None
            }

            self.logger.info(f"Nota fiscal processada: NF {resultado.get('numero')}")
            return resultado

        except Exception as e:
            self.logger.error(f"Erro ao ler nota fiscal {caminho}: {e}")
            return {'erro': str(e)}

    def ler_boleto(self, caminho: str) -> Dict:
        """
        Extrai informacoes de um boleto em PDF.

        Args:
            caminho: Caminho do arquivo PDF do boleto

        Returns:
            Dicionario com dados do boleto
        """
        try:
            texto = self.ler_texto(caminho)
            if not texto:
                return {'erro': 'Nao foi possivel ler o PDF'}

            texto_limpo = self._limpar_texto(texto)

            # Regex para codigo de barras (linha digitavel)
            codigo_barras_pattern = r'(\d{5}\.\d{5}\s+\d{5}\.\d{6}\s+\d{5}\.\d{6}\s+\d\s+\d{14})'
            valor_pattern = r'R\$[:\s]*(\d+[.,]\d{2})'
            vencimento_pattern = r'VENCIMENTO[:\s]*(\d{2}/\d{2}/\d{4})'

            codigo_match = re.search(codigo_barras_pattern, texto_limpo)
            valor_match = re.search(valor_pattern, texto_limpo)
            vencimento_match = re.search(vencimento_pattern, texto_limpo, re.IGNORECASE)

            resultado = {
                'arquivo': os.path.basename(caminho),
                'codigo_barras': codigo_match.group(1).replace(' ', '') if codigo_match else None,
                'valor': valor_match.group(1).replace(',', '.') if valor_match else None,
                'vencimento': vencimento_match.group(1) if vencimento_match else None
            }

            self.logger.info(f"Boleto processado: Venc {resultado.get('vencimento')}")
            return resultado

        except Exception as e:
            self.logger.error(f"Erro ao ler boleto {caminho}: {e}")
            return {'erro': str(e)}

    def ler_extrato_bancario(self, caminho: str) -> List[Dict]:
        """
        Extrai lancamentos de um extrato bancario em PDF.

        Args:
            caminho: Caminho do arquivo PDF do extrato

        Returns:
            Lista de dicionarios com os lancamentos
        """
        try:
            texto = self.ler_texto(caminho)
            if not texto:
                return []

            texto_limpo = self._limpar_texto(texto)
            lancamentos = []

            # Regex para linha de extrato: Data Descricao Valor
            # Exemplo: 15/01 PAGAMENTO PIX -150,00
            linha_pattern = r'(\d{2}/\d{2})\s+([A-Z][\w\s]+?)\s+(-?\d+[.,]\d{2})'

            matches = re.finditer(linha_pattern, texto_limpo)

            for match in matches:
                data = match.group(1)
                descricao = match.group(2).strip()
                valor = match.group(3).replace(',', '.')

                lancamentos.append({
                    'data': data,
                    'descricao': descricao,
                    'valor': float(valor),
                    'tipo': 'DEBITO' if '-' in match.group(3) else 'CREDITO'
                })

            self.logger.info(f"Extrato processado: {len(lancamentos)} lancamentos")
            return lancamentos

        except Exception as e:
            self.logger.error(f"Erro ao ler extrato {caminho}: {e}")
            return []

    def mesclar(self, arquivos: List[str], destino: str) -> bool:
        """
        Mescla multiplos PDFs em um unico arquivo.

        Args:
            arquivos: Lista de caminhos dos PDFs a mesclar
            destino: Caminho do arquivo de saida

        Returns:
            True se sucesso, False caso contrario
        """
        try:
            self.logger.info(f"Mesclando {len(arquivos)} PDFs")
            doc_final = fitz.open()

            for arquivo in arquivos:
                if not os.path.exists(arquivo):
                    self.logger.warning(f"Arquivo nao encontrado: {arquivo}")
                    continue

                doc = fitz.open(arquivo)
                doc_final.insert_pdf(doc)
                doc.close()

            # Garante que o diretorio de destino existe
            os.makedirs(os.path.dirname(destino), exist_ok=True)

            doc_final.save(destino)
            doc_final.close()

            self.logger.info(f"PDFs mesclados com sucesso: {destino}")
            return True

        except Exception as e:
            self.logger.error(f"Erro ao mesclar PDFs: {e}")
            return False

    def converter_para_imagem(self, caminho: str, pasta_destino: str) -> List[str]:
        """
        Converte cada pagina de um PDF em imagem PNG.

        Args:
            caminho: Caminho do arquivo PDF
            pasta_destino: Pasta onde salvar as imagens

        Returns:
            Lista com caminhos das imagens geradas
        """
        try:
            if not os.path.exists(caminho):
                self.logger.error(f"Arquivo nao encontrado: {caminho}")
                return []

            os.makedirs(pasta_destino, exist_ok=True)
            self.logger.info(f"Convertendo PDF para imagens: {caminho}")

            doc = fitz.open(caminho)
            imagens = []
            nome_base = os.path.splitext(os.path.basename(caminho))[0]

            for pagina_num in range(len(doc)):
                pagina = doc[pagina_num]
                
                # Converte a pagina em imagem
                mat = fitz.Matrix(self.dpi / 72, self.dpi / 72)
                pix = pagina.get_pixmap(matrix=mat)

                # Define nome do arquivo de saida
                nome_imagem = f"{nome_base}_pag{pagina_num + 1}.png"
                caminho_imagem = os.path.join(pasta_destino, nome_imagem)

                # Salva a imagem
                pix.save(caminho_imagem)
                imagens.append(caminho_imagem)

            doc.close()
            self.logger.info(f"{len(imagens)} imagens geradas")
            return imagens

        except Exception as e:
            self.logger.error(f"Erro ao converter PDF para imagem {caminho}: {e}")
            return []

    def _limpar_texto(self, texto: str) -> str:
        """
        Remove caracteres especiais e normaliza o texto.

        Args:
            texto: Texto a ser limpo

        Returns:
            Texto limpo e normalizado
        """
        # Remove quebras de linha excessivas
        texto = re.sub(r'\n+', ' ', texto)
        
        # Remove espacos multiplos
        texto = re.sub(r'\s+', ' ', texto)
        
        # Remove caracteres de controle
        texto = re.sub(r'[\x00-\x1F\x7F]', '', texto)
        
        return texto.strip()

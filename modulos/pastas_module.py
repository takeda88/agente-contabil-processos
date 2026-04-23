"""
Modulo de Pastas e Arquivos - Agente Contabil
Monitoramento, organizacao, classificacao e arquivamento
automatico de documentos contabeis.
"""

import os
import shutil
import logging
from typing import Callable, Optional, Dict
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class PastasModule:
    """
    Modulo de gestao inteligente de pastas e arquivos.
    Monitora diretorios, classifica e organiza documentos
    automaticamente conforme tipo e conteudo.
    """

    # Mapeamento de extensoes para categorias
    CATEGORIAS = {
        'fiscal': ['.xml', '.txt'],       # NFe, NFS, SPED
        'planilha': ['.xlsx', '.xls', '.csv'],
        'documento': ['.pdf', '.docx', '.doc'],
        'imagem': ['.jpg', '.jpeg', '.png', '.tiff'],
        'comprovante': ['.pdf'],
    }

    # Estrutura padrao de pastas contabeis
    ESTRUTURA_PASTAS = [
        'Notas_Fiscais/Entrada',
        'Notas_Fiscais/Saida',
        'Extratos_Bancarios',
        'SPED/ECD',
        'SPED/EFD',
        'SPED/ECF',
        'DARF',
        'FGTS',
        'INSS',
        'Contratos',
        'Declaracoes',
        'Relatorios',
        'Holerites',
        'Outros',
    ]

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self._observer = None

    def criar_estrutura_pastas(self, raiz: str):
        """
        Cria estrutura padrao de pastas contabeis.

        Args:
            raiz: Pasta raiz onde a estrutura sera criada
        """
        for pasta in self.ESTRUTURA_PASTAS:
            caminho = os.path.join(raiz, pasta)
            os.makedirs(caminho, exist_ok=True)
            self.logger.info(f"Pasta criada/verificada: {caminho}")

    def iniciar_monitoramento(self, caminho: str, callback: Callable):
        """
        Monitora pasta em tempo real e chama callback para novos arquivos.

        Args:
            caminho: Pasta a monitorar
            callback: Funcao chamada quando arquivo novo e detectado
        """
        from watchdog.observers import Observer
        from watchdog.events import FileSystemEventHandler

        class Handler(FileSystemEventHandler):
            def __init__(self, cb):
                self._cb = cb

            def on_created(self, event):
                if not event.is_directory:
                    self._cb(event.src_path)

        self._observer = Observer()
        self._observer.schedule(Handler(callback), caminho, recursive=True)
        self._observer.start()
        self.logger.info(f"Monitoramento iniciado em: {caminho}")

    def parar_monitoramento(self):
        """Para o monitoramento de pastas"""
        if self._observer:
            self._observer.stop()
            self._observer.join()
            self.logger.info("Monitoramento encerrado")

    def classificar_arquivo(self, caminho_arquivo: str) -> str:
        """
        Classifica um arquivo por tipo e nome.

        Args:
            caminho_arquivo: Caminho do arquivo

        Returns:
            Categoria do arquivo
        """
        nome = os.path.basename(caminho_arquivo).lower()
        ext = os.path.splitext(nome)[1].lower()

        # Classifica por nome
        if any(x in nome for x in ['nfe', 'nfs', 'nota_fiscal', 'notafiscal']):
            return 'Notas_Fiscais'
        elif any(x in nome for x in ['extrato', 'ofx', 'bancario']):
            return 'Extratos_Bancarios'
        elif any(x in nome for x in ['darf', 'gps', 'gre', 'grf']):
            return 'DARF'
        elif any(x in nome for x in ['fgts', 'gfip', 'sefip']):
            return 'FGTS'
        elif any(x in nome for x in ['holerite', 'folha', 'salario']):
            return 'Holerites'
        elif any(x in nome for x in ['sped', 'ecd', 'efd', 'ecf']):
            return 'SPED'
        elif any(x in nome for x in ['contrato', 'distrato', 'aditivo']):
            return 'Contratos'
        elif any(x in nome for x in ['declaracao', 'certidao', 'comprovante']):
            return 'Declaracoes'
        elif any(x in nome for x in ['relatorio', 'balancete', 'dre', 'bp']):
            return 'Relatorios'
        else:
            return 'Outros'

    def obter_pasta_destino(self, categoria: str, raiz: str = 'dados/documentos') -> str:
        """
        Retorna o caminho de destino para uma categoria de documento.

        Args:
            categoria: Categoria do documento
            raiz: Pasta raiz base

        Returns:
            Caminho completo da pasta de destino
        """
        ano_mes = datetime.now().strftime('%Y/%m')
        destino = os.path.join(raiz, categoria, ano_mes)
        os.makedirs(destino, exist_ok=True)
        return destino

    def mover(self, origem: str, destino_dir: str) -> Optional[str]:
        """
        Move arquivo para diretorio destino.
        Trata conflitos de nome adicionando timestamp.

        Args:
            origem: Caminho de origem do arquivo
            destino_dir: Diretorio de destino

        Returns:
            Caminho final do arquivo ou None em caso de erro
        """
        try:
            os.makedirs(destino_dir, exist_ok=True)
            nome = os.path.basename(origem)
            destino = os.path.join(destino_dir, nome)

            # Evita sobrescrever arquivo existente
            if os.path.exists(destino):
                base, ext = os.path.splitext(nome)
                ts = datetime.now().strftime('%Y%m%d_%H%M%S')
                destino = os.path.join(destino_dir, f"{base}_{ts}{ext}")

            shutil.move(origem, destino)
            self.logger.info(f"Arquivo movido: {origem} -> {destino}")
            return destino
        except Exception as e:
            self.logger.error(f"Erro ao mover {origem}: {e}")
            return None

    def copiar(self, origem: str, destino_dir: str) -> Optional[str]:
        """Copia arquivo para diretorio destino"""
        try:
            os.makedirs(destino_dir, exist_ok=True)
            nome = os.path.basename(origem)
            destino = os.path.join(destino_dir, nome)
            shutil.copy2(origem, destino)
            return destino
        except Exception as e:
            self.logger.error(f"Erro ao copiar {origem}: {e}")
            return None

    def listar_arquivos(self, pasta: str, extensoes: Optional[list] = None) -> list:
        """
        Lista todos os arquivos em uma pasta.

        Args:
            pasta: Caminho da pasta
            extensoes: Lista de extensoes para filtrar (ex: ['.pdf', '.xlsx'])

        Returns:
            Lista de caminhos de arquivos
        """
        arquivos = []
        for raiz, dirs, files in os.walk(pasta):
            for arquivo in files:
                if extensoes:
                    ext = os.path.splitext(arquivo)[1].lower()
                    if ext not in extensoes:
                        continue
                arquivos.append(os.path.join(raiz, arquivo))
        return arquivos

    def organizar_pasta(self, pasta: str):
        """
        Organiza todos os arquivos de uma pasta automaticamente.
        Classifica e move cada arquivo para subpasta correta.

        Args:
            pasta: Pasta a organizar
        """
        arquivos = self.listar_arquivos(pasta)
        self.logger.info(f"Organizando {len(arquivos)} arquivos em {pasta}")

        for arquivo in arquivos:
            categoria = self.classificar_arquivo(arquivo)
            destino = self.obter_pasta_destino(categoria, pasta)

            # Nao mover se ja esta na pasta correta
            if os.path.dirname(arquivo) != destino:
                self.mover(arquivo, destino)

        self.logger.info("Organizacao concluida")

    def gerar_relatorio_pasta(self, pasta: str) -> Dict:
        """
        Gera relatorio de conteudo de uma pasta.

        Args:
            pasta: Pasta a analisar

        Returns:
            Dicionario com estatisticas da pasta
        """
        arquivos = self.listar_arquivos(pasta)
        por_categoria = {}
        tamanho_total = 0

        for arquivo in arquivos:
            categoria = self.classificar_arquivo(arquivo)
            tamanho = os.path.getsize(arquivo)
            tamanho_total += tamanho

            if categoria not in por_categoria:
                por_categoria[categoria] = {'quantidade': 0, 'tamanho_bytes': 0}
            por_categoria[categoria]['quantidade'] += 1
            por_categoria[categoria]['tamanho_bytes'] += tamanho

        return {
            'pasta': pasta,
            'total_arquivos': len(arquivos),
            'tamanho_total_mb': round(tamanho_total / (1024*1024), 2),
            'por_categoria': por_categoria,
            'data_analise': datetime.now().isoformat()
        }

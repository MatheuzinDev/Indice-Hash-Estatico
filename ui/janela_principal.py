from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QLabel, QMainWindow, QVBoxLayout, QWidget

from core.armazenamento import Tabela
from core.erros import ErroIndice
from core.hashing import IndiceHashEstatico
from core.metricas import EstatisticasIndice
from ui.componentes import VisualizadorPaginas
from ui.paineis import PainelConfiguracao, PainelMetricas

COR_ERRO = "#b00020"


class JanelaPrincipal(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Índice Hash Estático")
        self.resize(780, 620)

        self.palavras: list[str] = []
        self.tamanho_pagina: int | None = None
        self.tabela: Tabela | None = None
        self.indice: IndiceHashEstatico | None = None

        self.painel_config = PainelConfiguracao()
        self.painel_config.arquivo_carregado.connect(self._ao_carregar_arquivo)
        self.painel_config.falha_carregamento.connect(self._ao_falhar_carregamento)
        self.painel_config.tamanho_pagina_definido.connect(self._ao_definir_tamanho_pagina)
        self.painel_config.tamanho_pagina_invalido.connect(self._ao_invalidar_tamanho_pagina)
        self.painel_config.indice_solicitado.connect(self._ao_construir_indice)

        self.tamanho_pagina = self.painel_config.tamanho_pagina()

        self.painel_metricas = PainelMetricas()
        self._visualizador = VisualizadorPaginas()
        self._status = QLabel("Selecione um arquivo de palavras para começar.")
        self._status.setWordWrap(True)

        central = QWidget()
        layout = QVBoxLayout(central)
        layout.addWidget(self.painel_config)
        layout.addWidget(self.painel_metricas)
        layout.addWidget(self._visualizador, stretch=1)
        layout.addWidget(self._status)
        self.setCentralWidget(central)

    def _ao_carregar_arquivo(self, palavras: list[str]) -> None:
        self.palavras = palavras
        self._mostrar_status("Arquivo carregado.")
        self._atualizar_paginacao()

    def _ao_falhar_carregamento(self, mensagem: str) -> None:
        self.palavras = []
        self._mostrar_erro(mensagem)
        self._atualizar_paginacao()

    def _ao_definir_tamanho_pagina(self, tamanho: int) -> None:
        self.tamanho_pagina = tamanho
        self._mostrar_status(f"Tamanho da página: {tamanho} registros.")
        self._atualizar_paginacao()

    def _ao_invalidar_tamanho_pagina(self, mensagem: str) -> None:
        self.tamanho_pagina = None
        self._mostrar_erro(mensagem)
        self._atualizar_paginacao()

    def _ao_construir_indice(self) -> None:
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        try:
            self.indice = IndiceHashEstatico(self.tabela)
        except ErroIndice as erro:
            self._invalidar_indice()
            self._mostrar_erro(str(erro))
            return
        finally:
            QApplication.restoreOverrideCursor()

        self.painel_metricas.definir_indice(EstatisticasIndice(self.indice))
        self._mostrar_status("Índice construído.")

    def _atualizar_paginacao(self) -> None:
        self._invalidar_indice()

        if not self.palavras or self.tamanho_pagina is None:
            self.tabela = None
            self.painel_metricas.definir_carga(len(self.palavras), None)
            self._visualizador.limpar()
            self.painel_config.habilitar_construcao(False)
            return

        self.tabela = Tabela(self.palavras, self.tamanho_pagina)
        self.painel_metricas.definir_carga(len(self.palavras), self.tabela.qtd_paginas)
        self._visualizador.mostrar(self.tabela)
        self.painel_config.habilitar_construcao(True)

    def _invalidar_indice(self) -> None:
        self.indice = None
        self.painel_metricas.limpar_indice()

    def _mostrar_status(self, mensagem: str) -> None:
        self._status.setText(mensagem)
        self._status.setStyleSheet("")

    def _mostrar_erro(self, mensagem: str) -> None:
        self._status.setText(mensagem)
        self._status.setStyleSheet(f"color: {COR_ERRO};")

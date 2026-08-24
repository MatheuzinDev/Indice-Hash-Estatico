from PySide6.QtWidgets import QLabel, QMainWindow, QVBoxLayout, QWidget

from core.armazenamento import Tabela
from ui.componentes import VisualizadorPaginas
from ui.paineis import PainelConfiguracao

COR_ERRO = "#b00020"


class JanelaPrincipal(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Índice Hash Estático")
        self.resize(760, 420)

        self.palavras: list[str] = []
        self.tamanho_pagina: int | None = None
        self.tabela: Tabela | None = None

        self.painel_config = PainelConfiguracao()
        self.painel_config.arquivo_carregado.connect(self._ao_carregar_arquivo)
        self.painel_config.falha_carregamento.connect(self._ao_falhar_carregamento)
        self.painel_config.tamanho_pagina_definido.connect(self._ao_definir_tamanho_pagina)
        self.painel_config.tamanho_pagina_invalido.connect(self._ao_invalidar_tamanho_pagina)

        self.tamanho_pagina = self.painel_config.tamanho_pagina()

        self._total = QLabel("Palavras carregadas: —")
        self._paginas = QLabel("Páginas: —")
        self._visualizador = VisualizadorPaginas()
        self._status = QLabel("Selecione um arquivo de palavras para começar.")
        self._status.setWordWrap(True)

        central = QWidget()
        layout = QVBoxLayout(central)
        layout.addWidget(self.painel_config)
        layout.addWidget(self._total)
        layout.addWidget(self._paginas)
        layout.addWidget(self._visualizador, stretch=1)
        layout.addWidget(self._status)
        self.setCentralWidget(central)

    def _ao_carregar_arquivo(self, palavras: list[str]) -> None:
        self.palavras = palavras
        total = f"{len(palavras):,}".replace(",", ".")
        self._total.setText(f"Palavras carregadas: {total}")
        self._status.setText("Arquivo carregado.")
        self._status.setStyleSheet("")
        self._atualizar_paginacao()

    def _ao_falhar_carregamento(self, mensagem: str) -> None:
        self.palavras = []
        self._total.setText("Palavras carregadas: —")
        self._status.setText(mensagem)
        self._status.setStyleSheet(f"color: {COR_ERRO};")
        self._atualizar_paginacao()

    def _ao_definir_tamanho_pagina(self, tamanho: int) -> None:
        self.tamanho_pagina = tamanho
        self._status.setText(f"Tamanho da página: {tamanho} registros.")
        self._status.setStyleSheet("")
        self._atualizar_paginacao()

    def _ao_invalidar_tamanho_pagina(self, mensagem: str) -> None:
        self.tamanho_pagina = None
        self._status.setText(mensagem)
        self._status.setStyleSheet(f"color: {COR_ERRO};")
        self._atualizar_paginacao()

    def _atualizar_paginacao(self) -> None:
        if not self.palavras or self.tamanho_pagina is None:
            self.tabela = None
            self._paginas.setText("Páginas: —")
            self._visualizador.limpar()
            return

        self.tabela = Tabela(self.palavras, self.tamanho_pagina)
        qtd = f"{self.tabela.qtd_paginas:,}".replace(",", ".")
        self._paginas.setText(f"Páginas: {qtd}")
        self._visualizador.mostrar(self.tabela)

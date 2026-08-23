from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
)

from core.armazenamento import carregar_palavras
from core.erros import ErroCarregamento


class PainelConfiguracao(QGroupBox):

    arquivo_carregado = Signal(list)
    falha_carregamento = Signal(str)

    def __init__(self, parent=None):
        super().__init__("Arquivo de dados", parent)

        self._botao_arquivo = QPushButton("Arquivo…")
        self._botao_arquivo.clicked.connect(self._escolher_arquivo)

        self._campo_caminho = QLineEdit()
        self._campo_caminho.setReadOnly(True)
        self._campo_caminho.setPlaceholderText("Nenhum arquivo selecionado")

        layout = QHBoxLayout(self)
        layout.addWidget(self._botao_arquivo)
        layout.addWidget(self._campo_caminho, stretch=1)

    def _escolher_arquivo(self) -> None:
        caminho, _ = QFileDialog.getOpenFileName(
            self,
            "Selecionar arquivo de palavras",
            "",
            "Arquivos de texto (*.txt);;Todos os arquivos (*)",
        )
        if caminho:
            self.carregar(caminho)

    def carregar(self, caminho: str) -> None:
        try:
            palavras = carregar_palavras(caminho)
        except ErroCarregamento as erro:
            self._campo_caminho.clear()
            self.falha_carregamento.emit(str(erro))
            return

        self._campo_caminho.setText(caminho)
        self.arquivo_carregado.emit(palavras)

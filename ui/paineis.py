from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
)

from core.armazenamento import carregar_palavras, validar_tamanho_pagina
from core.erros import ErroCarregamento, ErroTamanhoPagina

TAMANHO_PAGINA_PADRAO = "100"


class PainelConfiguracao(QGroupBox):

    arquivo_carregado = Signal(list)
    falha_carregamento = Signal(str)
    tamanho_pagina_definido = Signal(int)
    tamanho_pagina_invalido = Signal(str)

    def __init__(self, parent=None):
        super().__init__("Configuração", parent)

        self._botao_arquivo = QPushButton("Arquivo…")
        self._botao_arquivo.clicked.connect(self._escolher_arquivo)

        self._campo_caminho = QLineEdit()
        self._campo_caminho.setReadOnly(True)
        self._campo_caminho.setPlaceholderText("Nenhum arquivo selecionado")

        linha_arquivo = QHBoxLayout()
        linha_arquivo.addWidget(self._botao_arquivo)
        linha_arquivo.addWidget(self._campo_caminho, stretch=1)

        self._campo_tamanho = QLineEdit(TAMANHO_PAGINA_PADRAO)
        self._campo_tamanho.setMaximumWidth(90)
        self._campo_tamanho.textEdited.connect(self._ao_editar_tamanho)

        linha_tamanho = QHBoxLayout()
        linha_tamanho.addWidget(QLabel("Tamanho da página (registros):"))
        linha_tamanho.addWidget(self._campo_tamanho)
        linha_tamanho.addStretch()

        layout = QVBoxLayout(self)
        layout.addLayout(linha_arquivo)
        layout.addLayout(linha_tamanho)

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

    def _ao_editar_tamanho(self, texto: str) -> None:
        try:
            tamanho = validar_tamanho_pagina(texto)
        except ErroTamanhoPagina as erro:
            self.tamanho_pagina_invalido.emit(str(erro))
            return

        self.tamanho_pagina_definido.emit(tamanho)

    def tamanho_pagina(self) -> int:
        return validar_tamanho_pagina(self._campo_tamanho.text())

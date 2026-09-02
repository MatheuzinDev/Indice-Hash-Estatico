from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
)

from core.armazenamento import carregar_palavras, validar_tamanho_pagina
from core.erros import ErroCarregamento, ErroTamanhoPagina
from core.metricas import EstatisticasIndice

TAMANHO_PAGINA_PADRAO = "100"
VAZIO = "—"


def _milhar(numero: int) -> str:
    return f"{numero:,}".replace(",", ".")


def _percentual(valor: float) -> str:
    return f"{valor:.1f}".replace(".", ",") + "%"


def _segundos(valor: float) -> str:
    return f"{valor:.2f}".replace(".", ",") + " s"


class PainelConfiguracao(QGroupBox):

    arquivo_carregado = Signal(list)
    falha_carregamento = Signal(str)
    tamanho_pagina_definido = Signal(int)
    tamanho_pagina_invalido = Signal(str)
    indice_solicitado = Signal()

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

        self._botao_indice = QPushButton("Construir índice")
        self._botao_indice.setEnabled(False)
        self._botao_indice.clicked.connect(self._ao_clicar_construir)

        linha_indice = QHBoxLayout()
        linha_indice.addWidget(self._botao_indice)
        linha_indice.addStretch()

        layout = QVBoxLayout(self)
        layout.addLayout(linha_arquivo)
        layout.addLayout(linha_tamanho)
        layout.addLayout(linha_indice)

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

    def _ao_clicar_construir(self) -> None:
        self.indice_solicitado.emit()

    def tamanho_pagina(self) -> int:
        return validar_tamanho_pagina(self._campo_tamanho.text())

    def habilitar_construcao(self, habilitado: bool) -> None:
        self._botao_indice.setEnabled(habilitado)


class PainelMetricas(QGroupBox):

    def __init__(self, parent=None):
        super().__init__("Métricas", parent)

        self._registros = QLabel(VAZIO)
        self._paginas = QLabel(VAZIO)
        self._buckets = QLabel(VAZIO)
        self._capacidade = QLabel(VAZIO)
        self._taxa_colisoes = QLabel(VAZIO)
        self._taxa_overflow = QLabel(VAZIO)
        self._tempo = QLabel(VAZIO)

        layout = QFormLayout(self)
        layout.addRow("Registros (NR):", self._registros)
        layout.addRow("Páginas:", self._paginas)
        layout.addRow("Buckets (NB):", self._buckets)
        layout.addRow("Capacidade do bucket (FR):", self._capacidade)
        layout.addRow("Taxa de colisões:", self._taxa_colisoes)
        layout.addRow("Taxa de overflow:", self._taxa_overflow)
        layout.addRow("Tempo de construção:", self._tempo)

    def definir_carga(self, nr: int, qtd_paginas: int | None) -> None:
        self._registros.setText(_milhar(nr) if nr else VAZIO)
        self._paginas.setText(_milhar(qtd_paginas) if qtd_paginas else VAZIO)

    def definir_indice(self, estatisticas: EstatisticasIndice) -> None:
        self._buckets.setText(_milhar(estatisticas.nb))
        self._capacidade.setText(str(estatisticas.fr))
        self._taxa_colisoes.setText(_percentual(estatisticas.taxa_colisoes))
        self._taxa_overflow.setText(_percentual(estatisticas.taxa_overflow))
        self._tempo.setText(_segundos(estatisticas.tempo_construcao))

    def limpar_indice(self) -> None:
        for rotulo in (
            self._buckets,
            self._capacidade,
            self._taxa_colisoes,
            self._taxa_overflow,
            self._tempo,
        ):
            rotulo.setText(VAZIO)

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QFileDialog,
    QFormLayout,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
)

from core.armazenamento import carregar_palavras, validar_tamanho_pagina
from core.busca import ResultadoBuscaIndexada, ResultadoTableScan
from core.erros import ErroCarregamento, ErroTamanhoPagina
from core.metricas import Comparativo, EstatisticasIndice

TAMANHO_PAGINA_PADRAO = "100"
VAZIO = "—"


def _milhar(numero: int) -> str:
    return f"{numero:,}".replace(",", ".")


def _percentual(valor: float, casas: int = 1) -> str:
    return f"{valor:.{casas}f}".replace(".", ",") + "%"


def _segundos(valor: float) -> str:
    return f"{valor:.2f}".replace(".", ",") + " s"


def _milissegundos(valor: float) -> str:
    return f"{valor * 1000:.3f}".replace(".", ",") + " ms"


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


class PainelBusca(QGroupBox):

    busca_indexada_solicitada = Signal(str)
    table_scan_solicitado = Signal(str)
    chave_alterada = Signal()

    def __init__(self, parent=None):
        super().__init__("Busca", parent)

        self._tem_indice = False
        self._tem_tabela = False

        self._campo_chave = QLineEdit()
        self._campo_chave.setPlaceholderText("Palavra a procurar")
        self._campo_chave.textEdited.connect(self._ao_editar_chave)

        linha_chave = QHBoxLayout()
        linha_chave.addWidget(QLabel("Chave:"))
        linha_chave.addWidget(self._campo_chave, stretch=1)

        self._botao_indice = QPushButton("Buscar por índice")
        self._botao_indice.setEnabled(False)
        self._botao_indice.clicked.connect(self._ao_clicar_indice)

        self._botao_scan = QPushButton("Table scan")
        self._botao_scan.setEnabled(False)
        self._botao_scan.clicked.connect(self._ao_clicar_scan)

        linha_botoes = QHBoxLayout()
        linha_botoes.addWidget(self._botao_indice)
        linha_botoes.addWidget(self._botao_scan)
        linha_botoes.addStretch()

        layout = QVBoxLayout(self)
        layout.addLayout(linha_chave)
        layout.addLayout(linha_botoes)

    def chave(self) -> str:
        return self._campo_chave.text().strip()

    def definir_disponibilidade(self, tem_indice: bool, tem_tabela: bool) -> None:
        self._tem_indice = tem_indice
        self._tem_tabela = tem_tabela
        self._atualizar_botoes()

    def _ao_editar_chave(self, texto: str) -> None:
        self._atualizar_botoes()
        self.chave_alterada.emit()

    def _ao_clicar_indice(self) -> None:
        self.busca_indexada_solicitada.emit(self.chave())

    def _ao_clicar_scan(self) -> None:
        self.table_scan_solicitado.emit(self.chave())

    def _atualizar_botoes(self) -> None:
        tem_chave = bool(self.chave())
        self._botao_indice.setEnabled(tem_chave and self._tem_indice)
        self._botao_scan.setEnabled(tem_chave and self._tem_tabela)


class PainelComparativo(QGroupBox):

    def __init__(self, parent=None):
        super().__init__("Comparativo", parent)

        self._indice = self._criar_linha()
        self._scan = self._criar_linha()
        self._ganho = self._criar_linha()

        layout = QGridLayout(self)
        for coluna, titulo in enumerate(("", "Página", "Custo (páginas)", "Tempo")):
            layout.addWidget(QLabel(f"<b>{titulo}</b>"), 0, coluna)

        linhas = (("Busca indexada", self._indice), ("Table scan", self._scan), ("Ganho", self._ganho))
        for numero, (nome, rotulos) in enumerate(linhas, start=1):
            layout.addWidget(QLabel(nome), numero, 0)
            for coluna, rotulo in enumerate(rotulos, start=1):
                layout.addWidget(rotulo, numero, coluna)

    def definir_indice(self, resultado: ResultadoBuscaIndexada) -> None:
        self._preencher(self._indice, resultado)

    def definir_scan(self, resultado: ResultadoTableScan) -> None:
        self._preencher(self._scan, resultado)

    def definir_ganho(self, comparativo: Comparativo) -> None:
        self._ganho[0].setText(VAZIO)
        self._ganho[1].setText(_percentual(comparativo.diferenca_custo_percentual, 2) + " menos")
        self._ganho[2].setText(
            f"{_milissegundos(comparativo.diferenca_tempo_segundos)} ({comparativo.fator_aceleracao:.0f}×)"
        )

    def limpar(self) -> None:
        for linha in (self._indice, self._scan, self._ganho):
            for rotulo in linha:
                rotulo.setText(VAZIO)

    def _criar_linha(self) -> tuple[QLabel, QLabel, QLabel]:
        return QLabel(VAZIO), QLabel(VAZIO), QLabel(VAZIO)

    def _preencher(self, linha: tuple[QLabel, QLabel, QLabel], resultado) -> None:
        linha[0].setText(_milhar(resultado.pagina) if resultado.encontrada else "não encontrada")
        linha[1].setText(_milhar(resultado.custo_paginas))
        linha[2].setText(_milissegundos(resultado.tempo_segundos))

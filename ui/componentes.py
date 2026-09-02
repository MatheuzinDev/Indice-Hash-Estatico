from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QAbstractItemView,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QPushButton,
    QScrollArea,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)

from core.armazenamento import Tabela
from core.hashing import IndiceHashEstatico

REGISTROS_EXIBIDOS = 5
LARGURA_CAIXA_PAGINA = 220
ALTURA_DETALHE = 170
FAIXA = 500
ENTRADAS_OVERFLOW_EXIBIDAS = 10
COR_DESTAQUE = "#1565c0"
FUNDO_DESTAQUE = "#fff3c4"
ESTILO_DESTAQUE = f"QGroupBox {{ border: 2px solid {COR_DESTAQUE}; border-radius: 4px; }}"
AVISO_SEM_SCAN = "Execute um table scan para ver os registros lidos."
AVISO_SEM_INDICE = "Construa o índice para ver os buckets."
AVISO_SEM_SELECAO = "Clique num bucket para ver o conteúdo."


class VisualizadorPaginas(QGroupBox):

    def __init__(self, parent=None):
        super().__init__("Páginas", parent)

        self._caixa_primeira, self._titulo_primeira, self._registros_primeira = self._montar_caixa()
        self._caixa_destacada, self._titulo_destacada, self._registros_destacada = self._montar_caixa()
        self._caixa_ultima, self._titulo_ultima, self._registros_ultima = self._montar_caixa()

        self._aviso = QLabel("Carregue um arquivo para ver as páginas.")

        layout = QHBoxLayout(self)
        layout.addWidget(self._aviso)
        layout.addWidget(self._caixa_primeira)
        layout.addWidget(self._caixa_destacada)
        layout.addWidget(self._caixa_ultima)
        layout.addStretch()

        self.limpar()

    def _montar_caixa(self) -> tuple[QGroupBox, QLabel, QLabel]:
        titulo = QLabel()
        registros = QLabel()
        registros.setAlignment(Qt.AlignmentFlag.AlignTop)
        registros.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)

        caixa = QGroupBox()
        caixa.setMaximumWidth(LARGURA_CAIXA_PAGINA)
        layout = QVBoxLayout(caixa)
        layout.addWidget(titulo)
        layout.addWidget(registros)
        layout.addStretch()

        return caixa, titulo, registros

    def mostrar(self, tabela: Tabela, pagina_destacada: int | None = None) -> None:
        ultima = tabela.qtd_paginas - 1

        self._preencher(self._titulo_primeira, self._registros_primeira, tabela, 0)
        self._preencher(self._titulo_ultima, self._registros_ultima, tabela, ultima)

        self._aviso.hide()
        self._caixa_primeira.show()
        self._caixa_ultima.setVisible(ultima > 0)

        self._destacar(self._caixa_primeira, pagina_destacada == 0)
        self._destacar(self._caixa_ultima, pagina_destacada == ultima and ultima > 0)

        do_meio = pagina_destacada is not None and 0 < pagina_destacada < ultima
        if do_meio:
            self._preencher(
                self._titulo_destacada, self._registros_destacada, tabela, pagina_destacada
            )
        self._caixa_destacada.setVisible(do_meio)
        self._destacar(self._caixa_destacada, do_meio)

    def _preencher(self, titulo: QLabel, registros: QLabel, tabela: Tabela, num_pagina: int) -> None:
        pagina = tabela.ler_pagina(num_pagina)
        exibidos = pagina[:REGISTROS_EXIBIDOS]

        titulo.setText(f"<b>Página {num_pagina}</b> — {len(pagina)} registros")
        registros.setText("\n".join(exibidos))

    def _destacar(self, caixa: QGroupBox, ativo: bool) -> None:
        caixa.setStyleSheet(ESTILO_DESTAQUE if ativo else "")

    def limpar(self) -> None:
        self._caixa_primeira.hide()
        self._caixa_destacada.hide()
        self._caixa_ultima.hide()
        self._aviso.show()


class GradeBuckets(QGroupBox):

    def __init__(self, parent=None):
        super().__init__("Buckets", parent)

        self._indice: IndiceHashEstatico | None = None
        self._primeiro_da_faixa = 0
        self._destacado: int | None = None

        self._tabela = QTableWidget(0, 3)
        self._tabela.setHorizontalHeaderLabels(("Bucket", "Ocupação", "Overflow"))
        self._tabela.verticalHeader().setVisible(False)
        self._tabela.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self._tabela.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self._tabela.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._tabela.setMaximumWidth(300)
        self._tabela.itemSelectionChanged.connect(self._ao_selecionar)

        self._anterior = QPushButton("◀")
        self._anterior.setMaximumWidth(36)
        self._anterior.clicked.connect(self._ao_anterior)

        self._proximo = QPushButton("▶")
        self._proximo.setMaximumWidth(36)
        self._proximo.clicked.connect(self._ao_proximo)

        self._faixa = QLabel(AVISO_SEM_INDICE)

        linha_navegacao = QHBoxLayout()
        linha_navegacao.addWidget(self._anterior)
        linha_navegacao.addWidget(self._proximo)
        linha_navegacao.addWidget(self._faixa, stretch=1)

        self._detalhe = QLabel(AVISO_SEM_INDICE)
        self._detalhe.setAlignment(Qt.AlignmentFlag.AlignTop)
        self._detalhe.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)

        rolagem = QScrollArea()
        rolagem.setWidget(self._detalhe)
        rolagem.setWidgetResizable(True)
        rolagem.setMinimumHeight(ALTURA_DETALHE)

        conteudo = QHBoxLayout()
        conteudo.addWidget(self._tabela)
        conteudo.addWidget(rolagem, stretch=1)

        layout = QVBoxLayout(self)
        layout.addLayout(linha_navegacao)
        layout.addLayout(conteudo, stretch=1)

        self.limpar()

    def mostrar(self, indice: IndiceHashEstatico) -> None:
        self._indice = indice
        self._destacado = None
        self._ir_para_faixa(0)
        self._detalhe.setText(AVISO_SEM_SELECAO)

    def destacar(self, endereco_bucket: int) -> None:
        if self._indice is None:
            return

        self._destacado = endereco_bucket
        self._ir_para_faixa(endereco_bucket // FAIXA * FAIXA)

        linha = endereco_bucket - self._primeiro_da_faixa
        self._tabela.selectRow(linha)
        self._tabela.scrollToItem(self._tabela.item(linha, 0))

    def limpar_destaque(self) -> None:
        if self._indice is None:
            return

        self._destacado = None
        self._tabela.clearSelection()
        self._ir_para_faixa(self._primeiro_da_faixa)
        self._detalhe.setText(AVISO_SEM_SELECAO)

    def limpar(self) -> None:
        self._indice = None
        self._destacado = None
        self._tabela.setRowCount(0)
        self._faixa.setText(AVISO_SEM_INDICE)
        self._detalhe.setText(AVISO_SEM_INDICE)
        self._anterior.setEnabled(False)
        self._proximo.setEnabled(False)

    def _ir_para_faixa(self, primeiro: int) -> None:
        self._primeiro_da_faixa = primeiro
        ultimo = min(primeiro + FAIXA, self._indice.NB)

        self._tabela.setRowCount(ultimo - primeiro)
        for linha, endereco in enumerate(range(primeiro, ultimo)):
            self._preencher_linha(linha, endereco)

        self._faixa.setText(
            f"Buckets {primeiro} a {ultimo - 1} de {self._indice.NB}"
        )
        self._anterior.setEnabled(primeiro > 0)
        self._proximo.setEnabled(ultimo < self._indice.NB)

    def _ao_anterior(self) -> None:
        self._ir_para_faixa(max(self._primeiro_da_faixa - FAIXA, 0))

    def _ao_proximo(self) -> None:
        self._ir_para_faixa(self._primeiro_da_faixa + FAIXA)

    def _preencher_linha(self, linha: int, endereco: int) -> None:
        ocupadas = self._indice.proxima_posicao_livre[endereco]
        encadeadas = len(self._indice.overflow[endereco])
        textos = (str(endereco), f"{ocupadas}/{self._indice.FR}", str(encadeadas))

        for coluna, texto in enumerate(textos):
            item = QTableWidgetItem(texto)
            if endereco == self._destacado:
                item.setBackground(QColor(FUNDO_DESTAQUE))
            self._tabela.setItem(linha, coluna, item)

    def _ao_selecionar(self) -> None:
        linhas = self._tabela.selectionModel().selectedRows()
        if not linhas or self._indice is None:
            return

        self._detalhe.setText(self._texto_detalhe(self._primeiro_da_faixa + linhas[0].row()))

    def _texto_detalhe(self, endereco: int) -> str:
        ocupadas = self._indice.proxima_posicao_livre[endereco]
        entradas = self._indice.bucket[endereco][:ocupadas]
        cadeia = self._indice.overflow[endereco]

        linhas = [
            f"<b>Bucket {endereco}</b>",
            f"{ocupadas}/{self._indice.FR} ocupados · {len(cadeia)} em overflow",
            "",
        ]
        linhas.extend(f"{chave} → página {num_pagina}" for chave, num_pagina in entradas)

        if cadeia:
            linhas.append("")
            linhas.append("<b>Overflow</b>")
            linhas.extend(
                f"{chave} → página {num_pagina}"
                for chave, num_pagina in cadeia[:ENTRADAS_OVERFLOW_EXIBIDAS]
            )
            restantes = len(cadeia) - ENTRADAS_OVERFLOW_EXIBIDAS
            if restantes > 0:
                linhas.append(f"… e mais {restantes}")

        return "<br>".join(linhas)


class RegistrosLidos(QGroupBox):

    def __init__(self, parent=None):
        super().__init__("Registros lidos", parent)

        self._resumo = QLabel(AVISO_SEM_SCAN)
        self._resumo.setWordWrap(True)
        self._lista = QListWidget()

        layout = QVBoxLayout(self)
        layout.addWidget(self._resumo)
        layout.addWidget(self._lista, stretch=1)

    def mostrar(self, registros: list[str], total: int) -> None:
        self._lista.clear()
        self._lista.addItems(registros)

        total_formatado = f"{total:,}".replace(",", ".")
        if len(registros) < total:
            self._resumo.setText(f"Últimos {len(registros)} dos {total_formatado} registros lidos")
        else:
            self._resumo.setText(f"{total_formatado} registros lidos")

    def limpar(self) -> None:
        self._lista.clear()
        self._resumo.setText(AVISO_SEM_SCAN)

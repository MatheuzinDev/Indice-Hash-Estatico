from PySide6.QtCore import Qt
from PySide6.QtWidgets import QGroupBox, QHBoxLayout, QLabel, QListWidget, QVBoxLayout

from core.armazenamento import Tabela

REGISTROS_EXIBIDOS = 5
LARGURA_CAIXA_PAGINA = 220
COR_DESTAQUE = "#1565c0"
ESTILO_DESTAQUE = f"QGroupBox {{ border: 2px solid {COR_DESTAQUE}; border-radius: 4px; }}"
AVISO_SEM_SCAN = "Execute um table scan para ver os registros lidos."


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

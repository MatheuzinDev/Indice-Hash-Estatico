from PySide6.QtCore import Qt
from PySide6.QtWidgets import QGroupBox, QHBoxLayout, QLabel, QListWidget, QVBoxLayout

from core.armazenamento import Tabela

REGISTROS_EXIBIDOS = 5


class VisualizadorPaginas(QGroupBox):

    def __init__(self, parent=None):
        super().__init__("Páginas", parent)

        self._caixa_primeira, self._titulo_primeira, self._registros_primeira = self._montar_caixa()
        self._caixa_ultima, self._titulo_ultima, self._registros_ultima = self._montar_caixa()

        self._aviso = QLabel("Carregue um arquivo para ver as páginas.")

        layout = QHBoxLayout(self)
        layout.addWidget(self._aviso)
        layout.addWidget(self._caixa_primeira)
        layout.addWidget(self._caixa_ultima)
        layout.addStretch()

        self.limpar()

    def _montar_caixa(self) -> tuple[QGroupBox, QLabel, QLabel]:
        titulo = QLabel()
        registros = QLabel()
        registros.setAlignment(Qt.AlignmentFlag.AlignTop)
        registros.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)

        caixa = QGroupBox()
        layout = QVBoxLayout(caixa)
        layout.addWidget(titulo)
        layout.addWidget(registros)
        layout.addStretch()

        return caixa, titulo, registros

    def mostrar(self, tabela: Tabela) -> None:
        ultima = tabela.qtd_paginas - 1

        self._preencher(self._titulo_primeira, self._registros_primeira, tabela, 0)
        self._preencher(self._titulo_ultima, self._registros_ultima, tabela, ultima)

        self._aviso.hide()
        self._caixa_primeira.show()
        self._caixa_ultima.setVisible(ultima > 0)

    def _preencher(self, titulo: QLabel, registros: QLabel, tabela: Tabela, num_pagina: int) -> None:
        pagina = tabela.ler_pagina(num_pagina)
        exibidos = pagina[:REGISTROS_EXIBIDOS]

        titulo.setText(f"<b>Página {num_pagina}</b> — {len(pagina)} registros")
        registros.setText("\n".join(exibidos))

    def limpar(self) -> None:
        self._caixa_primeira.hide()
        self._caixa_ultima.hide()
        self._aviso.show()


AVISO_SEM_SCAN = "Execute um table scan para ver os registros lidos."


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

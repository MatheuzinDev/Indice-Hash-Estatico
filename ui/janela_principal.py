from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QVBoxLayout,
    QWidget,
)

from core.armazenamento import PaginasDaTabela, Tabela
from core.busca import (
    ResultadoBuscaIndexada,
    ResultadoTableScan,
    buscar_por_indice,
    table_scan,
)
from core.erros import ErroIndice
from core.hashing import IndiceHashEstatico
from core.metricas import EstatisticasIndice, comparar
from ui.componentes import GradeBuckets, RegistrosLidos, VisualizadorPaginas
from ui.paineis import PainelBusca, PainelComparativo, PainelConfiguracao, PainelMetricas

COR_ERRO = "#b00020"


class JanelaPrincipal(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Índice Hash Estático")
        self.resize(1200, 720)

        self.palavras: list[str] = []
        self.tamanho_pagina: int | None = None
        self.tabela: Tabela | None = None
        self.indice: IndiceHashEstatico | None = None
        self.resultado_indice: ResultadoBuscaIndexada | None = None
        self.resultado_scan: ResultadoTableScan | None = None

        self.painel_config = PainelConfiguracao()
        self.painel_config.arquivo_carregado.connect(self._ao_carregar_arquivo)
        self.painel_config.falha_carregamento.connect(self._ao_falhar_carregamento)
        self.painel_config.tamanho_pagina_definido.connect(self._ao_definir_tamanho_pagina)
        self.painel_config.tamanho_pagina_invalido.connect(self._ao_invalidar_tamanho_pagina)
        self.painel_config.indice_solicitado.connect(self._ao_construir_indice)

        self.tamanho_pagina = self.painel_config.tamanho_pagina()

        self.painel_busca = PainelBusca()
        self.painel_busca.busca_indexada_solicitada.connect(self._ao_buscar_por_indice)
        self.painel_busca.table_scan_solicitado.connect(self._ao_executar_table_scan)
        self.painel_busca.chave_alterada.connect(self._limpar_busca)

        self.painel_metricas = PainelMetricas()
        self.painel_comparativo = PainelComparativo()
        self._visualizador = VisualizadorPaginas()
        self._grade_buckets = GradeBuckets()
        self._registros_lidos = RegistrosLidos()
        self._status = QLabel("Selecione um arquivo de palavras para começar.")
        self._status.setWordWrap(True)

        coluna_esquerda = QVBoxLayout()
        coluna_esquerda.addWidget(self.painel_config)
        coluna_esquerda.addWidget(self.painel_metricas)
        coluna_esquerda.addStretch()

        coluna_direita = QVBoxLayout()
        coluna_direita.addWidget(self.painel_busca)
        coluna_direita.addWidget(self.painel_comparativo)
        coluna_direita.addWidget(self._registros_lidos, stretch=1)

        topo = QHBoxLayout()
        topo.addLayout(coluna_esquerda, stretch=1)
        topo.addLayout(coluna_direita, stretch=1)

        base = QHBoxLayout()
        base.addWidget(self._visualizador, stretch=1)
        base.addWidget(self._grade_buckets, stretch=1)

        central = QWidget()
        layout = QVBoxLayout(central)
        layout.addLayout(topo)
        layout.addLayout(base, stretch=1)
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
            self.painel_busca.definir_disponibilidade(False, True)
            self._mostrar_erro(str(erro))
            return
        finally:
            QApplication.restoreOverrideCursor()

        self.painel_metricas.definir_indice(EstatisticasIndice(self.indice))
        self._grade_buckets.mostrar(self.indice)
        self.painel_busca.definir_disponibilidade(True, True)
        self._mostrar_status("Índice construído.")

    def _ao_buscar_por_indice(self, chave: str) -> None:
        self.resultado_indice = buscar_por_indice(
            self.indice, PaginasDaTabela(self.tabela), chave
        )
        self.painel_comparativo.definir_indice(self.resultado_indice)
        self._grade_buckets.destacar(self.indice.funcao_hash(chave))
        self._visualizador.mostrar(self.tabela, self.resultado_indice.pagina)
        self._atualizar_ganho()

        if self.resultado_indice.encontrada:
            self._mostrar_status(
                f"'{chave}' encontrada na página {self.resultado_indice.pagina}, lendo 1 página."
            )
        else:
            self._mostrar_status(f"'{chave}' não encontrada pelo índice.")

    def _ao_executar_table_scan(self, chave: str) -> None:
        self.resultado_scan = table_scan(PaginasDaTabela(self.tabela), chave)
        self.painel_comparativo.definir_scan(self.resultado_scan)
        self._registros_lidos.mostrar(
            self.resultado_scan.registros_lidos, self.resultado_scan.total_registros_lidos
        )
        self._atualizar_ganho()

        paginas_lidas = self.resultado_scan.custo_paginas
        if self.resultado_scan.encontrada:
            self._mostrar_status(
                f"'{chave}' encontrada na página {self.resultado_scan.pagina}, "
                f"lendo {paginas_lidas} páginas."
            )
        else:
            self._mostrar_status(
                f"'{chave}' não encontrada após ler as {paginas_lidas} páginas."
            )

    def _atualizar_ganho(self) -> None:
        if self.resultado_indice is None or self.resultado_scan is None:
            return

        self.painel_comparativo.definir_ganho(
            comparar(self.resultado_indice, self.resultado_scan)
        )

    def _atualizar_paginacao(self) -> None:
        self._invalidar_indice()

        if not self.palavras or self.tamanho_pagina is None:
            self.tabela = None
            self.painel_metricas.definir_carga(len(self.palavras), None)
            self._visualizador.limpar()
            self.painel_config.habilitar_construcao(False)
            self.painel_busca.definir_disponibilidade(False, False)
            return

        self.tabela = Tabela(self.palavras, self.tamanho_pagina)
        self.painel_metricas.definir_carga(len(self.palavras), self.tabela.qtd_paginas)
        self._visualizador.mostrar(self.tabela)
        self.painel_config.habilitar_construcao(True)
        self.painel_busca.definir_disponibilidade(False, True)

    def _invalidar_indice(self) -> None:
        self.indice = None
        self.painel_metricas.limpar_indice()
        self._grade_buckets.limpar()
        self._limpar_busca()

    def _limpar_busca(self) -> None:
        self.resultado_indice = None
        self.resultado_scan = None
        self.painel_comparativo.limpar()
        self._registros_lidos.limpar()
        self._grade_buckets.limpar_destaque()

        if self.tabela is not None:
            self._visualizador.mostrar(self.tabela)

    def _mostrar_status(self, mensagem: str) -> None:
        self._status.setText(mensagem)
        self._status.setStyleSheet("")

    def _mostrar_erro(self, mensagem: str) -> None:
        self._status.setText(mensagem)
        self._status.setStyleSheet(f"color: {COR_ERRO};")

import sys

from PySide6.QtWidgets import QApplication

from ui.janela_principal import JanelaPrincipal


def main() -> int:
    aplicacao = QApplication(sys.argv)
    aplicacao.setApplicationName("Índice Hash Estático")

    janela = JanelaPrincipal()
    janela.show()

    return aplicacao.exec()


if __name__ == "__main__":
    sys.exit(main())

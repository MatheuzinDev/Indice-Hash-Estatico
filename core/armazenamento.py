import math
from pathlib import Path

from core.erros import (
    ArquivoIlegivel,
    ArquivoVazio,
    TamanhoPaginaInvalido,
    TamanhoPaginaNaoNumerico,
    TamanhoPaginaVazio,
)

def carregar_palavras(caminho: str | Path) -> list[str]:
    nome = Path(caminho).name
    palavras = []

    try:
        with Path(caminho).open(encoding="utf-8-sig") as arquivo:
            for linha in arquivo:
                palavra = linha.strip()
                if palavra:
                    palavras.append(palavra)
    except (OSError, UnicodeDecodeError):
        raise ArquivoIlegivel(nome)

    if not palavras:
        raise ArquivoVazio(nome)

    return palavras


def validar_tamanho_pagina(texto: str) -> int:
    texto = texto.strip()

    if not texto:
        raise TamanhoPaginaVazio()

    if not texto.lstrip("-").isdigit():
        raise TamanhoPaginaNaoNumerico(texto)

    tamanho = int(texto)
    if tamanho <= 0:
        raise TamanhoPaginaInvalido(tamanho)

    return tamanho


class Tabela:
    def __init__(self, palavras: list[str], tamanho_pagina: int):
        self.palavras = palavras
        self.tamanho_pagina = tamanho_pagina

    @property
    def qtd_paginas(self) -> int:
        return math.ceil(len(self.palavras) / self.tamanho_pagina)

    def ler_pagina(self, num_pagina: int) -> list[str]:
        inicio = num_pagina * self.tamanho_pagina
        return self.palavras[inicio : inicio + self.tamanho_pagina]


class PaginasDaTabela:
    def __init__(self, tabela: Tabela):
        self.tabela = tabela

    def __len__(self) -> int:
        return self.tabela.qtd_paginas

    def __getitem__(self, num_pagina: int) -> list[str]:
        return self.tabela.ler_pagina(num_pagina)

    def __iter__(self):
        for num_pagina in range(len(self)):
            yield self[num_pagina]

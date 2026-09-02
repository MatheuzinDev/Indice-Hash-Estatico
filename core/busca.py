from __future__ import annotations

import time
from collections import deque
from dataclasses import dataclass, field

from core.hashing import IndiceHashEstatico


@dataclass
class ResultadoBuscaIndexada:
    chave: str
    encontrada: bool
    pagina: int | None
    custo_paginas: int
    tempo_segundos: float


@dataclass
class ResultadoTableScan:
    chave: str
    encontrada: bool
    pagina: int | None
    custo_paginas: int
    tempo_segundos: float
    registros_lidos: list[str] = field(default_factory=list)
    total_registros_lidos: int = 0


def buscar_por_indice(indice: IndiceHashEstatico, paginas: list[list[str]], chave: str) -> ResultadoBuscaIndexada:
    inicio = time.perf_counter()
    entrada = indice.buscar(chave)

    if entrada is None:
        tempo = time.perf_counter() - inicio
        return ResultadoBuscaIndexada(chave, False, None, 0, tempo)

    _, pagina_id = entrada
    pagina = paginas[pagina_id]
    encontrada = chave in pagina
    tempo = time.perf_counter() - inicio

    return ResultadoBuscaIndexada(chave, encontrada, pagina_id if encontrada else None, 1, tempo)


def table_scan(paginas: list[list[str]], chave: str, tamanho_amostra: int = 200) -> ResultadoTableScan:
    inicio = time.perf_counter()
    amostra: deque[str] = deque(maxlen=tamanho_amostra)
    total_lidos = 0

    for pagina_id, pagina in enumerate(paginas):
        amostra.extend(pagina)
        total_lidos += len(pagina)
        if chave in pagina:
            tempo = time.perf_counter() - inicio
            return ResultadoTableScan(
                chave, True, pagina_id, pagina_id + 1, tempo, list(amostra), total_lidos
            )

    tempo = time.perf_counter() - inicio
    return ResultadoTableScan(
        chave, False, None, len(paginas), tempo, list(amostra), total_lidos
    )

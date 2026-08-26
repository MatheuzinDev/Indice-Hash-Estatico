"""HU09 — busca de uma chave usando o índice hash.
HU10 — table scan sequencial para comparação.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field

from core.hashing import IndexHashStatic


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


def buscar_por_indice(indice: IndexHashStatic, paginas: list[list[str]], chave: str) -> ResultadoBuscaIndexada:
    """RN19: aplica a função hash, localiza o bucket, recupera o endereço da
    página e carrega a página para localizar a tupla."""
    inicio = time.perf_counter() 
    entrada = indice.search(chave) 

    if entrada is None: 
        tempo = time.perf_counter() - inicio 
        return ResultadoBuscaIndexada(chave, False, None, 0, tempo) 

    _, pagina_id = entrada 
    pagina = paginas[pagina_id] 
    encontrada = chave in pagina 
    tempo = time.perf_counter() - inicio

    return ResultadoBuscaIndexada(chave, encontrada, pagina_id if encontrada else None, 1, tempo) 


def table_scan(paginas: list[list[str]], chave: str) -> ResultadoTableScan:
    """RN21: lê página por página, na ordem, até encontrar a chave."""
    inicio = time.perf_counter() 
    registros_lidos: list[str] = [] 

    for pagina_id, pagina in enumerate(paginas): 
        registros_lidos.extend(pagina) 
        if chave in pagina: 
            tempo = time.perf_counter() - inicio 
            return ResultadoTableScan(chave, True, pagina_id, pagina_id + 1, tempo, registros_lidos) 

    tempo = time.perf_counter() - inicio
    return ResultadoTableScan(chave, False, None, len(paginas), tempo, registros_lidos)

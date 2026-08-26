from core.busca import buscar_por_indice, table_scan


def comparar_busca(indice, paginas, chave):
    resultado_indice = buscar_por_indice(indice, paginas, chave)
    resultado_scan = table_scan(paginas, chave)

    return {
        "chave": chave,
        "indice": {
            "encontrado": resultado_indice.encontrada,
            "pagina": resultado_indice.pagina,
            "custo_paginas": resultado_indice.custo_paginas,
            "tempo_segundos": resultado_indice.tempo_segundos,
        },
        "table_scan": {
            "encontrado": resultado_scan.encontrada,
            "pagina": resultado_scan.pagina,
            "custo_paginas": resultado_scan.custo_paginas,
            "tempo_segundos": resultado_scan.tempo_segundos,
        },
        "diferenca_tempo_percentual": _diferenca_percentual(resultado_scan.tempo_segundos, resultado_indice.tempo_segundos),
        "diferenca_custo_percentual": _diferenca_percentual(resultado_scan.custo_paginas, resultado_indice.custo_paginas),
    }


def _diferenca_percentual(valor_scan, valor_indice):
    if valor_scan == 0:
        return 0.0
    return ((valor_scan - valor_indice) / valor_scan) * 100
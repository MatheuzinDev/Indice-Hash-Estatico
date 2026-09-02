from core.busca import ResultadoBuscaIndexada, ResultadoTableScan
from core.hashing import IndiceHashEstatico


class EstatisticasIndice:
    def __init__(self, indice: IndiceHashEstatico):
        self.nr = indice.NR
        self.nb = indice.NB
        self.fr = indice.FR
        self.colisoes = indice.total_colisoes
        self.buckets_com_overflow = len(indice.buckets_em_overflow)
        self.tempo_construcao = indice.tempo_construcao

    @property
    def taxa_colisoes(self) -> float:
        return self.colisoes / self.nr * 100 if self.nr else 0.0

    @property
    def taxa_overflow(self) -> float:
        return self.buckets_com_overflow / self.nb * 100 if self.nb else 0.0


class Comparativo:
    def __init__(self, resultado_indice: ResultadoBuscaIndexada, resultado_scan: ResultadoTableScan):
        self.custo_indice = resultado_indice.custo_paginas
        self.custo_scan = resultado_scan.custo_paginas
        self.tempo_indice = resultado_indice.tempo_segundos
        self.tempo_scan = resultado_scan.tempo_segundos

    @property
    def diferenca_custo_percentual(self) -> float:
        if not self.custo_scan:
            return 0.0
        return (self.custo_scan - self.custo_indice) / self.custo_scan * 100

    @property
    def diferenca_tempo_segundos(self) -> float:
        return self.tempo_scan - self.tempo_indice

    @property
    def fator_aceleracao(self) -> float:
        return self.tempo_scan / self.tempo_indice if self.tempo_indice else 0.0


def comparar(
    resultado_indice: ResultadoBuscaIndexada, resultado_scan: ResultadoTableScan
) -> Comparativo:
    return Comparativo(resultado_indice, resultado_scan)

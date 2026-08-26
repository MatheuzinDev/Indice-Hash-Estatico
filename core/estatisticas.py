class EstatisticasIndice:
    def __init__(self, indice):
        self.indice = indice

    @property
    def taxa_colisao(self) -> float:
        if self.indice.NR == 0:
            return 0.0
        return (self.indice.total_colisoes / self.indice.NR) * 100

    @property
    def taxa_overflow(self) -> float:
        if self.indice.NB == 0:
            return 0.0
        return (len(self.indice.buckets_em_overflow) / self.indice.NB) * 100
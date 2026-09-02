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

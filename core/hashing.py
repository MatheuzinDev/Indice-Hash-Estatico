class IndexHashStatic:
    def __init__(self, data: list[str]):
        self.NR = len(data)
        self.FR = self._validate_FR(int(self.NR * 0.50))
        self.NB = self._validate_NB((self.NR // self.FR) + 1)
        self.SIZE = 0
        self.bucket = self._init_bucket(self.NB, self.FR, data)
        print(f"Sistema inicializado: Foram criados {self.NB} buckets (NB) com capacidade {self.FR} (FR).")

    def _validate_FR(self, num: int):
        return num or 1

    def _validate_NB(self, num: int):
        if num <= self.NR / self.FR:
            raise ValueError(f"Erro na regra de negócio: NB ({num}) deve ser maior que NR/FR ({self.NR/self.FR})")
        return num

    def _init_bucket(self, NB: int, FR: int, data: list[str]):
        bucket = self._dinamic_bucket(NB, FR)
        bucket = self._population_bucket(bucket, data)
        return bucket

    def _dinamic_bucket(self, NB: int, FR: int):
        bucket = [None] * NB
        for i in range(0, NB):
             bucket[i] = [[None, i] for _ in range(FR)]
        return bucket

    def _population_bucket(self, bucket: list[None], data: list[str]):
        #TODO PRECISA CRIAR A FUNÇÃO HASH ANTES DE POPULAR O BUCKET
        return bucket

    def insert(self, key, value):
        pass

    def search(self, key):
        pass

    def delete(self, key):
        pass

    def hash(self):
        pass
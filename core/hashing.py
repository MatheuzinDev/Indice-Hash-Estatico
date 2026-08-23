import math

class IndexHashStatic:
    def __init__(self, data: list[str]):
        self.NR = len(data) + 1
        self.FR = self._validate_FR(20)
        self.COLISION = 0
        self.NB = self._validate_NB(math.ceil(self.NR / (self.FR * 0.70)))
        self.bucket = self._init_bucket(self.NB, self.FR, data)
        print(f"Sistema inicializado: Foram criados {self.NB} buckets (NB) com capacidade {self.FR} (FR).")
        print(f"Total de palavras armazenadas: {self.NR-1}. Total de colisões: {self.COLISION}.")

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
             bucket[i] = [[None, -1] for _ in range(FR)]
        return bucket

    def _population_bucket(self, bucket: list[None], data: list[str]):
        fr = self.FR
        local_size = 0
        hash_func = self.hash
        next_free_pos = [0] * self.NB

        for word in data:
            key = hash_func(word)
            pos = next_free_pos[key]
            if pos < fr:
                bucket[key][pos][0] = word
                bucket[key][pos][1] = local_size + 1
                next_free_pos[key] += 1 
                local_size += 1
            else:
                print(f"Alerta: Bucket {key} lotou na palavra '{word}'.")
                self.COLISION += 1
            
        return bucket

    def insert(self, value: str):
        key = self.hash(value)
        for bucket_pos in range(self.FR):
            if self.bucket[key][bucket_pos][0] is None: 
                self.bucket[key][bucket_pos][0] = value
                self.bucket[key][bucket_pos][1] = self.SIZE + 1
                self.SIZE = self.SIZE + 1
                return True
        print(f"Colisão máxima atingida! O bucket {key} está cheio.")
        self.COLISION += 1
        return False

    def search(self, value: str):
        key = self.hash(value)
        for bucket_pos in range(self.FR):
            slot_value = self.bucket[key][bucket_pos][0]
            if slot_value == value:
                return self.bucket[key][bucket_pos] 
            if slot_value is None:
                return None 
        return None

    def delete(self, key):
        pass

    def hash(self, value: str):
        hash = 5381
        for char in value:
            hash *= 33 + ord(char)
        return hash % self.NB

"""
Como usuário
Quero que o índice utilize uma função hash definida pela equipe
Para mapear chaves de busca em buckets.

Regras de Negócio
RN10: A função hash deve mapear uma chave em um endereço de bucket.
RN11: A função hash deve ser escolhida/projetada pela equipe.

Critérios de Aceitação
CA11: Dada uma chave, o sistema retorna sempre o mesmo bucket.
CA12: A função hash sempre retorna um bucket dentro do intervalo válido [0..NB-1].
"""
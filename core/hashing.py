
"""
Como usuário
Quero que o sistema crie automaticamente os buckets do índice
Para permitir a construção do índice hash estático.

Regras de Negócio
RN08: O número de buckets NB deve obedecer:
• NB > NR / FR, onde NR é o número de registros e FR é o tamanho do bucket.
RN09: FR (capacidade do bucket) deve ser definido pela equipe.

Critérios de Aceitação
CA08: O sistema calcula e exibe NB.
CA09: O sistema cria NB buckets com capacidade FR.
CA10: O sistema impede NB <= NR/FR.
"""

class IndexHashStatic:
    def __init__(self, data: list[str]):
        self.NR = len(data)
        self.FR = int(self.NR * 0.50)
        self.NB = self.NR // self.FR
        self.bucket = self.init_bucket(self.NB, self.FR)

    def init_bucket(self, NB: int, FR: int):
        bucket = [None] * FR
        for i in range(0, FR):
            bucket[i] = [None] * NB
        return bucket

    def insert(key, value):
        pass

    def search(key):
        pass

    def delete(key):
        pass

    def hash():
        pass
import math
import time
from core.armazenamento import Tabela

class IndiceHashEstatico:
    def __init__(self, dados: Tabela):
        tempo_inicial = time.time()

        self.NR = len(dados.palavras)
        self.TAMANHO = 0
        self.FR = self._validar_frequencia_registros(20)
        self.NB = self._validar_numero_buckets(
            math.ceil(self.NR / (self.FR * 0.70))
        )

        self.bucket = self._criar_bucket_dinamico(self.NB, self.FR)
        self.proxima_posicao_livre = [0] * self.NB

        self.overflow: list[list[list]] = [[] for _ in range(self.NB)]
        self.total_colisoes = 0
        self.total_overflow = 0
        self.buckets_em_overflow: set[int] = set()

        self._construir_indice_por_paginas(dados)

        tempo_final = time.time()

        print(f"Sistema inicializado: {self.NB} buckets (NB), "f"capacidade {self.FR} (FR).")
        print(f"Tempo de construção do índice: "f"{(tempo_final - tempo_inicial):.4f} segundos")

    def _validar_frequencia_registros(self, numero: int):
        return numero or 1

    def _validar_numero_buckets(self, numero: int):
        if numero < 1:
            raise ValueError("NB deve ser no mínimo 1")
        return numero

    def _criar_bucket_dinamico(self, quantidade_buckets: int, capacidade: int):
        bucket = [None] * quantidade_buckets

        for indice in range(quantidade_buckets):
            bucket[indice] = [[None, -1] for _ in range(capacidade)]

        return bucket

    def _construir_indice_por_paginas(self, dados: Tabela):
        total_paginas = dados.qtd_paginas

        for numero_pagina in range(total_paginas):
            registros_pagina = dados.ler_pagina(numero_pagina)

            for registro in registros_pagina:
                self.inserir(registro, numero_pagina)

    def inserir(self, valor: str, identificador_pagina: int):
        chave = self.funcao_hash(valor)
        posicao_bucket = self.proxima_posicao_livre[chave]

        if posicao_bucket < self.FR:
            self.bucket[chave][posicao_bucket][0] = valor
            self.bucket[chave][posicao_bucket][1] = identificador_pagina
            self.proxima_posicao_livre[chave] += 1
            self.TAMANHO += 1
            return True

        self.overflow[chave].append([valor, identificador_pagina])
        self.total_colisoes += 1
        self.total_overflow += 1
        self.buckets_em_overflow.add(chave)
        return True

    def buscar(self, valor: str):
        chave = self.funcao_hash(valor)

        for posicao_bucket in range(self.proxima_posicao_livre[chave]):
            if self.bucket[chave][posicao_bucket][0] == valor:
                return self.bucket[chave][posicao_bucket]

        for entrada in self.overflow[chave]:
            if entrada[0] == valor:
                return entrada

        return None

    def funcao_hash(self, valor: str):
        valor_hash = 5381

        for caractere in valor:
            valor_hash *= 33 + ord(caractere)

        return valor_hash % self.NB
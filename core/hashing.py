import math
import time

class IndexHashStatic:
    def __init__(self, datas: list[str], datas_per_page: int = 100):
        start_time = time.time()
        self.NR = len(datas)
        self.SIZE = 0
        self.FR = self._validate_FR(20)
        self.NB = self._validate_NB(math.ceil(self.NR / (self.FR * 0.70)))
        self.bucket = self._dinamic_bucket(self.NB, self.FR)
        self.next_free_pos = [0] * self.NB


        self.overflow: list[list[list]] = [[] for _ in range(self.NB)]
        self.total_colisoes = 0
        self.total_overflow = 0
        self.buckets_em_overflow: set[int] = set()

        self._build_index_from_pages(datas, datas_per_page)
        end_time = time.time()

        print(f"Sistema inicializado: {self.NB} buckets (NB), capacidade {self.FR} (FR).")
        print(f"Tempo de construção do índice: {(end_time - start_time):.4f} segundos")

    def _validate_FR(self, num: int):
        return num or 1

    def _validate_NB(self, num: int):
        if num < 1: raise ValueError("NB deve ser no mínimo 1")
        return num

    def _dinamic_bucket(self, NB: int, FR: int):
        bucket = [None] * NB
        for i in range(NB):
             bucket[i] = [[None, -1] for _ in range(FR)]
        return bucket

    def _build_index_from_pages(self, datas: list[str], datas_per_page: int):
        total_pages = math.ceil(self.NR / datas_per_page)

        for page_id in range(total_pages):
            start_idx = page_id * datas_per_page
            end_idx = start_idx + datas_per_page
            page_records = datas[start_idx : end_idx]

            for data in page_records:
                self.insert(data, page_id)

    def insert(self, value: str, page_id: int):
        key = self.hash(value) 
        bucket_pos = self.next_free_pos[key] 

        if bucket_pos < self.FR: 
            self.bucket[key][bucket_pos][0] = value 
            self.bucket[key][bucket_pos][1] = page_id 
            self.next_free_pos[key] += 1 
            self.SIZE += 1 
            return True 


        self.overflow[key].append([value, page_id])
        self.total_colisoes += 1
        self.total_overflow += 1 
        self.buckets_em_overflow.add(key) 
        return True 

    def search(self, value: str):
        key = self.hash(value)

        for bucket_pos in range(self.next_free_pos[key]):
            if self.bucket[key][bucket_pos][0] == value:
                return self.bucket[key][bucket_pos]

        for entrada in self.overflow[key]:
            if entrada[0] == value:
                return entrada

        return None

    def hash(self, value: str):
        hash_val = 5381
        for char in value:
            hash_val *= 33 + ord(char) 
        return hash_val % self.NB
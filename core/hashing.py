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
        hash_func = self.hash
        fr = self.FR
        
        for page_id in range(total_pages):
            start_idx = page_id * datas_per_page
            end_idx = start_idx + datas_per_page
            page_records = datas[start_idx : end_idx]

            for data in page_records:
                key = hash_func(data)
                pos = self.next_free_pos[key]

                if pos < fr:
                    self.bucket[key][pos][0] = data
                    self.bucket[key][pos][1] = page_id
                    self.next_free_pos[key] += 1 
                    self.SIZE += 1
                else:
                    print(f"Alerta: Bucket {key} lotou na palavra '{data}'.")

    def insert(self, value: str, page_id: int):
        key = self.hash(value)

        for bucket_pos in range(self.FR):
            if self.bucket[key][bucket_pos][0] is None: 
                self.bucket[key][bucket_pos][0] = value
                self.bucket[key][bucket_pos][1] = page_id
                self.SIZE += 1
                return True
                
        print(f"Colisão máxima atingida! O bucket {key} está cheio.")
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

    def hash(self, value: str):
        hash_val = 5381
        for char in value:
            hash_val *= 33 + ord(char) 
        return hash_val % self.NB
# Índice Hash Estático — Especificação de Implementação

**Linguagem:** Python 3.11+ · **Interface:** PySide6 (Qt) · **Base de dados:** `words_alpha.txt` (~466 mil palavras)

---

## 1. Decisões de stack

| Item | Escolha | Justificativa |
|---|---|---|
| Runtime | Python 3.11+ | Ganho real de performance em loops sobre 3.9/3.10 |
| GUI | PySide6 | Licença LGPL, `QTableWidget` e `QGridLayout` resolvem a visualização de páginas e buckets sem desenhar em canvas |
| Concorrência | `QThread` | Construção do índice fora da thread da UI (RNF01) |
| Cronometragem | `time.perf_counter()` | Relógio monotônico de alta resolução (RNF02, HU11) |
| Dependências externas | Apenas PySide6 | Nada de NumPy/Pandas — a rubrica exige explicar o código-fonte |

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install PySide6
```

> **Alternativa aceitável:** Tkinter (já vem na stdlib). Perde em aparência e o layout de buckets fica mais trabalhoso, mas atende o RNF04. **Não use Streamlit** — o modelo de re-execução do script inteiro inviabiliza o destaque passo a passo exigido pelo CA29.

---

## 2. Arquitetura de módulos

```
projeto/
├── main.py                 # ponto de entrada, instancia a janela
├── core/
│   ├── __init__.py
│   ├── hashing.py          # função hash FNV-1a + cálculo de NB
│   ├── storage.py          # Tabela, paginação, contador de acessos
│   ├── index.py            # Bucket, OverflowBucket, HashIndex
│   ├── search.py           # busca indexada e table scan
│   └── metrics.py          # dataclasses de estatísticas
├── ui/
│   ├── main_window.py      # layout geral
│   ├── panels.py           # painel de config, métricas, busca
│   └── widgets.py          # BucketGrid, PageView (com highlight)
└── data/
    └── words_alpha.txt
```

**Regra de ouro da separação:** nada em `core/` importa PySide6. Isso permite testar o índice por script e é o que torna a explicação do código na banca organizada.

---

## 3. Estruturas de dados

### 3.1 Tabela e páginas

A tabela é um **array plano** de strings. Página **não é uma cópia de dados** — é um intervalo calculado sobre esse array. Duplicar os registros em 4.666 objetos gastaria memória à toa e tornaria o custo de leitura fictício.

```python
# core/storage.py
from dataclasses import dataclass, field
import math

@dataclass
class Table:
    records: list[str]
    page_size: int
    page_reads: int = 0          # contador de acessos a disco simulados

    @property
    def num_pages(self) -> int:
        return math.ceil(len(self.records) / self.page_size)   # RN07

    def read_page(self, page_id: int) -> list[str]:
        """ÚNICO ponto de leitura de dados. Todo acesso passa por aqui."""
        if not 0 <= page_id < self.num_pages:
            raise IndexError(f"página {page_id} inexistente")
        self.page_reads += 1
        start = page_id * self.page_size
        return self.records[start:start + self.page_size]

    def reset_counter(self) -> None:
        self.page_reads = 0
```

Esse `read_page` é o coração da credibilidade do trabalho. Os critérios 7 e 11 valem 2,5 pontos e dependem de o custo ser medido, não estimado por fórmula.

### 3.2 Bucket e overflow

```python
# core/index.py
from dataclasses import dataclass, field

@dataclass
class Bucket:
    entries: list[tuple[str, int]] = field(default_factory=list)  # (chave, página)
    overflow: "Bucket | None" = None                              # encadeamento

    def is_full(self, fr: int) -> bool:
        return len(self.entries) >= fr
```

**Estratégia de overflow: encadeamento (lista ligada de buckets).** Escolhida sobre endereçamento aberto por dois motivos defensáveis na apresentação:

1. O custo de leitura fica explícito — cada bucket de overflow visitado é +1 acesso ao índice.
2. É trivial de desenhar na interface (uma cadeia visível ao lado do bucket base).

### 3.3 O índice

```python
@dataclass
class HashIndex:
    nb: int
    fr: int
    buckets: list[Bucket]
    collisions: int = 0              # RN14
    overflow_buckets: int = 0
    build_time: float = 0.0
    index_reads: int = 0
```

---

## 4. Função hash

`hash()` do Python é **randomizado por execução** (PYTHONHASHSEED) para strings. Usá-lo **viola diretamente o RNF05** (determinismo). Implementação manual obrigatória.

```python
# core/hashing.py
FNV_OFFSET = 0x811C9DC5
FNV_PRIME  = 0x01000193
MASK32     = 0xFFFFFFFF

def fnv1a(key: str) -> int:
    """FNV-1a de 32 bits. Determinístico entre execuções e máquinas."""
    h = FNV_OFFSET
    for byte in key.encode("utf-8"):
        h ^= byte
        h = (h * FNV_PRIME) & MASK32
    return h

def bucket_address(key: str, nb: int) -> int:
    return fnv1a(key) % nb          # RN10, CA12: sempre em [0, NB-1]
```

**Por que FNV-1a:** cinco linhas, avalancha razoável em strings curtas do alfabeto latino, e a explicação na banca é direta — XOR com o byte, multiplicação por primo, truncamento em 32 bits.

### Dimensionamento de NB

```python
def is_prime(n: int) -> bool:
    if n < 2: return False
    if n % 2 == 0: return n == 2
    i = 3
    while i * i <= n:
        if n % i == 0: return False
        i += 2
    return True

def next_prime(n: int) -> int:
    while not is_prime(n): n += 1
    return n

def compute_nb(nr: int, fr: int, slack: float = 1.25) -> int:
    """RN08: NB > NR/FR. Primo melhora a dispersão do módulo."""
    minimum = nr / fr
    nb = next_prime(math.ceil(minimum * slack))
    assert nb > minimum, "CA10 violado"
    return nb
```

**Valores de referência** para NR = 466.550 e FR = 32:

| Grandeza | Valor |
|---|---|
| NR / FR (mínimo teórico) | 14.579,7 |
| NB adotado (primo) | **18.229** |
| Fator de carga | 0,80 |
| Páginas com TP = 100 | 4.666 |

Fator de carga em 0,80 é deliberado: mantém overflow visível na demonstração (fica bonito na tela e prova que o algoritmo funciona) sem degradar a busca.

---

## 5. Construção do índice

Percorre **página por página** (RN12), não o array direto — isso é o que simula o custo real de leitura exigido pela HU06.

```python
# core/index.py
import time

def build_index(table: Table, fr: int) -> HashIndex:
    nr = len(table.records)
    nb = compute_nb(nr, fr)
    idx = HashIndex(nb=nb, fr=fr, buckets=[Bucket() for _ in range(nb)])

    t0 = time.perf_counter()
    for page_id in range(table.num_pages):
        for key in table.read_page(page_id):          # RN12
            insert(idx, key, page_id)
    idx.build_time = time.perf_counter() - t0         # CA14, RNF02
    return idx


def insert(idx: HashIndex, key: str, page_id: int) -> None:
    addr = bucket_address(key, idx.nb)
    bucket = idx.buckets[addr]

    if not bucket.is_full(idx.fr):
        bucket.entries.append((key, page_id))         # caso comum
        return

    # RN14: colisão SÓ é contabilizada quando o bucket está cheio
    idx.collisions += 1

    if bucket.overflow is None:
        bucket.overflow = Bucket()
        idx.overflow_buckets += 1                     # CA18

    # percorre a cadeia até achar espaço
    node = bucket.overflow
    while node.is_full(idx.fr):
        if node.overflow is None:
            node.overflow = Bucket()
            idx.overflow_buckets += 1
        node = node.overflow
    node.entries.append((key, page_id))               # CA17
```

**Atenção à RN14** — ela é contraintuitiva e vale 0,5 ponto (critério 8). Colisão *não* é "duas chaves no mesmo bucket". É **inserção em bucket que já atingiu FR**. Duas chaves caindo no bucket 42 com FR=32 e apenas 5 ocupantes **não contam como colisão**.

---

## 6. Busca

### 6.1 Busca indexada (HU09)

```python
# core/search.py
from dataclasses import dataclass

@dataclass
class SearchResult:
    found: bool
    key: str
    page_id: int | None
    index_reads: int        # buckets visitados
    data_reads: int         # páginas lidas
    elapsed: float
    visited_buckets: list[int]   # para o highlight da UI (CA29)


def index_search(table: Table, idx: HashIndex, key: str) -> SearchResult:
    table.reset_counter()
    t0 = time.perf_counter()

    addr = bucket_address(key, idx.nb)          # RN19.1
    index_reads = 0
    node = idx.buckets[addr]                    # RN19.2

    while node is not None:
        index_reads += 1
        for k, page_id in node.entries:
            if k == key:                        # RN19.3
                records = table.read_page(page_id)   # RN19.4
                return SearchResult(
                    found=key in records, key=key, page_id=page_id,
                    index_reads=index_reads, data_reads=table.page_reads,
                    elapsed=time.perf_counter() - t0, visited_buckets=[addr],
                )
        node = node.overflow

    return SearchResult(False, key, None, index_reads, 0,
                        time.perf_counter() - t0, [addr])   # CA20
```

**Custo total = `index_reads` + `data_reads`.** Reporte os dois separadamente na interface: acessos ao índice e acessos aos dados. Isso demonstra domínio do conceito e é exatamente o que o critério 11 avalia.

### 6.2 Table scan (HU10)

Precisa usar **o mesmo `read_page()`**, senão a comparação de tempo vira ficção.

```python
def table_scan(table: Table, key: str) -> SearchResult:
    table.reset_counter()
    t0 = time.perf_counter()
    scanned: list[str] = []

    for page_id in range(table.num_pages):      # RN21
        records = table.read_page(page_id)
        for rec in records:
            scanned.append(rec)
            if rec == key:
                return SearchResult(True, key, page_id, 0, table.page_reads,
                                    time.perf_counter() - t0, [])   # CA22
    return SearchResult(False, key, None, 0, table.page_reads,
                        time.perf_counter() - t0, [])
```

Para o CA21 (exibir os registros lidos), **não jogue 466 mil strings na tela**. Mostre os últimos ~200 registros lidos antes do acerto, ou pagine a lista. Uma lista completa trava a UI e não acrescenta nada à avaliação.

---

## 7. Métricas

| Métrica | Fórmula | Requisito |
|---|---|---|
| Taxa de colisões | `colisões / NR × 100` | RN24, CA25 |
| Taxa de overflow | `buckets_com_overflow / NB × 100` | RN25, CA26 |
| Custo indexado | `index_reads + data_reads` | CA19.3 |
| Custo do scan | `páginas lidas até encontrar` | CA22.2 |
| Diferença percentual | `(custo_scan − custo_índice) / custo_scan × 100` | CA24 |
| Diferença de tempo | `tempo_scan − tempo_índice` | RN22, CA23 |

```python
# core/metrics.py
@dataclass
class IndexStats:
    nr: int; nb: int; fr: int; num_pages: int
    collisions: int; overflow_buckets: int; build_time: float

    @property
    def collision_rate(self) -> float:
        return self.collisions / self.nr * 100 if self.nr else 0.0

    @property
    def overflow_rate(self) -> float:
        return self.overflow_buckets / self.nb * 100 if self.nb else 0.0
```

---

## 8. Interface gráfica

Janela única, quatro regiões. Nada de popups (RNF04).

```
┌────────────────────────────────────────────────────────────────┐
│  [Arquivo…]  Tam. página: [100]  FR: [32]   [Construir índice] │  ← config
├────────────────────────────────────────────────────────────────┤
│  NR: 466.550 │ Páginas: 4.666 │ NB: 18.229 │ FR: 32            │  ← métricas
│  Colisões: 12,4% │ Overflow: 31,2% │ Build: 1,84 s             │
├───────────────────────────────┬────────────────────────────────┤
│  PÁGINAS                      │  BUCKETS                       │
│  ┌─ Página 0 ──────────────┐  │  ┌──┬──┬──┬──┬──┬──┬──┬──┐    │
│  │ a, aa, aaa, aah, aahed  │  │  │  │  │██│  │  │  │  │  │    │
│  └─────────────────────────┘  │  ├──┼──┼──┼──┼──┼──┼──┼──┤    │
│  ┌─ Página 4665 ───────────┐  │  │  │  │  │  │  │  │  │  │    │
│  │ zyzzogeton, zyzzyva…    │  │  └──┴──┴──┴──┴──┴──┴──┴──┘    │
│  └─────────────────────────┘  │  [detalhe do bucket 8.412]     │
├───────────────────────────────┴────────────────────────────────┤
│  Chave: [_______]  [Buscar por índice]  [Table scan]           │  ← busca
│  Índice:  encontrada, pág. 2.103, custo 2 (1 idx + 1 dados), 0,04 ms │
│  Scan:    encontrada, pág. 2.103, custo 2.104 páginas, 187,2 ms      │
│  Ganho:   99,9% menos páginas · 4.680× mais rápido                   │
└────────────────────────────────────────────────────────────────┘
```

### Requisitos de UI que costumam ser esquecidos

- **CA07** — exibir **primeira e última** página com número e os 5 primeiros registros. Item barato de implementar e que aparece em dois critérios.
- **CA28** — o usuário precisa ver o conteúdo dos buckets. Renderizar 18.229 células é viável se cada uma for um retângulo colorido por ocupação; clicar abre o detalhe (chaves + páginas + cadeia de overflow).
- **CA29** — **durante a busca, destacar o bucket e a página acessados.** É o requisito mais exigente da interface. Guarde `visited_buckets` e `page_id` no `SearchResult` e pinte-os. Implemente isso na *primeira* versão, não como polimento final.
- **CA05** — bloquear tamanho de página zero, negativo ou vazio antes de prosseguir.
- **CA03** — tratar arquivo vazio ou ilegível com mensagem na própria janela.

### Não travar a interface

```python
class BuildWorker(QThread):
    finished_ok = Signal(object)
    progress = Signal(int)

    def __init__(self, table, fr):
        super().__init__(); self.table, self.fr = table, fr

    def run(self):
        idx = build_index(self.table, self.fr)   # emitir progress a cada 100 páginas
        self.finished_ok.emit(idx)
```

Carregar 466 mil linhas leva ~0,3 s; construir o índice em Python puro leva 1–3 s. Sem thread, a janela congela e dá impressão de travamento na apresentação.

---

## 9. Rastreabilidade — requisito → onde está implementado

| Requisito | Módulo / função |
|---|---|
| RN01–03, CA01–03 | `ui/panels.py` → carregamento e validação do TXT |
| RN04–05, CA04–05 | `ui/panels.py` → validação do tamanho de página |
| RN06–07, CA06–07 | `Table.num_pages`, `PageView` |
| RN08–09, CA08–10 | `compute_nb`, `HashIndex.__init__` |
| RN10–11, CA11–12 | `fnv1a`, `bucket_address` |
| RN12–13, CA13–14 | `build_index` |
| RN14–15, CA15–16 | `insert` (contador `collisions`) |
| RN16–17, CA17–18 | `insert` (cadeia `overflow`) |
| RN18–19, CA19–20 | `index_search` |
| RN20–21, CA21–22 | `table_scan` |
| RN22–23, CA23–24 | painel de comparação |
| RN24–25, CA25–26 | `IndexStats` |
| RN26–27, CA27–29 | `ui/widgets.py` |
| RNF01 | `QThread` + array plano |
| RNF02 | `HashIndex.build_time` |
| RNF05 | `fnv1a` manual (nunca `hash()`) |

---

## 10. Plano de execução

**Etapa 1 — Núcleo sem interface (1 dia).** `storage.py`, `hashing.py`, `index.py`, `search.py`. Valide por script: construir o índice, buscar 10 palavras conhecidas, imprimir métricas. Se isso funciona, 60% do trabalho está feito.

**Etapa 2 — Interface mínima (1 dia).** Janela, carregar arquivo, campos de configuração, botão construir, painel de métricas, primeira e última página.

**Etapa 3 — Buckets e busca (1 dia).** Grade de buckets, detalhe ao clicar, campo de busca, painel comparativo. **O highlight do CA29 entra aqui.**

**Etapa 4 — Acabamento (meio dia).** Thread de construção, validações, tratamento de erros, lista de registros do scan paginada.

**Etapa 5 — Preparação da apresentação (meio dia).** Cinco critérios exigem explicar código-fonte (5,5 pontos): carga de dados, tamanho de página, cálculo de páginas, função hash, cálculo de buckets e busca indexada. Cada integrante deve conseguir explicar pelo menos dois.

---

## 11. Armadilhas

1. **Usar `hash()` nativo** → quebra o RNF05. O valor muda a cada execução do programa.
2. **Usar `dict` como índice** → elimina colisão e overflow do problema. Perde os critérios 5 a 9 (3,5 pontos).
3. **Contar colisão errado** → RN14 conta apenas inserção em bucket cheio, não coincidência de endereço.
4. **Table scan sem `read_page`** → a comparação de tempo perde sentido e o critério 11 fica frágil.
5. **Copiar registros para dentro dos objetos de página** → desperdício de memória e custo de leitura fictício.
6. **Renderizar os 466 mil registros do scan** → congela a UI durante a demonstração.
7. **Deixar o CA29 para o fim** → é o item de interface mais visível na banca e o mais fácil de não dar tempo.
8. **NB não primo** → o módulo com número composto agrupa chaves e piora a taxa de colisão sem motivo.

---

## 12. Checklist da rubrica (10,0 pontos)

- [ ] **1,0** — Interface gráfica funcional, sem terminal, sem popups
- [ ] **1,5** — Carga de dados nas páginas *(explicar código)*
- [ ] **1,0** — Campo de entrada para tamanho da página *(explicar código)*
- [ ] **1,0** — Cálculo da quantidade de páginas *(explicar código)*
- [ ] **1,0** — Construção e uso da função hash *(explicar código)*
- [ ] **0,5** — Cálculo da quantidade de buckets *(explicar código)*
- [ ] **2,0** — Pesquisa com uso do índice *(explicar código)*
- [ ] **0,5** — Taxa de colisões calculada e exibida
- [ ] **0,5** — Taxa de overflows calculada e exibida
- [ ] **0,5** — Execução do table scan
- [ ] **0,5** — Estimativa de custo e comparativo de tempo índice × scan

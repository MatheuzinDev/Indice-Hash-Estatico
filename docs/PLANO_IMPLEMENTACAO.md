# Plano de Implementação — Índice Hash Estático (AV1)

> Derivado de `26.2 - Projeto 1 - Índice HASH.pdf` (requisitos oficiais) e
> `especificacao_indice_hash.md` (decisões técnicas da equipe).
> Histórico de mudanças em `REGISTRO_DE_ALTERACOES.md`.

**Organização:** o trabalho é fatiado por **história de usuário (HU)**. Cada HU é entregue
verticalmente — núcleo + interface + validação — e só é considerada pronta quando **todos os seus
critérios de aceitação** estão demonstráveis na tela. Nada de "faço todo o `core/` e depois toda a UI":
uma HU meio pronta não pontua.

---

## Situação atual

| Item | Estado |
|---|---|
| Repositório git | ✅ inicializado (branch `main`), sem commits |
| Estrutura de pastas | ✅ `core/`, `ui/`, `data/`, `docs/`, `scripts/` |
| `README.md`, `.gitignore`, `requirements.txt` | ✅ criados |
| Código-fonte | ❌ nada implementado |
| `data/words.txt` | ✅ presente e versionado — **NR = 466.550** |
| Python | ❌ **não instalado** (só o atalho da Microsoft Store) |
| `git config user.name` / `user.email` | ❌ não configurados |

---

## Ondas de entrega

| Onda | Conteúdo | Resultado visível |
|---|---|---|
| **0** | Ambiente + esqueleto da janela | Janela abre, vazia |
| **1** | HU01, HU02, HU03 | Carrega arquivo, pagina, mostra primeira e última página |
| **2** | HU04, HU05, HU06 | Índice construído, NB e tempo na tela |
| **3** | HU07, HU08 | Colisões e overflow tratados e contados |
| **4** | HU12, HU13 | Taxas de colisão e overflow exibidas |
| **5** | HU09 | Busca indexada funcionando com destaque visual |
| **6** | HU10, HU11 | Table scan e comparativo |
| **7** | HU14 (consolidação) + acabamento | Interface completa e apresentável |

`HU14` é **transversal**: começa na Onda 0 e recebe uma parcela em quase toda onda. Ver §HU14.

---

# Onda 0 — Ambiente e esqueleto

Não é uma HU, mas bloqueia todas elas.

- [ ] **0.1** Instalar Python 3.11+ (instalador oficial do python.org, marcando *Add python.exe to PATH*).
      Conferir com `python --version`.
- [ ] **0.2** Criar o venv e instalar dependências:
      ```powershell
      python -m venv .venv
      .venv\Scripts\Activate.ps1
      pip install -r requirements.txt
      ```
- [ ] ~~**0.3** Baixar a base de dados~~ — ✅ **feito**: `data/words.txt` já está no repositório
      (466.550 registros, 0 duplicatas). Ver `data/README.md`.
- [ ] **0.4** `main.py` — `QApplication` + `MainWindow` vazia que abre e fecha.
- [ ] **0.5** `ui/main_window.py` — janela única com quatro áreas reservadas (configuração, métricas,
      visualização, busca) e uma **faixa de status** no rodapé para mensagens de erro.
      Sem `QMessageBox` em lugar nenhum (RNF04).

**Pronto quando:** `python main.py` abre a janela com as quatro áreas demarcadas e fecha sem erro.

---

# EPIC 1 — Carga e Organização dos Dados

## HU01 — Carregar arquivo de palavras
`Onda 1` · `rubrica: critério 2 (1,5 pts, explicar código)`

> Como usuário, quero carregar um arquivo TXT contendo palavras únicas, para popular as páginas em
> memória a serem indexadas.

**Regras:** RN01 (uma palavra por linha) · RN02 (cada palavra é chave única) · RN03 (~466 mil palavras)

**Tarefas**
- [ ] `core/storage.py` → `load_words(path) -> list[str]`: lê o TXT, aplica `strip()`, descarta linhas
      vazias, abre com `encoding="utf-8"` e trata `UnicodeDecodeError`
- [ ] Levantar exceção com mensagem legível quando o arquivo estiver vazio ou ilegível
- [ ] `ui/panels.py` → botão "Arquivo…" com `QFileDialog` filtrando `*.txt`
- [ ] Exibir o total de palavras carregadas no painel de métricas
- [ ] Exibir erros na faixa de status da janela — **nunca** em popup nem no terminal

**Pronto quando**
- [ ] **CA01** — seleciona um `.txt` pela interface e os registros são carregados
- [ ] **CA02** — o total de palavras carregadas aparece na tela
- [ ] **CA03** — arquivo vazio ou ilegível gera mensagem de erro dentro da janela

**Depende de:** Onda 0
**Nota:** o `QFileDialog` é o seletor nativo do SO, não uma "janela popup" no sentido proibido pelo
RNF04 — que se refere a usar caixas de diálogo como interface principal.

---

## HU02 — Definir tamanho de página
`Onda 1` · `rubrica: critério 3 (1,0 pt, explicar código)`

> Como usuário, quero informar o tamanho da página (registros por página), para controlar como os
> registros serão divididos.

**Regras:** RN04 (entrada digitada na interface) · RN05 (maior que zero)

**Tarefas**
- [ ] `QSpinBox` para o tamanho da página, com mínimo 1 e padrão 100
- [ ] Validar antes de prosseguir: valor zero, negativo ou vazio **bloqueia** a construção
- [ ] Mensagem de validação na faixa de status
- [ ] Desabilitar o botão "Construir índice" enquanto o valor for inválido

**Pronto quando**
- [ ] **CA04** — existe um campo na interface para digitar o tamanho da página
- [ ] **CA05** — valor inválido impede a continuação, com mensagem explicando o motivo

**Depende de:** Onda 0
**Armadilha:** um `QSpinBox` com `minimum=1` já impede valores inválidos pela UI — mas a validação
tem que existir **no código também**, porque é ela que você vai explicar para a banca.

---

## HU03 — Dividir registros em páginas
`Onda 1` · `rubrica: critério 2 (1,5 pts) + critério 4 (1,0 pt), ambos explicar código`

> Como usuário, quero que o sistema divida automaticamente os registros em páginas, para simular
> armazenamento físico em disco.

**Regras:** RN06 (divisão depende do tamanho definido) · RN07 (nº de páginas = NR ÷ registros por página)

**Tarefas**
- [ ] `core/storage.py` → `Table(records, page_size)` — **array plano**; a página é um intervalo
      calculado sobre ele, nunca uma cópia dos dados
- [ ] `num_pages` = `math.ceil(len(records) / page_size)`
- [ ] `read_page(page_id)` — **único ponto de leitura de dados de todo o sistema**, incrementa
      `page_reads` e valida o intervalo
- [ ] `reset_counter()` — zera o contador antes de cada busca
- [ ] `ui/widgets.py` → `PageView`: primeira e última página, com número e os 5 primeiros registros
- [ ] Exibir a quantidade total de páginas no painel de métricas

**Pronto quando**
- [ ] **CA06** — a quantidade total de páginas aparece após carregar o arquivo
- [ ] **CA07** — primeira e última página exibidas com número e 5 primeiros registros

**Depende de:** HU01, HU02
**Por que importa:** `read_page` é o que dá credibilidade ao trabalho inteiro. Os critérios 7 e 11
(2,5 pts) dependem do custo ser **medido** por esse contador, não estimado por fórmula. Qualquer
leitura que passe por fora dele torna a comparação índice × scan uma ficção.

---

# EPIC 2 — Construção do Índice Hash Estático

## HU04 — Criar buckets do índice
`Onda 2` · `rubrica: critério 6 (0,5 pt, explicar código)`

> Como usuário, quero que o sistema crie automaticamente os buckets do índice.

**Regras:** RN08 (NB > NR/FR) · RN09 (FR definido pela equipe)

**Tarefas**
- [ ] `core/hashing.py` → `import math`, `is_prime(n)`, `next_prime(n)`
- [ ] `compute_nb(nr, fr, slack=1.25)` — NB primo, com folga de 25% sobre o mínimo teórico
- [ ] **Validar com `raise ValueError`, não `assert`** — `assert` some com `python -O` e o CA10 é
      requisito avaliado *(correção C4)*
- [ ] `ui/panels.py` → `QSpinBox` para FR, padrão 32 (RN09)
- [ ] `HashIndex` criado com exatamente NB buckets vazios de capacidade FR
- [ ] Exibir NB e FR no painel de métricas

**Pronto quando**
- [ ] **CA08** — o sistema calcula e exibe NB
- [ ] **CA09** — são criados NB buckets com capacidade FR
- [ ] **CA10** — o sistema impede NB ≤ NR/FR

**Depende de:** HU01, HU02
**Armadilha:** NB precisa ser **primo**. Módulo com número composto agrupa chaves e piora a taxa de
colisão sem motivo. E nunca deixe NB fixo no código — calcule a partir do NR real *(correção C7)*.

---

## HU05 — Implementar função hash
`Onda 2` · `rubrica: critério 5 (1,0 pt, explicar código)`

> Como usuário, quero que o índice utilize uma função hash definida pela equipe, para mapear chaves
> de busca em buckets.

**Regras:** RN10 (mapeia chave → endereço de bucket) · RN11 (projetada pela equipe)

**Tarefas**
- [ ] `core/hashing.py` → `fnv1a(key) -> int` — FNV-1a de 32 bits, implementação manual
- [ ] `bucket_address(key, nb) -> int` → `fnv1a(key) % nb`
- [ ] **Jamais usar `hash()` nativo** — é randomizado por execução via `PYTHONHASHSEED` e viola o RNF05
- [ ] Teste de determinismo em `scripts/smoke_test.py`: mesma chave → mesmo bucket em **duas execuções
      separadas do processo** (não só duas chamadas na mesma execução — isso não prova nada)

**Pronto quando**
- [ ] **CA11** — dada uma chave, o sistema retorna sempre o mesmo bucket
- [ ] **CA12** — o resultado está sempre no intervalo `[0, NB-1]`

**Depende de:** HU04
**Como explicar na banca:** XOR do byte com o acumulador, multiplicação pelo primo FNV, truncamento
em 32 bits pela máscara. Três operações, cinco linhas — dá para desenhar no quadro.

---

## HU06 — Construir o índice percorrendo as páginas
`Onda 2` · `rubrica: contribui para os critérios 2 e 7`

> Como usuário, quero que o sistema construa o índice percorrendo página por página, para simular o
> custo real de leitura.

**Regras:** RN12 (percorre páginas e registros) · RN13 (aplica hash, guarda chave + endereço da página)

**Tarefas**
- [ ] `core/index.py` → `build_index(table, fr, progress_cb=None)`
- [ ] Laço externo por `page_id`, chamando `table.read_page(page_id)` — **não** iterar o array direto
- [ ] Para cada chave: `bucket_address` → `insert(idx, key, page_id)`
- [ ] Cronometrar com `time.perf_counter()` e guardar em `HashIndex.build_time`
- [ ] Exibir o tempo de construção no painel de métricas
- [ ] `scripts/smoke_test.py` conferindo o CA13: soma das entradas de todos os buckets **e de todas as
      cadeias de overflow** == NR
- [ ] **`BuildWorker(QThread)`** — construção fora da thread da UI, emitindo progresso a cada N páginas
      (RNF01). Sem isso a janela congela por 1–3 s e parece travada na apresentação.

**Pronto quando**
- [ ] **CA13** — ao final, o índice contém todos os registros do arquivo
- [ ] **CA14** — o tempo de construção é exibido na interface

**Depende de:** HU03, HU04, HU05
**Armadilha:** percorrer `table.records` direto em vez de `read_page` é mais rápido e mais simples —
e destrói o RN12 e a medição de custo. O laço tem que ser por página.

---

# EPIC 3 — Tratamento de Colisões e Overflow

## HU07 — Resolver colisões
`Onda 3` · `rubrica: contribui para o critério 8`

> Como usuário, quero que o índice trate colisões, para que várias chaves no mesmo bucket sejam
> armazenadas corretamente.

**Regras:** RN14 (só conta colisão quando o bucket está cheio) · RN15 (algoritmo de resolução)

**Tarefas**
- [ ] `core/index.py` → `Bucket(entries, overflow)` com `is_full(fr)`
- [ ] `insert()` — se o bucket tem espaço, apenas anexa; **nada é contado**
- [ ] Incrementar `collisions` **exclusivamente** quando a inserção chega num bucket já cheio
- [ ] Teste no smoke test: inserir 5 chaves num bucket com FR=32 e conferir `collisions == 0`

**Pronto quando**
- [ ] **CA15** — registros são inseridos mesmo quando múltiplas chaves geram o mesmo bucket
- [ ] **CA16** — o sistema contabiliza as colisões que excedem o tamanho do bucket

**Depende de:** HU06
**⚠ Armadilha que vale 0,5 ponto:** a RN14 é contraintuitiva. Colisão **não** é "duas chaves no mesmo
bucket". É **inserção em bucket que já atingiu FR**. Duas chaves caindo no bucket 42 com FR=32 e apenas
5 ocupantes **não** contam como colisão. Contar errado é o erro mais comum neste trabalho.

---

## HU08 — Resolver overflow de buckets
`Onda 3` · `rubrica: contribui para o critério 9`

> Como usuário, quero que o índice trate overflow, para garantir que registros adicionais sejam
> armazenados quando um bucket exceder FR.

**Regras:** RN16 (considerar overflow) · RN17 (algoritmo de resolução)

**Tarefas**
- [ ] Estratégia: **encadeamento** — lista ligada de buckets de overflow a partir do bucket base
- [ ] `insert()` percorre a cadeia até achar espaço, criando um novo nó quando necessário
- [ ] **Dois contadores separados** *(correção C1)*:
      - `buckets_with_overflow` — incrementa **só** na criação do **primeiro** nó de um bucket base;
        é este que alimenta a taxa do RN25
      - `overflow_nodes` — total de nós alocados na estrutura inteira; informação complementar
- [ ] Teste no smoke test: um bucket base com 3 nós encadeados soma **1** em `buckets_with_overflow`
      e **3** em `overflow_nodes`

**Pronto quando**
- [ ] **CA17** — quando FR é excedido, a estratégia de overflow entra em ação
- [ ] **CA18** — o sistema contabiliza quantos buckets entraram em overflow

**Depende de:** HU07
**Por que encadeamento e não endereçamento aberto:** o custo de leitura fica explícito (cada nó
visitado é +1 acesso ao índice) e é trivial de desenhar na interface — uma cadeia visível ao lado do
bucket base. Ambos os argumentos são defensáveis na apresentação.
**⚠ Correção C1:** confundir "nós criados" com "buckets que entraram em overflow" faz a taxa
`overflow / NB` inflar e até ultrapassar 100%, o que a banca vai notar.

---

# EPIC 6 — Estatísticas e Métricas

## HU12 — Calcular taxa de colisões
`Onda 4` · `rubrica: critério 8 (0,5 pt)`

> Como usuário, quero visualizar a taxa de colisões, para avaliar a qualidade da função hash e do NB.

**Regras:** RN24 (calcular e exibir a taxa em %)

**Tarefas**
- [ ] `core/metrics.py` → `IndexStats.collision_rate` = `collisions / nr * 100`, protegido contra NR = 0
- [ ] Exibir no painel de métricas, formatado com uma casa decimal e o símbolo `%`

**Pronto quando**
- [ ] **CA25** — o percentual de colisões aparece na interface após construir o índice

**Depende de:** HU07

---

## HU13 — Calcular taxa de overflow
`Onda 4` · `rubrica: critério 9 (0,5 pt)`

> Como usuário, quero visualizar a taxa de overflow, para avaliar se FR e NB foram bem dimensionados.

**Regras:** RN25 (calcular e exibir a taxa em %)

**Tarefas**
- [ ] `IndexStats.overflow_rate` = `buckets_with_overflow / nb * 100` — usando o contador certo *(C1)*
- [ ] Exibir no painel de métricas, junto da taxa de colisões
- [ ] *(opcional, rende pontos de apresentação)* mostrar também `overflow_nodes` como
      "nós de overflow alocados"

**Pronto quando**
- [ ] **CA26** — o percentual de overflow aparece na interface após construir o índice

**Depende de:** HU08
**Referência:** com fator de carga em 0,80, a taxa de overflow fica visível na demonstração — prova
que o algoritmo funciona de verdade — sem degradar a busca.

---

# EPIC 4 — Pesquisa por Índice

## HU09 — Buscar uma chave usando o índice
`Onda 5` · `rubrica: critério 7 (2,0 pts, explicar código) — a maior nota isolada do trabalho`

> Como usuário, quero digitar uma chave e executar a busca via índice, para localizar rapidamente o
> registro e sua página.

**Regras:** RN18 (campo para a chave) · RN19 (hash → bucket → endereço da página → ler a página)

**Tarefas**
- [ ] `core/search.py` → `SearchResult(found, key, page_id, index_reads, data_reads, elapsed,
      visited_buckets, sample_records)`
- [ ] `index_search(table, idx, key)` seguindo exatamente os 4 passos do RN19
- [ ] `table.reset_counter()` no início, `time.perf_counter()` em volta
- [ ] Contar `index_reads` (buckets e nós de overflow visitados) e `data_reads` (páginas lidas)
      **separadamente**, e exibir os dois além do total
- [ ] **Registrar a cadeia inteira** em `visited_buckets`, não só o endereço inicial *(correção C6)* —
      é o que alimenta o destaque do CA29
- [ ] Ao achar a chave no bucket, ler a página e **verificar**; se a chave não estiver lá, é bug de
      construção — sinalizar a inconsistência explicitamente em vez de devolver "não encontrada"
      silenciosamente *(correção C2)*
- [ ] `ui/panels.py` → campo de texto para a chave + botão "Buscar por índice"
- [ ] Aplicar **apenas `strip()`** na chave digitada — **sem conversão de caixa**. O arquivo tem 4
      pares que diferem só pela caixa (`as`/`As`, `dino`/`Dino`, `the`/`The`, `to`/`To`); normalizar
      violaria a RN02. Ver §Decisões pendentes.
- [ ] **`ui/widgets.py` → `BucketGrid`**: buckets coloridos por ocupação; clicar abre o detalhe com
      chaves, páginas e a cadeia de overflow (isso entrega o **CA28** da HU14)
- [ ] **Destaque visual (CA29 da HU14)**: pintar o bucket visitado no `BucketGrid` e a página acessada
      no `PageView` durante a busca

**Pronto quando**
- [ ] **CA19** — a interface mostra se a chave foi encontrada, em qual página está, e o custo estimado
      em leituras de página
- [ ] **CA20** — chave inexistente resulta em "não encontrada"

**Depende de:** HU06, HU08
**⚠ Não deixe o destaque visual para o final.** O CA29 é o item de interface mais visível na banca e o
que mais frequentemente fica sem tempo. Ele nasce aqui, junto com a busca.
**Como explicar na banca:** custo total = `index_reads` + `data_reads`. Reportar os dois separados
demonstra domínio do conceito e é exatamente o que o critério 11 avalia.

---

# EPIC 5 — Table Scan e Comparação

## HU10 — Executar table scan até encontrar a chave
`Onda 6` · `rubrica: critério 10 (0,5 pt)`

> Como usuário, quero executar um table scan após informar uma chave, para comparar a busca indexada
> com a sequencial.

**Regras:** RN20 (botão habilitado após digitar a chave) · RN21 (lista os registros lidos, página por página)

**Tarefas**
- [ ] `core/search.py` → `table_scan(table, key, sample_size=200)`
- [ ] Usar **o mesmo `read_page()`** da busca indexada — senão a comparação de tempo vira ficção
- [ ] Guardar os registros lidos em `collections.deque(maxlen=200)` e devolver como `sample_records`
      *(correção C3 — a versão original acumulava centenas de milhares de strings numa lista que nunca
      era usada)*
- [ ] Botão "Table scan" desabilitado enquanto o campo de chave estiver vazio
- [ ] Exibir os registros lidos numa lista **limitada aos últimos ~200 antes do acerto**
- [ ] Medir: se o scan de uma palavra inexistente passar de ~2 s, rodar também em `QThread`

**Pronto quando**
- [ ] **CA21** — o sistema exibe os registros lidos durante o scan
- [ ] **CA22** — informa o número da página onde encontrou e o custo em páginas lidas

**Depende de:** HU03, HU09
**⚠ Armadilha:** jogar os 466 mil registros na tela congela a UI no meio da apresentação. O CA21 pede
que os registros lidos sejam exibidos, não que **todos** sejam exibidos de uma vez.

---

## HU11 — Comparar tempo e custo entre índice e scan
`Onda 6` · `rubrica: critério 11 (0,5 pt)`

> Como usuário, quero ver a diferença de tempo e custo entre índice e scan, para entender o ganho real
> de usar índice.

**Regras:** RN22 (diferença de tempo) · RN23 (custo estimado em acessos a disco)

**Tarefas**
- [ ] `core/metrics.py` → `compare(index_result, scan_result)` devolvendo diferença de custo em %,
      diferença de tempo absoluta e o fator de aceleração
- [ ] Painel comparativo lado a lado: linha do índice, linha do scan, linha do ganho
- [ ] Diferença percentual = `(custo_scan − custo_índice) / custo_scan × 100`
- [ ] Formatar tempos em ms com casas decimais suficientes — a busca indexada fica na casa dos
      microssegundos e arredondar para zero estraga a demonstração

**Pronto quando**
- [ ] **CA23** — a interface exibe o tempo de execução da busca com índice **e** do table scan
- [ ] **CA24** — exibe o custo estimado de ambos e a diferença percentual

**Depende de:** HU09, HU10

---

# EPIC 7 — Interface Gráfica e Visualização

## HU14 — Visualizar estruturas e funcionamento
`transversal, consolidada na Onda 7` · `rubrica: critério 1 (1,0 pt)`

> Como usuário, quero uma interface gráfica que mostre as estruturas e o funcionamento do índice,
> para entender visualmente como páginas, buckets e buscas funcionam.

**Regras:** RN26 (interface gráfica obrigatória) · RN27 (ilustrar páginas, buckets, processo de busca
e localização do registro)

Esta HU não é implementada de uma vez — cada critério nasce junto da história correspondente:

| Critério | Onde nasce | O quê |
|---|---|---|
| RN26 / RNF04 | Onda 0 | Janela única, sem terminal, sem popups de mensagem |
| **CA27** | HU03 | Primeira e última página visíveis |
| **CA28** | HU09 | Buckets e seus conteúdos visíveis, com detalhe ao clicar |
| **CA29** | HU09 | Bucket e página destacados durante a busca |

**Tarefas de consolidação (Onda 7)**
- [ ] Revisar o layout completo: quatro regiões coerentes, nada cortado ao redimensionar
- [ ] Desabilitar botões durante operações em andamento
- [ ] `QProgressBar` durante a construção do índice
- [ ] Varredura final por `QMessageBox` e `print()` esquecidos no código (RNF04)
- [ ] Tratamento de erro para busca acionada antes de o índice existir

**Pronto quando**
- [ ] **CA27** — o usuário consegue ver a primeira e a última página
- [ ] **CA28** — o usuário consegue ver os buckets e seus conteúdos
- [ ] **CA29** — durante a busca, o bucket e a página acessados são destacados

**⚠ Risco R2 — decidir antes de escrever o `BucketGrid`:** com NB ≈ 18 mil, criar um widget por bucket
trava a interface. Duas saídas viáveis: `QTableWidget` com faixa navegável (ex.: 500 buckets por vez)
ou um `QWidget` único com `paintEvent` desenhando os retângulos. Escolher **antes** de começar a HU09.

---

# Requisitos não funcionais — onde cada um é atendido

| RNF | Exigência | Atendido em |
|---|---|---|
| RNF01 | Suportar 466.000 registros sem travar | HU03 (array plano) + HU06 (`QThread`) + HU10 |
| RNF02 | Exibir o tempo de construção do índice | HU06 |
| RNF03 | Qualquer linguagem | Onda 0 — Python 3.11+ |
| RNF04 | Interface visual, sem terminal e sem popups | Onda 0 + HU14 |
| RNF05 | Determinismo: mesma chave → mesmo índice | HU05 (`fnv1a` manual, nunca `hash()`) |

---

# Validação contínua — `scripts/smoke_test.py`

Um único script, ampliado a cada onda, que valida o núcleo sem depender da interface:

| Onda | Passa a verificar |
|---|---|
| 1 | `load_words` devolve **exatamente 466.550** registros; `num_pages` bate com `ceil(NR / TP)`; `read_page` incrementa o contador |
| 2 | NB é primo e > NR/FR; `bucket_address` sempre em `[0, NB-1]`; **CA13** (total de entradas == NR) |
| 3 | Bucket com 5 de 32 ocupados não conta colisão; cadeia de 3 nós → `buckets_with_overflow == 1` |
| 5 | 10 palavras conhecidas encontradas na página correta; 2 inexistentes retornam não encontrada |
| 6 | `table_scan` e `index_search` concordam sobre a página de cada chave testada |

**Determinismo (RNF05):** rodar o script **duas vezes em processos separados** e comparar o bucket de
uma chave fixa. Duas chamadas na mesma execução não provam nada — o `PYTHONHASHSEED` só muda entre
processos.

---

# Correções pendentes na especificação técnica

Já distribuídas nas HUs acima; consolidadas aqui para conferência.

| # | Problema em `especificacao_indice_hash.md` | Onde corrigir |
|---|---|---|
| C1 | `overflow_buckets` conta nós criados, mas CA18/RN25 pedem buckets que entraram em overflow — a taxa infla e pode passar de 100% | HU08, HU13 |
| C2 | `index_search` devolve `found=key in records` já tendo achado a chave no bucket, mascarando inconsistência de construção | HU09 |
| C3 | `table_scan` acumula todos os registros lidos numa lista que nunca é usada | HU10 |
| C4 | `assert` em `compute_nb` desaparece com `python -O`, e o CA10 é avaliado | HU04 |
| C5 | `compute_nb` usa `math.ceil` sem `import math` no trecho de `hashing.py` | HU04 |
| C6 | `visited_buckets` guarda só o endereço inicial, não a cadeia percorrida | HU09 |
| C7 | Números de referência (NR = 466.550 → NB = 18.229) assumem um arquivo específico | HU04 |

---

# Riscos

| # | Risco | Mitigação |
|---|---|---|
| R1 | Python não instalado → nada roda | Onda 0.1, antes de tudo |
| R2 | Renderizar ~18 mil células trava a UI | Decidir a estratégia do `BucketGrid` antes da HU09 — ver HU14 |
| R3 | CA29 deixado para o fim | Está dentro da HU09, não no acabamento |
| ~~R4~~ | ~~Base de dados ausente na apresentação~~ | ✅ **eliminado** — `data/words.txt` está versionado |
| R5 | Scan de palavra inexistente demora | Medir na HU10; passar para `QThread` se passar de ~2 s |
| R6 | Usar `dict` "por conveniência" em algum ponto do índice | O índice é `list[Bucket]`, ponto. `dict` elimina colisão e overflow do problema e derruba os critérios 5 a 9 (3,5 pts) |

---

# Decisões pendentes da equipe

1. ✅ **Arquivo de dados** — resolvido: `words.txt`, 466.550 registros, batendo exatamente com o
   enunciado e com os valores de referência da especificação (NB = 18.229 para FR = 32).
2. ✅ **Versionar o TXT** — resolvido: `data/words.txt` está no repositório. Risco R4 eliminado.
3. ✅ **Busca sensível a maiúsculas** — resolvido: **sim, sensível**. Ver a análise abaixo.
4. **FR fixo ou configurável?** RN09 deixa a critério da equipe. Recomendação: campo na UI com padrão
   32 — permite demonstrar ao vivo o efeito de FR na taxa de colisões.
5. **Divisão das HUs entre os integrantes** — ver quadro abaixo.

### Por que a busca é sensível a maiúsculas

A recomendação anterior era normalizar a entrada para minúsculas. **A análise do arquivo real
derrubou essa ideia.** O `words.txt` contém 4 pares que só diferem pela caixa das letras:

```
as / As      dino / Dino      the / The      to / To
```

Normalizar para minúsculas transformaria esses 4 pares em chaves duplicadas, violando a **RN02**
("cada palavra do arquivo deve ser considerada uma chave única") e tornando o **CA13** ambíguo — o
índice teria 466.550 entradas para 466.546 chaves distintas.

**Decisão:** a chave é armazenada e comparada exatamente como aparece no arquivo. Na HU09, a entrada
do usuário recebe apenas `strip()`, **nunca** conversão de caixa. Buscar `zwolle` retorna "não
encontrada" e isso está correto — a chave existente é `Zwolle`.

**Na apresentação:** vale mencionar que 27% do arquivo (125.427 linhas) não é composto só de letras
minúsculas — há números (`1080`), hífens (`10-point`), símbolos (`&c`) e siglas (`ZZZ`). A função
hash opera sobre os bytes UTF-8, então nada disso a afeta.

---

# Divisão da equipe e preparação da apresentação

Cinco critérios (**5,5 pts**) exigem **explicar o código-fonte**. Cada integrante precisa dominar pelo
menos dois blocos.

| Bloco a explicar | HU | Arquivo / função | Pontos | Responsável |
|---|---|---|---|---|
| Carga de dados nas páginas | HU01, HU03 | `storage.py` → `load_words`, `Table` | 1,5 | |
| Entrada do tamanho da página | HU02 | `ui/panels.py` → validação | 1,0 | |
| Cálculo da quantidade de páginas | HU03 | `Table.num_pages` | 1,0 | |
| Construção e uso da função hash | HU05 | `hashing.py` → `fnv1a`, `bucket_address` | 1,0 | |
| Cálculo da quantidade de buckets | HU04 | `hashing.py` → `compute_nb` | 0,5 | |
| Pesquisa com uso do índice | HU09 | `search.py` → `index_search` | 2,0 | |

- [ ] Preencher a coluna "Responsável"
- [ ] Roteiro de demonstração: carregar → configurar → construir → buscar chave existente → buscar
      chave inexistente → table scan → comparativo
- [ ] Ensaiar com o arquivo completo, nunca com amostra reduzida
- [ ] Decorar as chaves de teste (já levantadas do `words.txt` — detalhes em `data/README.md`):

| Posição | Chave | Demonstra |
|---|---|---|
| Início | `2` | Índice e scan custam quase o mesmo |
| Meio | `hash` | Caso intermediário |
| Fim | `ZZZ` | O scan lê o arquivo inteiro — ganho do índice fica dramático |
| Inexistente | `xyzzyplugh` | CA20 e o pior caso do scan |

---

# Checklist da rubrica (10,0 pontos)

| ✓ | Pts | Critério | HU |
|---|---|---|---|
| [ ] | 1,0 | Interface gráfica funcional, sem terminal, sem popups | HU14 |
| [ ] | 1,5 | Carga de dados nas páginas *(explicar código)* | HU01, HU03 |
| [ ] | 1,0 | Campo de entrada para tamanho da página *(explicar código)* | HU02 |
| [ ] | 1,0 | Cálculo da quantidade de páginas *(explicar código)* | HU03 |
| [ ] | 1,0 | Construção e uso da função hash *(explicar código)* | HU05 |
| [ ] | 0,5 | Cálculo da quantidade de buckets *(explicar código)* | HU04 |
| [ ] | 2,0 | Pesquisa com uso do índice *(explicar código)* | HU09 |
| [ ] | 0,5 | Taxa de colisões calculada e exibida | HU12 |
| [ ] | 0,5 | Taxa de overflows calculada e exibida | HU13 |
| [ ] | 0,5 | Execução do table scan | HU10 |
| [ ] | 0,5 | Estimativa de custo e comparativo de tempo índice × scan | HU11 |

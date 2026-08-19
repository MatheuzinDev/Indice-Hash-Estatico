# Registro de Alterações

Toda alteração feita pelo assistente neste projeto é anotada aqui, em ordem cronológica
(mais recente por último).

**Regra do projeto:** nunca executar `git add` nem `git commit` sem pedido explícito do usuário —
sempre perguntar antes.

---

## 2026-08-19

### Criado `PLANO_IMPLEMENTACAO.md`
Plano de execução do trabalho, montado a partir da leitura do
`26.2 - Projeto 1 - Índice HASH.pdf` e do `especificacao_indice_hash.md`.

Conteúdo: situação atual do repositório, Etapa 0 (ambiente) a Etapa 5 (apresentação) com
critérios de saída, lista de correções a aplicar na especificação técnica (C1–C7), riscos
(R1–R6), decisões pendentes da equipe, tabela de rastreabilidade requisito → local e o
checklist da rubrica.

Verificações feitas durante a análise:
- `words_alpha.txt` **não está** no projeto.
- Python **não está instalado** na máquina (apenas o atalho da Microsoft Store em
  `%LOCALAPPDATA%\Microsoft\WindowsApps`).
- A pasta **não é** um repositório git.

### Criado `REGISTRO_DE_ALTERACOES.md`
Este arquivo.

---

## 2026-08-19 — Preparação do repositório para o GitHub

### `git init`
Repositório inicializado com a branch padrão `main`. **Nenhum `git add` ou `git commit` foi
executado** — aguardando autorização do usuário.

Pendência detectada: `git config user.name` e `user.email` **não estão configurados** na máquina.
Precisam ser definidos antes do primeiro commit.

### Estrutura de pastas criada
`core/`, `ui/`, `data/`, `docs/`, `scripts/` — conforme a arquitetura definida em
`especificacao_indice_hash.md`.

### Documentação movida para `docs/`
Os quatro arquivos de documentação saíram da raiz e foram para `docs/`:
- `26.2 - Projeto 1 - Índice HASH.pdf`
- `especificacao_indice_hash.md`
- `PLANO_IMPLEMENTACAO.md`
- `REGISTRO_DE_ALTERACOES.md`

Motivo: deixar a raiz com o código e os arquivos de projeto, padrão esperado num repositório
público. O `README.md` aponta para todos eles.

### Criado `README.md`
Descrição do projeto, requisitos, instruções de instalação e execução, árvore de diretórios
comentada, índice da documentação e tabela da equipe (a preencher).

### Criado `.gitignore`
Ignora `.venv/`, `__pycache__/`, caches de ferramentas, arquivos de editor, arquivos de sistema
e **`data/*.txt`** — a base de palavras não é versionada.

### Criado `requirements.txt`
Dependência única: `PySide6>=6.6`.

### Criado `data/README.md`
Instruções de download da base (PowerShell e Bash), comparação entre `words_alpha.txt` (~370 mil)
e `words.txt` (~466 mil), e o formato esperado do arquivo.

### Criados `core/__init__.py` e `ui/__init__.py`
Docstrings apenas, marcando os pacotes. `core/__init__.py` registra a regra de que o núcleo não
importa PySide6.

### Criado `scripts/.gitkeep`
Mantém a pasta no versionamento enquanto ela está vazia.

### Reescrito `docs/PLANO_IMPLEMENTACAO.md` — agora organizado por história de usuário
A estrutura anterior era por etapas técnicas (núcleo → interface → acabamento). Foi substituída por
uma organização por **HU01 a HU14**, com entrega vertical: cada história inclui núcleo, interface e
validação, e só é dada como pronta quando todos os seus critérios de aceitação estão demonstráveis
na tela.

Mudanças principais:
- Ondas de entrega (0 a 7) agrupando as HUs por EPIC em ordem de dependência.
- Cada HU traz: a narrativa da história, as regras de negócio, as tarefas, os critérios de aceitação
  como checklist de "pronto quando", as dependências, e as armadilhas específicas.
- Nota da rubrica atribuída a cada HU.
- As correções C1–C7 foram distribuídas nas HUs onde precisam ser aplicadas, e mantidas numa tabela
  consolidada ao final.
- `HU14` marcada como transversal, com um quadro mostrando em qual HU cada critério dela nasce
  (CA27 na HU03, CA28 e CA29 na HU09).
- Nova seção de validação contínua descrevendo o que `scripts/smoke_test.py` passa a verificar a
  cada onda.
- A tabela de rastreabilidade genérica foi substituída pelo mapeamento requisito → HU, que já está
  embutido em cada história.

---

## 2026-08-19 — Base de dados incorporada ao repositório

### `words.txt` movido da raiz para `data/words.txt`
Arquivo colocado na raiz pelo usuário, realocado conforme a estrutura definida.

### `.gitignore` ajustado para versionar a base
A regra `data/*.txt` continua valendo, com a exceção `!data/words.txt`. Assim a base oficial entra no
repositório e qualquer outro TXT que a equipe deixe em `data/` fica de fora. Regras conferidas com
`git check-ignore`.

### Análise do arquivo — três achados que afetam o plano

| Verificação | Resultado |
|---|---|
| Registros | **466.550** — bate exatamente com o enunciado e com os valores de referência da especificação (NB = 18.229 para FR = 32) |
| Linhas vazias | 0 |
| Chaves duplicadas exatas | 0 — RN02 satisfeito |
| Duplicatas ignorando caixa | **4** — `as`/`As`, `dino`/`Dino`, `the`/`The`, `to`/`To` |
| Linhas não puramente minúsculas | 125.427 (27%) — números, hífens, símbolos, siglas |

### Decisão revertida: a busca passa a ser **sensível a maiúsculas**
O plano recomendava normalizar a chave digitada para minúsculas. A análise do arquivo real derrubou
essa recomendação: os 4 pares que diferem só pela caixa virariam chaves duplicadas, violando a RN02 e
tornando o CA13 ambíguo (466.550 entradas para 466.546 chaves distintas).

Passa a valer: a chave é armazenada e comparada exatamente como está no arquivo, e a entrada do
usuário recebe apenas `strip()`.

### Documentos atualizados
- **`data/README.md`** — reescrito: caracterização do arquivo em uso, alerta sobre a sensibilidade a
  maiúsculas com a justificativa pela RN02, tabela de chaves sugeridas para a demonstração
  (`2`, `hash`, `ZZZ`, `xyzzyplugh`) e instruções para trocar de arquivo.
- **`README.md`** — a seção de base de dados deixou de mandar baixar o arquivo; a árvore de
  diretórios agora mostra `data/words.txt`.
- **`docs/PLANO_IMPLEMENTACAO.md`**:
  - Situação atual: base marcada como presente, com NR = 466.550.
  - Onda 0: item 0.3 (baixar a base) marcado como concluído.
  - HU09: tarefa de normalização trocada por "apenas `strip()`, sem conversão de caixa", com a
    justificativa.
  - Decisões pendentes: itens 1, 2 e 3 resolvidos, com uma seção nova explicando a análise que levou
    à sensibilidade a maiúsculas.
  - Risco R4 (base ausente na apresentação) marcado como eliminado.
  - Validação contínua: a Onda 1 passa a conferir o número exato de 466.550 registros.
  - Preparação da apresentação: as chaves de teste deixaram de ser genéricas e viraram uma tabela
    com as palavras reais do arquivo.

**Nenhum `git add` ou `git commit` foi executado.**

---

## Arquivos não modificados

`26.2 - Projeto 1 - Índice HASH.pdf` e `especificacao_indice_hash.md` tiveram apenas a localização
alterada (raiz → `docs/`). O conteúdo dos dois permanece intacto.

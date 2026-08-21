# Índice Hash Estático

Simulador de um **índice hash estático** sobre uma tabela dividida em páginas, com interface
gráfica, tratamento de colisões e overflow, e comparação entre busca indexada e *table scan*.

Trabalho da AV1 de Banco de Dados — Universidade de Fortaleza.

---

## O que o sistema faz

- Carrega um arquivo TXT com uma palavra única por linha (a palavra é a chave de busca)
- Divide os registros em páginas de tamanho definido pelo usuário
- Constrói um índice hash estático com `NB` buckets de capacidade `FR`, percorrendo página por página
- Trata colisões e transbordamento (*bucket overflow*) por encadeamento
- Busca uma chave pelo índice e informa página, custo em acessos e tempo
- Executa *table scan* sequencial para comparação
- Exibe taxa de colisões, taxa de overflow e o comparativo de custo e tempo entre as duas buscas

---

## Requisitos

- Python 3.11 ou superior
- PySide6 (única dependência externa)

---

## Instalação

```powershell
git clone <URL-DO-REPOSITORIO>
cd projeto-banco-dados-av1

python -m venv .venv
.venv\Scripts\Activate.ps1        # Linux/macOS: source .venv/bin/activate

pip install -r requirements.txt
```

### Base de dados

O arquivo `data/words.txt` (466.550 registros) **já vem no repositório** — não é preciso baixar nada.
Detalhes sobre o conteúdo e a sensibilidade a maiúsculas na busca em
[`data/README.md`](data/README.md).

---

## Execução

```powershell
python main.py
```

---

## Estrutura do projeto

```
projeto-banco-dados-av1/
├── main.py                      # ponto de entrada
├── core/                        # lógica pura — não importa PySide6
│   ├── erros.py                 # exceções e mensagens de erro
│   ├── funcao_hash.py           # função hash FNV-1a e cálculo de NB
│   ├── armazenamento.py         # tabela, paginação e contador de acessos
│   ├── indice.py                # Bucket, overflow e construção do índice
│   ├── busca.py                 # busca indexada e table scan
│   └── metricas.py              # estatísticas e comparativos
├── ui/                          # interface gráfica
│   ├── janela_principal.py
│   ├── paineis.py
│   └── componentes.py
└── data/words.txt               # base de dados (466.550 registros)
```

**Regra de separação:** nada em `core/` importa PySide6. Isso mantém o núcleo testável por script
e a explicação do código na apresentação organizada.

**Idioma do código:** todo o código é escrito em português — módulos, classes, funções, variáveis e
comentários. As exceções são os termos do glossário do enunciado (`bucket`, `overflow`, `hash`,
`table_scan`), as siglas oficiais (`nr`, `nb`, `fr`, `tp`) e a API do PySide6. O glossário completo de
nomes está no plano de implementação da equipe.

---

## Documentação

A documentação de planejamento fica na pasta `docs/`, que **não é versionada** — é material interno da
equipe e circula fora do repositório:

| Documento | Conteúdo |
|---|---|
| `docs/26.2 - Projeto 1 - Índice HASH.pdf` | Enunciado oficial com as histórias de usuário |
| `docs/especificacao_indice_hash.md` | Decisões técnicas da equipe |
| `docs/PLANO_IMPLEMENTACAO.md` | Plano geral por história de usuário, com as convenções de nomenclatura |
| `docs/plans/` | Plano detalhado de cada história, escrito sob demanda |
| `docs/REGISTRO_DE_ALTERACOES.md` | Histórico de alterações |

---

## Equipe

| Nome | Matrícula |
|---|---|
| Matheus Diógenes | 2310277 |
| Guilherme Garcia | 2310255 |
| Matheus Holanda | 2320306 |
| Taís Moreira | 2320471 |

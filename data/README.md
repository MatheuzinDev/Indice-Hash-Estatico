# Base de dados

## `words.txt` — arquivo em uso

**Versionado no repositório.** Quem clonar já tem tudo pronto para rodar, sem download.

| Característica | Valor |
|---|---|
| Origem | [dwyl/english-words](https://github.com/dwyl/english-words) |
| Tamanho | 4,9 MB |
| Registros (NR) | **466.550** |
| Linhas vazias | 0 |
| Chaves duplicadas | 0 — RN02 satisfeito |

O total de 466.550 registros bate exatamente com o número citado no enunciado e com os valores de
referência da `especificacao_indice_hash.md` (NB = 18.229 para FR = 32).

---

## Formato e conteúdo

- Uma entrada por linha (RN01)
- Cada entrada é única no arquivo e serve como chave de busca (RN02)
- Codificação UTF-8

O arquivo **não contém apenas palavras minúsculas**. Ele inclui:

- números: `2`, `1080`, `10th`
- entradas com hífen: `10-point`
- abreviações com símbolo: `&c`
- nomes próprios e siglas em maiúsculas: `Zwolle`, `Zworykin`, `ZZ`, `zZt`, `ZZZ`

Cerca de **125.427 linhas (27%)** não são compostas apenas por letras minúsculas. Isso não é problema
para o índice — a função hash opera sobre os bytes UTF-8 de qualquer string.

---

## ⚠ A busca é sensível a maiúsculas

Existem **4 pares** que só diferem pela caixa das letras: `as`/`As`, `dino`/`Dino`, `the`/`The`,
`to`/`To`.

Por isso a chave é armazenada e comparada **exatamente como aparece no arquivo**. Normalizar tudo para
minúsculas transformaria esses 4 pares em chaves duplicadas e violaria a RN02 ("cada palavra é uma
chave única").

**Consequência prática:** ao digitar a chave na interface, respeite a caixa. Buscar `Zwolle` encontra;
buscar `zwolle` retorna "não encontrada" — e está correto, porque `zwolle` de fato não existe no
arquivo. A interface aplica apenas `strip()` na entrada, nunca conversão de caixa.

---

## Palavras sugeridas para a demonstração

| Posição no arquivo | Chave | Serve para |
|---|---|---|
| Início | `2` | Índice e scan custam quase o mesmo — o scan acha logo |
| Meio | `hash` | Caso intermediário |
| Fim | `ZZZ` | O scan lê o arquivo inteiro — o ganho do índice fica dramático |
| Inexistente | `xyzzyplugh` | Demonstra o CA20 e o pior caso do scan |

---

## Usar outro arquivo

Nada no código depende do nome ou do tamanho do arquivo — basta selecionar outro `.txt` pela
interface. O `.gitignore` versiona apenas `data/words.txt`; qualquer outro TXT colocado em `data/`
fica fora do repositório.

Alternativa conhecida do mesmo repositório de origem:

```powershell
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/dwyl/english-words/master/words_alpha.txt" -OutFile "data\words_alpha.txt"
```

`words_alpha.txt` tem ~370 mil entradas, apenas alfabéticas e todas minúsculas — mais limpo, porém
não bate com os 466 mil citados no enunciado.

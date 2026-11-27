# MiniLang: Definição Formal

Este documento define formalmente a linguagem MiniLang: alfabeto, gramática EBNF,
precedência e associatividade, programas de exemplo comentados e a especificação
do analisador léxico (tabela de tokens e tabela de transições do autômato).

---

## 1. Alfabeto (tokens)

O alfabeto da gramática sintática é o conjunto de **tokens** produzidos pelo lexer.
Cada token é uma classe de lexemas.

| Categoria | Tokens |
|-----------|--------|
| Literais | `INT` (inteiros não negativos), `TRUE`, `FALSE` |
| Identificador | `ID` |
| Palavras reservadas | `IF`, `ELSE`, `WHILE`, `FOR`, `PRINT` (e `TRUE`, `FALSE`) |
| Aritméticos | `PLUS` (`+`), `MINUS` (`-`), `STAR` (`*`), `SLASH` (`/`) |
| Relacionais | `LT` (`<`), `GT` (`>`), `LE` (`<=`), `GE` (`>=`) |
| Igualdade | `EQ` (`==`), `NE` (`!=`) |
| Atribuição | `ASSIGN` (`=`) |
| Delimitadores | `LPAREN` (`(`), `RPAREN` (`)`), `LBRACE` (`{`), `RBRACE` (`}`), `SEMI` (`;`) |
| Fim de entrada | `EOF` |

Elementos **descartados** pelo lexer (não chegam ao parser): espaços, tabulações,
quebras de linha, comentários de linha `// ...` e comentários de bloco `/* ... */`.

O alfabeto de **caracteres** aceito no código-fonte (fora de comentários) é:
letras ASCII `a-z A-Z`, `_`, dígitos `0-9`, espaço, tabulação, `\r`, `\n` e os
símbolos `+ - * / < > = ! ( ) { } ;`. Qualquer outro caractere (ex.: `@`, `#`, `ç`)
é erro léxico. Dentro de comentários, qualquer caractere é aceito.

---

## 2. Gramática EBNF

Notação: `{ X }` = zero ou mais repetições; `[ X ]` = opcional; `|` = alternativa;
terminais entre aspas ou em MAIÚSCULAS (nomes de token).

```ebnf
(* ---------- Estrutura do programa ---------- *)
programa       = { comando } EOF ;

comando        = atribuicao ";"
               | print ";"
               | if
               | while
               | for
               | bloco ;

bloco          = "{" { comando } "}" ;

atribuicao     = ID "=" expressao ;

print          = "print" "(" expressao ")" ;

if             = "if" "(" expressao ")" bloco [ "else" bloco ] ;

while          = "while" "(" expressao ")" bloco ;

for            = "for" "(" atribuicao ";" expressao ";" atribuicao ")" bloco ;
(*                      inicialização    condição    atualização          *)
(* As três cláusulas são obrigatórias: não existe produção vazia para elas. *)

(* ---------- Expressões: um não terminal por nível de precedência ---------- *)
(* Do MENOS prioritário (topo) para o MAIS prioritário (base).               *)

expressao      = igualdade ;

igualdade      = relacional [ ( "==" | "!=" ) relacional ] ;          (* não associativo *)

relacional     = aditiva [ ( "<" | ">" | "<=" | ">=" ) aditiva ] ;     (* não associativo *)

aditiva        = multiplicativa { ( "+" | "-" ) multiplicativa } ;     (* esquerda *)

multiplicativa = unaria { ( "*" | "/" ) unaria } ;                     (* esquerda *)

unaria         = "-" unaria
               | primaria ;                                            (* direita *)

primaria       = INT
               | "true"
               | "false"
               | ID
               | "(" expressao ")" ;
```

### Propriedades da gramática

1. **Sem recursão à esquerda.** Nenhuma produção começa com o próprio não terminal.
   As repetições de operadores usam `{ ... }`, o que permite análise descendente recursiva.
2. **LL(1).** Em toda escolha entre alternativas, o primeiro token decide a produção:
   - `comando`: FIRST(atribuicao) = {ID}, FIRST(print) = {print}, FIRST(if) = {if},
     FIRST(while) = {while}, FIRST(for) = {for}, FIRST(bloco) = {`{`}. Conjuntos disjuntos.
   - `unaria`: `-` versus FIRST(primaria) = {INT, true, false, ID, `(`}. Disjuntos.
   - `primaria`: cinco alternativas com primeiros tokens distintos.
   - `if`: o `[ "else" bloco ]` é decidido olhando se o próximo token é `else`.
3. **Sem ambiguidade de `else` pendente** (dangling else): como o corpo do `if` é
   obrigatoriamente um `bloco` com chaves, `if (a) { if (b) { } } else { }` só tem uma árvore.

---

## 3. Precedência e associatividade

| Nível | Operadores | Associatividade | Produção | Exemplo e agrupamento |
|:-----:|------------|-----------------|----------|-----------------------|
| 1 (menor) | `==` `!=` | não associativo | `igualdade` | `a < b == true` = `(a < b) == true` |
| 2 | `<` `>` `<=` `>=` | não associativo | `relacional` | `x + 1 < y` = `(x + 1) < y` |
| 3 | `+` `-` (binários) | esquerda | `aditiva` | `1 - 2 - 3` = `(1 - 2) - 3` |
| 4 | `*` `/` | esquerda | `multiplicativa` | `8 / 4 / 2` = `(8 / 4) / 2` |
| 5 | `-` (unário) | direita | `unaria` | `--5` = `-(-5)` |
| 6 (maior) | `( )`, literais, variáveis | não se aplica | `primaria` | `(1 + 2) * 3` |

**Como a gramática impõe a precedência:** um operador de nível mais alto aparece
numa produção mais "profunda". Para derivar `1 + 2 * 3`, `aditiva` só enxerga
`multiplicativa` como operandos; logo `2 * 3` precisa ser derivado inteiro dentro
de uma `multiplicativa` antes de participar da soma.

**Como a gramática impõe a associatividade:**
- `{ ( "+" | "-" ) multiplicativa }` é implementado com um laço que sempre coloca o
  resultado acumulado como **filho esquerdo**: associatividade à esquerda.
- `unaria = "-" unaria` é recursiva à direita: associatividade à direita.
- `[ op relacional ]` permite **no máximo um** operador por nível. `1 < 2 < 3` não é
  derivável: comparações são não associativas (o encadeamento não tem significado
  útil numa linguagem com tipos `int` e `bool` separados).

---

## 4. Programas de exemplo comentados

### Exemplo 1: válido (usa while, for, if/else e precedência)

```
x = 10;
y = 2 * (x + 5);          // y = 30
while (x > 0) {
    x = x - 1;
}
soma = 0;
for (i = 0; i < 5; i = i + 1) {
    soma = soma + i;
}
if (soma > 20) { print(soma); } else { print(0); }   // imprime 0
```

**Justificativa:** todos os lexemas pertencem a tokens da seção 1; cada comando é
derivável de `comando` (atribuições terminadas em `;`, `while` e `for` com
parênteses e bloco, `for` com as três cláusulas, `if` com `else` opcional presente).
Semanticamente, toda variável é atribuída antes de ser lida, todas as condições
(`x > 0`, `i < 5`, `soma > 20`) são do tipo `bool` e não há divisão.

### Exemplo 2: inválido, erro léxico

```
x = 10;
y = x @ 2;
z = 3abc;
```

**Erro reportado:** `Erro léxico [linha 2, coluna 7]: caractere inválido '@'`

**Justificativa:** `@` não pertence ao alfabeto de caracteres da linguagem; a partir
do estado inicial q0, a classe `outro` não tem transição (seção 5.3), então o
autômato para em um estado de não aceitação. Se o `@` fosse removido, a linha 3
também seria rejeitada: `3abc` leva o autômato de q2 (inteiro) a q3 (número
malformado), que não é estado de aceitação, pois nenhuma expressão regular de token
descreve um dígito seguido de letra.

### Exemplo 3: inválido, erro sintático (laço for mal formado)

```
soma = 0;
for (i = 0; i < 10) {
    soma = soma + i;
}
```

**Erro reportado:** `Erro sintático [linha 2, coluna 19]: esperado ';' após a condição do for (o for exige as três cláusulas), encontrado ')'`

**Justificativa:** todos os tokens são válidos, mas a sequência não é derivável.
A produção `for = "for" "(" atribuicao ";" expressao ";" atribuicao ")" bloco` exige,
após a condição `i < 10`, o terminal `";"` seguido de uma `atribuicao`. O token
encontrado é `)`. Como não existe produção vazia para a atualização (cláusulas
vazias estão fora do escopo), não há derivação possível.

### Exemplo 4: inválido, erro semântico (condição não booleana em laço)

```
x = 5;
while (x) {
    x = x - 1;
}
```

**Erro reportado:** `Erro semântico [linha 2, coluna 8]: condição do while deve ser booleana, mas é do tipo int`

**Justificativa:** o programa é léxica e sintaticamente correto (`while "(" expressao ")" bloco`,
e `x` é uma `expressao` válida). A gramática livre de contexto não distingue tipos;
a restrição violada é semântica: a condição de `while`, `for` e `if` deve avaliar
para `bool`, e `x` vale `5` (`int`).

### Exemplo 5: inválido, erros semânticos (variável não definida e divisão por zero)

```
for (i = 0; j < 10; i = i + 1) {
    print(i);
}
```

**Erro reportado:** `Erro semântico [linha 1, coluna 13]: variável 'j' não definida`

```
a = 10;
b = a - 10;
print(a / b);
```

**Erro reportado:** `Erro semântico [linha 3, coluna 9]: divisão por zero`

**Justificativa:** ambos são sintaticamente válidos. No primeiro, a variável usada
na condição do laço (`j`) nunca foi inserida na tabela de símbolos: a restrição
"toda variável deve ser atribuída antes de ser lida" é violada. No segundo, o
divisor `b` só é conhecido em tempo de execução (vale `0`), o que mostra por que a
verificação semântica precisa ser feita durante a interpretação e não apenas
analisando o texto.

---

## 5. Lexer

### 5.1 Tabela de tokens

| Tipo | Padrão (expressão regular) | Exemplos |
|------|----------------------------|----------|
| `INT` | `[0-9]+` | `0`, `42`, `007` |
| `ID` | `[a-zA-Z_][a-zA-Z0-9_]*` (exceto palavras reservadas) | `x`, `soma`, `_tmp`, `whilex` |
| `IF` | `if` | `if` |
| `ELSE` | `else` | `else` |
| `WHILE` | `while` | `while` |
| `FOR` | `for` | `for` |
| `PRINT` | `print` | `print` |
| `TRUE` | `true` | `true` |
| `FALSE` | `false` | `false` |
| `PLUS` | `\+` | `+` |
| `MINUS` | `-` | `-` |
| `STAR` | `\*` | `*` |
| `SLASH` | `/` | `/` |
| `LT` | `<` | `<` |
| `GT` | `>` | `>` |
| `LE` | `<=` | `<=` |
| `GE` | `>=` | `>=` |
| `EQ` | `==` | `==` |
| `NE` | `!=` | `!=` |
| `ASSIGN` | `=` | `=` |
| `LPAREN` | `\(` | `(` |
| `RPAREN` | `\)` | `)` |
| `LBRACE` | `\{` | `{` |
| `RBRACE` | `\}` | `}` |
| `SEMI` | `;` | `;` |
| (descartado) espaço | `[ \t\r\n]+` | espaços e quebras de linha |
| (descartado) comentário de linha | `//[^\n]*` | `// comentário` |
| (descartado) comentário de bloco | `/\*([^*]|\*+[^*/])*\*+/` | `/* comentário */` |

**Regras de desempate:**
1. **Maior casamento:** o lexer consome o lexema mais longo possível. `<=` é um `LE`,
   não `LT` seguido de `ASSIGN`; `whilex` é um `ID`, não `WHILE` seguido de `x`.
2. **Prioridade das palavras reservadas:** se o lexema mais longo casa ao mesmo tempo
   com `ID` e com uma palavra reservada (ex.: `while`), vence a palavra reservada.

**Observação sobre negativos:** `INT` não inclui sinal. `-5` são dois tokens
(`MINUS`, `INT`), e o sinal é tratado pela produção `unaria` da gramática.

### 5.2 Alfabeto do autômato (classes de caracteres)

Para reduzir a tabela, caracteres com o mesmo comportamento em todos os estados
são agrupados em classes:

| Classe | Caracteres |
|--------|------------|
| L | `a-z`, `A-Z`, `_` |
| D | `0-9` |
| esp | espaço, `\t`, `\r` |
| `\n` | quebra de linha |
| `/` `*` `=` `<` `>` `!` `+` `-` `(` `)` `{` `}` `;` | o próprio caractere (uma classe cada) |
| outro | qualquer outro caractere |

### 5.3 Tabela de transições do AFD

Legenda: `→` estado inicial; `*` estado de aceitação; célula vazia = sem transição
(o autômato para e decide pelo estado atual).

| Estado | L | D | esp | \n | `/` | `*` | `=` | `<` | `>` | `!` | `+` | `-` | `(` | `)` | `{` | `}` | `;` | outro |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| →q0 | q1 | q2 | q4 | q4 | q5 | q20 | q14 | q10 | q12 | q16 | q18 | q19 | q21 | q22 | q23 | q24 | q25 |  |
| *q1 | q1 | q1 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| *q2 | q3 | q2 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| q3 | q3 | q3 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| *q4 |  |  | q4 | q4 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| *q5 |  |  |  |  | q6 | q7 |  |  |  |  |  |  |  |  |  |  |  |  |
| *q6 | q6 | q6 | q6 |  | q6 | q6 | q6 | q6 | q6 | q6 | q6 | q6 | q6 | q6 | q6 | q6 | q6 | q6 |
| q7 | q7 | q7 | q7 | q7 | q7 | q8 | q7 | q7 | q7 | q7 | q7 | q7 | q7 | q7 | q7 | q7 | q7 | q7 |
| q8 | q7 | q7 | q7 | q7 | q9 | q8 | q7 | q7 | q7 | q7 | q7 | q7 | q7 | q7 | q7 | q7 | q7 | q7 |
| *q9 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| *q10 |  |  |  |  |  |  | q11 |  |  |  |  |  |  |  |  |  |  |  |
| *q11 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| *q12 |  |  |  |  |  |  | q13 |  |  |  |  |  |  |  |  |  |  |  |
| *q13 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| *q14 |  |  |  |  |  |  | q15 |  |  |  |  |  |  |  |  |  |  |  |
| *q15 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| q16 |  |  |  |  |  |  | q17 |  |  |  |  |  |  |  |  |  |  |  |
| *q17 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| *q18 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| *q19 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| *q20 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| *q21 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| *q22 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| *q23 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| *q24 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| *q25 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

### 5.4 Estados: significado e decisão ao parar

| Estado | Nome no código | Significado | Ao parar |
|--------|----------------|-------------|----------|
| q0 | `INICIO` | nenhum caractere lido | erro: caractere inválido |
| q1 | `ID` | `[a-zA-Z_][a-zA-Z0-9_]*` | emite `ID` ou palavra reservada |
| q2 | `INT` | `[0-9]+` | emite `INT` |
| q3 | `NUM_MAL` | dígitos seguidos de letra (`1x`) | erro: literal numérico malformado |
| q4 | `ESPACO` | espaços e quebras de linha | descarta |
| q5 | `BARRA` | `/` | emite `SLASH` |
| q6 | `COM_LINHA` | `//` e o resto da linha | descarta |
| q7 | `COM_BLOCO` | dentro de `/* ...` | erro: comentário não fechado |
| q8 | `COM_ESTRELA` | dentro de `/* ... *` | erro: comentário não fechado |
| q9 | `COM_FIM` | `/* ... */` completo | descarta |
| q10 | `MENOR` | `<` | emite `LT` |
| q11 | `MENOR_IG` | `<=` | emite `LE` |
| q12 | `MAIOR` | `>` | emite `GT` |
| q13 | `MAIOR_IG` | `>=` | emite `GE` |
| q14 | `ATRIB` | `=` | emite `ASSIGN` |
| q15 | `IGUAL` | `==` | emite `EQ` |
| q16 | `EXCL` | `!` | erro: `!` isolado |
| q17 | `DIF` | `!=` | emite `NE` |
| q18 a q25 | `MAIS` ... `PVIRG` | `+ - * ( ) { } ;` | emite o token correspondente |

**Construção:** cada expressão regular da seção 5.1 foi convertida em um AFD; os
autômatos foram unidos por um estado inicial comum (q0) e determinizados. Os
prefixos compartilhados ficaram em um único estado: `<` e `<=` compartilham q10;
`=` e `==` compartilham q14; `/`, `//` e `/*` compartilham q5. Os estados q3, q7, q8
e q16 não são de aceitação: eles existem para que o lexer saiba **qual** erro reportar.

**Correspondência com o código:** esta tabela é exatamente o dicionário
`TRANSICOES` de `src/lexer.py` (os nomes da coluna "Nome no código" são as chaves
usadas lá). O teste `test_todo_estado_de_aceitacao_e_alcancavel_pela_tabela`
verifica a consistência entre a tabela de transições e a de aceitação.

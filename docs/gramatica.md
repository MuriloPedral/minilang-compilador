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

**Ausência de recursão à esquerda direta e indireta.** Não basta procurar uma
produção que comece por si própria: também é necessário excluir um caminho
`A ⇒+ A α` por outros não terminais antes de consumir um terminal. Nesta
gramática, a cadeia inicial das expressões segue `expressao → igualdade →
relacional → aditiva → multiplicativa → unaria → primaria`, sem retorno à
esquerda. A volta de `primaria` para `expressao` exige consumir `(`; a recursão
de `unaria` exige consumir `-`. Nos comandos, atribuições começam por `ID`,
blocos por `{` e os controles por suas palavras reservadas. As repetições EBNF
podem ser expandidas como `lista = item lista | ε`, com item não anulável:
consome-se pelo menos um token antes de voltar à lista. Os sufixos opcionais
começam por operadores ou `else`. Logo não há ciclo de chamadas à esquerda
que retorne ao mesmo não terminal sem consumir entrada.

**Escolhas LL(1).** O parser usa um token de antecipação. Em `comando`, os
conjuntos FIRST das alternativas são, respectivamente, `{ID}`, `{print}`,
`{if}`, `{while}`, `{for}` e o conjunto unitário com o token `{`: disjuntos. Em `unaria`, `-` distingue-se
de FIRST(primaria) = `{INT, true, false, ID, (}`. As cinco alternativas de
`primaria` também têm inícios diferentes.

As alternativas vazias exigem conferir FOLLOW, além de FIRST. Para resumir:
`C = FIRST(comando)`, `D = {), ;}`, `I = {==, !=}`,
`R = {<, >, <=, >=}` e `A = {+, -}`. `C` inclui o token de abertura de bloco `{`; `ε` denota a alternativa vazia.

| Escolha EBNF | FIRST da continuação não vazia | FOLLOW do auxiliar na expansão BNF (quando escolher ε) |
|-------------|--------------------------------|----------------------------------------------------------------------|
| Repetição de comandos | C | EOF ou `}` |
| Sufixo opcional de `else` | `else` | C, EOF ou `}` |
| Sufixo opcional de igualdade | I | D |
| Sufixo opcional relacional | R | I ou D |
| Repetição aditiva | A | R, I ou D |
| Repetição multiplicativa | `*` ou `/` | A, R, I ou D |

Em cada linha, FIRST da continuação e FOLLOW do auxiliar são disjuntos.
As escolhas internas de operadores têm tokens distintos. Na expansão BNF
usada na auditoria (com `print` e controles expandidos em `comando`), foram
obtidos 17 não terminais, 39 produções e 107 células preenchidas na tabela
preditiva, sem conflitos. Esses números dependem da expansão escolhida;
o argumento aplicável à EBNF é a disjunção das escolhas descritas acima.
Um token fora dos conjuntos esperados leva a diagnóstico, não à aceitação.

**Sem `else` pendente.** Os corpos exigem blocos com chaves. Em
`if (a) { if (b) { } } else { }`, o fechamento dos blocos determina o dono
do `else`; ele não pertence a FOLLOW do sufixo opcional do `if` interno.
Não existe produção `else if`; o `else` deve ser seguido de bloco.

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

### Regras semânticas adotadas

As regras de tipos são verificadas durante a interpretação, no caminho
executado. Não há análise estática de todos os ramos.

- Valores são `int` ou `bool`, tratados como tipos distintos mesmo que Python
  permita usar booleanos como inteiros. A variável guarda o tipo do valor atual:
  `x = 1; x = true;` é permitido.
- A atribuição avalia o lado direito antes de inserir/atualizar o símbolo.
  Ler uma variável sem atribuição anterior no caminho executado gera erro.
- `+`, `-`, `*`, `/`, menos unário e relações de ordem exigem inteiros.
  A divisão inteira trunca em direção a zero: `-7 / 2` resulta em `-3`.
  Divisor zero produz erro semântico.
- `==` e `!=` exigem operandos do mesmo tipo. A não associatividade é por
  nível: `1 < 2 < 3` é rejeitado, mas `1 < 2 == true` é válido.
- `if`, `while` e `for` exigem condição booleana, sem conversão implícita.
  `for` executa inicialização uma vez; depois condição, corpo e atualização.
- Blocos compartilham uma tabela de símbolos global; chaves não criam escopo.
  `print` apresenta booleanos como `true`/`false`. Expressões binárias avaliam
  o operando esquerdo antes do direito.
- Programa e bloco vazios são válidos. Os limites de recursos estão na seção 6.

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
malformado), que não é estado de aceitação. Essa rejeição é uma regra léxica
adicional: sem ela, as regex isoladas permitiriam separar `3` e `abc`.

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
divisor `b` é conferido durante a execução e vale `0`. Neste exemplo, uma
análise estática com propagação de constantes também poderia descobrir o zero;
o projeto escolhe a verificação dinâmica para tratar uniformemente valores e
caminhos de execução, sem implementar essa análise adicional.

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
| `EOF` | marcador sintético de fim de entrada | emitido uma vez após a leitura |
| (descartado) espaço | `[ \t\r\n]+` | espaços e quebras de linha |
| (descartado) comentário de linha | `//[^\n]*` | `// comentário` |
| (descartado) comentário de bloco | `/\*([^*]\|\*+[^*/])*\*+/` | `/* comentário */` |

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

### 5.5 Justificativa do reconhecimento e correspondência com o código

A implementação constrói diretamente uma tabela determinística por classes
de caracteres em `_construir_transicoes`. A justificativa abaixo relaciona
seus estados às expressões regulares; não afirma que foram materializadas
etapas intermediárias de AFN, união ou determinização que não estão registradas.

Para uma classe e estado existe no máximo um destino. Células ausentes são
transições de parada do reconhecedor de um lexema: a aceitação é decidida pelo
estado atual, sem consumir o próximo caractere. Formalmente, os autômatos dos
lexemas podem ser totalizados com um estado poço não final; o scanner mantém
a decisão de fronteira do token separada dessa apresentação do autômato.

Os seguintes invariantes decorrem das transições, por indução sobre os
caracteres consumidos a partir de q0:

| Família de estados | Invariante e decisão |
|-------------------|----------------------|
| q1 (`ID`) | O primeiro caractere é letra ASCII ou `_`; os seguintes são letras, `_` ou dígitos. Só essas classes mantêm q1. Ao parar, emite ID ou reclassifica uma palavra reservada. |
| q2 (`INT`) | O prefixo é não vazio e só contém dígitos. Outro dígito mantém q2; letra ou `_` leva obrigatoriamente a q3. |
| q3 (`NUM_MAL`) | O prefixo começou com dígitos e passou a conter letra ou `_`; letras e dígitos completam a sequência malformada. É estado não final: gera erro, sem voltar para emitir o prefixo numérico. |
| q4 | Só foram consumidos espaços, tabulações, CR ou LF; a sequência é descartada. |
| q5 e q6 | q5 reconhece `/`; um segundo `/` leva a q6, que consome até antes de LF ou até EOF e descarta o comentário. CR isolado é conteúdo do comentário, conforme `//[^\n]*`. |
| q7, q8 e q9 | Depois de `/*`, q7 está no corpo; q8 guarda uma ou mais estrelas finais; somente `/` a partir de q8 encerra em q9. Só q9 aceita o comentário completo. EOF em q7/q8 produz erro. Não há comentários de bloco aninhados. |
| Operadores e delimitadores | Os caminhos de um caractere reconhecem os símbolos da tabela. Os prefixos `<`, `>`, `=` e `!` distinguem as versões com `=`; `!` isolado termina em estado não final. |

Assim, um estado final só emite o padrão correspondente da tabela 5.1; espaços
e comentários completos são reconhecidos e descartados. Reciprocamente, um
lexema que satisfaz um desses padrões percorre as transições dessa família e
chega ao estado final apropriado, respeitadas as fronteiras e a política de
sequências malformadas. Caracteres não reconhecidos a partir de q0 geram erro.

**Regra de `1x`.** Os padrões de INT e ID, isoladamente, permitiriam os tokens
`1` e `x`. O enunciado exige rejeitar essa entrada; por isso a transição
q2 → q3 ao ler letra/`_` tem precedência sobre a emissão do prefixo INT.
Isso não é consequência apenas do maior casamento. O mesmo comprometimento
com o prefixo `/*` exige erro em comentário não fechado, sem voltar a emitir
`/` e `*` como operadores. Para as entradas válidas, os ciclos de ID, INT e
os operadores de dois caracteres implementam o reconhecimento mais longo
permitido. Palavras reservadas são reclassificadas após ler o ID inteiro.

Ao avançar em LF, o lexer incrementa a linha e reinicia a coluna em 1;
nos demais caracteres incrementa a coluna em uma unidade, inclusive tabulações.
A CLI usa a normalização de quebras de linha da leitura textual do Python.
EOF é acrescentado explicitamente, sem lexema, na posição após o último caractere.
O limite de tamanho de INT é aplicado depois, no parser (seção 6).

As 468 células da tabela 5.3 correspondem ao dicionário `TRANSICOES`, usando
o mapa de nomes da seção 5.4. A auditoria conferiu essa correspondência.
O teste chamado `test_todo_estado_de_aceitacao_e_alcancavel_pela_tabela`
verifica apenas se os estados finais aparecem como destinos; não demonstra
sozinho alcance desde q0. Testes e comparação de tabelas fornecem evidência
de implementação, não substituem a justificativa pelos invariantes.

## 6. Limites operacionais da implementação

As produções anteriores descrevem a sintaxe. A implementação didática aplica
limites de recursos adicionais; uma entrada derivável pode ser rejeitada ao
excedê-los. Esses diagnósticos não significam que a gramática deixou de ser LL(1).

| Recurso | Limite e comportamento |
|---------|------------------------|
| Literal inteiro | Até 640 caracteres decimais, incluindo zeros à esquerda e sem contar o sinal, que é operador unário. O parser rejeita literais maiores com `ErroSintatico`, na posição do literal. |
| Valor inteiro | De `-(10**640 - 1)` a `10**640 - 1`. Cada expressão avaliada deve respeitar essa faixa, inclusive resultados intermediários; excedê-la produz `ErroSemantico` na expressão responsável. A impressão também verifica a faixa antes da conversão decimal. |
| Aninhamento sintático | Até 50 delimitadores abertos simultaneamente, contando parênteses e chaves juntos. O parser faz uma verificação iterativa dos tokens antes da análise recursiva. Os parênteses de `print`, `if`, `while` e `for` também contam. |
| Sinais consecutivos | Até 50 tokens `MINUS` consecutivos. Essa verificação evita recursão excessiva em `unaria`; inclui um eventual menos binário anterior à sequência unária. |
| Profundidade na execução | Até 100 chamadas simultâneas de comandos e expressões, contadas em conjunto pelo interpretador. O limite considera a forma da AST, não o total de comandos ou iterações já executados. Uma soma extensa pode atingir esse limite sem parênteses aninhados. |
| Iterações | Mantido o limite padrão de 10.000 por execução de cada laço, configurável pela API `max_iteracoes`; atingir o limite não demonstra que o programa é infinito. |
| Arquivo de entrada | UTF-8. Bytes inválidos produzem mensagem de leitura na saída de erro e código de saída 2. |

Os limites numéricos evitam depender do limite de conversão decimal da versão
do Python. As proteções globais do interpretador Python não são desativadas.
Se a pilha disponível do ambiente for menor que a necessária mesmo dentro dos
limites fixados, `RecursionError` é traduzido especificamente em diagnóstico de
profundidade; outros erros de programação não são capturados genericamente.

Os diagnósticos de limites sintáticos e de execução usam linha e coluna e saem
pela CLI com código 1, como os demais erros MiniLang. A classificação de um
literal extenso como sintático indica a etapa que aplica a restrição; os seus
dígitos continuam sendo reconhecidos como token `INT` pelo lexer.

Os limites são de tamanho e profundidade locais, não um orçamento global de
tempo ou memória. O núcleo obrigatório da linguagem e os exemplos usuais foram
preservados. Os testes verificam fronteiras aceitas e rejeitadas.

## 7. Referências conceituais

- [Cornell CS 4120 — Top-down (LL) parsing](https://www.cs.cornell.edu/courses/cs4120/2026sp/notes/topdown/): critério de escolhas preditivas por FIRST/FOLLOW aplicado na seção 2.
- [Cornell CS 4120 — Automating Lexical Analysis](https://www.cs.cornell.edu/courses/cs4120/2026sp/notes/leximpl/): relação entre padrões regulares e autômatos aplicada na seção 5.5. O código deste projeto usa construção direta da tabela.

Referências consultadas na revisão de 28/11/2026; a gramática e as escolhas
específicas acima descrevem a implementação MiniLang deste grupo.

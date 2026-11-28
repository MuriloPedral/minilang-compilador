# MiniLang Compilador

Compilador-intérprete didático da disciplina Linguagens Formais e Compiladores
(UNIT, turma GP0029V NO07A, Profa. Layse Santos Souza).

Pipeline: `código-fonte → lexer por AFD → parser descendente recursivo → AST → interpretador`.

## Integrantes

| Integrante | Responsabilidade principal |
|------------|----------------------------|
| Rene Mendonça Marinho | (a) gramática e exemplos; (b) lexer |
| Franck Patrick Hora Vasconcelos | (c) parser; (d) AST |
| Murilo Pedral Mota | (e) interpretador e tabela de símbolos; (f) catálogo de erros; integração e auditoria centralizada |
| Todos | (g) testes, diário e relatório; (h) vídeo e preparação para a arguição |

## Requisitos e instalação

Python 3.10 ou superior, com pip e venv. A dependência de testes é
`pytest==8.3.3`, declarada em `requirements.txt`. O compilador usa somente a
biblioteca padrão. A execução registrada mais recente usou Python 3.12.6;
não foi realizada uma matriz de testes de todas as versões suportadas.

Clone o projeto e entre na raiz:

```text
git clone https://github.com/MuriloPedral/minilang-compilador.git
cd minilang-compilador
```

No Windows, com PowerShell (sem precisar ativar o ambiente):

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m src.interpreter exemplos/programa_valido.ml
.\.venv\Scripts\python.exe -m src.interpreter exemplos/programa_invalido.ml
```

Se o pytest apontar falta de permissão na pasta temporária padrão, use uma
pasta exclusiva dentro do ambiente já criado:

```powershell
.\.venv\Scripts\python.exe -m pytest -q --basetemp=.venv/pytest-temporarios
```

Reserve esse caminho aos temporários dos testes; o pytest gerencia seu conteúdo.

No Linux/macOS:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m pytest -q
.venv/bin/python -m src.interpreter exemplos/programa_valido.ml
.venv/bin/python -m src.interpreter exemplos/programa_invalido.ml
```

Execute os comandos a partir da raiz do repositório. Com um ambiente Python
que já tenha as dependências, os comandos equivalentes são:

```text
python -m pytest -q
python -m src.interpreter exemplos/programa_valido.ml
python -m src.interpreter exemplos/programa_invalido.ml
```

## Resultados esperados

A suíte após a estabilização do conjunto 1 contém **207 testes**. Na validação
final de 28/11/2026, uma cópia limpa com ambiente novo e instalação por
requirements.txt teve **207 testes aprovados**. Os exemplos e os nove erros do
catálogo também foram conferidos. Isso não constitui prova de ausência de defeitos.

O programa válido imprime:

```text
30
10
9
8
7
6
5
4
3
2
1
0
120
true
```

O programa inválido é rejeitado com:

```text
Erro sintático [linha 13, coluna 19]: esperado ';' após a condição do for (o for exige as três cláusulas), encontrado ')'
```

| Código de saída | Significado |
|-----------------|-------------|
| 0 | Execução concluída |
| 1 | Erro MiniLang: léxico, sintático, semântico ou limite de recursos |
| 2 | Uso incorreto da CLI ou falha de leitura, incluindo UTF-8 inválido |

O retorno 1 do exemplo inválido é esperado, não uma falha de instalação.
As mensagens de erro são escritas em stderr. No PowerShell, consulte
`$LASTEXITCODE` imediatamente após o comando; em bash, use `echo $?`.

## Linguagem e limites

Inteiros, booleanos, atribuição, print, aritmética, comparação, if/else,
blocos, while e for com três cláusulas obrigatórias. Suporta comentários
`//` e `/* ... */`. Os blocos compartilham escopo global; a tipagem é dinâmica
e as condições precisam ser booleanas. A divisão inteira trunca para zero.
Diagnósticos interrompem no primeiro erro, sem recuperação.

- Literais: até 640 caracteres decimais, contando zeros à esquerda, sem o sinal.
- Valores: magnitude menor que `10**640`, inclusive resultados intermediários.
- Sintaxe: até 50 delimitadores abertos simultaneamente e 50 sinais de menos consecutivos.
- Execução: até 100 chamadas simultâneas de comandos e expressões.
- Laços: padrão de 10.000 iterações por execução de cada laço, configurável pela API `max_iteracoes`.
- Entrada: arquivos UTF-8. BOM não é removido automaticamente.

Esses limites são operacionais; não há orçamento global de tempo/memória.
Funções, escopos aninhados, tipos compostos, código nativo, break/continue,
cláusulas vazias do for e tutor com LLM não fazem parte desta implementação.
Veja a política completa na [gramática](docs/gramatica.md#6-limites-operacionais-da-implementação).

## Organização e documentos

| Caminho | Conteúdo |
|---------|----------|
| `src/` | Lexer, parser, AST e interpretador |
| `tests/validos/` | Casos válidos e de borda |
| `tests/invalidos/` | Diagnósticos e laço infinito com limite |
| `exemplos/` | Programas válido e inválido |
| [docs/gramatica.md](docs/gramatica.md) | Definição formal, exemplos, tabelas e limites |
| [docs/diario_de_bordo.md](docs/diario_de_bordo.md) | Registro do processo e das verificações |
| [declaracao_IA.md](declaracao_IA.md) | Ferramentas, finalidades e responsabilidades |
| [docs/relatorio.pdf](docs/relatorio.pdf) | Relatório de 3 páginas: fundamentação, árvores, semântica, catálogo de erros e análise crítica de IA; produzido e revisado no conjunto 3 |

## Uso de IA generativa

O projeto utilizou IA na geração inicial, explicação e revisão de artefatos,
auditoria, testes, documentação e apoio à integração. Segundo as informações
confirmadas pelo grupo, Rene e Franck utilizaram **Claude Code — Opus 5.5**;
Murilo utilizou **Codex — GPT-6.1 Sol**. O pacote inicial registra geração com
Claude Code, inclusive do interpretador depois integrado com Codex.

O [diário](docs/diario_de_bordo.md) distingue relatos do pacote, commits e
execuções observadas; a [declaração](declaracao_IA.md) detalha o uso por etapa.
As verificações centralizadas não são atribuídas como execuções individuais
dos colegas. O grupo responde pelas decisões e pela explicação da entrega.

## Situação da entrega

Código e documentação técnica validados: **pronto para gravar o vídeo**.
O relatório tem três páginas e foi conferido visualmente. O diário registra
o processo real; o histórico Git disponível vai de 26 a 28/11 e não comprova
as quatro semanas esperadas no enunciado.

A entrega ainda depende do vídeo/link, da postagem individual do repositório
no Teams, do anexo do PDF e da preparação de todos para a arguição.
O fechamento técnico não substitui essas obrigações.

## Vídeo de apresentação

**Pendente de gravação e publicação.** Será entregue em `docs/apresentacao.mp4`
ou por link público nesta seção, até 29/11/2026, conforme o enunciado.

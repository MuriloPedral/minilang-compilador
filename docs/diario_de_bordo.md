# Diário de Bordo

Este diário distingue três fontes: **observado na sessão** (comandos e
resultados executados com Murilo), **histórico Git** (autoria e data dos
commits) e **relato do material/grupo** (atividades anteriores sem reprodução
histórica disponível). Ferramentas/modelos foram informados pelo grupo:
Claude Code — Opus 5.5 para Rene e Franck; Codex — GPT-6.1 Sol para Murilo.
O nome do modelo informado não é deduzido dos commits.

O histórico Git disponível começa em 26/11/2026 e não comprova quatro semanas
de evolução. As entradas retrospectivas abaixo foram consolidadas em
28/11/2026 usando evidências existentes; não são registros produzidos na data
original nem alteram as datas dos commits.

## Semana de 23/11 a 29/11/2026

### Antecedentes — relato do pacote, sem execução histórica observada

O `DOCUMENTO_COMPLETO_MiniLang.md` do pacote registra início do projeto em
24/11 e geração inicial assistida por Claude Code: leitura do enunciado,
esqueleto, código, testes, gramática e instruções por integrante. Não há
commits de 24/11 no histórico disponível. Os resultados e falhas dessa geração
são relatos do material, não novas execuções deste diário.

Dois episódios relatados na seção 9.2 desse documento foram preservados como
candidatos à análise crítica: comentário de erro indicava coluna 18 em vez de
19; testes do parser usavam caminhos dependentes do diretório de execução e
foram ajustados para `Path(__file__).resolve().parents[2]`. As versões anteriores
a essas correções não constam no histórico Git disponível. Não se atribui uma
data exata a esses dois episódios nem uma decisão individual não documentada.

**Conceitos:** rastreamento de posições léxicas e reprodutibilidade de testes.

### 26/11/2026 — Compreensão, auditoria e publicação do esqueleto

**Fonte:** sessão de trabalho com Murilo e histórico Git.
**Objetivo/pedido:** entender o pacote, comparar o código com o PDF oficial e
verificar sua correção antes da integração. **Ferramenta:** Codex.

Foram lidos o enunciado de oito páginas e o material do pacote. A primeira
tentativa de executar testes revelou ausência de pytest no Python disponível;
depois pytest 8.3.3 foi instalado em uma pasta externa de auditoria. Houve
também restrição de leitura dessa instalação pelo ambiente isolado, resolvida
pela execução autorizada com acesso às dependências. Esses obstáculos eram
do ambiente, não falhas de implementação.

**Comandos/verificações observados:** `python -m pytest -q` com dependências da
auditoria: 186 aprovados na referência; execução dos dois exemplos; comparação
dos PDFs pelo SHA256; 8.000 casos gerados (aritmética, comparação, precedência,
laços e lexer independente); 468 células do AFD; expansão BNF com FIRST/FOLLOW
sem conflitos LL(1); montagem dos zips com 50/105/186 testes aprovados.
Os números de casos gerados e a montagem pertencem à referência original,
antes dos limites adotados no conjunto 1, não à suíte atual do repositório.

**Achados:** exceções com inteiros grandes, expressões profundas e codificação
inválida; relatório ausente e documentos incompletos. Os cinco cenários foram
encaminhados à estabilização, não considerados corrigidos nessa auditoria.

**Decisões:** integração por partes, branches dos integrantes e preservação de
evidências reais. A cópia inicial foi comparada ao esqueleto: 25 arquivos iguais.
O commit `80b270b` publicou o esqueleto; `3b14bf6` registra alteração posterior
do .gitignore por Murilo. O Git demonstra esses commits, não o entendimento
individual nem as conversas privadas dos integrantes.

### 27/11/2026 — Integração da gramática e do lexer

**Fonte:** histórico Git, conferido retrospectivamente em 28/11.
**Responsável:** Rene; apoio de Claude Code informado pelo grupo.
**Objetivo:** integrar os arquivos do pacote de gramática, exemplos e lexer.

| Commit | Autor registrado | Conteúdo |
|--------|------------------|----------|
| `210ee7c` | Renemarinho | Gramática e exemplos |
| `9ac415e` | Renemarinho | Analisador léxico |
| `58dab22` | Renemarinho | Testes léxicos |
| `d4cc1d2` | Murilo | Merge do PR #1 |

Os arquivos foram integrados à main. Não há nesta sessão a saída dos comandos
executados no computador de Rene; não se declara aprovação individual dos
testes apenas com base nos commits. A montagem centralizada da referência
já havia produzido 50 testes aprovados nessa etapa. A auditoria da integração
real está registrada na entrada seguinte.

### 28/11/2026 — Parser/AST, auditoria da integração e pacote de Murilo

**Fonte:** histórico Git e comandos observados na sessão com Murilo.
**Objetivo/pedido:** conferir as branches, integrar as partes e declarar o uso de IA.

| Commit | Autor registrado | Conteúdo |
|--------|------------------|----------|
| `146a635` | Franck Patrick | Nós da AST |
| `4d0eb74` | Franck Patrick | Parser descendente recursivo |
| `f39a008` | Franck Patrick | Testes do parser e da AST |
| `6992bc4` | Murilo | Merge do PR #2 |
| `fb5d945` | Murilo | Restauração de `*_NAO_COMMITAR.md` |
| `35554bb` | Murilo | Integração do interpretador e símbolos |
| `edcc4a7` | Murilo | Testes de execução e laços |
| `9750391` | Murilo | Testes de erros semânticos e limite de iterações |
| `8dafd3d` | Murilo | Merge direto de feat/interpreter na main |

Franck usou Claude Code segundo a confirmação do grupo. Não foram observadas
as conversas privadas nem as execuções em seu computador. A contribuição de
Murilo usou Codex para conferir e integrar o pacote previamente gerado, sem
atribuir a esta integração uma nova escrita integral do interpretador.

**Comandos e resultados centralizados:** `git fetch`, `git log`,
`git branch -r --merged` e `git ls-remote`: lexer e parser/AST já integrados;
`python -B -m pytest -q -p no:cacheprovider`: 105 aprovados antes do pacote de
Murilo e 186 após a cópia dos cinco arquivos. Os dois exemplos mantiveram suas
saídas e códigos. A branch feat/interpreter foi criada, os quatro commits foram
publicados e o merge direto foi enviado à main sem PR, conforme solicitado.
Verificação remota confirmou `8dafd3d`; a árvore de trabalho ficou limpa.

**Declaração de IA:** Murilo confirmou ferramentas/modelos e uso de IA dos três
integrantes. A declaração foi preenchida localmente, sem commit nessa rodada,
separando usos informados de testes centralizados e de documentos pendentes.

### 28/11/2026 — Conjunto 1: estabilização técnica

**Responsável:** Murilo Pedral Mota, com apoio do Codex. Modelo informado pelo
usuário: GPT-6.1 Sol. As execuções abaixo são centralizadas e não atribuídas a
Rene ou Franck.

**Pedido resumido:** reproduzir as cinco falhas conhecidas no repositório atual,
adotar soluções mínimas, adicionar regressões e documentar os resultados, sem
reescrever a arquitetura, produzir o relatório final ou fazer commit/push.

**Estado inicial observado:** main no commit `8dafd3d`, com alteração local em
`declaracao_IA.md` preservada. A suíte inicial teve **186 passed in 0.36s**.

**Problemas reproduzidos antes da correção:**

| Entrada/cenário | Resultado inicial | Tratamento adotado |
|----------------|-------------------|--------------------|
| Literal com 4.301 dígitos | ValueError na conversão para int | Limite de 640 caracteres decimais por literal e diagnóstico sintático com posição |
| Multiplicar x por 10 em 4.301 iterações e imprimir | ValueError ao converter resultado para texto | Faixa de magnitude com 640 dígitos, verificada em cada expressão avaliada; diagnóstico semântico antes da conversão |
| 150 parênteses aninhados | RecursionError no parser | Verificação iterativa dos tokens, limite conjunto de 50 delimitadores abertos e de 50 sinais de menos consecutivos |
| Soma de 1.500 termos | RecursionError na avaliação da AST | Limite de 100 chamadas simultâneas de comandos/expressões e restauração do contador mesmo após erro |
| Arquivo contendo byte FF | UnicodeDecodeError | Captura específica, mensagem de leitura UTF-8 e código de saída 2 |

**Uso da IA e decisão:** foram aceitas as alterações produzidas e verificadas
na execução assistida para limites documentados e testes de regressão.
Mantidos lexer por AFD, parser descendente recursivo, nós da AST, assinaturas
públicas existentes, semântica usual e limite por laço. Não foi usado aumento
global de recursão, desativação de proteção numérica ou captura de Exception.
As capturas específicas de RecursionError são salvaguardas para pilhas menores.

**Conceitos aplicados:** distinção entre gramática formal e limites operacionais,
separação das fases de diagnóstico, preservação da precedência e da AST,
invariantes de avaliação e testes de fronteira/regressão.

**Comandos e resultados:**

- `git status --short --branch` e leitura da auditoria anterior: estado local
  conferido, declaração existente preservada.
- `python -B -m pytest -q -p no:cacheprovider`: 186 aprovados antes das alterações.
- Casos controlados pela API `executar`/`main`: cinco falhas confirmadas antes.
- Após adicionar os testes, a primeira execução teve 202 aprovados e 5 erros de
  preparação: PermissionError no diretório temporário padrão do pytest. Não
  foram falhas de asserção do compilador. O problema de ambiente foi contornado
  por uma pasta temporária isolada da auditoria.
- `python -B -m pytest -q -p no:cacheprovider --basetemp=<pasta temporária isolada>`:
  **207 passed in 0.81s**, incluindo 21 novos casos, fronteiras numéricas e de
  profundidade, reutilização após erro e diagnósticos pela CLI.
- Neste ambiente o pytest 8.3.3 é carregado por PYTHONPATH da pasta externa
  `.audit_deps`; nenhuma dependência nova foi adicionada a requirements.txt.

**Arquivos afetados:** parser e interpretador; testes válidos e inválidos dessas
fases; seção de limites da gramática e do README; declaração de IA e este diário.

**Pendências:** consolidar documentação e histórico anterior no conjunto 2;
produzir e conferir o relatório no conjunto 3; validação limpa e publicação no
conjunto 4; vídeo e obrigações individuais. Nenhum commit ou push nesta rodada.

**Auditoria de saída do conjunto 1:** os cinco cenários foram executados também
como processos reais com `python -X utf8 -B -m src.interpreter <arquivo>`.
Os quatro limites retornaram código 1 com diagnóstico e posição; o UTF-8
inválido retornou código 2. Nenhum dos cinco produziu traceback.
Os exemplos `programa_valido.ml` e `programa_invalido.ml` mantiveram a saída
esperada, os códigos 0/1 e, no inválido, a posição linha 13, coluna 19.
Uma fronteira mista com 50 delimitadores abertos e 50 sinais de menos foi
aceita. Os limites globais do Python permaneceram 1.000 para recursão e
4.300 dígitos para conversão decimal neste ambiente.
`git diff --check` não apontou erros de whitespace. A revisão das alterações
não encontrou regressões nos casos exercitados. Os 186 testes anteriores
continuam aprovados, junto aos 21 novos. Funcionalidades obrigatórias preservadas.

**Resultado: PODE AVANÇAR para o conjunto 2.** Os limites documentados são
restrições operacionais locais, não uma garantia de recursos ilimitados.
Nenhum PDF final, commit ou push foi produzido nesta rodada.

### 28/11/2026 — Conjunto 2: consolidação da documentação textual

**Responsável:** Murilo, com apoio do Codex; modelo informado pelo usuário:
GPT-6.1 Sol. **Pedido:** consolidar gramática, diário, README e declaração
usando o código estabilizado, sem PDF, commit ou push.

**Alterações e decisões:**

- Gramática: explicação de recursão à esquerda direta/indireta e escolhas
  LL(1), inclusive FIRST/FOLLOW de alternativas vazias e repetições; regras
  semânticas; EOF sintético na tabela; correção do separador Markdown na regex
  do comentário de bloco; justificativa do AFD por invariantes e política de
  rejeição de 1x, sem atribuir etapas de AFN/determinização não demonstradas.
- Foi corrigida uma afirmação excessiva sobre divisão por zero: o exemplo
  constante pode ser analisado estaticamente, embora a implementação escolhida
  verifique os valores durante a execução. Os limites do conjunto 1 foram mantidos.
- Diário: consolidação retrospectiva da única semana evidenciada, distinguindo
  os relatos do pacote, a autoria/datas dos commits e as execuções centralizadas.
- README: comandos de instalação e execução, resultados e códigos de saída,
  informações de IA e links. Relatório e vídeo continuam marcados como ausentes.
- Declaração: registro do conjunto 2 e distinção entre a auditoria original de
  8.000 casos e as verificações atuais com os limites já implementados.

**Uso de IA:** o texto foi elaborado com apoio da ferramenta e conferido por
comparações com arquivos, histórico e execução dos exemplos. A revisão dos
critérios de FIRST/FOLLOW e AFD consultou as notas primárias Cornell CS 4120
citadas na gramática. Não foram inventadas conversas privadas ou execuções dos
colegas. A captura do histórico não permite assegurar entendimento individual.

**Comandos e verificações desta rodada:**

- `git status`, `git log --date=short` e `git show`: 15 commits citados no diário
  conferidos, com autoria e datas entre 26 e 28/11. Não houve fetch ou publicação.
- Comparação SHA256 dos arquivos versionados no início/fim da rodada: fontes,
  testes e demais arquivos fora dos quatro documentos preservados, incluindo
  as alterações locais do conjunto 1.
- Script auxiliar externo `.audit/consolidar_conjunto2.py`: a primeira tentativa
  teve erro de sintaxe no próprio auxiliar antes de escrever arquivos; corrigido
  o auxiliar e aplicada a documentação. Isso não foi falha do compilador.
- `.audit/auditar_conjunto2.py`: conferência de formatação/tabulação das tabelas,
  blocos de código e links; o único destino local de link ainda inexistente é
  relatorio.pdf, identificado explicitamente como pendente. O vídeo não recebeu
  link fictício. As 468 células do AFD e suas marcações de aceitação conferem.
- Seis programas distribuídos nos cinco exemplos da gramática executados: um
  válido com saída 0 e cinco inválidos com as mensagens/posições documentadas.
  Dez verificações adicionais conferiram as regras semânticas descritas.
- `python -m venv .venv` e
  `.\.venv\Scripts\python.exe -m pip install -r requirements.txt`: concluídos.
  Nenhuma dependência foi acrescentada ao projeto; o ambiente está ignorado.
- Ao conferir pytest no novo ambiente, uma primeira seleção de basetemp dentro
  de .pytest_cache falhou porque a pasta-pai não existia (202 aprovados e 5 erros
  de preparação). Ajustado para uma pasta exclusiva dentro de .venv, cujo pai
  existe; o README inclui essa alternativa para problemas de temporários.
- `.\.venv\Scripts\python.exe -B -m pytest -q -p no:cacheprovider
  --basetemp=.venv/pytest-temporarios-conjunto2`: **207 passed in 0.84s**.
- Os exemplos programa_valido.ml e programa_invalido.ml também foram executados
  com o Python de .venv e corresponderam às saídas/códigos do README.
- As instruções Linux/macOS foram conferidas textualmente, sem execução neste
  ambiente Windows. A validação da cópia final limpa permanece no conjunto 4.

**Auditoria de saída:** documentação coerente com o código e os limites 640/50/100;
comandos Windows de ambiente/instalação e execução verificados; datas/autorias
conferidas no Git; sem campos de template no README ou diário. O status histórico
de cada rodada foi mantido como histórico, e o estado atual aparece nesta entrada
e na declaração. Nenhuma fonte ou teste foi alterado nesta rodada.

**Resultado: PODE AVANÇAR para o conjunto 3.** Permanecem a produção/conferência
do relatório, a validação final e publicação do conjunto 4, o vídeo e as
obrigações individuais. O histórico continua limitado a uma semana evidenciada.
Não foi produzido PDF nem feito commit/push.

### 28/11/2026 — Conjunto 3: relatório final em PDF

**Responsável:** Murilo, com apoio do Codex; modelo informado pelo usuário:
GPT-6.1 Sol. **Pedido:** produzir docs/relatorio.pdf em duas a três páginas,
com os conteúdos técnicos do enunciado, análise crítica de IA e revisão visual,
sem anexos presumidamente autorizados e sem commit/push.

**Materiais consultados:** PDF oficial completo (oito páginas); código atual,
gramática, declaração e registros deste diário; auditoria anterior. A skill de
PDF orientou geração com ReportLab e renderização/inspeção com Poppler. Foram
consultadas referências primárias Cornell CS 4120 (AFD, LL e LR/LALR) e LLVM
(parser/AST), citadas com links no próprio PDF. Uma tentativa de consulta ao
manual do GNU Bison retornou timeout; ele não foi usado como fonte no relatório.

**Conteúdo produzido:**

- Página 1: resposta à pergunta de pesquisa; fundamentação aplicada do lexer,
  padrões, estados e diagnósticos; parser LL(1), precedência e associatividade;
  árvores de 1 + 2 * 3 e (1 + 2) * 3; comparação com LR/LALR; definição dos nós.
- Página 2: programa completo e AST real com while e for e suas três cláusulas;
  preservação da semântica; símbolos, inserção/busca e semântica operacional de
  cada comando; evidências anteriores da suíte e limites de recursos.
- Página 3: catálogo com nove erros executados (três de cada categoria), coluna,
  mensagem e causa; justificativa do diagnóstico; quatro exemplos de uso de IA
  (precedência aceita, limites numéricos, profundidade e leitura UTF-8); referências.

**Uso de IA e decisões:** texto, estrutura, geração e auditoria auxiliados pelo
Codex. A análise utiliza correções e testes observados no conjunto 1 e o código
atual. A geração inicial com Claude Code aparece como relato do pacote, sem
inventar execuções privadas dos integrantes. Não se mediu ganho de tempo nem
se declarou entendimento individual comprovado. O histórico de 26 a 28/11
continua explicitamente distinto da expectativa de quatro semanas.

**Comandos e verificações:**

- Leitura integral por pypdf e conferência dos itens b a g do enunciado.
- `.audit/gerar_relatorio.py`: geração do PDF e de evidências externas ao repo.
  As duas árvores de expressão vieram de analisar/formatar e as execuções
  retornaram 7 e 9. A AST de programa foi produzida pelo mesmo formatador;
  sua execução imprimiu 0 e deixou x=1 e i=1.
- Nove entradas executadas pela API: léxicos (@, 1x, comentário não fechado),
  sintáticos (operando ausente, while sem parêntese, for sem atualização),
  semânticos (variável indefinida, divisão por zero e condição não booleana em
  while). Todos os textos e posições do catálogo foram obtidos dos erros reais.
- `pdftoppm -r 140 -png`: renderização e inspeção de todas as páginas. A primeira
  revisão identificou proximidade ao rodapé na página 2 e quebra ruim de um
  rótulo. A definição dos nós foi deslocada para a página 1, o rótulo foi
  ajustado e uma redundância crítica foi reduzida; fontes não foram diminuídas.
  As páginas foram renderizadas e revistas novamente após os ajustes.
- `pdfinfo` e pypdf: três páginas A4, arquivo sem criptografia; fontes Arial,
  Arial Bold e Consolas embutidas e quatro links de referências presentes.
  Corpo principal 10,4 pt, tabelas 9,4 pt, textos complementares 9,2 pt e
  árvores 9,1 pt, mantidos entre as revisões de layout.
- `pdftotext -bbox` e `.audit/auditar_relatorio.py`: textos dentro das margens,
  ausência de caracteres de substituição, mensagens conferidas por extração,
  árvores conferidas com código, fronteira de soma em print (99 aceita, 100
  diagnosticada) e preservação de fontes/testes por SHA256.
- Os 207 testes aprovados citados no PDF são o resultado já registrado no
  conjunto 2; esta rodada não é apresentada como nova execução integral da suíte.

**Auditoria de saída:** os 16 pontos de conteúdo foram mapeados às páginas no
registro externo tmp/pdfs/conjunto3/auditoria.json. Os requisitos solicitados
para o relatório couberam em três páginas sem anexos e sem cortes/sobreposições
visíveis após revisão. Não houve conflito de formato a encaminhar. README e
declaração agora identificam o PDF como produzido, não como pendente.

**Resultado: PODE AVANÇAR para o conjunto 4.** Nenhuma fonte/teste foi alterada
nesta rodada e não foram observadas regressões nos casos executados. Permanecem
a validação final em cópia limpa, publicação, vídeo e obrigações individuais.
A limitação histórica de quatro semanas não foi eliminada pela produção do PDF.
Nenhum commit ou push foi realizado.

### 28/11/2026 — Conjunto 4: auditoria final e preparação da publicação

**Responsável:** Murilo, com apoio do Codex; modelo informado pelo usuário:
GPT-6.1 Sol. **Pedido:** conferir requisitos, validar cópia limpa, registrar
resultados e publicar na main, sem force push ou alteração de autoria/histórico.

**Matriz de requisitos conferida nesta rodada:**

| Requisito | Arquivo/evidência | Situação | Pendência |
|-----------|------------------|----------|-----------|
| a — definição e exemplos | docs/gramatica.md; exemplos/*.ml | Conferido | Nenhuma técnica identificada |
| b — lexer e autômato | src/lexer.py; tabelas da gramática; relatório p. 1; testes léxicos | Conferido | Nenhuma técnica identificada |
| c — parser e árvores | src/parser.py; relatório p. 1–2; testes do parser | Conferido | Nenhuma técnica identificada |
| d — AST e preservação | src/ast_nodes.py; relatório p. 1–2; test_ast.py | Conferido | Nenhuma técnica identificada |
| e — interpretador/símbolos | src/interpreter.py; relatório p. 2; testes de execução | Conferido | Nenhuma técnica identificada |
| f — diagnósticos | relatório p. 3; testes inválidos; nove execuções na cópia limpa | Conferido | Nenhuma técnica identificada |
| g — testes, diário, relatório e histórico | 207 testes aprovados; este diário; PDF de três páginas; Git | Artefatos técnicos conferidos | Histórico de 26–28/11 não comprova quatro semanas |
| h — vídeo e arguição | README indica vídeo pendente | Externo ao fechamento técnico | Gravar/publicar vídeo e preparar defesa |
| IA, acesso e submissão | declaracao_IA.md; README; GitHub público confirmado por API | Documentos/acesso conferidos | Cada integrante postar no Teams e anexar PDF |

**Estado inicial e preservação:** `git fetch origin` confirmou main local e
remota no commit `8dafd3d`. Havia dez arquivos modificados pelos conjuntos
anteriores e o novo docs/relatorio.pdf; nenhuma alteração já estava preparada
no índice. A conferência preservou essas mudanças. Não havia commits remotos
novos a incorporar antes da auditoria.

**Estrutura e exclusões:** os 26 arquivos previstos foram enumerados com
`git ls-files --cached --others --exclude-standard`. Incluem os quatro módulos,
inicializadores, nove arquivos de testes, documentação e exemplos. A lista não
contém instruções locais, .env, ambientes, caches ou auxiliares. `git check-ignore`
confirmou as exclusões de *_NAO_COMMITAR.md, .venv, .pytest_cache e __pycache__.
Os auxiliares da auditoria ficam na pasta externa minilang-entrega-completa,
fora da raiz do repositório publicado.

**Validação limpa observada:**

- `.audit/validar_entrega_limpa.py` criou uma pasta exclusiva fora do projeto,
  copiou apenas os 26 arquivos da entrega atual e comparou seus SHA256.
  Nenhum arquivo foi completado com a referência e nenhum ambiente foi copiado.
- `python -m venv .venv` criou um ambiente novo nessa cópia; o Python dele
  instalou somente `-m pip install -r requirements.txt`. PYTHONPATH/PYTHONHOME
  foram removidos do ambiente dos subprocessos para não usar a instalação da
  auditoria anterior. Plugins externos de pytest não foram carregados.
- `python -B -m pytest -q -p no:cacheprovider
  --basetemp=.venv/pytest-temporarios`: **207 passed in 0.76s**. A pasta
  temporária exclusiva evita a restrição já documentada do ambiente Windows.
- O programa válido imprimiu a sequência do README e retornou 0; o inválido
  retornou 1 com erro sintático na linha 13, coluna 19.
- As nove entradas do catálogo foram executadas pela CLI nessa cópia, com
  três erros por categoria. Mensagens e posições coincidiram integralmente
  com as evidências usadas no PDF. Incluem erro sintático e semântico em laço.
- Arquivo UTF-8 inválido, argumentos ausentes e arquivo inexistente retornaram
  2, sem traceback. A suíte completa cobriu laços com 0, 1 e N iterações,
  atualização diferente e interrupção de laço infinito por limite.
- PDF: três páginas, mesmo SHA256 do artefato visualmente revisado no conjunto
  3. Fontes, testes e exemplos permaneceram idênticos entre original e cópia.
- Links locais conferidos e sem destino ausente; limites, correções, 207 testes
  e origem dos registros coerentes entre os documentos. Registros de etapas
  anteriores que diziam pendente são históricos, não o estado atual.
- A API pública do GitHub confirmou repositório público e branch padrão main.

**Uso de IA e decisões:** aceito o fechamento técnico baseado nas verificações,
sem ampliar a linguagem ou inserir melhorias opcionais. A IA auxiliou a matriz,
a cópia isolada, os comandos, a conferência dos documentos e o preparo dos commits.
README e declaração foram atualizados para registrar a validação concluída.
Essas duas atualizações e esta entrada foram sincronizadas depois com a cópia
auditada; a verificação final dos arquivos preparados antecede os commits.

**Publicação autorizada:** os commits do fechamento preservam os autores e
commits anteriores, organizando correções, documentação e relatório. O envio
à main deve ser confirmado pela referência remota após o push. Esta entrada
registra a auditoria que autoriza o envio; a confirmação da publicação é a
igualdade entre o commit local e o remoto, consultável no histórico Git.

**Resultado: PRONTO PARA GRAVAR O VÍDEO.** Nenhuma falha técnica obrigatória
foi identificada na auditoria final. Não significa entrega total: permanecem
vídeo/link até 29/11, postagem individual no Teams, anexo do relatório e
preparação da arguição de 01/12. Não foram feitas postagens ou mensagens no
Teams. O histórico não distribuído por quatro semanas continua sendo uma
limitação de conformidade; não foram criadas evidências ou datas artificiais.

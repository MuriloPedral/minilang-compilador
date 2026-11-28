# Declaração de Uso de IA Generativa

Em atendimento às regras do Projeto da Unidade II da disciplina Linguagens Formais e Compiladores (UNIT).

## Situação

- [x] O grupo utilizou ferramentas de IA generativa.
- [ ] O grupo não utilizou ferramentas de IA generativa.

O grupo declara uso de IA durante o desenvolvimento: interpretação do enunciado, planejamento, geração inicial de artefatos, explicação e revisão do código, auditoria, testes, documentação e apoio às operações de Git/GitHub. O uso abrangeu as partes dos três integrantes.

As ferramentas e os modelos abaixo foram confirmados por Murilo em nome do grupo; não foram inferidos a partir dos commits.

## Ferramentas e integrantes

| Integrante | Ferramenta | Versão / modelo informado | Responsabilidade principal |
|------------|------------|--------------------------|----------------------------|
| Rene Mendonça Marinho | Claude Code | Opus 5.5 | Gramática, exemplos e lexer |
| Franck Patrick Hora Vasconcelos | Claude Code | Opus 5.5 | Parser e AST |
| Murilo Pedral Mota | Codex | GPT-6.1 Sol | Interpretador, tabela de símbolos, catálogo de erros, auditoria integrada e consolidação da entrega |

## Uso por etapa

| Etapa | Ferramenta | Finalidade específica | Responsável |
|-------|------------|-----------------------|-------------|
| Enunciado e planejamento | Claude Code e Codex | Apoiar a interpretação dos requisitos, a definição do escopo, a divisão das tarefas e a organização do esqueleto e dos pacotes | Grupo; consolidação por Murilo |
| Gramática EBNF e exemplos | Claude Code | Apoiar a criação, explicação e revisão do alfabeto, das produções, da precedência e associatividade e dos exemplos válidos e inválidos | Rene |
| Lexer | Claude Code | Apoiar a criação e a auditoria do analisador léxico, das tabelas de tokens e transições do AFD e dos diagnósticos | Rene |
| Parser | Claude Code | Apoiar a criação, explicação e auditoria do parser descendente recursivo e do tratamento das expressões, dos comandos e dos laços | Franck |
| AST | Claude Code | Apoiar a criação e revisão dos nós, de seus campos e da representação textual das árvores | Franck |
| Interpretador e tabela de símbolos | Claude Code na geração inicial do pacote, conforme seu material de contexto; Codex na integração e conferência | Apoiar a implementação sobre a AST, as operações com símbolos e as verificações semânticas; integrar e validar o pacote recebido | Murilo |
| Catálogo de erros | Claude Code nas fases léxica e sintática; Codex na revisão integrada | Apoiar a identificação, explicação e organização dos erros e dos exemplos de diagnóstico | Rene e Franck nas respectivas fases; Murilo na consolidação |
| Testes | Claude Code e Codex | Apoiar a geração e a revisão de casos válidos, inválidos e de borda e a interpretação dos resultados | Cada integrante em sua parte; Murilo na verificação integrada |
| Auditoria integrada | Codex | Comparar o projeto com o enunciado e referências técnicas, executar testes adicionais, conferir o AFD e calcular FIRST/FOLLOW da gramática expandida | Murilo |
| Git/GitHub | Claude Code e Codex | Apoiar clonagem, extração dos pacotes, branches, commits e integração; executar o commit inicial e a integração do pacote de Murilo sob sua orientação | Rene e Franck em suas branches; Murilo na integração |
| Estabilização técnica (conjunto 1) | Codex | Reproduzir defeitos, implementar limites e tratamento de codificação, adicionar testes de regressão e registrar decisões e resultados | Murilo |
| Documentação e declaração de IA | Claude Code e Codex | Apoiar instruções individuais, material de contexto, explicações técnicas e a elaboração desta declaração | Grupo; consolidação por Murilo |
| Consolidação textual (conjunto 2) | Codex | Conferir a gramática com o código, corrigir fundamentação e tabelas, consolidar o histórico real e atualizar README e declaração | Murilo |
| Auditoria final e publicação (conjunto 4) | Codex | Conferir os requisitos, preparar cópia limpa dos arquivos reais, instalar dependências em ambiente novo, executar suíte/exemplos/diagnósticos e apoiar commits e envio à main sob autorização de Murilo | Murilo |
| Relatório final (conjunto 3) | Codex | Elaborar o texto técnico e a análise crítica; gerar o PDF em três páginas; conferir árvores e diagnósticos com execuções e revisar visualmente as páginas renderizadas | Grupo; consolidação por Murilo |

## Declarações individuais

**Rene Mendonça Marinho:** utilizou Claude Code, modelo informado Opus 5.5, como apoio à criação, explicação e revisão dos artefatos de definição formal e análise léxica, incluindo exemplos, tabelas e testes. O uso foi confirmado por Murilo; o histórico registra os commits da parte de Rene.

**Franck Patrick Hora Vasconcelos:** utilizou Claude Code, modelo informado Opus 5.5, como apoio à criação, explicação e revisão do parser e da AST, incluindo testes e o tratamento das construções sintáticas. O uso foi confirmado por Murilo; o histórico registra os commits da parte de Franck.

**Murilo Pedral Mota:** utilizou Codex, modelo informado GPT-6.1 Sol, para compreender o projeto, auditar código e documentação, executar testes, analisar diagnósticos, preparar orientações para o grupo e integrar arquivos no Git/GitHub. Também utilizou a ferramenta para elaborar esta declaração com base nas informações fornecidas pelo grupo. A integração utilizou o interpretador previamente gerado no pacote; não se atribui ao Codex uma nova implementação integral desse módulo.

Estas declarações registram o uso informado das ferramentas e não constituem assinaturas digitais dos integrantes.

## Verificações centralizadas executadas

Na auditoria e na integração conduzidas por Murilo com apoio do Codex, foram documentadas:

**Auditoria e integração anteriores à estabilização (26 a 28/11):**

- Execução da suíte original completa: 186 testes aprovados.
- Execução de 8.000 casos gerados, incluindo aritmética, comparações, precedência, laços e comparação com um lexer independente, sem divergências nos resultados esperados.
- Conferência das 468 células da tabela de transições do AFD com o código.
- Cálculo de FIRST/FOLLOW de uma expansão independente da EBNF em BNF, sem conflitos na tabela preditiva LL(1).
- Montagem isolada dos pacotes em sequência, com 50, 105 e 186 testes aprovados.
- Verificação da main após a integração de Rene e Franck: 105 testes aprovados.
- Integração do pacote de Murilo: 186 testes aprovados e resultados dos exemplos válido e inválido conferidos.

**Estabilização e consolidação textual em 28/11:** o conjunto 1 passou com 207
testes, após incluir 21 casos. No conjunto 2, foram conferidos os seis programas
dos exemplos comentados, as 468 células do AFD, os links e tabelas e os commits
citados no diário. O ambiente Windows foi criado conforme o README, com
instalação por requirements.txt, e a suíte voltou a passar com 207 testes.
As instruções Linux/macOS foram conferidas, mas não executadas neste Windows.
Os 8.000 casos gerados anteriores não foram reapresentados como nova execução
do código estabilizado.

Essas execuções pertencem à verificação centralizada e não são atribuídas como execuções individuais de Rene ou Franck. Os resultados não constituem prova de ausência de todos os defeitos.

A auditoria inicial identificou exceções não tratadas com inteiros grandes, expressões profundas e arquivos de codificação inválida. Em 28/11/2026, no conjunto 1, os cinco casos foram reproduzidos no projeto integrado e tratados com limites explícitos de recursos e diagnóstico de UTF-8 inválido. Foram adicionados 21 casos de regressão/fronteira; a suíte passou de 186 para 207 testes aprovados. A integração anterior dos pacotes e esta correção são atividades distintas.

## Responsabilidade e registros complementares

O grupo assume a responsabilidade pela conferência dos artefatos, pelas decisões de aceitar ou alterar sugestões e pela compreensão do código e dos conceitos necessários à defesa oral. A IA não substitui essa responsabilidade.

Os commits registram a evolução dos arquivos, mas não comprovam isoladamente o conteúdo das conversas com IA ou o entendimento individual. As atividades devem ser documentadas com datas reais e com identificação de quem efetivamente as realizou.

Nesta atualização, `docs/diario_de_bordo.md` reúne os antecedentes relatados no
pacote, o histórico Git de 26 a 28/11 e as execuções observadas nas auditorias,
na integração e nos conjuntos 1 e 2. As entradas retrospectivas indicam suas
fontes; não há evidência de quatro semanas de commits. `docs/relatorio.pdf`
foi produzido no conjunto 3 com três páginas, incluindo a análise crítica
baseada nesses registros. O texto e a diagramação foram gerados com auxílio
do Codex/ReportLab, com árvores obtidas do código, nove diagnósticos conferidos
por execução e inspeção visual das páginas renderizadas. A validação final em
cópia limpa foi concluída no conjunto 4: 26 arquivos copiados sem usar a
referência nem o ambiente anterior, instalação por requirements.txt e 207
testes aprovados, com exemplos e nove diagnósticos conferidos. A publicação
dessas alterações na main integra o fechamento autorizado do conjunto 4 e
é comprovada pelo histórico e pela referência remota, não por esta declaração.
O vídeo e as obrigações individuais continuam a cargo do grupo.

Atualização: 28/11/2026.

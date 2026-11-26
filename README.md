# MiniLang Compilador

Compilador-intérprete da linguagem didática **MiniLang**, desenvolvido para a disciplina Linguagens Formais e Compiladores (UNIT, turma GP0029V NO07A, Profa. Layse Santos Souza).

Pipeline: `código-fonte -> lexer -> parser -> AST -> interpretador`

## Integrantes

| Nome | Responsabilidade principal |
|------|----------------------------|
| Franck Patrick Hora Vasconcelos | (c) parser, (d) AST |
| Murilo Pedral Mota | (e) interpretador e tabela de símbolos, (f) catálogo de erros |
| Rene Mendonça Marinho | (a) gramática e exemplos, (b) lexer |
| Todos | (g) suíte de testes, diário e relatório, (h) vídeo |

## Requisitos

- Python 3.10+
- Dependências: `pip install -r requirements.txt`

## Execução

```bash
# executar um programa MiniLang (a implementar)
python -m src.interpreter exemplos/programa_valido.ml

# rodar a suíte de testes
python -m pytest -v
```

## Estrutura

```
docs/        relatório, gramática, diário de bordo, vídeo
exemplos/    programas MiniLang válido e inválido
src/         lexer, parser, AST, interpretador
tests/       testes válidos e inválidos (pytest)
```

## Uso de IA generativa

Ferramenta(s) utilizada(s): **a preencher pelo grupo** (nome e versão/modelo).
Detalhamento por etapa em [declaracao_IA.md](declaracao_IA.md) e registro semanal em [docs/diario_de_bordo.md](docs/diario_de_bordo.md).

## Vídeo de apresentação

`docs/apresentacao.mp4` ou link público: **a preencher**.

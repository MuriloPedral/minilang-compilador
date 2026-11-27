"""Testes do lexer com entradas VÁLIDAS (item b).

Resultado esperado: todas as entradas são convertidas em tokens sem erro;
os tipos, lexemas e posições (linha, coluna) batem com os esperados;
espaços e comentários são descartados; a lista termina sempre com EOF.
"""

import pytest

from src.lexer import ACEITACAO, TRANSICOES, Token, tokenizar


def tipos(fonte):
    return [t.tipo for t in tokenizar(fonte)]


def test_programa_vazio_gera_apenas_eof():
    assert tipos("") == ["EOF"]


def test_atribuicao_simples():
    assert tokenizar("x = 10;") == [
        Token("ID", "x", 1, 1),
        Token("ASSIGN", "=", 1, 3),
        Token("INT", "10", 1, 5),
        Token("SEMI", ";", 1, 7),
        Token("EOF", "", 1, 8),
    ]


@pytest.mark.parametrize("palavra,tipo", [
    ("if", "IF"), ("else", "ELSE"), ("while", "WHILE"), ("for", "FOR"),
    ("print", "PRINT"), ("true", "TRUE"), ("false", "FALSE"),
])
def test_palavras_reservadas(palavra, tipo):
    assert tipos(palavra) == [tipo, "EOF"]


@pytest.mark.parametrize("ident", ["whilex", "forma", "iff", "_tmp", "x1", "Soma_Total2"])
def test_identificador_que_comeca_com_palavra_reservada_e_id(ident):
    # Maior casamento: "whilex" é um único ID, não WHILE seguido de x.
    assert tipos(ident) == ["ID", "EOF"]


@pytest.mark.parametrize("fonte,esperado", [
    ("<", ["LT"]), ("<=", ["LE"]), (">", ["GT"]), (">=", ["GE"]),
    ("=", ["ASSIGN"]), ("==", ["EQ"]), ("!=", ["NE"]),
    ("+ - * /", ["PLUS", "MINUS", "STAR", "SLASH"]),
    ("( ) { } ;", ["LPAREN", "RPAREN", "LBRACE", "RBRACE", "SEMI"]),
])
def test_operadores_e_delimitadores(fonte, esperado):
    assert tipos(fonte) == esperado + ["EOF"]


def test_maior_casamento_em_operadores_de_dois_caracteres():
    # "<==" deve ser "<=" seguido de "=", e não "<" seguido de "==".
    assert tipos("<==") == ["LE", "ASSIGN", "EOF"]
    assert tipos("===") == ["EQ", "ASSIGN", "EOF"]


def test_operadores_colados_sem_espaco():
    assert tipos("x=y+1*(2-3)/4;") == [
        "ID", "ASSIGN", "ID", "PLUS", "INT", "STAR", "LPAREN", "INT",
        "MINUS", "INT", "RPAREN", "SLASH", "INT", "SEMI", "EOF",
    ]


def test_comentario_de_linha_e_descartado():
    assert tipos("x = 1; // comentário com @ e 1x\ny = 2;") == [
        "ID", "ASSIGN", "INT", "SEMI", "ID", "ASSIGN", "INT", "SEMI", "EOF",
    ]


def test_comentario_de_linha_no_fim_do_arquivo():
    assert tipos("x = 1; // fim sem quebra de linha") == ["ID", "ASSIGN", "INT", "SEMI", "EOF"]


def test_comentario_de_bloco_multilinha_e_descartado():
    fonte = "x = 1;\n/* linha 1\n   linha 2 ** com estrelas */\ny = 2;"
    tokens = tokenizar(fonte)
    assert [t.tipo for t in tokens] == [
        "ID", "ASSIGN", "INT", "SEMI", "ID", "ASSIGN", "INT", "SEMI", "EOF",
    ]
    y = tokens[4]
    assert (y.lexema, y.linha, y.coluna) == ("y", 4, 1)


def test_comentario_de_bloco_terminando_com_varias_estrelas():
    assert tipos("/* abc ***/ x") == ["ID", "EOF"]


def test_barra_sozinha_e_divisao():
    assert tipos("a / b") == ["ID", "SLASH", "ID", "EOF"]


def test_posicoes_em_varias_linhas():
    tokens = tokenizar("x = 1;\n  print(x);")
    p = tokens[4]
    assert (p.tipo, p.linha, p.coluna) == ("PRINT", 2, 3)


def test_programa_com_while_e_for():
    fonte = "while (x < 10) { x = x + 1; } for (i = 0; i < 3; i = i + 1) { print(i); }"
    t = tipos(fonte)
    assert t[0] == "WHILE" and "FOR" in t and t[-1] == "EOF"


def test_todo_estado_de_aceitacao_e_alcancavel_pela_tabela():
    # Garante que a tabela de transições e a tabela de aceitação são consistentes.
    destinos = set(TRANSICOES.values())
    assert set(ACEITACAO) <= destinos

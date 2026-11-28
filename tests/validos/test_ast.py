"""Testes de construção e verificação da AST (item d).

Resultado esperado: a AST gerada pelo parser é igual à construída manualmente
com as classes de src/ast_nodes.py; o for guarda as três cláusulas em campos
separados; parênteses, ';' e chaves não aparecem como nós; e a função
`formatar` produz a árvore em texto indentado.
"""

from src.ast_nodes import (
    Atribuicao, Bloco, Booleano, For, Inteiro, OpBinaria, Print, Programa,
    Variavel, While, formatar,
)
from src.parser import analisar


def test_ast_de_1_mais_2_vezes_3():
    esperado = Programa([
        Atribuicao("r", OpBinaria("+", Inteiro(1), OpBinaria("*", Inteiro(2), Inteiro(3))))
    ])
    assert analisar("r = 1 + 2 * 3;") == esperado


def test_ast_de_1_mais_2_entre_parenteses_vezes_3():
    esperado = Programa([
        Atribuicao("r", OpBinaria("*", OpBinaria("+", Inteiro(1), Inteiro(2)), Inteiro(3)))
    ])
    assert analisar("r = (1 + 2) * 3;") == esperado


def test_as_duas_expressoes_geram_arvores_diferentes():
    a = analisar("r = 1 + 2 * 3;")
    b = analisar("r = (1 + 2) * 3;")
    assert a != b


def test_parenteses_redundantes_nao_geram_nos():
    assert analisar("r = ((((7))));") == analisar("r = 7;")


def test_ast_do_for_com_as_tres_clausulas():
    prog = analisar("for (i = 0; i < 10; i = i + 1) { print(i); }")
    esperado = For(
        inicializacao=Atribuicao("i", Inteiro(0)),
        condicao=OpBinaria("<", Variavel("i"), Inteiro(10)),
        atualizacao=Atribuicao("i", OpBinaria("+", Variavel("i"), Inteiro(1))),
        corpo=Bloco([Print(Variavel("i"))]),
    )
    assert prog.comandos == [esperado]


def test_ast_do_while():
    prog = analisar("while (x > 0) { x = x - 1; }")
    assert prog.comandos == [
        While(
            condicao=OpBinaria(">", Variavel("x"), Inteiro(0)),
            corpo=Bloco([Atribuicao("x", OpBinaria("-", Variavel("x"), Inteiro(1)))]),
        )
    ]


def test_igualdade_ignora_posicao():
    assert Inteiro(1, linha=5, coluna=9) == Inteiro(1)


def test_inteiro_e_booleano_sao_nos_diferentes():
    assert Inteiro(1) != Booleano(True)


def test_formatar_expressao():
    texto = formatar(OpBinaria("+", Inteiro(1), OpBinaria("*", Inteiro(2), Inteiro(3))))
    assert texto == (
        "OpBinaria +\n"
        "  esquerda: Inteiro 1\n"
        "  direita: OpBinaria *\n"
        "    esquerda: Inteiro 2\n"
        "    direita: Inteiro 3"
    )


def test_formatar_for():
    texto = formatar(analisar("for (i = 0; i < 3; i = i + 1) { print(i); }"))
    assert texto == (
        "Programa\n"
        "  For\n"
        "    inicializacao: Atribuicao i\n"
        "      valor: Inteiro 0\n"
        "    condicao: OpBinaria <\n"
        "      esquerda: Variavel i\n"
        "      direita: Inteiro 3\n"
        "    atualizacao: Atribuicao i\n"
        "      valor: OpBinaria +\n"
        "        esquerda: Variavel i\n"
        "        direita: Inteiro 1\n"
        "    corpo: Bloco\n"
        "      Print\n"
        "        expressao: Variavel i"
    )


def test_formatar_booleano():
    assert formatar(Booleano(False)) == "Booleano false"

"""Testes do parser com entradas VÁLIDAS (item c).

Resultado esperado: cada programa é aceito e a AST produzida respeita
precedência (* e / antes de + e -), associatividade à esquerda
(1 - 2 - 3 == (1 - 2) - 3), parênteses, e as estruturas if, while e for.
"""

from pathlib import Path

from src.ast_nodes import (
    Atribuicao, Bloco, Booleano, For, If, Inteiro, OpBinaria, OpUnaria,
    Print, Programa, Variavel, While,
)
from src.parser import analisar

RAIZ = Path(__file__).resolve().parents[2]


def expr(fonte_expr):
    """Faz o parse de 'r = <expr>;' e devolve só a expressão."""
    return analisar(f"r = {fonte_expr};").comandos[0].valor


def B(op, e, d):
    return OpBinaria(op, e, d)


def I(v):
    return Inteiro(v)


def test_programa_vazio():
    assert analisar("") == Programa([])


def test_programa_so_com_comentarios():
    assert analisar("// nada\n/* nada */") == Programa([])


def test_precedencia_multiplicacao_antes_da_soma():
    assert expr("1 + 2 * 3") == B("+", I(1), B("*", I(2), I(3)))


def test_parenteses_alteram_precedencia():
    assert expr("(1 + 2) * 3") == B("*", B("+", I(1), I(2)), I(3))


def test_associatividade_a_esquerda_subtracao():
    assert expr("1 - 2 - 3") == B("-", B("-", I(1), I(2)), I(3))


def test_associatividade_a_esquerda_divisao():
    assert expr("8 / 4 / 2") == B("/", B("/", I(8), I(4)), I(2))


def test_mistura_de_niveis():
    # 1 + 2 * 3 - 4 / 2  ==  (1 + (2 * 3)) - (4 / 2)
    assert expr("1 + 2 * 3 - 4 / 2") == B(
        "-", B("+", I(1), B("*", I(2), I(3))), B("/", I(4), I(2))
    )


def test_menos_unario():
    assert expr("-5") == OpUnaria("-", I(5))
    assert expr("--5") == OpUnaria("-", OpUnaria("-", I(5)))
    assert expr("-2 * 3") == B("*", OpUnaria("-", I(2)), I(3))
    assert expr("4 - -1") == B("-", I(4), OpUnaria("-", I(1)))


def test_comparacao_tem_precedencia_menor_que_aritmetica():
    assert expr("x + 1 < y * 2") == B(
        "<", B("+", Variavel("x"), I(1)), B("*", Variavel("y"), I(2))
    )


def test_igualdade_tem_precedencia_menor_que_relacional():
    assert expr("a < b == true") == B("==", B("<", Variavel("a"), Variavel("b")), Booleano(True))


def test_comparacao_encadeada_com_parenteses_e_valida():
    assert expr("(1 < 2) == (3 < 4)") == B("==", B("<", I(1), I(2)), B("<", I(3), I(4)))


def test_print():
    assert analisar("print(x + 1);").comandos == [Print(B("+", Variavel("x"), I(1)))]


def test_if_com_else():
    prog = analisar("if (x > 0) { print(x); } else { print(0); }")
    assert prog.comandos == [
        If(B(">", Variavel("x"), I(0)),
           Bloco([Print(Variavel("x"))]),
           Bloco([Print(I(0))]))
    ]


def test_if_sem_else():
    prog = analisar("if (true) { x = 1; }")
    assert prog.comandos == [If(Booleano(True), Bloco([Atribuicao("x", I(1))]), None)]


def test_while():
    prog = analisar("while (x < 10) { x = x + 1; }")
    assert prog.comandos == [
        While(B("<", Variavel("x"), I(10)),
              Bloco([Atribuicao("x", B("+", Variavel("x"), I(1)))]))
    ]


def test_for_com_as_tres_clausulas():
    prog = analisar("for (i = 0; i < 10; i = i + 1) { print(i); }")
    (laco,) = prog.comandos
    assert isinstance(laco, For)
    assert laco.inicializacao == Atribuicao("i", I(0))
    assert laco.condicao == B("<", Variavel("i"), I(10))
    assert laco.atualizacao == Atribuicao("i", B("+", Variavel("i"), I(1)))
    assert laco.corpo == Bloco([Print(Variavel("i"))])


def test_laco_com_corpo_vazio():
    assert analisar("while (false) { }").comandos == [While(Booleano(False), Bloco([]))]


def test_lacos_aninhados():
    prog = analisar(
        "for (i = 0; i < 2; i = i + 1) { while (j < 2) { j = j + 1; } }"
    )
    (laco,) = prog.comandos
    assert isinstance(laco.corpo.comandos[0], While)


def test_bloco_solto():
    assert analisar("{ x = 1; { y = 2; } }").comandos == [
        Bloco([Atribuicao("x", I(1)), Bloco([Atribuicao("y", I(2))])])
    ]


def test_programa_exemplo_do_enunciado():
    fonte = """
    x = 10;
    y = 2 * (x + 5);
    while (x > 0) { print(x); x = x - 1; }
    soma = 0;
    for (i = 0; i < 5; i = i + 1) { soma = soma + i; }
    if (soma > 20) { print(soma); } else { print(0); }
    """
    tipos = [type(c).__name__ for c in analisar(fonte).comandos]
    assert tipos == ["Atribuicao", "Atribuicao", "While", "Atribuicao", "For", "If"]


def test_posicao_dos_nos():
    prog = analisar("x = 1;\nwhile (x < 3) { x = x + 1; }")
    laco = prog.comandos[1]
    assert (laco.linha, laco.coluna) == (2, 1)


def test_arquivo_exemplos_programa_valido():
    prog = analisar((RAIZ / "exemplos" / "programa_valido.ml").read_text(encoding="utf-8"))
    tipos = {type(c).__name__ for c in prog.comandos}
    assert {"While", "For", "If"} <= tipos

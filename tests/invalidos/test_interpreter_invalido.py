"""Testes de rejeição de programas INVÁLIDOS pelo interpretador (itens e e f,
categoria: erros semânticos).

Resultado esperado: cada programa lança ErroSemantico com a mensagem abaixo.
  - "print(y);"                         -> variável 'y' não definida
  - "x = 10 / 0;"                       -> divisão por zero
  - "x = 1 + true;"                     -> tipo incompatível: '+' exige operandos int
  - "while (1) { }"                     -> condição do while deve ser booleana, mas é do tipo int
  - "for (i = 0; i; i = i + 1) { }"     -> condição do for deve ser booleana
  - "while (k < 10) { k = k + 1; }"     -> variável 'k' não definida (variável de controle)
  - "x = 1 == true;"                    -> '==' exige operandos do mesmo tipo
A saída produzida ANTES do erro é preservada (execução é interrompida no erro).
"""

import pytest

from src.interpreter import ErroSemantico, executar
from src.lexer import ErroLexico
from src.parser import ErroSintatico


def erro_de(fonte, saida=None) -> ErroSemantico:
    with pytest.raises(ErroSemantico) as info:
        executar(fonte, saida=saida if saida is not None else (lambda s: None))
    return info.value


# ---------------- Variável não definida ----------------

def test_variavel_nao_definida():
    e = erro_de("print(y);")
    assert e.mensagem == "variável 'y' não definida"
    assert (e.linha, e.coluna) == (1, 7)


def test_variavel_usada_antes_de_definida():
    assert "'x' não definida" in erro_de("y = x + 1; x = 2;").mensagem


def test_variavel_definida_so_em_ramo_nao_executado():
    assert "'z' não definida" in erro_de("if (false) { z = 1; } print(z);").mensagem


def test_variavel_de_controle_nao_definida_no_while():
    e = erro_de("while (k < 10) { k = k + 1; }")
    assert "'k' não definida" in e.mensagem


def test_variavel_de_controle_errada_na_condicao_do_for():
    e = erro_de("for (i = 0; j < 10; i = i + 1) { }")
    assert "'j' não definida" in e.mensagem


def test_variavel_nao_definida_na_atualizacao_do_for():
    assert "'k' não definida" in erro_de("for (i = 0; i < 3; i = k + 1) { }").mensagem


# ---------------- Divisão por zero ----------------

def test_divisao_por_zero_literal():
    e = erro_de("x = 10 / 0;")
    assert e.mensagem == "divisão por zero"
    assert (e.linha, e.coluna) == (1, 8)


def test_divisao_por_zero_calculada():
    assert "divisão por zero" in erro_de("a = 5; b = a - 5; print(a / b);").mensagem


# ---------------- Tipo incompatível ----------------

@pytest.mark.parametrize("expr,op", [
    ("1 + true", "+"), ("false - 1", "-"), ("true * true", "*"),
    ("4 / false", "/"), ("true < 1", "<"), ("false >= false", ">="),
])
def test_aritmetica_e_relacional_com_bool(expr, op):
    e = erro_de(f"x = {expr};")
    assert f"tipo incompatível: '{op}' exige operandos int" in e.mensagem


@pytest.mark.parametrize("expr", ["1 == true", "false != 0"])
def test_igualdade_entre_tipos_diferentes(expr):
    assert "exige operandos do mesmo tipo" in erro_de(f"x = {expr};").mensagem


def test_menos_unario_em_bool():
    assert "'-' unário exige int, recebeu bool" in erro_de("x = -true;").mensagem


# ---------------- Condição não booleana ----------------

def test_condicao_nao_booleana_no_while():
    e = erro_de("x = 3; while (x) { x = x - 1; }")
    assert e.mensagem == "condição do while deve ser booleana, mas é do tipo int"


def test_condicao_nao_booleana_no_for():
    assert "condição do for deve ser booleana" in erro_de("for (i = 0; i + 1; i = i + 1) { }").mensagem


def test_condicao_nao_booleana_no_if():
    assert "condição do if deve ser booleana" in erro_de("if (1) { }").mensagem


# ---------------- Comportamento geral ----------------

def test_saida_anterior_ao_erro_e_preservada():
    saida: list[str] = []
    erro_de("print(1); print(2); print(nada);", saida=saida.append)
    assert saida == ["1", "2"]


def test_erro_semantico_dentro_do_laco_interrompe_na_iteracao_certa():
    saida: list[str] = []
    e = erro_de("for (i = 3; i > -1; i = i - 1) { print(6 / i); }", saida=saida.append)
    assert saida == ["2", "3", "6"]
    assert e.mensagem == "divisão por zero"


def test_erros_de_fases_anteriores_nao_sao_semanticos():
    with pytest.raises(ErroLexico):
        executar("x = @;")
    with pytest.raises(ErroSintatico):
        executar("x = (1 + ;")

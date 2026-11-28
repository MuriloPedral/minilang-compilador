"""Testes do parser com entradas INVÁLIDAS (itens c e f, categoria: erros sintáticos).

Resultado esperado: cada entrada lança ErroSintatico; a mensagem indica o que
era esperado e o que foi encontrado, na posição (linha, coluna) do token problemático.
Exemplos:
  - "x = (1 + ;"                       -> expressão esperada, encontrado ';'
  - "for (i = 0; i < 10) { }"          -> esperado ';' após a condição do for ... encontrado ')'
  - "for (i = 0; i < 10; ) { }"        -> esperado identificador no início da atualização do for
  - "for (;;) { }"                     -> esperado identificador no início da inicialização do for
  - "while x < 3 { }"                  -> esperado '(' após 'while'
  - "x = 1 < 2 < 3;"                   -> comparações relacionais encadeadas não são permitidas
"""

from pathlib import Path

import pytest

from src.parser import ErroSintatico, analisar

RAIZ = Path(__file__).resolve().parents[2]


def erro_de(fonte) -> ErroSintatico:
    with pytest.raises(ErroSintatico) as info:
        analisar(fonte)
    return info.value


# ---------------- Expressões ----------------

def test_expressao_incompleta_do_enunciado():
    e = erro_de("x = (1 + ;")
    assert "expressão esperada, encontrado ';'" in e.mensagem
    assert (e.linha, e.coluna) == (1, 10)


def test_parentese_nao_fechado():
    e = erro_de("x = (1 + 2;")
    assert "')' para fechar o '(' aberto na linha 1, coluna 5" in e.mensagem


def test_operador_sem_operando_direito():
    assert "expressão esperada" in erro_de("x = 1 * ;").mensagem


def test_comparacoes_relacionais_encadeadas():
    assert "relacionais encadeadas" in erro_de("x = 1 < 2 < 3;").mensagem


def test_comparacoes_de_igualdade_encadeadas():
    assert "igualdade encadeadas" in erro_de("x = 1 == 1 == true;").mensagem


# ---------------- Comandos ----------------

def test_falta_ponto_e_virgula():
    e = erro_de("x = 1\ny = 2;")
    assert "esperado ';' após a atribuição, encontrado 'y'" in e.mensagem
    assert (e.linha, e.coluna) == (2, 1)


def test_atribuicao_sem_igual():
    assert "esperado '=' após 'x'" in erro_de("x 1;").mensagem


def test_comando_comecando_com_numero():
    assert "início de comando inválido: '5'" in erro_de("5;").mensagem


def test_else_sem_if():
    assert "'else' sem 'if'" in erro_de("else { x = 1; }").mensagem


def test_bloco_nao_fechado():
    e = erro_de("if (true) { x = 1;")
    assert "'}' para fechar o bloco aberto na linha 1, encontrado fim do arquivo" in e.mensagem


def test_print_sem_parenteses():
    assert "esperado '(' após 'print'" in erro_de("print x;").mensagem


def test_if_sem_chaves():
    assert "'{' para abrir o bloco do if" in erro_de("if (x > 0) print(x);").mensagem


# ---------------- Laços mal formados ----------------

def test_for_sem_clausula_de_atualizacao():
    e = erro_de("for (i = 0; i < 10) { print(i); }")
    assert "esperado ';' após a condição do for (o for exige as três cláusulas), encontrado ')'" in e.mensagem
    assert (e.linha, e.coluna) == (1, 19)


def test_for_com_atualizacao_vazia():
    e = erro_de("for (i = 0; i < 10; ) { }")
    assert "identificador no início da atualização do for" in e.mensagem


def test_for_com_clausulas_vazias():
    e = erro_de("for (;;) { }")
    assert "identificador no início da inicialização do for" in e.mensagem


def test_for_com_condicao_vazia():
    assert "expressão esperada, encontrado ';'" in erro_de("for (i = 0; ; i = i + 1) { }").mensagem


def test_for_com_inicializacao_que_nao_e_atribuicao():
    assert "inicialização do for" in erro_de("for (5; i < 3; i = i + 1) { }").mensagem


def test_for_sem_fechar_parentese():
    assert "')' após a atualização do for" in erro_de("for (i = 0; i < 3; i = i + 1 { }").mensagem


def test_while_sem_parenteses():
    assert "esperado '(' após 'while'" in erro_de("while x < 3 { x = x + 1; }").mensagem


def test_while_sem_condicao():
    assert "expressão esperada, encontrado ')'" in erro_de("while () { }").mensagem


def test_while_sem_bloco():
    assert "'{' para abrir o bloco do while" in erro_de("while (true) x = 1;").mensagem


def test_arquivo_exemplos_programa_invalido():
    e = erro_de((RAIZ / "exemplos" / "programa_invalido.ml").read_text(encoding="utf-8"))
    assert "após a condição do for" in e.mensagem
    assert e.linha == 13

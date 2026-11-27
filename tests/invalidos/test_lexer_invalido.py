"""Testes do lexer com entradas INVÁLIDAS (itens b e f, categoria: erros léxicos).

Resultado esperado: cada entrada lança ErroLexico com a mensagem e a posição abaixo.
  - "x = @;"          -> Erro léxico [linha 1, coluna 5]: caractere inválido '@'
  - "x = 1x;"         -> Erro léxico [linha 1, coluna 5]: literal numérico malformado '1x' ...
  - "/* sem fim"      -> Erro léxico [linha 1, coluna 1]: comentário de bloco '/*' não fechado ...
  - "a ! b"           -> Erro léxico [linha 1, coluna 3]: caractere '!' isolado ...
  - "x = #", "$", "ç" -> caractere inválido
"""

import pytest

from src.lexer import ErroLexico, ErroMiniLang, tokenizar


def erro_de(fonte) -> ErroLexico:
    with pytest.raises(ErroLexico) as info:
        tokenizar(fonte)
    return info.value


def test_caractere_invalido_arroba():
    e = erro_de("x = @;")
    assert "caractere inválido '@'" in e.mensagem
    assert (e.linha, e.coluna) == (1, 5)


def test_numero_seguido_de_letra():
    e = erro_de("x = 1x;")
    assert "literal numérico malformado '1x'" in e.mensagem
    assert (e.linha, e.coluna) == (1, 5)


def test_numero_seguido_de_identificador_longo():
    e = erro_de("y = 123abc + 1;")
    assert "'123abc'" in e.mensagem


def test_comentario_de_bloco_nao_fechado():
    e = erro_de("/* sem fim")
    assert "não fechado" in e.mensagem
    assert (e.linha, e.coluna) == (1, 1)


def test_comentario_de_bloco_nao_fechado_terminando_em_estrela():
    e = erro_de("x = 1;\n/* quase fechado *")
    assert "não fechado" in e.mensagem
    assert (e.linha, e.coluna) == (2, 1)


def test_exclamacao_isolada():
    e = erro_de("a ! b")
    assert "'!' isolado" in e.mensagem
    assert (e.linha, e.coluna) == (1, 3)


@pytest.mark.parametrize("c", ["#", "$", "&", "|", "ç", "\"", ".", ","])
def test_outros_caracteres_fora_do_alfabeto(c):
    e = erro_de(f"x = {c};")
    assert f"caractere inválido '{c}'" in e.mensagem


def test_posicao_do_erro_em_linha_posterior():
    e = erro_de("x = 1;\ny = 2;\n  z = @;")
    assert (e.linha, e.coluna) == (3, 7)


def test_mensagem_formatada_por_categoria():
    e = erro_de("@")
    assert isinstance(e, ErroMiniLang)
    assert str(e) == "Erro léxico [linha 1, coluna 1]: caractere inválido '@'"

"""Testes de laço infinito com limite de iterações (itens e e g).

Resultado esperado: um laço que ultrapassa `max_iteracoes` é interrompido com
ErroLimiteIteracoes (subclasse de ErroSemantico), sem travar a suíte:
  "laço while excedeu o limite de N iterações (possível laço infinito)"
Os testes usam limites pequenos (100 a 1000) para rodar em milissegundos.
"""

import pytest

from src.interpreter import (
    MAX_ITERACOES_PADRAO, ErroLimiteIteracoes, ErroSemantico, executar,
)


def erro_de(fonte, max_iteracoes, saida=None) -> ErroLimiteIteracoes:
    with pytest.raises(ErroLimiteIteracoes) as info:
        executar(fonte, saida=saida or (lambda s: None), max_iteracoes=max_iteracoes)
    return info.value


def test_while_true_e_interrompido():
    e = erro_de("while (true) { }", max_iteracoes=1000)
    assert e.mensagem == "laço while excedeu o limite de 1000 iterações (possível laço infinito)"
    assert (e.linha, e.coluna) == (1, 1)


def test_while_sem_atualizar_a_variavel_de_controle():
    e = erro_de("x = 0;\nwhile (x < 10) { print(x); }", max_iteracoes=100)
    assert "laço while excedeu o limite de 100" in e.mensagem
    assert e.linha == 2


def test_for_com_atualizacao_que_nao_avanca():
    e = erro_de("for (i = 0; i < 10; i = i) { }", max_iteracoes=100)
    assert "laço for excedeu o limite de 100" in e.mensagem


def test_for_com_atualizacao_na_direcao_errada():
    e = erro_de("for (i = 0; i < 10; i = i - 1) { }", max_iteracoes=100)
    assert "laço for" in e.mensagem


def test_saida_produzida_antes_da_interrupcao():
    saida: list[str] = []
    erro_de("x = 0; while (true) { print(x); x = x + 1; }", max_iteracoes=3, saida=saida.append)
    assert saida == ["0", "1", "2"]


def test_limite_conta_por_laco_e_nao_global():
    # Dois laços de 80 iterações com limite 100 não devem disparar o erro.
    fonte = """
    for (i = 0; i < 80; i = i + 1) { }
    for (j = 0; j < 80; j = j + 1) { }
    print(i + j);
    """
    saida: list[str] = []
    executar(fonte, saida=saida.append, max_iteracoes=100)
    assert saida == ["160"]


def test_erro_de_limite_e_um_erro_semantico():
    with pytest.raises(ErroSemantico):
        executar("while (true) { }", max_iteracoes=10)


def test_limite_padrao():
    assert MAX_ITERACOES_PADRAO == 10_000

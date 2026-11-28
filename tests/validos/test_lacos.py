"""Testes de borda dos laços while e for (itens e e g).

Resultado esperado (saída de print em cada caso):
  - laço que NÃO executa (condição falsa na entrada)      -> nenhuma saída do corpo
  - laço que executa UMA vez                               -> uma saída
  - laço que executa N vezes                               -> N saídas, em ordem
  - for com atualização que altera a variável de controle  -> passo diferente de 1
  - semântica do for: init; testa; corpo; atualização; testa...
"""

from src.interpreter import executar


def rodar(fonte, **kwargs) -> list[str]:
    saida: list[str] = []
    executar(fonte, saida=saida.append, **kwargs)
    return saida


# ---------------- while ----------------

def test_while_que_nao_executa():
    assert rodar("x = 10; while (x < 0) { print(x); } print(99);") == ["99"]


def test_while_que_executa_uma_vez():
    assert rodar("x = 0; while (x < 1) { print(x); x = x + 1; }") == ["0"]


def test_while_que_executa_n_vezes():
    assert rodar("x = 0; while (x < 5) { print(x); x = x + 1; }") == ["0", "1", "2", "3", "4"]


def test_while_com_condicao_false_literal():
    assert rodar("while (false) { print(1); }") == []


# ---------------- for ----------------

def test_for_que_nao_executa():
    assert rodar("for (i = 5; i < 5; i = i + 1) { print(i); }") == []


def test_for_que_nao_executa_ainda_assim_roda_a_inicializacao():
    assert rodar("for (i = 7; i < 0; i = i + 1) { } print(i);") == ["7"]


def test_for_que_executa_uma_vez():
    assert rodar("for (i = 0; i < 1; i = i + 1) { print(i); }") == ["0"]


def test_for_que_executa_n_vezes():
    assert rodar("for (i = 0; i < 4; i = i + 1) { print(i); }") == ["0", "1", "2", "3"]


def test_for_com_passo_dois():
    assert rodar("for (i = 0; i < 10; i = i + 2) { print(i); }") == ["0", "2", "4", "6", "8"]


def test_for_decrescente():
    assert rodar("for (i = 3; i > 0; i = i - 1) { print(i); }") == ["3", "2", "1"]


def test_for_com_atualizacao_multiplicativa():
    assert rodar("for (i = 1; i < 100; i = i * 3) { print(i); }") == ["1", "3", "9", "27", "81"]


def test_corpo_do_for_alterando_a_variavel_de_controle():
    # O corpo soma 1 e a atualização soma 1: passo efetivo de 2.
    assert rodar("for (i = 0; i < 6; i = i + 1) { print(i); i = i + 1; }") == ["0", "2", "4"]


def test_variavel_de_controle_permanece_apos_o_for():
    # Sem escopo aninhado: i continua definida com o valor que encerrou o laço.
    assert rodar("for (i = 0; i < 3; i = i + 1) { } print(i);") == ["3"]


def test_ordem_de_execucao_do_for():
    # init; testa; corpo; atualização; testa; corpo; atualização; testa (falso)
    fonte = """
    passos = 0;
    for (i = 0; i < 2; i = i + 1) {
        print(i);
        passos = passos + 1;
    }
    print(passos);
    print(i);
    """
    assert rodar(fonte) == ["0", "1", "2", "2"]


# ---------------- aninhamento e limite ----------------

def test_lacos_aninhados():
    fonte = """
    for (i = 1; i <= 2; i = i + 1) {
        j = 0;
        while (j < 2) {
            print(i * 10 + j);
            j = j + 1;
        }
    }
    """
    assert rodar(fonte) == ["10", "11", "20", "21"]


def test_laco_com_exatamente_o_limite_de_iteracoes_e_permitido():
    assert len(rodar("for (i = 0; i < 50; i = i + 1) { print(i); }", max_iteracoes=50)) == 50

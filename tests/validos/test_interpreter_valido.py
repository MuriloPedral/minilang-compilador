"""Testes do interpretador com programas VÁLIDOS (item e).

Resultado esperado: cada programa executa sem erro e a saída produzida por
print (lista de strings, uma por chamada) é exatamente a indicada em cada teste.
A tabela de símbolos guarda o valor e o tipo final de cada variável.
"""

from pathlib import Path

import pytest

from src.interpreter import Interpretador, TabelaSimbolos, executar
from src.parser import analisar

RAIZ = Path(__file__).resolve().parents[2]


def rodar(fonte, **kwargs) -> list[str]:
    saida: list[str] = []
    executar(fonte, saida=saida.append, **kwargs)
    return saida


# ---------------- Expressões ----------------

@pytest.mark.parametrize("expr,esperado", [
    ("1 + 2 * 3", "7"),
    ("(1 + 2) * 3", "9"),
    ("10 - 4 - 3", "3"),          # associatividade à esquerda: (10 - 4) - 3
    ("100 / 10 / 5", "2"),        # (100 / 10) / 5
    ("-5 + 2", "-3"),
    ("--5", "5"),
    ("7 / 2", "3"),               # divisão inteira
    ("-7 / 2", "-3"),             # truncada em direção a zero (não -4)
    ("7 / -2", "-3"),
    ("-7 / -2", "3"),
    ("0 / 5", "0"),
])
def test_aritmetica(expr, esperado):
    assert rodar(f"print({expr});") == [esperado]


@pytest.mark.parametrize("expr,esperado", [
    ("3 < 5", "true"), ("5 < 3", "false"),
    ("3 > 5", "false"), ("5 >= 5", "true"), ("4 <= 3", "false"),
    ("2 == 2", "true"), ("2 != 2", "false"),
    ("true == true", "true"), ("true != false", "true"),
    ("1 + 1 == 2", "true"),
    ("(1 < 2) == (3 > 4)", "false"),
])
def test_comparacoes_e_booleanos(expr, esperado):
    assert rodar(f"print({expr});") == [esperado]


def test_print_de_literais_booleanos():
    assert rodar("print(true); print(false);") == ["true", "false"]


# ---------------- Variáveis e tabela de símbolos ----------------

def test_atribuicao_e_leitura():
    assert rodar("x = 10; y = x * 2; print(y);") == ["20"]


def test_reatribuicao_com_outro_tipo_e_permitida():
    # Decisão de projeto: tipagem dinâmica (o tipo é do valor, não da variável).
    interp = executar("x = 1; x = true;", saida=lambda s: None)
    simbolo = interp.tabela.buscar("x")
    assert (simbolo.tipo, simbolo.valor) == ("bool", True)


def test_tabela_de_simbolos_insercao_e_busca():
    tabela = TabelaSimbolos()
    tabela.inserir("x", 5, linha=1)
    tabela.inserir("x", 6, linha=3)
    s = tabela.buscar("x")
    assert (s.nome, s.tipo, s.valor, s.linha) == ("x", "int", 6, 1)
    assert tabela.contem("x") and not tabela.contem("y")
    assert len(tabela) == 1


def test_tabela_distingue_bool_de_int():
    tabela = TabelaSimbolos()
    tabela.inserir("b", True)
    assert tabela.buscar("b").tipo == "bool"


# ---------------- Comandos ----------------

def test_if_verdadeiro_e_falso():
    fonte = "x = 5; if (x > 0) { print(1); } else { print(2); }"
    assert rodar(fonte) == ["1"]
    assert rodar(fonte.replace("x = 5", "x = -5")) == ["2"]


def test_if_sem_else_com_condicao_falsa_nao_faz_nada():
    assert rodar("if (false) { print(1); } print(2);") == ["2"]


def test_bloco_solto_nao_cria_escopo():
    # Escopo único: variável criada dentro do bloco continua visível fora dele.
    assert rodar("{ x = 3; } print(x);") == ["3"]


def test_variavel_criada_no_if_existe_depois_se_o_ramo_executou():
    assert rodar("if (true) { y = 7; } print(y);") == ["7"]


def test_programa_exemplo_do_enunciado():
    fonte = """
    x = 10;
    y = 2 * (x + 5);
    while (x > 0) { print(x); x = x - 1; }
    soma = 0;
    for (i = 0; i < 5; i = i + 1) { soma = soma + i; }
    if (soma > 20) { print(soma); } else { print(0); }
    """
    assert rodar(fonte) == ["10", "9", "8", "7", "6", "5", "4", "3", "2", "1", "0"]


def test_arquivo_exemplos_programa_valido():
    fonte = (RAIZ / "exemplos" / "programa_valido.ml").read_text(encoding="utf-8")
    assert rodar(fonte) == [
        "30", "10", "9", "8", "7", "6", "5", "4", "3", "2", "1", "0", "120", "true",
    ]


def test_interpretador_usa_print_por_padrao(capsys):
    Interpretador().executar(analisar("print(42);"))
    assert capsys.readouterr().out == "42\n"

def test_inteiro_na_fronteira_pode_ser_calculado_e_impresso():
    maior = "9" * 640
    assert rodar(f"print({maior}); print(-{maior});") == [maior, "-" + maior]
    assert rodar("x=1;for(i=0;i<639;i=i+1){x=x*10;}print(x);") == ["1" + "0" * 639]


def test_profundidade_de_execucao_na_fronteira():
    # Print + 98 operadores + literal = 100 chamadas simultâneas.
    assert rodar("print(" + "+".join(["1"] * 99) + ");") == ["99"]


def test_limite_de_profundidade_nao_acumula_entre_comandos():
    assert rodar("print(1);" * 1500) == ["1"] * 1500

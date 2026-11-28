"""Interpretador e tabela de símbolos da MiniLang (item e).

O interpretador percorre a AST (tree-walking interpreter): cada tipo de nó
tem um método `_exec_<no>` (comandos) ou `_aval_<no>` (expressões).

Tipos em tempo de execução: `int` e `bool`. A verificação semântica é
DINÂMICA: os erros são detectados no momento em que o comando é executado.
Isso é necessário porque:
  - divisão por zero depende do valor calculado;
  - "variável não definida" depende do caminho executado (uma variável
    atribuída só dentro de um if pode ou não existir depois dele).

Uso pela linha de comando:
    python -m src.interpreter exemplos/programa_valido.ml
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from typing import Callable

from .ast_nodes import (
    Atribuicao, Bloco, Booleano, Expressao, For, If, Inteiro, No,
    OpBinaria, OpUnaria, Print, Programa, Variavel, While,
)
from .lexer import ErroMiniLang
from .parser import analisar

MAX_ITERACOES_PADRAO = 10_000

Valor = int | bool


class ErroSemantico(ErroMiniLang):
    categoria = "semântico"


class ErroLimiteIteracoes(ErroSemantico):
    """Laço ultrapassou `max_iteracoes` (provável laço infinito)."""


def tipo_de(valor: Valor) -> str:
    # Em Python, bool é subclasse de int: True + 1 == 2. Por isso o teste usa
    # `type(...) is bool` e não isinstance(valor, int), senão bool passaria por int.
    return "bool" if type(valor) is bool else "int"


def formatar_valor(valor: Valor) -> str:
    if type(valor) is bool:
        return "true" if valor else "false"
    return str(valor)


# --------------------------------------------------------------------------
# Tabela de símbolos
# --------------------------------------------------------------------------

@dataclass
class Simbolo:
    nome: str
    tipo: str          # "int" ou "bool" (tipo do valor atual)
    valor: Valor
    linha: int         # linha da primeira definição


class TabelaSimbolos:
    """Escopo único global (escopo aninhado está fora do escopo do projeto).

    Estrutura: dicionário (tabela hash) nome -> Simbolo.
    Inserção e busca em O(1) em média.
    """

    def __init__(self) -> None:
        self._simbolos: dict[str, Simbolo] = {}

    def inserir(self, nome: str, valor: Valor, linha: int = 0) -> None:
        """Define a variável ou atualiza seu valor e tipo (tipagem dinâmica)."""
        existente = self._simbolos.get(nome)
        linha_def = existente.linha if existente else linha
        self._simbolos[nome] = Simbolo(nome, tipo_de(valor), valor, linha_def)

    def buscar(self, nome: str, linha: int = 0, coluna: int = 0) -> Simbolo:
        """Devolve o símbolo ou lança ErroSemantico se a variável não foi definida."""
        simbolo = self._simbolos.get(nome)
        if simbolo is None:
            raise ErroSemantico(f"variável '{nome}' não definida", linha, coluna)
        return simbolo

    def contem(self, nome: str) -> bool:
        return nome in self._simbolos

    def __len__(self) -> int:
        return len(self._simbolos)


# --------------------------------------------------------------------------
# Interpretador
# --------------------------------------------------------------------------

_ARITMETICOS = {"+", "-", "*", "/"}
_RELACIONAIS = {"<", ">", "<=", ">="}
_IGUALDADE = {"==", "!="}


class Interpretador:
    def __init__(
        self,
        saida: Callable[[str], None] | None = None,
        max_iteracoes: int = MAX_ITERACOES_PADRAO,
    ):
        self.tabela = TabelaSimbolos()
        self.saida = saida if saida is not None else print
        self.max_iteracoes = max_iteracoes

    def executar(self, programa: Programa) -> None:
        for comando in programa.comandos:
            self._executar(comando)

    # ------------------------------------------------------------------
    # Comandos
    # ------------------------------------------------------------------

    def _executar(self, no: No) -> None:
        getattr(self, f"_exec_{type(no).__name__.lower()}")(no)

    def _exec_atribuicao(self, no: Atribuicao) -> None:
        valor = self._avaliar(no.valor)
        self.tabela.inserir(no.nome, valor, no.linha)

    def _exec_print(self, no: Print) -> None:
        self.saida(formatar_valor(self._avaliar(no.expressao)))

    def _exec_bloco(self, no: Bloco) -> None:
        for comando in no.comandos:
            self._executar(comando)

    def _exec_if(self, no: If) -> None:
        if self._condicao(no.condicao, "if"):
            self._executar(no.entao)
        elif no.senao is not None:
            self._executar(no.senao)

    def _exec_while(self, no: While) -> None:
        iteracoes = 0
        while self._condicao(no.condicao, "while"):
            iteracoes = self._contar_iteracao(iteracoes, no, "while")
            self._executar(no.corpo)

    def _exec_for(self, no: For) -> None:
        self._executar(no.inicializacao)
        iteracoes = 0
        while self._condicao(no.condicao, "for"):
            iteracoes = self._contar_iteracao(iteracoes, no, "for")
            self._executar(no.corpo)
            self._executar(no.atualizacao)

    def _condicao(self, expr: Expressao, comando: str) -> bool:
        valor = self._avaliar(expr)
        if type(valor) is not bool:
            raise ErroSemantico(
                f"condição do {comando} deve ser booleana, mas é do tipo {tipo_de(valor)}",
                expr.linha, expr.coluna,
            )
        return valor

    def _contar_iteracao(self, iteracoes: int, no: No, comando: str) -> int:
        iteracoes += 1
        if iteracoes > self.max_iteracoes:
            raise ErroLimiteIteracoes(
                f"laço {comando} excedeu o limite de {self.max_iteracoes} iterações "
                "(possível laço infinito)",
                no.linha, no.coluna,
            )
        return iteracoes

    # ------------------------------------------------------------------
    # Expressões
    # ------------------------------------------------------------------

    def _avaliar(self, no: Expressao) -> Valor:
        return getattr(self, f"_aval_{type(no).__name__.lower()}")(no)

    def _aval_inteiro(self, no: Inteiro) -> Valor:
        return no.valor

    def _aval_booleano(self, no: Booleano) -> Valor:
        return no.valor

    def _aval_variavel(self, no: Variavel) -> Valor:
        return self.tabela.buscar(no.nome, no.linha, no.coluna).valor

    def _aval_opunaria(self, no: OpUnaria) -> Valor:
        valor = self._avaliar(no.operando)
        if type(valor) is not int:
            raise ErroSemantico(
                f"tipo incompatível: '-' unário exige int, recebeu {tipo_de(valor)}",
                no.linha, no.coluna,
            )
        return -valor

    def _aval_opbinaria(self, no: OpBinaria) -> Valor:
        esq = self._avaliar(no.esquerda)
        dir_ = self._avaliar(no.direita)
        op = no.op

        if op in _IGUALDADE:
            if tipo_de(esq) != tipo_de(dir_):
                raise ErroSemantico(
                    f"tipo incompatível: '{op}' exige operandos do mesmo tipo, "
                    f"recebeu {tipo_de(esq)} e {tipo_de(dir_)}",
                    no.linha, no.coluna,
                )
            return esq == dir_ if op == "==" else esq != dir_

        # Aritméticos e relacionais: só int.
        if type(esq) is not int or type(dir_) is not int:
            raise ErroSemantico(
                f"tipo incompatível: '{op}' exige operandos int, "
                f"recebeu {tipo_de(esq)} e {tipo_de(dir_)}",
                no.linha, no.coluna,
            )

        if op == "+":
            return esq + dir_
        if op == "-":
            return esq - dir_
        if op == "*":
            return esq * dir_
        if op == "/":
            if dir_ == 0:
                raise ErroSemantico("divisão por zero", no.linha, no.coluna)
            return _dividir_truncando(esq, dir_)
        if op == "<":
            return esq < dir_
        if op == ">":
            return esq > dir_
        if op == "<=":
            return esq <= dir_
        if op == ">=":
            return esq >= dir_
        raise ErroSemantico(f"operador desconhecido '{op}'", no.linha, no.coluna)  # defensivo


def _dividir_truncando(a: int, b: int) -> int:
    """Divisão inteira truncada em direção a zero (como C e Java): -7 / 2 == -3.

    O operador `//` do Python arredonda para baixo (-7 // 2 == -4), por isso
    não pode ser usado diretamente.
    """
    quociente = abs(a) // abs(b)
    return -quociente if (a < 0) != (b < 0) else quociente


# --------------------------------------------------------------------------
# Atalhos e linha de comando
# --------------------------------------------------------------------------

def executar(
    fonte: str,
    saida: Callable[[str], None] | None = None,
    max_iteracoes: int = MAX_ITERACOES_PADRAO,
) -> Interpretador:
    """Executa o código-fonte completo (lexer -> parser -> interpretador).

    Devolve o interpretador para permitir inspecionar a tabela de símbolos.
    """
    programa = analisar(fonte)
    interpretador = Interpretador(saida=saida, max_iteracoes=max_iteracoes)
    interpretador.executar(programa)
    return interpretador


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 1:
        print("uso: python -m src.interpreter <arquivo.ml>", file=sys.stderr)
        return 2
    try:
        with open(argv[0], encoding="utf-8") as f:
            fonte = f.read()
    except OSError as e:
        print(f"não foi possível ler '{argv[0]}': {e.strerror}", file=sys.stderr)
        return 2
    try:
        executar(fonte)
    except ErroMiniLang as e:
        print(e, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

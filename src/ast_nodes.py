"""Nós da AST (árvore sintática abstrata) da MiniLang (item d).

Cada classe corresponde a uma construção com significado para a execução.
Tokens que só servem para guiar a análise sintática (parênteses, chaves,
ponto e vírgula, a palavra 'else') e as produções intermediárias de
precedência (igualdade, relacional, aditiva...) NÃO viram nós: a precedência
já fica codificada na própria forma da árvore.

Os campos `linha` e `coluna` guardam a posição no fonte apenas para mensagens
de erro. Eles são ignorados na comparação (compare=False), então dois nós são
iguais quando têm a mesma estrutura, independentemente de onde estavam no código.
"""

from __future__ import annotations

from dataclasses import dataclass, field, fields
from typing import Optional, Union


@dataclass
class No:
    linha: int = field(default=0, compare=False, repr=False, kw_only=True)
    coluna: int = field(default=0, compare=False, repr=False, kw_only=True)


# --------------------------------------------------------------------------
# Expressões
# --------------------------------------------------------------------------

@dataclass
class Inteiro(No):
    valor: int


@dataclass
class Booleano(No):
    valor: bool


@dataclass
class Variavel(No):
    nome: str


@dataclass
class OpBinaria(No):
    op: str                 # '+', '-', '*', '/', '<', '>', '<=', '>=', '==', '!='
    esquerda: Expressao
    direita: Expressao


@dataclass
class OpUnaria(No):
    op: str                 # '-'
    operando: Expressao


Expressao = Union[Inteiro, Booleano, Variavel, OpBinaria, OpUnaria]


# --------------------------------------------------------------------------
# Comandos
# --------------------------------------------------------------------------

@dataclass
class Atribuicao(No):
    nome: str
    valor: Expressao


@dataclass
class Print(No):
    expressao: Expressao


@dataclass
class Bloco(No):
    comandos: list[Comando] = field(default_factory=list)


@dataclass
class If(No):
    condicao: Expressao
    entao: Bloco
    senao: Optional[Bloco] = None


@dataclass
class While(No):
    condicao: Expressao
    corpo: Bloco


@dataclass
class For(No):
    inicializacao: Atribuicao
    condicao: Expressao
    atualizacao: Atribuicao
    corpo: Bloco


Comando = Union[Atribuicao, Print, Bloco, If, While, For]


@dataclass
class Programa(No):
    comandos: list[Comando] = field(default_factory=list)


# --------------------------------------------------------------------------
# Impressão da árvore como texto indentado (usada no relatório e na depuração)
# --------------------------------------------------------------------------

_CAMPOS_POSICAO = {"linha", "coluna"}


def _formatar_escalar(valor) -> str:
    if isinstance(valor, bool):
        return "true" if valor else "false"
    return str(valor)


def _rotulo(no: No) -> str:
    partes = [type(no).__name__]
    for f in fields(no):
        if f.name in _CAMPOS_POSICAO:
            continue
        valor = getattr(no, f.name)
        if valor is None or isinstance(valor, (No, list)):
            continue
        partes.append(_formatar_escalar(valor))
    return " ".join(partes)


def _filhos(no: No):
    for f in fields(no):
        if f.name in _CAMPOS_POSICAO:
            continue
        valor = getattr(no, f.name)
        if isinstance(valor, No):
            yield f.name, valor
        elif isinstance(valor, list):
            for item in valor:
                yield None, item


def formatar(no: No, nivel: int = 0, campo: str | None = None) -> str:
    """Devolve a AST como texto indentado, ex.:

    OpBinaria +
      esquerda: Inteiro 1
      direita: OpBinaria *
        esquerda: Inteiro 2
        direita: Inteiro 3
    """
    prefixo = "  " * nivel + (f"{campo}: " if campo else "")
    linhas = [prefixo + _rotulo(no)]
    for nome, filho in _filhos(no):
        linhas.append(formatar(filho, nivel + 1, nome))
    return "\n".join(linhas)

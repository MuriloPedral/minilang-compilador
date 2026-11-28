"""Parser descendente recursivo da MiniLang (item c).

Técnica: análise descendente recursiva preditiva, LL(1).
Cada não terminal da gramática EBNF (docs/gramatica.md) vira um método.
A decisão de qual produção usar é tomada olhando apenas o token atual
(1 token de lookahead), o que é possível porque a gramática:
  - não tem recursão à esquerda (as repetições usam { ... } em EBNF, que
    viram laços `while` no código);
  - tem conjuntos FIRST disjuntos entre as alternativas de `comando`
    (ID, print, if, while, for, '{').

Precedência: um método por nível, do menos para o mais prioritário
(igualdade -> relacional -> aditiva -> multiplicativa -> unaria -> primaria).
Quanto mais "funda" a chamada, mais forte o operador se liga aos operandos.

Associatividade:
  - '+ - * /' são associativos à esquerda: o laço `while` reconstrói a árvore
    sempre colocando o resultado anterior como filho ESQUERDO;
  - '-' unário é associativo à direita (chamada recursiva em `unaria`);
  - comparações são NÃO associativas: a forma `a < b < c` é rejeitada.

Estratégia de erro: o parser para no primeiro erro sintático, sem tentar
recuperação, e informa linha, coluna, o que era esperado e o que foi encontrado.
"""

from __future__ import annotations

from .ast_nodes import (
    Atribuicao, Bloco, Booleano, Comando, Expressao, For, If, Inteiro,
    OpBinaria, OpUnaria, Print, Programa, Variavel, While,
)
from .lexer import ErroMiniLang, Token, tokenizar


# Limites de implementação; não alteram as produções da gramática.
MAX_DIGITOS_INTEIRO = 640
MAX_ANINHAMENTO_SINTATICO = 50


class ErroSintatico(ErroMiniLang):
    categoria = "sintático"


def _descrever(token: Token) -> str:
    return "fim do arquivo" if token.tipo == "EOF" else f"'{token.lexema}'"


_IGUALDADE = ("EQ", "NE")
_RELACIONAL = ("LT", "GT", "LE", "GE")
_ADITIVO = ("PLUS", "MINUS")
_MULTIPLICATIVO = ("STAR", "SLASH")


class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.pos = 0

    # ------------------------------------------------------------------
    # Utilitários
    # ------------------------------------------------------------------

    @property
    def atual(self) -> Token:
        return self.tokens[self.pos]

    def _ver(self, *tipos: str) -> bool:
        return self.atual.tipo in tipos

    def _avancar(self) -> Token:
        token = self.atual
        if token.tipo != "EOF":
            self.pos += 1
        return token

    def _consumir(self, tipo: str, esperado: str) -> Token:
        if self.atual.tipo != tipo:
            raise self._erro(f"esperado {esperado}, encontrado {_descrever(self.atual)}")
        return self._avancar()

    def _erro(self, mensagem: str) -> ErroSintatico:
        return ErroSintatico(mensagem, self.atual.linha, self.atual.coluna)

    # ------------------------------------------------------------------
    # programa = { comando } EOF ;
    # ------------------------------------------------------------------

    def programa(self) -> Programa:
        self._verificar_aninhamento()
        comandos: list[Comando] = []
        try:
            while not self._ver("EOF"):
                comandos.append(self.comando())
        except RecursionError:
            # Salvaguarda para ambientes com uma pilha disponível menor.
            raise self._erro("profundidade sintática excedeu a capacidade de análise") from None
        return Programa(comandos, linha=1, coluna=1)

    def _verificar_aninhamento(self) -> None:
        """Limita delimitadores e sequências de menos antes da análise recursiva."""
        nivel = sinais = 0
        for token in self.tokens:
            if token.tipo in ("LPAREN", "LBRACE"):
                nivel += 1
                if nivel > MAX_ANINHAMENTO_SINTATICO:
                    raise ErroSintatico(
                        f"aninhamento sintático excedeu o limite de {MAX_ANINHAMENTO_SINTATICO} níveis",
                        token.linha, token.coluna,
                    )
            elif token.tipo in ("RPAREN", "RBRACE"):
                nivel = max(0, nivel - 1)
            sinais = sinais + 1 if token.tipo == "MINUS" else 0
            if sinais > MAX_ANINHAMENTO_SINTATICO:
                raise ErroSintatico(
                    f"sequência de '-' excedeu o limite de {MAX_ANINHAMENTO_SINTATICO} sinais",
                    token.linha, token.coluna,
                )

    # ------------------------------------------------------------------
    # comando = atribuicao ";" | print ";" | if | while | for | bloco ;
    # ------------------------------------------------------------------

    def comando(self) -> Comando:
        if self._ver("ID"):
            no = self.atribuicao()
            self._consumir("SEMI", "';' após a atribuição")
            return no
        if self._ver("PRINT"):
            no = self.print_()
            self._consumir("SEMI", "';' após print(...)")
            return no
        if self._ver("IF"):
            return self.if_()
        if self._ver("WHILE"):
            return self.while_()
        if self._ver("FOR"):
            return self.for_()
        if self._ver("LBRACE"):
            return self.bloco()
        if self._ver("ELSE"):
            raise self._erro("'else' sem 'if' correspondente")
        raise self._erro(
            f"início de comando inválido: {_descrever(self.atual)} "
            "(esperado atribuição, print, if, while, for ou bloco)"
        )

    # atribuicao = ID "=" expressao ;
    def atribuicao(self, contexto: str = "atribuição") -> Atribuicao:
        nome = self._consumir("ID", f"identificador no início da {contexto}")
        self._consumir("ASSIGN", f"'=' após '{nome.lexema}'")
        valor = self.expressao()
        return Atribuicao(nome.lexema, valor, linha=nome.linha, coluna=nome.coluna)

    # print = "print" "(" expressao ")" ;
    def print_(self) -> Print:
        t = self._consumir("PRINT", "'print'")
        self._consumir("LPAREN", "'(' após 'print'")
        expr = self.expressao()
        self._consumir("RPAREN", "')' para fechar print(...)")
        return Print(expr, linha=t.linha, coluna=t.coluna)

    # if = "if" "(" expressao ")" bloco [ "else" bloco ] ;
    def if_(self) -> If:
        t = self._avancar()
        self._consumir("LPAREN", "'(' após 'if'")
        condicao = self.expressao()
        self._consumir("RPAREN", "')' após a condição do if")
        entao = self.bloco("if")
        senao = None
        if self._ver("ELSE"):
            self._avancar()
            senao = self.bloco("else")
        return If(condicao, entao, senao, linha=t.linha, coluna=t.coluna)

    # while = "while" "(" expressao ")" bloco ;
    def while_(self) -> While:
        t = self._avancar()
        self._consumir("LPAREN", "'(' após 'while'")
        condicao = self.expressao()
        self._consumir("RPAREN", "')' após a condição do while")
        corpo = self.bloco("while")
        return While(condicao, corpo, linha=t.linha, coluna=t.coluna)

    # for = "for" "(" atribuicao ";" expressao ";" atribuicao ")" bloco ;
    def for_(self) -> For:
        t = self._avancar()
        self._consumir("LPAREN", "'(' após 'for'")
        inicializacao = self.atribuicao("inicialização do for")
        self._consumir("SEMI", "';' após a inicialização do for")
        condicao = self.expressao()
        self._consumir("SEMI", "';' após a condição do for (o for exige as três cláusulas)")
        atualizacao = self.atribuicao("atualização do for")
        self._consumir("RPAREN", "')' após a atualização do for")
        corpo = self.bloco("for")
        return For(inicializacao, condicao, atualizacao, corpo, linha=t.linha, coluna=t.coluna)

    # bloco = "{" { comando } "}" ;
    def bloco(self, dono: str | None = None) -> Bloco:
        contexto = f" do {dono}" if dono else ""
        abre = self._consumir("LBRACE", f"'{{' para abrir o bloco{contexto}")
        comandos: list[Comando] = []
        while not self._ver("RBRACE", "EOF"):
            comandos.append(self.comando())
        self._consumir("RBRACE", f"'}}' para fechar o bloco aberto na linha {abre.linha}")
        return Bloco(comandos, linha=abre.linha, coluna=abre.coluna)

    # ------------------------------------------------------------------
    # Expressões (um método por nível de precedência)
    # ------------------------------------------------------------------

    def expressao(self) -> Expressao:
        return self.igualdade()

    # igualdade = relacional [ ( "==" | "!=" ) relacional ] ;   (não associativo)
    def igualdade(self) -> Expressao:
        esquerda = self.relacional()
        if self._ver(*_IGUALDADE):
            op = self._avancar()
            direita = self.relacional()
            esquerda = OpBinaria(op.lexema, esquerda, direita, linha=op.linha, coluna=op.coluna)
            if self._ver(*_IGUALDADE):
                raise self._erro(
                    "comparações de igualdade encadeadas não são permitidas "
                    "('==' e '!=' são não associativos); use parênteses"
                )
        return esquerda

    # relacional = aditiva [ ( "<" | ">" | "<=" | ">=" ) aditiva ] ;   (não associativo)
    def relacional(self) -> Expressao:
        esquerda = self.aditiva()
        if self._ver(*_RELACIONAL):
            op = self._avancar()
            direita = self.aditiva()
            esquerda = OpBinaria(op.lexema, esquerda, direita, linha=op.linha, coluna=op.coluna)
            if self._ver(*_RELACIONAL):
                raise self._erro(
                    "comparações relacionais encadeadas não são permitidas "
                    "('<', '>', '<=', '>=' são não associativos)"
                )
        return esquerda

    # aditiva = multiplicativa { ( "+" | "-" ) multiplicativa } ;   (assoc. à esquerda)
    def aditiva(self) -> Expressao:
        esquerda = self.multiplicativa()
        while self._ver(*_ADITIVO):
            op = self._avancar()
            direita = self.multiplicativa()
            esquerda = OpBinaria(op.lexema, esquerda, direita, linha=op.linha, coluna=op.coluna)
        return esquerda

    # multiplicativa = unaria { ( "*" | "/" ) unaria } ;   (assoc. à esquerda)
    def multiplicativa(self) -> Expressao:
        esquerda = self.unaria()
        while self._ver(*_MULTIPLICATIVO):
            op = self._avancar()
            direita = self.unaria()
            esquerda = OpBinaria(op.lexema, esquerda, direita, linha=op.linha, coluna=op.coluna)
        return esquerda

    # unaria = "-" unaria | primaria ;   (assoc. à direita)
    def unaria(self) -> Expressao:
        if self._ver("MINUS"):
            op = self._avancar()
            operando = self.unaria()
            return OpUnaria("-", operando, linha=op.linha, coluna=op.coluna)
        return self.primaria()

    # primaria = INT | "true" | "false" | ID | "(" expressao ")" ;
    def primaria(self) -> Expressao:
        t = self.atual
        if t.tipo == "INT":
            self._avancar()
            if len(t.lexema) > MAX_DIGITOS_INTEIRO:
                raise ErroSintatico(
                    f"literal inteiro excedeu o limite de {MAX_DIGITOS_INTEIRO} dígitos",
                    t.linha, t.coluna,
                )
            return Inteiro(int(t.lexema), linha=t.linha, coluna=t.coluna)
        if t.tipo in ("TRUE", "FALSE"):
            self._avancar()
            return Booleano(t.tipo == "TRUE", linha=t.linha, coluna=t.coluna)
        if t.tipo == "ID":
            self._avancar()
            return Variavel(t.lexema, linha=t.linha, coluna=t.coluna)
        if t.tipo == "LPAREN":
            self._avancar()
            expr = self.expressao()
            self._consumir(
                "RPAREN",
                f"')' para fechar o '(' aberto na linha {t.linha}, coluna {t.coluna}",
            )
            return expr
        raise self._erro(f"expressão esperada, encontrado {_descrever(t)}")


def analisar(fonte: str) -> Programa:
    """Atalho: código-fonte -> tokens -> AST. Lança ErroLexico ou ErroSintatico."""
    return Parser(tokenizar(fonte)).programa()

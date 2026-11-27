"""Analisador léxico da MiniLang (item b).

O lexer é a implementação direta de um AFD (autômato finito determinístico)
construído a partir das expressões regulares de cada token (ver
docs/gramatica.md, seção "Lexer"). O código NÃO usa o módulo `re`: ele apenas
consulta a tabela TRANSICOES, que é a mesma tabela de transições documentada.

Estratégia de reconhecimento: maior casamento (maximal munch).
A partir do estado inicial, o autômato consome caracteres enquanto existir
transição definida para (estado atual, classe do próximo caractere).
Quando não há transição, o estado em que o autômato parou decide:
  - estado de aceitação     -> emite o token (ou descarta, se for espaço/comentário);
  - estado de não aceitação -> erro léxico com mensagem específica daquele estado.
"""

from __future__ import annotations

from dataclasses import dataclass


# --------------------------------------------------------------------------
# Erros
# --------------------------------------------------------------------------

class ErroMiniLang(Exception):
    """Base de todos os erros do compilador (léxico, sintático, semântico)."""

    categoria = "MiniLang"

    def __init__(self, mensagem: str, linha: int = 0, coluna: int = 0):
        self.mensagem = mensagem
        self.linha = linha
        self.coluna = coluna
        super().__init__(str(self))

    def __str__(self) -> str:
        return f"Erro {self.categoria} [linha {self.linha}, coluna {self.coluna}]: {self.mensagem}"


class ErroLexico(ErroMiniLang):
    categoria = "léxico"


# --------------------------------------------------------------------------
# Token
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class Token:
    tipo: str      # ex.: "INT", "ID", "WHILE", "PLUS", "EOF"
    lexema: str    # texto exato reconhecido no código-fonte
    linha: int
    coluna: int


# Palavras reservadas: reconhecidas pelo mesmo estado de ID e depois
# reclassificadas por consulta a esta tabela.
PALAVRAS_RESERVADAS = {
    "if": "IF",
    "else": "ELSE",
    "while": "WHILE",
    "for": "FOR",
    "print": "PRINT",
    "true": "TRUE",
    "false": "FALSE",
}


# --------------------------------------------------------------------------
# Alfabeto do autômato: classes de caracteres
# --------------------------------------------------------------------------
# Agrupar caracteres em classes reduz a tabela de transições sem mudar a
# linguagem reconhecida: todos os caracteres de uma classe levam ao mesmo
# estado a partir de qualquer estado.

CLASSES = (
    "letra", "digito", "espaco", "nl",
    "/", "*", "=", "<", ">", "!",
    "+", "-", "(", ")", "{", "}", ";",
    "outro",
)

_SIMBOLOS = set("/*=<>!+-(){};")


def classe_de(c: str) -> str:
    """Mapeia um caractere para a sua classe no alfabeto do autômato."""
    if c == "_" or "a" <= c <= "z" or "A" <= c <= "Z":
        return "letra"
    if "0" <= c <= "9":
        return "digito"
    if c in (" ", "\t", "\r"):
        return "espaco"
    if c == "\n":
        return "nl"
    if c in _SIMBOLOS:
        return c
    return "outro"


# --------------------------------------------------------------------------
# Estados e tabela de transições
# --------------------------------------------------------------------------

ESTADO_INICIAL = "INICIO"


def _construir_transicoes() -> dict[tuple[str, str], str]:
    t: dict[tuple[str, str], str] = {}

    def add(origem: str, classes, destino: str) -> None:
        for c in classes:
            t[(origem, c)] = destino

    # Identificadores e palavras reservadas: letra (letra | digito)*
    add("INICIO", ["letra"], "ID")
    add("ID", ["letra", "digito"], "ID")

    # Inteiros: digito+   (digito seguido de letra -> estado de erro NUM_MAL)
    add("INICIO", ["digito"], "INT")
    add("INT", ["digito"], "INT")
    add("INT", ["letra"], "NUM_MAL")
    add("NUM_MAL", ["letra", "digito"], "NUM_MAL")

    # Espaços em branco e quebras de linha (descartados)
    add("INICIO", ["espaco", "nl"], "ESPACO")
    add("ESPACO", ["espaco", "nl"], "ESPACO")

    # '/', comentário de linha '//' e comentário de bloco '/* ... */'
    add("INICIO", ["/"], "BARRA")
    add("BARRA", ["/"], "COM_LINHA")
    add("COM_LINHA", [c for c in CLASSES if c != "nl"], "COM_LINHA")
    add("BARRA", ["*"], "COM_BLOCO")
    add("COM_BLOCO", [c for c in CLASSES if c != "*"], "COM_BLOCO")
    add("COM_BLOCO", ["*"], "COM_ESTRELA")
    add("COM_ESTRELA", ["*"], "COM_ESTRELA")
    add("COM_ESTRELA", ["/"], "COM_FIM")
    add("COM_ESTRELA", [c for c in CLASSES if c not in ("*", "/")], "COM_BLOCO")

    # Operadores de um ou dois caracteres
    add("INICIO", ["<"], "MENOR")
    add("MENOR", ["="], "MENOR_IG")
    add("INICIO", [">"], "MAIOR")
    add("MAIOR", ["="], "MAIOR_IG")
    add("INICIO", ["="], "ATRIB")
    add("ATRIB", ["="], "IGUAL")
    add("INICIO", ["!"], "EXCL")
    add("EXCL", ["="], "DIF")

    # Símbolos de um caractere
    for simbolo, estado in (
        ("+", "MAIS"), ("-", "MENOS"), ("*", "ESTRELA"),
        ("(", "APAR"), (")", "FPAR"), ("{", "ACHAVE"), ("}", "FCHAVE"),
        (";", "PVIRG"),
    ):
        add("INICIO", [simbolo], estado)

    return t


TRANSICOES = _construir_transicoes()

# Estados de aceitação -> tipo do token emitido (None = reconhecido e descartado)
ACEITACAO: dict[str, str | None] = {
    "ID": "ID",
    "INT": "INT",
    "ESPACO": None,
    "COM_LINHA": None,
    "COM_FIM": None,
    "BARRA": "SLASH",
    "MENOR": "LT",
    "MENOR_IG": "LE",
    "MAIOR": "GT",
    "MAIOR_IG": "GE",
    "ATRIB": "ASSIGN",
    "IGUAL": "EQ",
    "DIF": "NE",
    "MAIS": "PLUS",
    "MENOS": "MINUS",
    "ESTRELA": "STAR",
    "APAR": "LPAREN",
    "FPAR": "RPAREN",
    "ACHAVE": "LBRACE",
    "FCHAVE": "RBRACE",
    "PVIRG": "SEMI",
}

# Estados que NÃO são de aceitação: INICIO, NUM_MAL, COM_BLOCO, COM_ESTRELA, EXCL.


# --------------------------------------------------------------------------
# Lexer
# --------------------------------------------------------------------------

class Lexer:
    def __init__(self, fonte: str):
        self.fonte = fonte
        self.pos = 0
        self.linha = 1
        self.coluna = 1

    def tokenizar(self) -> list[Token]:
        tokens: list[Token] = []
        while self.pos < len(self.fonte):
            token = self._proximo_token()
            if token is not None:
                tokens.append(token)
        tokens.append(Token("EOF", "", self.linha, self.coluna))
        return tokens

    def _avancar(self) -> None:
        if self.fonte[self.pos] == "\n":
            self.linha += 1
            self.coluna = 1
        else:
            self.coluna += 1
        self.pos += 1

    def _proximo_token(self) -> Token | None:
        inicio, linha, coluna = self.pos, self.linha, self.coluna
        estado = ESTADO_INICIAL

        # Executa o AFD até não existir transição (maior casamento).
        while self.pos < len(self.fonte):
            proximo = TRANSICOES.get((estado, classe_de(self.fonte[self.pos])))
            if proximo is None:
                break
            estado = proximo
            self._avancar()

        lexema = self.fonte[inicio:self.pos]

        if estado in ACEITACAO:
            tipo = ACEITACAO[estado]
            if tipo is None:
                return None
            if tipo == "ID":
                tipo = PALAVRAS_RESERVADAS.get(lexema, "ID")
            return Token(tipo, lexema, linha, coluna)

        raise self._erro(estado, lexema, linha, coluna)

    def _erro(self, estado: str, lexema: str, linha: int, coluna: int) -> ErroLexico:
        if estado == ESTADO_INICIAL:
            return ErroLexico(f"caractere inválido '{self.fonte[self.pos]}'", linha, coluna)
        if estado == "NUM_MAL":
            return ErroLexico(
                f"literal numérico malformado '{lexema}': um número não pode ser "
                "seguido de letra (identificadores devem começar com letra ou '_')",
                linha, coluna,
            )
        if estado in ("COM_BLOCO", "COM_ESTRELA"):
            return ErroLexico("comentário de bloco '/*' não fechado (falta '*/')", linha, coluna)
        if estado == "EXCL":
            return ErroLexico("caractere '!' isolado: o único operador com '!' é '!='", linha, coluna)
        return ErroLexico(f"sequência inválida '{lexema}'", linha, coluna)  # defensivo


def tokenizar(fonte: str) -> list[Token]:
    """Atalho: converte o código-fonte em lista de tokens (terminada por EOF)."""
    return Lexer(fonte).tokenizar()

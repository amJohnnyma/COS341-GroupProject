TOKEN_KEYWORDS = {
    "void", "return",
    "num",
    "print",
    "nop",
    "comment",
    "mod",
    "add",
    "sub",
    "mul",
    "div",
    "neg",
    "if", "then", "else",
    "not",
    "and",
    "or",
    "eq",
    "larger",
    "lesser",
    "do",
    "while",
    "until",
}


PUNC = {

    ":", "(", ")", "{", "}", ";", "=",

}



TOKEN_TAG_MAP = {

    "$": "EOF",
    ":": "COLON",
    ";": "SEMICOLON",
    "(": "LPAREN",
    ")": "RPAREN",
    "{": "LBRACE",
    "}": "RBRACE",
    "=": "ASSIGN",

}




class Token:


    def init(self, token_type: str, value: str = ""):

        self.type = token_type

        self.value = value if value is not None else token_type


    def eq(self, other):

        if isinstance(other, str):

            return self.type == other

        return NotImplemented


    def repr(self):

        return f"Token({self.type!r}, {self.value!r})"
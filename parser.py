import xml.etree.ElementTree as ET
#import lexer
import ntstruct as TOKEN

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
    """Represents a single lexical token."""
    def __init__(self, token_type: str, value: str = ""):
        self.type = token_type
        self.value = value if value is not None else token_type

    def __eq__(self, other):
        if isinstance(other, str):
            return self.type == other or self.value == other
        return super().__eq__(other)

    def __repr__(self):
        return f"Token({self.type}, {self.value!r})"


class Lexer:
    """Mock Lexer returning a hardcoded token sequence."""
    def __init__(self):
        self.tokens: list[Token] = [
            # V_DECL
            Token("USER-DEFINED-NAME", "#x"),
            Token("USER-DEFINED-NAME", "#y"),
            Token(":", ":"),
            
            # F_DECL
            Token("num", "num"),
            Token("USER-DEFINED-NAME", "#add_one"),
            Token("(", "("),
            Token("USER-DEFINED-NAME", "#a"),
            Token(")", ")"),
            Token("{", "{"),
            # Inner P
            Token(":", ":"),
            Token(":", ":"),
            Token("USER-DEFINED-NAME", "#a"),
            Token("=", "="),
            Token("add", "add"),
            Token("(", "("),
            Token("USER-DEFINED-NAME", "#a"),
            Token("NUM", "1"),
            Token(")", ")"),
            Token(";", ";"),
            Token("return", "return"),
            Token("(", "("),
            Token("USER-DEFINED-NAME", "#a"),
            Token(")", ")"),
            Token("}", "}"),
            Token(":", ":"),

            # Top-level ALGO
            Token("USER-DEFINED-NAME", "#x"),
            Token("=", "="),
            Token("NUM", "10"),
            Token(";", ";"),
            Token("while", "while"),
            Token("larger", "larger"),
            Token("(", "("),
            Token("USER-DEFINED-NAME", "#x"),
            Token("NUM", "0"),
            Token(")", ")"),
            Token("do", "do"),
            Token("{", "{"),
            Token("print", "print"),
            Token("(", "("),
            Token("USER-DEFINED-NAME", "#x"),
            Token(")", ")"),
            Token(";", ";"),
            Token("}", "}"),
            Token(";", ";"),

            # EOF Marker
            Token("$", "$")
        ]
        self.position = 0

    def lookahead(self) -> str:
        if self.position < len(self.tokens):
            return self.tokens[self.position].type
        return "$"

    def get_next_token(self) -> Token:
        if self.position < len(self.tokens):
            token = self.tokens[self.position]
            self.position += 1
            return token
        return Token("$", "$")

class ParseError(Exception):
    def __init__(self, Exception) -> None:
        print(Exception)

class Node:
    def __init__(self, name:str, is_terminal:bool = False, value:str = ""):
        self.name = name
        self.is_terminal = is_terminal
        self.value = value
        self.children: list["Node"] = []

    def add_child(self, child: "Node"):
        if child is not None:
            self.children.append(child)

    def to_xml_element(self) -> ET.Element:
        elem = ET.Element(self.name)
        if self.is_terminal and self.value:
            elem.text = self.value
        for child in self.children:
            elem.append(child.to_xml_element())
        return elem

    def to_tree_str(self, indent: str = "", is_last: bool = True)->str:
        marker = "└── " if is_last else "├── "
        val_str = f" ({self.value})" if self.is_terminal and self.value else ""
        result = f"{indent}{marker}{self.name}{val_str}\n"

        indent += "    " if is_last else "│   "
        for i, child in enumerate(self.children):
            last = (i == len(self.children) - 1)
            result += child.to_tree_str(indent, last)
        return result
        


class Parser:
    def __init__(self) -> None:
        self.lexer = Lexer()
        self.root : Node
    
    def parse(self) -> Node:
        self.root = self._parse_SPL_PROG()
        return self.root


    def _error(self, expected:str, got:str):
        raise ParseError(f"Syntax Error: Expected {expected}, got {got}")

    def _lookahead(self) -> str:
        return self.lexer.lookahead()



    def _expect(self, expected_token_type: str):
        token = self.lexer.get_next_token()

        if token == expected_token_type or token.type == expected_token_type:
            tag_name = TOKEN_TAG_MAP.get(token.type, str(token.type))
            return Node(name=tag_name, is_terminal=True, value=str(token.value))
        else:
            self._error(expected_token_type, f"{token}")

    def _parse_SPL_PROG(self) -> Node:
        node = Node("SPL_PROG")
        node.add_child(self._parse_P())
        node.add_child(self._expect("$"))
        return node

    def _parse_P(self)-> Node:
        node = Node("P")
        node.add_child(self._parse_V_DECL())
        node.add_child(self._expect(":"))
        node.add_child(self._parse_F_DECL())
        node.add_child(self._expect(":"))
        node.add_child(self._parse_ALGO())
        return node



    def _parse_V_DECL(self)->Node:
        node = Node("V_DECL")
        if self._lookahead() == "USER-DEFINED-NAME": # This should check the first char
            node.add_child(self._expect("USER-DEFINED-NAME"))
            node.add_child(self._parse_V_DECL())
        else:
            node.add_child(Node("ε"))

        return node

    def _parse_F_DECL(self) -> Node:
        node = Node("F_DECL")
        if self._lookahead() in ("void", "num"):
            node.add_child(self._parse_F_TYPE())
            node.add_child(self._parse_F_DECL())
        else:
            node.add_child(Node("ε"))

        return node


    def _parse_F_TYPE(self):
        node = Node("F_TYPE")
        lookahead = self._lookahead()

        if lookahead == "void":
            node.add_child(self._expect("void"))
            node.add_child(self._expect("USER-DEFINED-NAME"))
            node.add_child(self._expect("("))
            node.add_child(self._parse_V_DECL())
            node.add_child(self._expect(")"))
            node.add_child(self._expect("{"))

            node.add_child(self._parse_P())
            node.add_child(self._expect("return"))
            node.add_child(self._expect("}"))
        elif lookahead == "num":
            node.add_child(self._expect("num"))
            node.add_child(self._expect("USER-DEFINED-NAME"))
            node.add_child(self._expect("("))
            node.add_child(self._parse_V_DECL())
            node.add_child(self._expect(")"))
            node.add_child(self._expect("{"))

            node.add_child(self._parse_P())
            node.add_child(self._expect("return"))

            node.add_child(self._expect("("))

            node.add_child(self._parse_TERM())
            node.add_child(self._expect(")"))
            node.add_child(self._expect("}"))
        else:
            self._error("void or num", lookahead)

        return node


    def _parse_ALGO(self)->Node:
        node = Node("ALGO")
        FIRST_INSTR = {"USER-DEFINED-NAME", "print", "nop", "comment", "if", "do", "while", "until"}

        if self._lookahead() in FIRST_INSTR:
            node.add_child(self._parse_INSTR())
            node.add_child(self._expect(";"))
            node.add_child(self._parse_ALGO())
        else:
            node.add_child(Node("EPSILON"))

        return node

    def _parse_OUTP(self)->Node:
        node = Node("OUTP")
        if self._lookahead() == "(":
            node.add_child(self._expect("("))
            node.add_child(self._parse_TERM())
            node.add_child(self._expect(")"))
        else:
            node.add_child(self._expect("STRING"))

        return node


    def _parse_INSTR(self)->Node:
        node = Node("INSTR")
        look = self._lookahead()

        if look == "USER-DEFINED-NAME":
            node.add_child(self._expect("USER-DEFINED-NAME"))
            node.add_child(self._parse_INSTRTAIL())
        elif look == "print":
            node.add_child(self._expect("print"))
            node.add_child(self._parse_OUTP())
        elif look == "nop":
            node.add_child(self._expect("nop"))
        elif look == "comment":
            node.add_child(self._expect("comment"))
            node.add_child(self._expect("STRING"))
        elif look == "if":
            node.add_child(self._parse_BRANCH())
        elif look in ("while", "until", "do"):
            node.add_child(self._parse_LOOP())
        else:
            self._error("Instruction", look)
        return node



    def _parse_INPUT(self)->Node:
        node = Node("INPUT")
        FIRST_TERM = {"USER-DEFINED-NAME", "NUM", "mod", "add", "sub", "mul", "div", "neg"}

        if self._lookahead() in FIRST_TERM:
            node.add_child(self._parse_TERM())
            node.add_child(self._parse_INPUT())
        else:
            node.add_child(Node("EPSILON"))
        return node

    def _parse_INSTRTAIL(self)->Node:
        node = Node("INSTRTAIL")
        look = self._lookahead()

        if look == "(":
            node.add_child(self._expect("("))
            node.add_child(self._parse_INPUT())
            node.add_child(self._expect(")"))
        elif look == "=":
            node.add_child(self._expect("="))
            node.add_child(self._parse_TERM())
        else:
            self._error("( or =", look)

        return node


    def _parse_TERM(self)->Node:
        node = Node("TERM")
        look = self._lookahead()
        
        if look == "USER-DEFINED-NAME":
            node.add_child(self._expect("USER-DEFINED-NAME"))
            node.add_child(self._parse_TERMTAIL())
        elif look == "NUM":
            node.add_child(self._expect("NUM"))
        elif look in ("mod", "add", "sub", "mul", "div"):
            node.add_child(self._expect(look))
            node.add_child(self._expect("("))
            node.add_child(self._parse_TERM())
            node.add_child(self._parse_TERM())
            node.add_child(self._expect(")"))
        else:
            self._error("TERM", look)
        return node

    def _parse_TERMTAIL(self)->Node:
        node = Node("TERMTAIL")
        if self._lookahead() == "(":
            node.add_child(self._expect("("))
            node.add_child(self._parse_INPUT())
            node.add_child(self._expect(")"))
        else:
            node.add_child(Node("EPSILON"))

        return node

    def _parse_BOOL(self)->Node:
        node = Node("BOOL")
        look = self._lookahead()
        
        if look == "not":
            node.add_child(self._expect("not"))
            node.add_child(self._expect("("))
            node.add_child(self._parse_BOOL())
            node.add_child(self._expect(")"))
        elif look in ("and", "or"):
            node.add_child(self._expect(look))
            node.add_child(self._expect("("))
            node.add_child(self._parse_BOOL())
            node.add_child(self._parse_BOOL())
            node.add_child(self._expect(")"))
        elif look in ("eq", "larger", "lesser"):
            node.add_child(self._expect(look))
            node.add_child(self._expect("("))
            node.add_child(self._parse_TERM())
            node.add_child(self._parse_TERM())
            node.add_child(self._expect(")"))
        else:
            self._error("BOOL expression", look)
        return node



    def _parse_BRANCH(self)->Node:
        node = Node("BRANCH")
        node.add_child(self._expect("if"))
        node.add_child(self._parse_BOOL())
        node.add_child(self._expect("then"))
        node.add_child(self._expect("{"))
        node.add_child(self._parse_ALGO())
        node.add_child(self._expect("}"))
        node.add_child(self._expect("else"))
        node.add_child(self._expect("{"))
        node.add_child(self._parse_ALGO())
        node.add_child(self._expect("}"))
        return node

    def _parse_LOOP(self)->Node:
        node = Node("LOOP")
        look = self._lookahead()

        if look in ("while", "until"):
            node.add_child(self._parse_COND())
            node.add_child(self._parse_BOOL())
            node.add_child(self._expect("do"))
            node.add_child(self._expect("{"))
            node.add_child(self._parse_ALGO())
            node.add_child(self._expect("}"))
        elif look == "do":
            node.add_child(self._expect("do"))
            node.add_child(self._expect("{"))
            node.add_child(self._parse_ALGO())
            node.add_child(self._expect("}"))
            node.add_child(self._parse_COND())
            node.add_child(self._parse_BOOL())
        else:
            self._error("LOOP expression", look)
        return node

    def _parse_COND(self)->Node:
        node = Node("COND")
        look = self._lookahead()
        if look in ("while", "until"):
            node.add_child(self._expect(look))
        else:
            self._error("while or until", look)
        return node


def generate_xml_string(root_node: Node) -> str:
    """Converts the root Node into a formatted XML string."""
    xml_elem = root_node.to_xml_element()
    ET.indent(xml_elem, space="    ")
    xml_str = ET.tostring(xml_elem, encoding="unicode")
    return f'<?xml version="1.0" encoding="UTF-8"?>\n{xml_str}'


if __name__ == "__main__":
    parser = Parser()
    root = parser.parse()

    print(root.to_tree_str())

    with open("output.txt", "w", encoding="utf-8") as f:
        f.write(root.to_tree_str())

    with open("output.xml", "w", encoding="utf-8") as f:
        f.write(generate_xml_string(root))

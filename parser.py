
import xml.etree.ElementTree as ET
from lexer import Lexer
from tokens import Token, TOKEN_TAG_MAP



class ParseError(Exception):
   
    def __init__(self, message: str) -> None:
       
        super().__init__(message)



class Node:


    _next_id = 0


    def __init__(self, contents: str, is_terminal: bool = False):
       
        self.id = Node._next_id
        Node._next_id += 1
        self.contents = contents
        self.is_terminal = is_terminal
        self.children: list["Node"] = []
        self.parent: "Node | None" = None


    def add_child(self, child: "Node"):
       
        if child is not None:
           
            child.parent = self
            self.children.append(child)


    def all_nodes(self):

        yield self
        for c in self.children:
            yield from c.all_nodes()



def write_tree_xml(root: Node, filename: str = "tree.xml"):

    tree_el = ET.Element("TREE")


    for node in root.all_nodes():
      
        node_el = ET.SubElement(tree_el, "NODE")

        id_el = ET.SubElement(node_el, "ID")
        id_el.text = str(node.id)

        contents_el = ET.SubElement(node_el, "CONTENTS")
        contents_el.text = node.contents


        if node.children:
           
            children_el = ET.SubElement(node_el, "CHILDREN")
            children_el.text = ",".join(str(c.id) for c in node.children)


        if node.parent is not None:
           
            parent_el = ET.SubElement(node_el, "PARENT")
            parent_el.text = str(node.parent.id)

    ET.indent(tree_el, space="  ")
    xml_str = ET.tostring(tree_el, encoding="unicode")
   
    with open(filename, "w", encoding="utf-8") as f:
        
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write(xml_str)



def tag_for(token_type: str) -> str:
   
    return TOKEN_TAG_MAP.get(token_type, token_type)



class Parser:

    def __init__(self, lexer: Lexer):
      
        self.lexer = lexer
        self._buffered_token = None
        self.root: Node | None = None


    def parse(self) -> Node:
      
        self.root = self._parse_SPL_PROG()
       
        return self.root


    def _error(self, expected: str, got: str):
       
        raise ParseError(f"Syntax Error: Expected {expected}, got {got}")


    def _peek(self) -> Token:
       
        if self._buffered_token is None:
         
            self._buffered_token = self.lexer.get_next_token()
      
        return self._buffered_token


    def _lookahead(self) -> str:
       
        return self._peek().type


    def _expect(self, expected_token_type: str) -> Node:
      
        token = self._peek()
        self._buffered_token = None

        if token.type == expected_token_type:
            return Node(contents=token.value, is_terminal=True)
       
        else:
       
            self._error(expected_token_type, f"{token}")


    def _parse_SPL_PROG(self) -> Node:
       
        node = Node("SPL_PROG")
        node.add_child(self._parse_P())
        node.add_child(self._expect("$"))
      
        return node


    def _parse_P(self) -> Node:
      
        node = Node("P")
        node.add_child(self._parse_V_DECL())
        node.add_child(self._expect(":"))
        node.add_child(self._parse_F_DECL())
        node.add_child(self._expect(":"))
        node.add_child(self._parse_ALGO())
     
        return node


    def _parse_V_DECL(self) -> Node:
      
        node = Node("V_DECL")
      
        if self._lookahead() == "USER-DEFINED-NAME":
      
            node.add_child(self._expect("USER-DEFINED-NAME"))
            node.add_child(self._parse_V_DECL())
      
        else:
     
            node.add_child(Node("epsilon", is_terminal=True))
     
        return node


    def _parse_F_DECL(self) -> Node:
       
        node = Node("F_DECL")
        
        if self._lookahead() in ("void", "num"):
        
            node.add_child(self._parse_F_TYPE())
            node.add_child(self._parse_F_DECL())
       
        else:
          
            node.add_child(Node("epsilon", is_terminal=True))
       
        return node


    def _parse_F_TYPE(self) -> Node:
      
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


    def _parse_ALGO(self) -> Node:
       
        node = Node("ALGO")
        FIRST_INSTR = {"USER-DEFINED-NAME", "print", "nop", "comment", "if", "do", "while", "until"}

        if self._lookahead() in FIRST_INSTR:
          
            node.add_child(self._parse_INSTR())
            node.add_child(self._expect(";"))
            node.add_child(self._parse_ALGO())
      
        else:
          
            node.add_child(Node("epsilon", is_terminal=True))

      
        return node


    def _parse_OUTP(self) -> Node:
       
        node = Node("OUTP")
       
        if self._lookahead() == "(":
          
            node.add_child(self._expect("("))
            node.add_child(self._parse_TERM())
            node.add_child(self._expect(")"))
        
        else:
       
            node.add_child(self._expect("STRING"))
       
        return node


    def _parse_INSTR(self) -> Node:
      
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


    def _parse_INPUT(self) -> Node:
     
        node = Node("INPUT")
       
        FIRST_TERM = {"USER-DEFINED-NAME", "NUM", "mod", "add", "sub", "mul", "div", "neg"}

        if self._lookahead() in FIRST_TERM:
          
            node.add_child(self._parse_TERM())
            node.add_child(self._parse_INPUT())
      
        else:
          
            node.add_child(Node("epsilon", is_terminal=True))
      
        return node


    def _parse_INSTRTAIL(self) -> Node:
     
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


    def _parse_TERM(self) -> Node:
       
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
       
        elif look == "neg":
         
            node.add_child(self._expect("neg"))
            node.add_child(self._expect("("))
            node.add_child(self._parse_TERM())
            node.add_child(self._expect(")"))
       
        else:
            self._error("TERM", look)
       
        return node


    def _parse_TERMTAIL(self) -> Node:
       
        node = Node("TERMTAIL")
       
        if self._lookahead() == "(":
            node.add_child(self._expect("("))
            node.add_child(self._parse_INPUT())
            node.add_child(self._expect(")"))
       
        else:
           
            node.add_child(Node("epsilon", is_terminal=True))
       
        return node


    def _parse_BOOL(self) -> Node:
       
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


    def _parse_BRANCH(self) -> Node:
       
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


    def _parse_LOOP(self) -> Node:
       
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


    def _parse_COND(self) -> Node:
       
        node = Node("COND")
        look = self._lookahead()
       
        if look in ("while", "until"):
       
            node.add_child(self._expect(look))
       
        else:
       
            self._error("while or until", look)
       
        return node



if __name__ == "__main__":
    
    import sys

    
    if len(sys.argv) < 2:
     
        print("Usage: python parser.py <SPL-source-file>")
        sys.exit(1)

    
    with open(sys.argv[1], "r", encoding="utf-8") as f:
      
        source = f.read()

    
    lexer = Lexer(source)
    parser = Parser(lexer)

    
    try:
    
        root = parser.parse()
        write_tree_xml(root, "tree.xml")
        print("Parse successful. Wrote tree.xml")
    
    except ParseError as e:
      
        print(f"SYNTAX ERROR: {e}")
        sys.exit(1)
    
    except Exception as e:
      
        print(f"LEXICAL ERROR: {e}")
        sys.exit(1)

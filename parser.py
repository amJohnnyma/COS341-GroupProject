
import lexer
import ntstruct as TOKEN



# Tree Data Structure
# Token requests -> What is the lexers function to retrieve the next token

class ParseError:
    def __init__(self, Exception) -> None:
        print(Exception)




class Parser:
    def __init__(self) -> None:
        self.lexer = lexer.Lexer()
        self.tree = tree
    
    def parse(self):
        self._parse_SPL_PROG()


    def _error(self, msg):
        pass

    def _lookahead(self, TOKEN):
        token = lexer.lookahead()



    def _expect(self, TOKEN):
        token = lexer.get_next_token()
        # Check first idx incase it is a USER-DEFINED-NAME -> Must start with #


        if token == TOKEN:
            self.tree.add(token)
            return true
        else:
            #Raise errorV_DECL
            pass

    def _parse_SPL_PROG(self):
        self.tree.add("SPL_PROG")
        self.tree.add(self._parse_P())
        self._expect("$")

    def _parse_P(self):

        self.tree.add("PROG")
        self.tree.add(self._parse_V_DECL())
        self._expect(":")
        self.tree.add(self._parse_F_DECL())
        self._expect(":")
        self.tree.add(self._parse_ALGO())
        self._expect(":")


    def _parse_V_DECL(self):

        self.tree.add("V_DECL")
        if self._expect(" ") #epsilon
            return
        # else
        self._expect("#")
        #add UDN to some list and tree
        self.tree.add(self._parse_V_DECL())
        return
    def _parse_F_DECL(self):

        self.tree.add("F_DECL")
        pass
    def _parse_F_TYPE(self):

        self.tree.add("F_TYPE")
        pass
    def _parse_ALGO(self):

        self.tree.add("ALGO")
        pass
    def _parse_OUTP(self):

        self.tree.add("OUTP")
        
        pass
    def _parse_INSTR(self):

        self.tree.add("INSTR")
        pass
    def _parse_INSTRTAIL(self):

        self.tree.add("INSTRTAIL")
        pass
    def _parse_INPUT(self):

        self.tree.add("INPUT")
        pass
    def _parse_TERM(self):

        self.tree.add("TERM")
        pass

    def _parse_TERMTAIL(self):

        self.tree.add("TERMTAIL")
        pass
    def _parse_BRANCH(self):

        self.tree.add("BRANCH")
        pass
    def _parse_BOOL(self):

        self.tree.add("BOOL")
        pass
    def _parse_LOOP(self):

        self.tree.add("LOOP")
        pass
    def _parse_COND(self):

        self.tree.add("COND")
        pass




    def get_tree(self):
        #return the tree
        pass


def generate_xml():
    parser = Parser()
    parser.parse()
    tree = parser.get_tree()
    # tree to xml
    # return xml



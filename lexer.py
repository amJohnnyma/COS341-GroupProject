import re
from tokens import Token, TOKEN_KEYWORDS, PUNC



NUM_RE = re.compile(

    r"^(0|(-?0\.[0-9]*[1-9])|(-?[1-9][0-9]*\.[0-9]*[1-9])|(-?[1-9][0-9]*))$"

)





class LexError(Exception):
   
    pass



class Lexer:


    def __init__(self, source: str):
      
        self.source = source
       
        self.pos = 0


    def _next_chunk(self, start_pos: int):

        pos = start_pos

        while pos < len(self.source) and self.source[pos] in (" ", "\n", "\r", "\t"):
           
            pos += 1

        if pos >= len(self.source):
            
            return None, pos

        chunk_start = pos

        if self.source[pos] == '"':
            pos += 1
            while pos < len(self.source):
                if self.source[pos] == '"':
                    pos+=1
                    break
                if self.source[pos] in ("/n", "/r"):
                    break
                pos += 1

            return self.source[chunk_start:pos], pos

        while pos < len(self.source) and self.source[pos] not in (" ", "\n", "\r", "\t"):
         
            pos += 1


        return self.source[chunk_start:pos], pos


    def get_next_token(self) -> Token:
      
        chunk, new_pos = self._next_chunk(self.pos)
       
        self.pos = new_pos

        if chunk is None:
          
            return Token("$", "$")

        return self.classify(chunk)


    def look_ahead(self) -> Token:
      
        chunk, _ = self._next_chunk(self.pos)

        if chunk is None:
           
            return Token("$", "$")
       
        return self.classify(chunk)


    def classify(self, token: str) -> Token:

        if token.startswith("#"):
            
            return self.check_UDN(token)

        elif token.startswith('"'):
           
            return self.check_string(token)

        elif token[0].isdigit() or (token[0] == "-" and len(token) > 1):
           
            return self.check_num(token)

        else:
           
            return self.check_keyword_symbol(token)


    def check_UDN(self, token: str) -> Token:

        for char in token[1:]:

            if not (("a" <= char <= "z") or ("0" <= char <= "9")):

                raise LexError(f"Invalid USER-DEFINED-NAME: '{token}'")

        return Token("USER-DEFINED-NAME", token)



    def check_string(self, token: str) -> Token:

        if not token.endswith('"') or len(token) < 2:
           
            raise LexError(f"Invalid STRING: '{token}'")

        for char in token[1:-1]:
          
            if not (
                ("a" <= char <= "z")
                or ("0" <= char <= "9")
                or char in (" ", ",", ".", ":", "-", "?", "!")
           
            ):
           
                raise LexError(f"Invalid STRING: '{token}'")

       
        return Token("STRING", token)


    def check_num(self, token: str) -> Token:


        if not NUM_RE.match(token):
         
            raise LexError(f"Invalid NUM: '{token}'")
       
        
        return Token("NUM", token)


    def check_keyword_symbol(self, token: str) -> Token:
      
        if token == "$":
       
            return Token("$", "$")
        
        if token in TOKEN_KEYWORDS:
       
            return Token(token, token)
        
        if token in PUNC:
       
            return Token(token, token)
        
       
        raise LexError(f"Unrecognized token: '{token}'")

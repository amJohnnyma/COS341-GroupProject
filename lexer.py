import ntstruct

class Lexer:
    
    def __init__(self, source: str):
        self.source = source
        self.pos = 0
    
    def get_next_token(self):
        while (self.pos < len(self.source) and self.source[self.pos] in [" ", "\n", "\r"]):
            self.pos += 1
        if self.pos >= len(self.source):
            return None
        startPos = self.pos

        while (self.pos < len(self.source) and self.source[self.pos] not in [" ", "\n", "\r"]):
            self.pos += 1
            
        token = self.source[startPos:self.pos]
        return self.classify(token)

    def classify(self, token):
        if token.startswith("#"):
            return self.check_UDN(token)
        elif token.startswith('"'):
            return self.check_string(token)
        elif token[0].isdigit() or token[0] == "-":
            return self.check_num(token)
        
        else:
            return self.check_keyword_symbol(token)
    
    def check_UDN(self, token):
        for char in token[1:]:
            if not (('a' <= char <= 'z') or ('0' <= char <= '9')):
                raise ValueError(f"UDN: {token} is invalid")
        return (token)
    
    def check_string(self, token):
        if not token.endswith('"'):
            raise ValueError(f"String: {token} is invalid")
        for char in token[1:-1]:
            if not (('a' <= char <= 'z') or ('0' <= char <= '9') or (char == ',') or (char == '.') or (char == ':') or (char == '-') or (char == '?') or (char == '!')):
                raise ValueError(f"String: {token} is invalid")

        return (token)
    
    def check_num(self, token):
        pass
    
    def check_keyword_symbol(self, token):
        pass

    def look_ahead(self):
        temp_pos = self.pos
        while (temp_pos < len(self.source) and self.source[temp_pos] in [" ", "\n", "\r"]):
            temp_pos += 1
        if temp_pos >= len(self.source):
            return None
        startPos = temp_pos

        while (temp_pos < len(self.source) and self.source[temp_pos] not in [" ", "\n", "\r"]):
            temp_pos += 1
            
        token = self.source[startPos:temp_pos]
        return self.classify(token)


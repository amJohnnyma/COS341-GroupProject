import ntstruct

class Lexer:
    _TOKEN[] = {ntstruct.NTSTRUCT(2)} 
    
    def __init__(self) -> None:
        pass
    def _next_token(self):
        pass


def get_next_token():
    # Must be a singleton of type
    object = Lexer()
    object.__init__()
    object._next_token()

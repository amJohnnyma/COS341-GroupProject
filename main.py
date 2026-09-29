from parser import Parser, ParseError, write_tree_xml
from lexer import Lexer
from symbol_table import SymbolTable
from tree_crawl import TreeCrawl
from semantic_check import run_all_checks

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
        crawler = TreeCrawl("tree.xml")
        crawler.print_tree()
        crawler.print_all_scopes()
        symbol_table = SymbolTable(crawler)

        errors = run_all_checks(crawler, symbol_table)
        if errors: 
            for error in errors:
                print(error)
            sys.exit(1)

        symbol_table.print_table()
    
    except ParseError as e:
      
        print(f"SYNTAX ERROR: {e}")
        sys.exit(1)
    
    except Exception as e:
      
        print(f"LEXICAL ERROR: {e}")
        sys.exit(1)


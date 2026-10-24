from parser import Parser, ParseError, write_tree_xml
from lexer import Lexer
from symbol_table import SymbolTable, Type
from tree_crawl import TreeCrawl
from semantic_check import run_all_checks
from type_analyser import TypeAnalyser, TypeAnalysisError
from code_generator import CodeGenerator
from pathlib import Path





if __name__ == "__main__":
    import sys

    # Windows consoles/pipes default to cp1252, which can't print the tree's box-drawing characters
    sys.stdout.reconfigure(encoding="utf-8")

    if len(sys.argv) < 2:
        print("Usage: python main.py <SPL-source-file>")
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
        type_analyser = TypeAnalyser(symbol_table)



        errors = run_all_checks(crawler, symbol_table)
        if errors:
            for error in errors:
                print(error)
            sys.exit(1)

        type_analyser.perform_type_checking()
        symbol_table.print_table()

        print("--- Code Generation Started ---")
        



       
        program_type = Type.NUMERIC
        for node in crawler.nodes.values():
            if node.contents and "." in node.contents:
                program_type = Type.FLOAT_NUMERIC
                break


        
        codegen = CodeGenerator(symbol_table, program_type)
        root_id = next(nid for nid, node in crawler.nodes.items() if node.parent is None)
        
        codegen.trans_SPL_PROG(root_id)

        filename = Path(sys.argv[1]).stem
        
        with open(filename + ".c", "w", encoding="utf-8") as f:
            for line in codegen.output:
                f.write(line + "\n")


        print(f"--- Code Generation Successful: Wrote output in C ---")
        print(f"--- Build with: gcc {filename}.c -o {filename}")
        print(f"--- Run with: ./{filename}")




    except ParseError as e:
        print(f"SYNTAX ERROR: {e}")
        sys.exit(1)
    except TypeAnalysisError as e:
        print(e)
        sys.exit(1)
    except Exception as e:
        print(f"LEXICAL ERROR: {e}")
        sys.exit(1)

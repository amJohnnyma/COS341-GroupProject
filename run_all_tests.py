
import contextlib
import glob
import io
import os
import sys

from lexer import Lexer
import parser as parser_module
from parser import Parser, write_tree_xml
from tree_crawl import TreeCrawl
from symbol_table import SymbolTable, Type
from semantic_check import run_all_checks
import type_analyser
from type_analyser import TypeAnalyser
from code_generator import CodeGenerator

ErrorClass = getattr(type_analyser, "TypeAnalysisError", TypeError)
CONFLICT = "A float-integer-conflict might perhaps be possible"

for path in sorted(glob.glob("tests/progs/*.txt")):
    name = os.path.basename(path)
    expect_ok = name.startswith("ok_")

    parser_module.Node._next_id = 0
    root = Parser(Lexer(open(path).read())).parse()
    write_tree_xml(root, "tree.xml")
    crawler = TreeCrawl("tree.xml")
    st = SymbolTable(crawler)

    errors_2a = run_all_checks(crawler, st)
    if errors_2a:
        print(f"{name:<32} FAIL (phase 2a errors: {errors_2a})")
        continue

    try:
        with contextlib.redirect_stdout(io.StringIO()):
            TypeAnalyser(st).perform_type_checking()
        errors = []
    except ErrorClass as e:
        errors = [str(e)]

    passed = (not errors) if expect_ok else bool(errors)
    if name == "bad_mod_and_div.spl":
        passed = errors == [CONFLICT]

    program_type = Type.NUMERIC 
    
    codegen = CodeGenerator(st, program_type)
    root_id = next(nid for nid, node in crawler.nodes.items() if node.parent is None)
    
    codegen.trans_SPL_PROG(root_id)
    
    with open(path + ".c", "w") as f:
        for line in codegen.output:
            f.write(line + "\n")


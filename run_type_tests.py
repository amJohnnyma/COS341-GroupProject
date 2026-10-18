import contextlib
import glob
import io
import os
import sys

from lexer import Lexer
import parser as parser_module
from parser import Parser, write_tree_xml
from tree_crawl import TreeCrawl
from symbol_table import SymbolTable
from semantic_check import run_all_checks
import type_analyser
from type_analyser import TypeAnalyser

ErrorClass = getattr(type_analyser, "TypeAnalysisError", TypeError)
CONFLICT = "A float-integer-conflict might perhaps be possible"

failed = 0
total = 0
for path in sorted(glob.glob("tests/types/*.spl")):
    name = os.path.basename(path)
    expect_ok = name.startswith("ok_")
    total += 1

    parser_module.Node._next_id = 0
    root = Parser(Lexer(open(path).read())).parse()
    write_tree_xml(root, "tree.xml")
    crawler = TreeCrawl("tree.xml")
    st = SymbolTable(crawler)

    errors_2a = run_all_checks(crawler, st)
    if errors_2a:
        failed += 1
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

    if not passed:
        failed += 1
    print(f"{name:<32} {'PASS' if passed else 'FAIL'}")
    for e in errors:
        print(f"    {e}")

print()
print(f"{total - failed} of {total} passed")
sys.exit(1 if failed else 0)

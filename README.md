# COS341 Group Project (Group) - SPL Compiler Front-End & Code Generator

A lexical analyzer, LL(1) top-down parser, syntax tree visualizer, semantic analyzer, and target code generator for the Simple Programming Language (SPL), built for COS341.

## Members
| Member Name | Student Number | Role |
| :--- | :--- | :--- |
| **Christopher Adolph** | 23535548 | Speaker |
| **Dewald Colesky** | 23536030 | Developer |
| **Heinrich Romer** | 23538181 | Developer |
| **Jonty Honey** | 23536862 | Developer |


## What this project does

- **Phase 1:** Lexing, parsing, and syntax tree generation (writes `tree.xml`)

- **Phase 2a:** Semantic analysis, including scope resolution, symbol table construction, and name/function rule checking

- **Phase 2b / 1st Class:** Target code generation, translating SPL source files into human-legible **C** code (`output.c`), compiled and tested using standard `gcc` environments.


## Requirements

Python 3.10 or newer.

For the optional graph visualizer only, you also need Graphviz.

To create an executable PyInstaller is required.

### Build the executable

Install PyInstaller:

```bash
pip install pyinstaller

```

Build a single-file executable from `parser.py` (or `main.py`):

```bash
pyinstaller --onefile --name group-8 main.py

```

## Usage

### Executable Usage

---

Run the executable (program file must be next to executable):

```bash
./group-8 <filename>

```

---

### Developer Usage

---

Run the parser, semantic analyzer, and code generator manually (must be next to main.py):

```bash
python3 main.py <filename>

```

This will run all compiler phases and output `<filename>.c`.

#### Compiling and Running Generated C Code

To compile and execute the generated C target code using `gcc`:

```bash
gcc output.c -o program
./program

```

Generate a visual graph of the tree (optional, requires Graphviz):

```bash
python3 graph_gen.py

```

This converts `tree.xml` into `syntax_tree.png`.

---

On success, this writes `tree.xml` (the syntax tree in the required ID, CONTENTS, CHILDREN, PARENT format) and `output.c` (the generated target code).

On failure, it prints one of:

* `SYNTAX ERROR: ...` if the input does not match the SPL grammar
* `LEXICAL ERROR: ...` if the input contains an invalid token
* One or more `SEMANTIC ERROR: ...` lines if the input is syntactically valid but violates a naming, scope, or function rule

## Important note about the end of input

The pseudo symbol `$` is NOT literally included at the end of a real test file. `$` is only used to talk about the grammar and the parser, it is not an actual member symbol of the SPL language itself. Our lexer automatically produces an end of file `$` token once it reaches the end of the input, whether or not the file itself contains a literal `$` character.

## Project structure

| File | Owner | Purpose |
| --- | --- | --- |
| `tokens.py` | shared | Shared `Token` class, keyword and symbol tables |
| `lexer.py` | shared | Tokenizes SPL source into a stream of `Token`s |
| `parser.py` | shared | Recursive descent LL(1) parser, builds the syntax tree and writes `tree.xml` |
| `graph_gen.py` | shared | Renders `tree.xml` as a `syntax_tree.png` image using Graphviz |
| `tree_crawl.py` | Colesky | Walks the syntax tree, assigns scope levels, builds the scope hierarchy |
| `symbol_table.py` | Jonty | Builds the symbol table from the scope tree, assigns unique internal (`sys###`) names |
| `variable_rules.py` | Heinrich | Checks variable declaration and usage rules: ancestor lookup, no duplicates, no parameter masking |
| `function_rules.py` | Christopher | Checks function rules: name uniqueness, strictly hierarchic call resolution, recursion detection |
| `code_generator.py` | Christopher | Translates the checked AST and symbol table into human-legible C source code (`<filename>.c`) |
| `semantic_check.py` | shared | Combines all semantic rule checks into one entry point |

## Grammar

```
SPL_PROG -> P $
P        -> V_DECL : F_DECL : ALGO
V_DECL   -> epsilon | USER-DEFINED-NAME V_DECL
F_DECL   -> epsilon | F_TYPE F_DECL
F_TYPE   -> void NAME ( V_DECL ) { P return }
         | num  NAME ( V_DECL ) { P return ( TERM ) }
ALGO     -> epsilon | INSTR ; ALGO
INSTR    -> USER-DEFINED-NAME INSTRTAIL | print OUTP | nop
         | comment STRING | BRANCH | LOOP
INSTRTAIL -> ( INPUT ) | = TERM
TERM     -> USER-DEFINED-NAME TERMTAIL | NUM
         | mod/add/sub/mul/div ( TERM TERM ) | neg ( TERM )
BRANCH   -> if BOOL then { ALGO } else { ALGO }
BOOL     -> not(BOOL) | and/or(BOOL BOOL) | eq/larger/lesser(TERM TERM)
LOOP     -> COND BOOL do { ALGO } | do { ALGO } COND BOOL
COND     -> while | until

```

Left factored for LL(1) parsing. `INSTRTAIL` and `TERMTAIL` resolve the shared `USER-DEFINED-NAME` prefix with one token of lookahead.

## Semantic rules implemented

Variables: a declared name must exist in the usage's own scope or an ancestor scope, with the nearest declaration winning. No two declarations of the same kind are allowed at one scope level. A function's local variables may not mask its own parameters.

Functions: no duplicate function names are allowed at a scope level. Function calls are strictly hierarchic, meaning a call must resolve within the caller's own immediate scope, never an ancestor's. This one rule structurally blocks both direct and indirect recursion, along with sideways calls between sibling functions' private helpers.

## Code Generation & Target Environment Notes

* **Target Code Language:** Standard **C** (`<filename>.c`), structured to be human-legible for inspection.
* **Preferred Run-Test Environment:** Fully compliant with standard C compilers (`gcc`, specifically tested against `gcc 15+`).
* **Submission Tier:** Submitted under the **"1st Class" Category** (incorporating full semantic analysis, type checking, and target code generation).

## Status

* [x] Phase 1: Lexer, Parser, Syntax Tree (`tree.xml`)
* [x] Phase 2a: Scope analysis, Symbol Table, Variable and Function semantic rules
* [x] Phase 2b: Target Code Generation (`output.c`) compatible with `gcc`
* [x] Executable build and packaging for submission

```

---

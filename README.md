# COS341 Group Project - SPL Compiler Front-End

A lexical analyzer, LL(1) top-down parser, syntax tree visualizer, and semantic analyzer for the Simple Programming Language (SPL), built for COS341.

## What this project does

- Phase 1: Lexing, parsing, and syntax tree generation (writes `tree.xml`)
- Phase 2a: Semantic analysis, including scope resolution, symbol table construction, and name/function rule checking

## Requirements

Python 3.10 or newer.

For the optional graph visualizer only, you also need Graphviz.

## Setup

Create and activate a virtual environment:

```
python3 -m venv .venv
source .venv/bin/activate
```

Install the Python wrapper for Graphviz (only needed if you want the tree image, not needed for parsing itself):

```
pip install graphviz
```

Graphviz must also be installed on your operating system for the image renderer to work:

* Linux (Ubuntu/Debian): `sudo apt install graphviz`
* macOS: `brew install graphviz`
* Windows: download from graphviz.org and add it to PATH

## Usage

Run the parser and semantic analyzer on an SPL source file:

```
python3 parser.py <filename>
```

On success, this writes `tree.xml` (the syntax tree in the required ID, CONTENTS, CHILDREN, PARENT format).

On failure, it prints one of:

* `SYNTAX ERROR: ...` if the input does not match the SPL grammar
* `LEXICAL ERROR: ...` if the input contains an invalid token
* One or more `SEMANTIC ERROR: ...` lines if the input is syntactically valid but violates a naming, scope, or function rule

Generate a visual graph of the tree (optional, requires Graphviz):

```
python3 graph_gen.py
```

This converts `tree.xml` into `syntax_tree.png`.

## Important note about the end of input

The pseudo symbol `$` is NOT literally included at the end of a real test file. `$` is only used to talk about the grammar and the parser, it is not an actual member symbol of the SPL language itself. Our lexer automatically produces an end of file `$` token once it reaches the end of the input, whether or not the file itself contains a literal `$` character. Do not add code that requires a literal `$` at the end of the file, since real grading test files will not have one.

## Project structure

| File | Owner | Purpose |
|---|---|---|
| `tokens.py` | shared | Shared `Token` class, keyword and symbol tables |
| `lexer.py` | shared | Tokenizes SPL source into a stream of `Token`s |
| `parser.py` | shared | Recursive descent LL(1) parser, builds the syntax tree and writes `tree.xml` |
| `graph_gen.py` | shared | Renders `tree.xml` as a `syntax_tree.png` image using Graphviz |
| `tree_crawl.py` | Colesky | Walks the syntax tree, assigns scope levels, builds the scope hierarchy |
| `symbol_table.py` | Jonty | Builds the symbol table from the scope tree, assigns unique internal (`sys###`) names |
| `variable_rules.py` | Heinrich | Checks variable declaration and usage rules: ancestor lookup, no duplicates, no parameter masking |
| `function_rules.py` | Christopher | Checks function rules: name uniqueness, strictly hierarchic call resolution, recursion detection |
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

## Test cases

### Basic statements

Assignment:
```
: : #x = 5 ; $
```

Arithmetic addition:
```
: : #x = add ( 3 4 ) ; $
```

Negation:
```
: : #x = neg ( 9 ) ; $
```

Function call instruction:
```
: : #log ( 1 ) ; $
```

Branching (if then else):
```
: : if eq ( #x 0 ) then { print ( #x ) ; } else { nop ; } ; $
```

While loop:
```
: : while larger ( #x 0 ) do { #x = sub ( #x 1 ) ; } ; $
```

Do until loop:
```
: : do { nop ; } until eq ( #x 0 ) ; $
```

### Advanced benchmarks

Recursion and arithmetic (factorial). Tests num function declarations, local variable declarations, recursive calls, and nested arithmetic expressions:
```
#result #temp :
num #fact ( #n ) {
  #res : :
  if eq ( #n 0 ) then {
    #res = 1 ;
  } else {
    #res = mul ( #n #fact ( sub ( #n 1 ) ) ) ;
  } ;
  return ( #res )
} :
#result = #fact ( 5 ) ;
print ( #result ) ;
$
```

Control flow, strings, and void functions. Tests void functions, nested loops (while and do until), multi variable conditions (and, or, not), and string output:
```
#i #j #max #found :
void #reset ( #v ) {
  : :
  #v = 0 ;
  nop ;
  return
} :
#i = 0 ;
#max = 10 ;
while lesser ( #i #max ) do {
  #j = 0 ;
  do {
    if and ( not ( eq ( #i #j ) ) larger ( mod ( #i 2 ) 0 ) ) then {
      print "match found" ;
      #found = 1 ;
    } else {
      nop ;
    } ;
    #j = add ( #j 1 ) ;
  } until or ( eq ( #j #max ) eq ( #found 1 ) ) ;
  #i = add ( #i 1 ) ;
} ;
#reset ( #i ) ;
$
```

Nested scopes and prefix expression trees. Tests function declarations inside local scopes and deeply nested operator trees:
```
#val :
num #outer ( ) {
  :
  num #inner ( #a #b ) {
    : :
    return ( add ( #a #b ) )
  } :
  #val = #inner ( neg ( 10 ) 20 ) ;
  return ( #val )
} :
#val = #outer ( ) ;
print ( add ( sub ( mul ( div ( neg ( 100 ) 2 ) 3 ) 4 ) mod ( 10 3 ) ) ) ;
$
```

Semantic rule tests live in `tests/`:

| File | Tests |
|---|---|
| `NESTED.txt` / `SERIALNESTED.txt` | Valid deeply nested and sibling function declarations, 0 errors expected |
| `MaskTest.txt` | Parameter masked by a local variable |
| `tests/VariableErrors.txt` | Duplicate declaration, masking, and undeclared variable, combined |
| `tests/VariableValid.txt` | Valid variable usage across nested scopes |
| `tests/DirectRecursion.txt` | A function calling itself |
| `tests/IndirectRecursion.txt` | Two functions calling each other |
| `tests/SidewaysCall.txt` | Sibling functions attempting to call each other's private sub-functions |
| `tests/DupFunc.txt` | Two functions with the same name at one level |

## Building the submission (Phase 1 upload)

Per Announcement #25, the Phase 1 upload requires an executable, a PDF user manual, and both packaged into one ZIP file. Follow these steps.

### Step 1: Build the executable

Install PyInstaller:

```
pip install pyinstaller
```

Build a single-file executable from `parser.py`. Run this on the same operating system the tutors will use to test it (PyInstaller does not cross compile, a build made on Linux only runs on Linux, a build made on Windows only runs on Windows):

```
pyinstaller --onefile --name group-XX parser.py
```

Replace `XX` with your actual group number. The output executable appears in the `dist/` folder, for example `dist/group-XX.exe` on Windows or `dist/group-XX` on Linux/macOS.

Test the built executable directly before packaging it, using one of the test files above, to confirm it behaves exactly like running `python3 parser.py <file>` did:

```
dist/group-XX.exe tests/VariableValid.txt
```

### Step 2: Write the user manual

Create a short PDF named `group-XX.pdf` that explains to the tutors how to run the executable. It must include:

* How to run the program from a command line (exact command, exact argument order)
* What output to expect on success (tree.xml) and on failure (error message types)
* The full names and student numbers of every member of the project group

### Step 3: Package into one ZIP file

Place the executable and the PDF into one ZIP file named `group-XX.zip`:

```
zip group-XX.zip dist/group-XX.exe group-XX.pdf
```

(On Windows, right click both files and choose "Send to > Compressed (zipped) folder", then rename the result to `group-XX.zip`.)

### Step 4: Upload

Only the group's designated speaker uploads `group-XX.zip` to ClickUp before the deadline. Every other group member makes no upload.

### Submission checklist

- [ ] Executable built and named `group-XX.exe` (or matching platform naming)
- [ ] Executable tested standalone, not just via `python3 parser.py`
- [ ] PDF user manual written, named `group-XX.pdf`, includes full names and student numbers of every group member
- [ ] Both files zipped into one `group-XX.zip`
- [ ] Only the speaker uploads, before the deadline

### Critical reminders from the announcement

* If the speaker fails to upload before the deadline, the whole group gets 0 points.
* If the tutors find the exe file not runnable, the whole group gets 0 points. Tutors will not attempt to fix anything.
* Submissions are tested with 6 black box test cases, 0.5 points each, for a maximum of 3 points on this phase.
* The pseudo symbol `$` is not literally included at the end of a test file. The lexer must handle end of file correctly on its own, without a literal `$` present.

## Status

- [x] Phase 1: Lexer, Parser, Syntax Tree (`tree.xml`)
- [x] Phase 2a: Scope analysis, Symbol Table, Variable and Function semantic rules
- [ ] Executable build and packaging for Phase 1 submission
- [ ] Phase 2b / later phases (TBD)

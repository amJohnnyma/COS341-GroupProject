import re
from symbol_table import Type






class CodeGenerator:
    def __init__(self, symbol_table, program_type):
        self.symbol_table = symbol_table
        self.crawler = symbol_table.crawler
        self.typ = "float" if program_type == Type.FLOAT_NUMERIC else "int"
        
        self.var_counter = 0
        self.label_counter = 0
        self.code_mine = {}
        self.output = []





    def new_var(self):
        self.var_counter += 1
        return f"v{self.var_counter}"




    def new_label(self):
        self.label_counter += 1
        return f"L{self.label_counter}"




    def emit(self, line):
        self.output.append(line)




    def get_children(self, node):
        if not node: return []
        kids = [self.crawler.getNode(cid) for cid in node.children_ids]
        return [k for k in kids if k is not None]




    def get_sys_name(self, node_id):
        name = self.symbol_table.get_internal_name(node_id)
        if name: return name
        node = self.crawler.getNode(node_id)
        if not node: return None
        original_name = node.contents
        for entry in self.symbol_table.entries:
            if entry.original_name == original_name:
                return entry.internal_name
        return original_name.replace("#", "sys_")




    def trans_SPL_PROG(self, node_id):
        node = self.crawler.getNode(node_id)
        p_node = next((c for c in self.get_children(node) if c.contents == "P"), None)
        if not p_node: return



        self.trans_P(p_node.id, is_mine=True)
        self.emit("#include <stdio.h>")
        self.emit("int main() {")
        self.trans_P(p_node.id, is_mine=False)
        self.emit("return 0;")
        self.emit("}")





    def trans_P(self, node_id, is_mine=False):
        node = self.crawler.getNode(node_id)
        children = self.get_children(node)
        
        v_decl = next((c for c in children if c.contents == "V_DECL"), None)
        f_decl = next((c for c in children if c.contents == "F_DECL"), None)
        algo = next((c for c in children if c.contents == "ALGO"), None)



        if is_mine:
            self.emit("/* begin of the non-executable code-mine for later inlining */")
            if f_decl: self.trans_F_DECL(f_decl.id)
            self.emit("/* end of the non-executable code-mine */")
            self.emit("/* begin of executable C code */")
        else:
            if v_decl: self.trans_V_DECL(v_decl.id)
            if algo: self.trans_ALGO(algo.id)





    def trans_V_DECL(self, node_id):
        node = self.crawler.getNode(node_id)
        for child in self.get_children(node):
            if child.contents.startswith("#"):
                name = self.get_sys_name(child.id)
                if name:
                    self.emit(f"{self.typ} {name};")
            elif child.contents == "V_DECL":
                self.trans_V_DECL(child.id)





    def trans_ALGO(self, node_id):
        node = self.crawler.getNode(node_id)
        for child in self.get_children(node):
            if child.contents == "INSTR":
                self.trans_INSTR(child.id)
            elif child.contents == "ALGO":
                self.trans_ALGO(child.id)
                




    def trans_INSTR(self, node_id):
        node = self.crawler.getNode(node_id)
        for child in self.get_children(node):
            if child.contents == "BRANCH":
                self.trans_BRANCH(child.id)
            elif child.contents == "LOOP":
                self.trans_LOOP(child.id)
            elif child.contents == "INSTRTAIL":
                self.trans_INSTRTAIL(child.id)
            elif child.contents == "OUTP":
                self.trans_OUTP(child.id)




    def trans_INSTRTAIL(self, node_id):
        node = self.crawler.getNode(node_id)
        children = self.get_children(node)
        first = children[0]
        name_id = node.parent.children_ids[0]
        internal_name = self.get_sys_name(name_id)



        if first.contents == "=":
            term_id = children[1].id
            self.trans_TERM(term_id, internal_name)
        else:
            arg_terms = []
            if len(children) >= 3:
                input_node = children[1]
                if input_node.contents == "INPUT":
                    current = input_node
                    while current and current.contents == "INPUT":
                        for cid in current.children_ids:
                            c = self.crawler.getNode(cid)
                            if c and c.contents == "TERM":
                                arg_terms.append(c.id)
                        if current.children_ids:
                            current = self.crawler.getNode(current.children_ids[-1])
                        else:
                            break
            name_node = self.crawler.getNode(name_id)
            self.inline_function(name_node.contents if name_node else "", arg_terms)





    def trans_TERM(self, node_id, result_var):
        node = self.crawler.getNode(node_id)
        children = self.get_children(node)
        if not children: return
        first = children[0]

        if first.contents.replace('.', '', 1).isdigit():
            self.emit(f"{result_var} = {first.contents};")
        elif first.contents.startswith("#"):
            has_input = False
            arg_terms = []
            if len(children) >= 2:
                termtail = children[1]
                if termtail.contents == "TERMTAIL":
                    for cid in termtail.children_ids:
                        c = self.crawler.getNode(cid)
                        if c and c.contents == "INPUT":
                            has_input = True
                            current = c
                            while current and current.contents == "INPUT":
                                for scid in current.children_ids:
                                    sc = self.crawler.getNode(scid)
                                    if sc and sc.contents == "TERM":
                                        arg_terms.append(sc.id)
                                if current.children_ids:
                                    current = self.crawler.getNode(current.children_ids[-1])
                                else:
                                    break




            if has_input:
                self.inline_function(first.contents, arg_terms, result_var)
            else:
                internal_name = self.get_sys_name(first.id)
                self.emit(f"{result_var} = {internal_name};")

        elif first.contents in ("add", "sub", "mul", "div", "mod"):
            op_sym = {"add": "+", "sub": "-", "mul": "*", "div": "/", "mod": "%"}[first.contents]
            t1, t2 = self.new_var(), self.new_var()
            self.emit(f"{self.typ} {t1};")
            self.emit(f"{self.typ} {t2};")
            self.trans_TERM(children[2].id, t1)
            self.trans_TERM(children[3].id, t2)
            self.emit(f"{result_var} = {t1} {op_sym} {t2};")



        elif first.contents == "neg":
            t1 = self.new_var()
            self.emit(f"{self.typ} {t1};")
            self.trans_TERM(children[2].id, t1)
            self.emit(f"{result_var} = -{t1};")






    def trans_BOOL(self, node_id, targetLabel, dummyLabel):
        node = self.crawler.getNode(node_id)
        children = self.get_children(node)
        if not children: return
        op = children[0].contents
        
        if op == "not":
            self.trans_BOOL(children[2].id, dummyLabel, targetLabel)
        elif op == "or":
            self.trans_BOOL(children[2].id, targetLabel, dummyLabel)
            self.trans_BOOL(children[3].id, targetLabel, dummyLabel)
        elif op == "and":
            self.trans_BOOL(children[2].id, dummyLabel, targetLabel)
            self.trans_BOOL(children[3].id, dummyLabel, targetLabel)
        elif op in ("eq", "larger", "lesser"):
            op_sym = {"eq": "==", "larger": ">", "lesser": "<"}[op]
            t1, t2 = self.new_var(), self.new_var()
            self.emit(f"{self.typ} {t1};")
            self.emit(f"{self.typ} {t2};")
            self.trans_TERM(children[2].id, t1)
            self.trans_TERM(children[3].id, t2)
            self.emit(f"if ({t1} {op_sym} {t2}) goto {targetLabel};")





    def trans_BRANCH(self, node_id):
        node = self.crawler.getNode(node_id)
        children = self.get_children(node)
        bool_node = next((c for c in children if c.contents == "BOOL"), None)
        algos = [c for c in children if c.contents == "ALGO"]
        if not bool_node or len(algos) < 2: return
        
        La, Lb, Lc = self.new_label(), self.new_label(), self.new_label()
        self.emit("/* if */")
        self.trans_BOOL(bool_node.id, La, Lb)
        self.emit(f"{Lb}: /* else */")
        self.trans_ALGO(algos[1].id)
        self.emit(f"goto {Lc};")
        self.emit(f"{La}: /* then */")
        self.trans_ALGO(algos[0].id)
        self.emit(f"{Lc}: /* continue */")





    def trans_LOOP(self, node_id):
        node = self.crawler.getNode(node_id)
        children = self.get_children(node)
        bool_node = next((c for c in children if c.contents == "BOOL"), None)
        algo_node = next((c for c in children if c.contents == "ALGO"), None)
        if not bool_node or not algo_node: return
        
        is_do_while = False
        for c in children:
            if c.contents == "do":
                is_do_while = True
                break
            if c.contents == "COND":
                break

        Lstart, Lbody, Lend = self.new_label(), self.new_label(), self.new_label()

        if is_do_while:
            self.emit(f"{Lstart}:")
            self.trans_ALGO(algo_node.id)
            self.trans_BOOL(bool_node.id, Lstart, Lend)
            self.emit(f"{Lend}:")
        else:
            self.emit(f"{Lstart}:")
            self.trans_BOOL(bool_node.id, Lbody, Lend)
            self.emit(f"goto {Lend};")
            self.emit(f"{Lbody}:")
            self.trans_ALGO(algo_node.id)
            self.emit(f"goto {Lstart};")
            self.emit(f"{Lend}:")

 


    def trans_OUTP(self, node_id):
        node = self.crawler.getNode(node_id)
        children = self.get_children(node)
        if not children: return
        first = children[0]
        
        if first.contents.startswith('"'):

          
            clean_str = first.contents[1:-1]
            self.emit(f'printf("%s\\n", "{clean_str}");')
            
        elif first.contents == "(":
            t = self.new_var()
            self.emit(f"{self.typ} {t};")
            term_node_id = next((cid for cid in node.children_ids if self.crawler.getNode(cid).contents == "TERM"), None)
            if term_node_id is None and len(node.children_ids) > 1:
                term_node_id = node.children_ids[1]
                
            self.trans_TERM(term_node_id, t)
            
            # FIX: Use %f for floats, %d for ints
            fmt = "%f" if self.typ == "float" else "%d"
            self.emit(f'printf("{fmt}\\n", {t});')


   
   
    def trans_F_DECL(self, node_id):
        node = self.crawler.getNode(node_id)
        for child in self.get_children(node):
            if child.contents == "F_TYPE":
                self.trans_F_TYPE(child.id)
            elif child.contents == "F_DECL":
                self.trans_F_DECL(child.id)


  
  
    def trans_F_TYPE(self, node_id):
        node = self.crawler.getNode(node_id)
        children = self.get_children(node)
        
        name_node = next((c for c in children if c.contents.startswith("#")), None)
        if not name_node: return
            
        func_name = name_node.contents
            
        old_output = self.output
        self.output = []
        
        v_decl = next((c for c in children if c.contents == "V_DECL"), None)
        if v_decl:
            self.trans_V_DECL(v_decl.id)
        
        p_node = next((c for c in children if c.contents == "P"), None)
        if p_node:
            p_children = self.get_children(p_node)
            
            f_decl_inner = next((c for c in p_children if c.contents == "F_DECL"), None)
            if f_decl_inner:
                self.trans_F_DECL(f_decl_inner.id)
            
            v_decl_inner = next((c for c in p_children if c.contents == "V_DECL"), None)
            if v_decl_inner:
                self.trans_V_DECL(v_decl_inner.id)
         
            algo_node = next((c for c in p_children if c.contents == "ALGO"), None)
            if algo_node:
                self.trans_ALGO(algo_node.id)

        return_var = None
        term_node = next((c for c in children if c.contents == "TERM"), None)
        if term_node:
            return_var = self.new_var()
            self.emit(f"{self.typ} {return_var};")
            self.trans_TERM(term_node.id, return_var)

        self.code_mine[func_name] = {
            "code": list(self.output),
            "return_var": return_var
        }
        self.output = old_output


  
  
  
    def inline_function(self, func_name, arg_terms, result_var=None):
        if func_name not in self.code_mine:
            self.emit(f"/* WARNING: {func_name} not in code mine */")
            return

        prefix = f"f{self.var_counter}_"
        self.var_counter += 1
        
        raw_code = self.code_mine[func_name]["code"]
        return_var = self.code_mine[func_name]["return_var"]
        
        local_sys_names = []
        for raw_line in raw_code:
            m = re.match(rf'^{self.typ} (sys\d+);$', raw_line)
            if m:
                local_sys_names.append(m.group(1))
        local_sys_set = set(local_sys_names)
        
        declarations = []
        body = []

        for raw_line in raw_code:
            is_decl = bool(re.match(rf'^{self.typ} (sys\d+|v\d+);$', raw_line))
            line = raw_line
            
            for sys_name in local_sys_set:
                line = re.sub(rf'\b{sys_name}\b', f'{prefix}{sys_name}', line)
            
            line = re.sub(r'\bv(\d+)\b', rf'{prefix}v\1', line)
            line = re.sub(r'\bL(\d+)\b', rf'{prefix}L\1', line)
            
            if is_decl:
                declarations.append(line)
            else:
                body.append(line)

        for dec in declarations:
            self.emit(dec)
        
        for i, arg_term_id in enumerate(arg_terms):
            if i < len(local_sys_names):
                arg_var = self.new_var()
                self.emit(f"{self.typ} {arg_var};")
                self.trans_TERM(arg_term_id, arg_var)
                self.emit(f"{prefix}{local_sys_names[i]} = {arg_var};")
        
        for line in body:
            self.emit(line)
        
        if result_var and return_var:
            self.emit(f"{result_var} = {prefix}{return_var};")

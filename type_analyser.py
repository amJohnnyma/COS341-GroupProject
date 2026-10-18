from symbol_table import SymbolTable, SymbolEntry, Type
from tree_crawl import SLNode

from typing import Optional


class TypeAnalysisError(Exception):
    pass



class TypeAnalyser:
    def __init__(self, st : SymbolTable):
        self.symbol_table = st
        self.crawler = st.crawler


    def perform_type_checking(self):
        print("--- Type Check Started ---")
        self._check_mod_div_rule()
        root_id = next(nid for nid, node in self.crawler.nodes.items() if node.parent is None)
        result = self._check_SPL_PROG(root_id)
        print(f"--- Type Check Ended: {result} ---")
        if result != Type.OK:
            raise TypeAnalysisError(f"TYPE ERROR: type analysis failed at SPL_PROG (node {root_id})")


    def _check_mod_div_rule(self):
        nodes = self.crawler.nodes.values()
        has_mod = any(n.contents == "mod" for n in nodes)
        has_div = any(n.contents == "div" for n in nodes)
        if has_mod and has_div:
            raise TypeAnalysisError("A float-integer-conflict might perhaps be possible")
        if has_mod:
            for n in nodes:
                if n.children_ids or n.parent is None or n.parent.contents != "TERM":
                    continue
                if len(n.parent.children_ids) == 1 and "." in n.contents:
                    raise TypeAnalysisError(
                        f"TYPE ERROR: decimal number {n.contents} (node {n.id}) "
                        f"is not allowed because the program uses mod")


    def _check_SPL_PROG(self, node_id : int):
        node : Optional[SLNode] = self.crawler.getNode(node_id)
        if node is None:
            return Type.UNKNOWN
        results = []
        for child_id in node.children_ids:
            child = self.crawler.getNode(child_id)
            if child is not None and child.contents == "P":
                results.append(self._check_P(child_id))
        return Type.OK if all(r == Type.OK for r in results) else Type.UNKNOWN


    def _check_P(self, node_id : int):
        node : Optional[SLNode] = self.crawler.getNode(node_id)
        if node is None:
            return Type.UNKNOWN
        results = []
        for child_id in node.children_ids:
            child = self.crawler.getNode(child_id)
            if child is None:
                continue
            if child.contents == "V_DECL":
                results.append(self._check_V_DECL(child_id))
            elif child.contents == "F_DECL":
                results.append(self._check_F_DECL(child_id))
            elif child.contents == "ALGO":
                results.append(self._check_ALGO(child_id))
        return Type.OK if all(r == Type.OK for r in results) else Type.UNKNOWN


    def _check_V_DECL(self, node_id : int):
        node : Optional[SLNode] = self.crawler.getNode(node_id)
        if node is None:
            return Type.UNKNOWN
        for child_id in node.children_ids:
            child = self.crawler.getNode(child_id)
            if child is None:
                continue
            if child_id in self.symbol_table.lookup:
                internal_name = self.symbol_table.get_internal_name(child_id)
                if internal_name is not None:
                    for entry in self.symbol_table.entries:
                        if entry.internal_name == internal_name:
                            entry.setType(Type.NUMERIC)
                            break
            elif child.contents == "V_DECL":
                self._check_V_DECL(child_id)
            elif child.contents == "epsilon":
                pass
        return Type.OK


    def _check_F_DECL(self, node_id : int):
        node : Optional[SLNode] = self.crawler.getNode(node_id)
        if node is None:
            return Type.UNKNOWN
        results = []
        for child_id in node.children_ids:
            child = self.crawler.getNode(child_id)
            if child is None:
                continue
            if child.contents == "F_TYPE":
                results.append(self._check_F_TYPE(child_id))
            elif child.contents == "F_DECL":
                results.append(self._check_F_DECL(child_id))
            elif child.contents == "epsilon":
                pass
        return Type.OK if all(r == Type.OK for r in results) else Type.UNKNOWN


    def _check_F_TYPE(self, node_id : int):
        node : Optional[SLNode] = self.crawler.getNode(node_id)
        if node is None:
            return Type.UNKNOWN
        keyword = self.crawler.getNode(node.children_ids[0])
        name_id = node.children_ids[1]
        entry = self.symbol_table.get_entry(name_id)
        if keyword is None or entry is None:
            return Type.UNKNOWN
        # void -> procedure, num -> numeric
        entry.setType(Type.PROCEDURE if keyword.contents == "void" else Type.NUMERIC)
        for child_id in node.children_ids:
            child = self.crawler.getNode(child_id)
            if child is None:
                continue
            if child.contents == "V_DECL" and self._check_V_DECL(child_id) != Type.OK:
                raise TypeAnalysisError(
                    f"TYPE ERROR: parameters of function {entry.original_name} (node {child_id}) are not ok")
            elif child.contents == "P" and self._check_P(child_id) != Type.OK:
                raise TypeAnalysisError(
                    f"TYPE ERROR: body of function {entry.original_name} (node {child_id}) is not ok")
            elif child.contents == "TERM" and self._check_TERM(child_id) != Type.NUMERIC:
                raise TypeAnalysisError(
                    f"TYPE ERROR: return value of num function {entry.original_name} "
                    f"(node {child_id}) is not numeric")
        return Type.OK



    def _check_ALGO(self, node_id : int):
        node : Optional[SLNode] = self.crawler.getNode(node_id)
        if node is None:
            return Type.UNKNOWN
        results = []
        for child_id in node.children_ids:
            child = self.crawler.getNode(child_id)
            if child is None:
                continue
            if child.contents == "INSTR":
                results.append(self._check_INSTR(child_id))
            elif child.contents == "ALGO":
                results.append(self._check_ALGO(child_id))
        return Type.OK if all(r == Type.OK for r in results) else Type.UNKNOWN


    def _check_OUTP(self, node_id : int):
        node : Optional[SLNode] = self.crawler.getNode(node_id)
        if node is None:
            return Type.UNKNOWN
        results = []
        for child_id in node.children_ids:
            child = self.crawler.getNode(child_id)
            if child is not None and child.contents == "TERM":
                results.append(self._check_TERM(child_id))
        return Type.OK if all(r == Type.OK for r in results) else Type.UNKNOWN


    def _check_INSTR(self, node_id : int):
        node : Optional[SLNode] = self.crawler.getNode(node_id)
        if node is None:
            return Type.UNKNOWN
        results = []
        for child_id in node.children_ids:
            child = self.crawler.getNode(child_id)
            if child is None:
                continue
            if child.contents == "INSTRTAIL":
                results.append(self._check_INSTRTAIL(child_id))
            elif child.contents == "OUTP":
                results.append(self._check_OUTP(child_id))
            elif child.contents == "BRANCH":
                results.append(self._check_BRANCH(child_id))
            elif child.contents == "LOOP":
                results.append(self._check_LOOP(child_id))
        return Type.OK if all(r == Type.OK for r in results) else Type.UNKNOWN


    def _check_INPUT(self, node_id : int):
        node : Optional[SLNode] = self.crawler.getNode(node_id)
        if node is None:
            return Type.UNKNOWN
        results = []
        for child_id in node.children_ids:
            child = self.crawler.getNode(child_id)
            if child is None:
                continue
            if child.contents == "TERM":
                results.append(self._check_TERM(child_id))
            elif child.contents == "INPUT":
                results.append(self._check_INPUT(child_id))
        return Type.OK if all(r == Type.OK for r in results) else Type.UNKNOWN



    def _check_INSTRTAIL(self, node_id : int):
        node : Optional[SLNode] = self.crawler.getNode(node_id)
        if node is None or node.parent is None:
            return Type.UNKNOWN
        # INSTR -> NAME INSTRTAIL
        name_id = node.parent.children_ids[0]
        first = self.crawler.getNode(node.children_ids[0])
        if first is not None and first.contents == "=":
            return self._check_ASSIGN(name_id, node.children_ids[1])
        return self._check_CALL(name_id, node.children_ids[1])


    def _check_ASSIGN(self, name_id : int, term_id : int):
        # INSTR -> NAME = TERM
        name = self.crawler.getNode(name_id)
        if self.symbol_table.name_type(name_id) != Type.NUMERIC:
            raise TypeAnalysisError(
                f"TYPE ERROR: assignment target {name.contents} (node {name_id}) is not numeric")
        if self._check_TERM(term_id) != Type.NUMERIC:
            raise TypeAnalysisError(
                f"TYPE ERROR: value assigned to {name.contents} (node {term_id}) is not numeric")
        return Type.OK


    def _check_CALL(self, name_id : int, input_id : int):
        # INSTR -> NAME ( INPUT )
        name = self.crawler.getNode(name_id)
        if self.symbol_table.call_type(name_id) != Type.PROCEDURE:
            raise TypeAnalysisError(
                f"TYPE ERROR: {name.contents} (node {name_id}) is called as an instruction "
                f"but is not a void procedure")
        if self._check_INPUT(input_id) != Type.OK:
            raise TypeAnalysisError(
                f"TYPE ERROR: arguments of call to {name.contents} (node {input_id}) are not ok")
        return Type.OK




    def _check_TERM(self, node_id : int):
        node : Optional[SLNode] = self.crawler.getNode(node_id)
        if node is None:
            return Type.UNKNOWN
        results = []
        for child_id in node.children_ids:
            child = self.crawler.getNode(child_id)
            if child is None:
                continue
            if child.contents == "TERMTAIL":
                results.append(self._check_TERMTAIL(child_id))
            elif child.contents == "TERM":
                results.append(self._check_TERM(child_id))
        return Type.OK if all(r == Type.OK for r in results) else Type.UNKNOWN



    def _check_TERMTAIL(self, node_id : int):
        node : Optional[SLNode] = self.crawler.getNode(node_id)
        if node is None:
            return Type.UNKNOWN
        results = []
        for child_id in node.children_ids:
            child = self.crawler.getNode(child_id)
            if child is not None and child.contents == "INPUT":
                results.append(self._check_INPUT(child_id))
        return Type.OK if all(r == Type.OK for r in results) else Type.UNKNOWN



    def _check_BOOL(self, node_id : int):
        node : Optional[SLNode] = self.crawler.getNode(node_id)
        if node is None:
            return Type.UNKNOWN
        results = []
        for child_id in node.children_ids:
            child = self.crawler.getNode(child_id)
            if child is None:
                continue
            if child.contents == "BOOL":
                results.append(self._check_BOOL(child_id))
            elif child.contents == "TERM":
                results.append(self._check_TERM(child_id))
        return Type.OK if all(r == Type.OK for r in results) else Type.UNKNOWN



    def _check_BRANCH(self, node_id : int):
        node : Optional[SLNode] = self.crawler.getNode(node_id)
        if node is None:
            return Type.UNKNOWN
        results = []
        for child_id in node.children_ids:
            child = self.crawler.getNode(child_id)
            if child is None:
                continue
            if child.contents == "BOOL":
                results.append(self._check_BOOL(child_id))
            elif child.contents == "ALGO":
                results.append(self._check_ALGO(child_id))
        return Type.OK if all(r == Type.OK for r in results) else Type.UNKNOWN



    def _check_LOOP(self, node_id : int):
        node : Optional[SLNode] = self.crawler.getNode(node_id)
        if node is None:
            return Type.UNKNOWN
        results = []
        for child_id in node.children_ids:
            child = self.crawler.getNode(child_id)
            if child is None:
                continue
            if child.contents == "COND":
                results.append(self._check_COND(child_id))
            elif child.contents == "BOOL":
                results.append(self._check_BOOL(child_id))
            elif child.contents == "ALGO":
                results.append(self._check_ALGO(child_id))
        return Type.OK if all(r == Type.OK for r in results) else Type.UNKNOWN



    def _check_COND(self, node_id : int):
        return Type.OK



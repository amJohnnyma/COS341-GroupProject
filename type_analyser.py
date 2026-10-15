from symbol_table import SymbolTable, SymbolEntry, Type
from tree_crawl import SLNode

from typing import Optional



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
            raise TypeError(f"Type analysis failed at SPL_PROG (node {root_id})")


    def _check_mod_div_rule(self):
        has_mod = False
        has_div = False
        for node in self.crawler.nodes.values():
            if node.contents == "mod":
                has_mod = True
            elif node.contents == "div":
                has_div = True
        if has_mod and has_div:
            raise TypeError("A float-integer-conflict might perhaps be possible")


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
        results = []
        for child_id in node.children_ids:
            child = self.crawler.getNode(child_id)
            if child is None:
                continue
            if child.contents == "V_DECL":
                results.append(self._check_V_DECL(child_id))
            elif child.contents == "P":
                results.append(self._check_P(child_id))
            elif child.contents == "TERM":
                results.append(self._check_TERM(child_id))
        return Type.OK if all(r == Type.OK for r in results) else Type.UNKNOWN


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
        if node is None:
            return Type.UNKNOWN
        results = []
        for child_id in node.children_ids:
            child = self.crawler.getNode(child_id)
            if child is None:
                continue
            if child.contents == "INPUT":
                results.append(self._check_INPUT(child_id))
            elif child.contents == "TERM":
                results.append(self._check_TERM(child_id))
        return Type.OK if all(r == Type.OK for r in results) else Type.UNKNOWN



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



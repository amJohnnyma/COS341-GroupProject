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
        # Ensure we get a node with no parents (probably id = 0 but just incase)
        root_id =next(nid for nid, node in self.crawler.nodes.items() if node.parent is None) 
        self._check_SPL_PROG(root_id)

        print("--- Type Check Ended---")

    def _check_mod_div_rule(self):
        pass

    def _check_SPL_PROG(self, node_id : int):
        node : Optional[SLNode] = self.crawler.getNode(node_id)

        if node is not None:
            for child_id in node.children_ids:
                child = self.crawler.getNode(child_id)
                if child is not None:
                    if child.contents == "P":
                        self._check_P(child_id)
        return Type.OK

    def _check_P(self, node_id : int):
        node : Optional[SLNode] = self.crawler.getNode(node_id)

        if node is not None:
            for child_id in node.children_ids:
                child = self.crawler.getNode(child_id)
                if child is not None:
                    if child.contents == "V_DECL":
                        self._check_V_DECL(child_id)
                    if child.contents == "F_DECL":
                        self._check_F_DECL(child_id)

        return Type.OK


    def _check_V_DECL(self, node_id : int):
        node : Optional[SLNode] = self.crawler.getNode(node_id)

        if node is not None:
            for child_id in node.children_ids:
                child = self.crawler.getNode(child_id)
                if child is not None:
                    if child_id in self.symbol_table.lookup:
                        internal_name = self.symbol_table.get_internal_name(child_id)
                        if internal_name is not None:
                            for entry in self.symbol_table.entries:
                                if entry.internal_name == internal_name:
                                    entry.setType(Type.NUMERIC)
                                    break
                    # We expect V_DECL afterwards or epsilon
                    elif child.contents == "V_DECL":
                        self._check_V_DECL(child_id)
                    elif child.contents == "epsilon":
                        pass

        return Type.OK


    def _check_F_DECL(self, node_id : int):
        node : Optional[SLNode] = self.crawler.getNode(node_id)

        if node is not None:
            for child_id in node.children_ids:
                child = self.crawler.getNode(child_id)
                # Expect F_TYPE -> F_DECL | epsilon
                if child is not None:
                    if child.contents == "F_TYPE":
                        self._check_F_TYPE(child_id)
                    elif child.contents == "F_DECL":
                        self._check_F_DECL(child_id)
                    elif child.contents == "epsilon":
                        pass
        return Type.OK


    def _check_F_TYPE(self, node_id : int):
        node : Optional[SLNode] = self.crawler.getNode(node_id)

        if node is not None:
            for child_id in node.children_ids:
                child = self.crawler.getNode(child_id)
                if child is not None:
                    if child.contents == "V_DECL":
                        self._check_V_DECL(child_id)
                    elif child.contents == "P":
                        self._check_P(child_id)
                    elif child.contents == "TERM":
                        self._check_TERM(child_id)
        return Type.OK


    def _check_ALGO(self, node_id : int):
        node : Optional[SLNode] = self.crawler.getNode(node_id)

        if node is not None:
            for child_id in node.children_ids:
                child = self.crawler.getNode(child_id)
                if child is not None:
                    if child.contents == "INSTR":
                        self._check_INSTR(child_id)
                    elif child.contents == "ALGO":
                        self._check_ALGO(child_id)
        return Type.OK

    def _check_OUTP(self, node_id : int):
        node : Optional[SLNode] = self.crawler.getNode(node_id)

        if node is not None:
            for child_id in node.children_ids:
                child = self.crawler.getNode(child_id)
                if child is not None:
                    if child.contents == "TERM":
                        self._check_TERM(child_id)
        return Type.OK

    def _check_INSTR(self, node_id : int):
        node : Optional[SLNode] = self.crawler.getNode(node_id)

        if node is not None:
            for child_id in node.children_ids:
                child = self.crawler.getNode(child_id)
                if child is not None:
                    if child.contents == "INSTRTAIL":
                        self._check_INSTRTAIL(child_id)
                    elif child.contents == "OUTP":
                        self._check_OUTP(child_id)
                    elif child.contents == "BRANCH":
                        self._check_BRANCH(child_id)
                    elif child.contents == "LOOP":
                        self._check_LOOP(child_id)
        return Type.OK

    def _check_INPUT(self, node_id : int):
        node : Optional[SLNode] = self.crawler.getNode(node_id)

        if node is not None:
            for child_id in node.children_ids:
                child = self.crawler.getNode(child_id)
                if child is not None:
                    if child.contents == "TERM":
                        self._check_TERM(child_id)
                    elif child.contents == "INPUT":
                        self._check_INPUT(child_id)
        return Type.OK

    def _check_INSTRTAIL(self, node_id : int):
        node : Optional[SLNode] = self.crawler.getNode(node_id)

        if node is not None:
            for child_id in node.children_ids:
                child = self.crawler.getNode(child_id)
                if child is not None:
                    if child.contents == "INPUT":
                        self._check_INPUT(child_id)
                    elif child.contents == "TERM":
                        self._check_TERM(child_id)
        return Type.OK

    def _check_TERM(self, node_id : int):
        node : Optional[SLNode] = self.crawler.getNode(node_id)

        if node is not None:
            for child_id in node.children_ids:
                child = self.crawler.getNode(child_id)
                if child is not None:
                    if child.contents == "TERMTAIL":
                        self._check_TERMTAIL(child_id)
                    elif child.contents == "TERM":
                        self._check_TERM(child_id)
        return Type.OK

    def _check_TERMTAIL(self, node_id : int):
        node : Optional[SLNode] = self.crawler.getNode(node_id)

        if node is not None:
            for child_id in node.children_ids:
                child = self.crawler.getNode(child_id)
                if child is not None:
                    if child.contents == "INPUT":
                        self._check_INPUT(child_id)
        return Type.OK

    def _check_BOOL(self, node_id : int):
        node : Optional[SLNode] = self.crawler.getNode(node_id)

        if node is not None:
            for child_id in node.children_ids:
                child = self.crawler.getNode(child_id)
                if child is not None:
                    if child.contents == "BOOL":
                        self._check_BOOL(child_id)
                    elif child.contents == "TERM":
                        self._check_TERM(child_id)
        return Type.OK

    def _check_BRANCH(self, node_id : int):
        node : Optional[SLNode] = self.crawler.getNode(node_id)

        if node is not None:
            for child_id in node.children_ids:
                child = self.crawler.getNode(child_id)
                if child is not None:
                    if child.contents == "BOOL":
                        self._check_BOOL(child_id)
                    elif child.contents == "ALGO":
                        self._check_ALGO(child_id)
        return Type.OK

    def _check_LOOP(self, node_id : int):
        node : Optional[SLNode] = self.crawler.getNode(node_id)

        if node is not None:
            for child_id in node.children_ids:
                child = self.crawler.getNode(child_id)
                if child is not None:
                    if child.contents == "COND":
                        self._check_COND(child_id)
                    elif child.contents == "BOOL":
                        self._check_BOOL(child_id)
                    elif child.contents == "ALGO":
                        self._check_ALGO(child_id)
        return Type.OK

    def _check_COND(self, node_id : int):
        return Type.OK

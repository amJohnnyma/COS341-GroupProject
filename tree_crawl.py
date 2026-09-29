import xml.etree.ElementTree as ET
from typing import Optional, List, Dict

class ScopeLevel:
    def __init__(self, scope_id = 0, level = 0, parent = None):
        self.scope_id = scope_id
        self.level = level
        self.parent = parent

        self.variables = {}
        self.functions = {}

class SLNode:
    def __init__(self, node_id, contents, children, parent_id):
        self.id = node_id
        self.contents = contents
        self.children_ids = children
        self.parent_id = parent_id

        self.parent : Optional[SLNode] = None
        self.scope_level :Optional[ScopeLevel] = None

    def __repr__(self):
        return f"Node(ID={self.id}, Contents='{self.contents}', Scope={self.scope_level})"

class TreeCrawl:
    def __init__(self, filename):
        self.nodes = {}
        self._load_xml(filename)
        self._next_scope_id = 0
        self.all_scopes:list[ScopeLevel] = []

        root_scope = ScopeLevel(scope_id=self._get_next_scope_id(), level=0,parent=None)
        self.crawl_tree(node_id =0, parent_node=None,current_scope=root_scope)

    def getNode(self, node_id:int) -> Optional[SLNode]:
        return self.nodes.get(node_id)

    def _get_next_scope_id(self) -> int:
        sid = self._next_scope_id
        self._next_scope_id += 1
        return sid

    def _add_scope(self, scope_level):
        if not any(s.scope_id == scope_level.scope_id for s in self.all_scopes):
            self.all_scopes.append(scope_level)

    def print_all_scopes(self):
        for s in self.all_scopes:
            print(f"ID={s.scope_id}, Level={s.level}")

    def get_all_scopes(self):
        return self.all_scopes

    def _load_xml(self, filename):
        self.tree = ET.parse(filename)
        self.root = self.tree.getroot()

        for node_elem in self.root.findall('NODE'):

            id_elem: Optional[ET.Element] = node_elem.find('ID')
            node_id: int = int(id_elem.text) if (id_elem is not None and id_elem.text) else 0

            contents_elem: Optional[ET.Element] = node_elem.find('CONTENTS')
            contents: str = contents_elem.text if (contents_elem is not None and contents_elem.text) else ""

            children_elem = node_elem.find('CHILDREN')
            if children_elem is not None and children_elem.text:
                children_ids = [int(x) for x in children_elem.text.split(',')]
            else:
                children_ids = []

            parent_elem : Optional[ET.Element] = node_elem.find('PARENT')
            parent_id : Optional[int] = None

            if parent_elem is not None and parent_elem.text:
                parent_id = int(parent_elem.text.strip())
            self.nodes[node_id] = SLNode(node_id, contents, children_ids, parent_id)

    def crawl_tree(self, node_id, parent_node:Optional[SLNode]=None, current_scope = None):

        # 1. Read through node by node:
        # 2. If the node is "F_TYPE"
        # -> its own num/void keyword + NAME stay in the ENCLOSING scope
        # -> its params (V_DECL), body (P), and return-value (TERM) all get
        #    ONE new shared scope (the function's own scope)
        # 3. Continue from 1
        if current_scope is None:
            current_scope = ScopeLevel()
        node : Optional[SLNode] = self.getNode(node_id)
        if not node:
            return

        node.parent = parent_node
        node.scope_level = current_scope
        self._add_scope(current_scope)

        if node.contents == "F_TYPE":
            # One new scope shared by this function's params, body, and
            # return-value expression -- NOT by the F_TYPE node itself,
            # so the function's own name stays visible at the enclosing
            # scope (needed for sibling/caller lookups).
            func_scope = ScopeLevel(
                scope_id=self._get_next_scope_id(),
                level=current_scope.level + 1,
                parent=current_scope)
            self._add_scope(func_scope)

            for child_id in node.children_ids:
                child = self.getNode(child_id)
                if child and child.contents in ("V_DECL", "P", "TERM"):
                    self.crawl_tree(child_id, parent_node=node, current_scope=func_scope)
                else:
                    self.crawl_tree(child_id, parent_node=node, current_scope=current_scope)
            return

        for child_id in node.children_ids:
            self.crawl_tree(child_id, parent_node=node, current_scope=current_scope)


# From Gemini
    def print_tree(self, node_id: int = 0, prefix: str = "", is_last: bool = True):
            """Prints an ASCII hierarchy tree showing contents, ID, Parent ID, Scope ID, and Scope Level."""
            node = self.getNode(node_id)
            if not node:
                return

            connector = "└── " if is_last else "├── "
            parent_info = f"Parent={node.parent.id}" if node.parent else "Parent=None"

            # Format scope output cleanly using object parameters
            if node.scope_level:
                scope_info = f"SL: {node.scope_level.level} [ScopeID: {node.scope_level.scope_id}]"
            else:
                scope_info = "SL: None"

            print(f"{prefix}{connector}[ID:{node.id}] '{node.contents}' ({parent_info}) -> {scope_info}")

            new_prefix = prefix + ("    " if is_last else "│   ")

            count = len(node.children_ids)
            for i, child_id in enumerate(node.children_ids):
                self.print_tree(child_id, prefix=new_prefix, is_last=(i == count - 1))

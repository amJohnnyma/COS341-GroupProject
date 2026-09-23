import xml.etree.ElementTree as ET
from typing import Optional, List, Dict

class SLNode:
    def __init__(self, node_id, contents, children, parent_id):
        self.id = node_id
        self.contents = contents
        self.children_ids = children
        self.parent_id = parent_id

        self.parent : Optional[SLNode] = None
        self.scope_level = 0

    def __repr__(self):
        return f"Node(ID={self.id}, Contents='{self.contents}', Scope={self.scope_level})"

class TreeCrawl:
    def __init__(self, filename):
        self.nodes = {}
        self._load_xml(filename)
        self.crawl_tree(node_id =0, parent_node=None, current_scope=0)

    def getNode(self, node_id:int) -> Optional[SLNode]:
        return self.nodes.get(node_id)

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

    def crawl_tree(self, node_id, parent_node:Optional[SLNode]=None, current_scope = 0):

        # 1. Read through node by node:
        # 2. If the node is "P"
        # -> Inherit previous scope level
        # --> Process children on scope level + 1
        # 3. Continue from 1
        node : Optional[SLNode] = self.getNode(node_id)
        if not node:
            return

        node.parent = parent_node

        is_nested_p = (
                node.contents == "P"
                and parent_node is not None
                and parent_node.contents == "F_TYPE"
                )

        child_scope = current_scope + 1 if is_nested_p else current_scope
        node.scope_level = current_scope

        for child_id in node.children_ids:
            self.crawl_tree(child_id, parent_node=node, current_scope=child_scope)

        '''
        OPTION INCASE SCOPE INCREASES ON RETURN, expressions, etc.)
        node.parent = parent_node
        node.scope_level = current_scope

        for child_id in node.children_ids:
            # If current node is F_TYPE, its children (P, return, expressions) live in the function's new scope
            if node.contents == "F_TYPE":
                child_scope = current_scope + 1
            else:
                child_scope = current_scope

            self.crawl_tree(node_id=child_id, parent_node=node, current_scope=child_scope)
        '''

    def print_tree(self, node_id: int = 0, prefix: str = "", is_last: bool = True):
            """Prints an ASCII hierarchy tree showing contents, ID, Parent ID, and Scope Level."""
            node = self.getNode(node_id)
            if not node:
                return

            # Formatting markers for hierarchy visualization
            connector = "└── " if is_last else "├── "
            
            # Determine parent display string
            parent_info = f"Parent={node.parent.id}" if node.parent else "Parent=None"

            # Print current node details
            print(f"{prefix}{connector}[ID:{node.id}] '{node.contents}' ({parent_info}) -> SL: {node.scope_level}")

            # Update prefix for children branches
            new_prefix = prefix + ("    " if is_last else "│   ")

            # Recursively print all child nodes
            count = len(node.children_ids)
            for i, child_id in enumerate(node.children_ids):
                self.print_tree(child_id, prefix=new_prefix, is_last=(i == count - 1))




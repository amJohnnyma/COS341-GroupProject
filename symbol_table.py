from typing import Optional
from tree_crawl import TreeCrawl, ScopeLevel, SLNode


class SymbolEntry:
    def __init__(self, original_name, internal_name, scope, decl_node_id, kind):
        self.original_name = original_name
        # sys3
        self.internal_name = internal_name
        # which scope this was declared in
        self.scope = scope
        # node id of the name in tree.xml  
        self.decl_node_id = decl_node_id 
        self.kind = kind 

    def __repr__(self):
        return (f"SymbolEntry({self.original_name} -> {self.internal_name}, "
                f"kind={self.kind}, scope_id={self.scope.scope_id}, "
                f"level={self.scope.level}, node={self.decl_node_id})")


class SymbolTable:
    # just stores stuff, C and D do the actual checks
    # variables/functions map name -> list of entries, not one entry,
    # otherwise stuff like param #a + local #a in MaskTest would overwrite each other

    def __init__(self, crawler: TreeCrawl):
        self.crawler = crawler
        self._next_sys = 0
        self.entries: list[SymbolEntry] = []
        self.lookup: dict[int, str] = {}   
        self._populate()

    def _new_internal_name(self) -> str:
        name = f"sys{self._next_sys}"
        self._next_sys += 1
        return name

    def _add(self, node: SLNode, kind: str):
        scope = node.scope_level
        entry = SymbolEntry(
            original_name=node.contents,
            internal_name=self._new_internal_name(),
            scope=scope,
            decl_node_id=node.id,
            kind=kind)
        
        table = scope.functions if kind == "function" else scope.variables
        table.setdefault(node.contents, []).append(entry)
        self.entries.append(entry)
        self.lookup[node.id] = entry.internal_name

    def _populate(self):
        # ids are in preorder so this goes through the program top to bottom
        for node_id in sorted(self.crawler.nodes):
            node = self.crawler.getNode(node_id)
            if node is None or node.children_ids or node.parent is None:
                continue

            parent = node.parent

            # V_DECL -> USER-DEFINED-NAME V_DECL  
            if parent.contents == "V_DECL" and node.contents != "epsilon":
                self._add(node, self._vdecl_kind(parent))

            # F_TYPE -> void/num USER-DEFINED-NAME 
            elif parent.contents == "F_TYPE" and parent.children_ids[1] == node.id:
                self._add(node, "function")

    @staticmethod
    def _vdecl_kind(vdecl: SLNode) -> str:
        # Climb the V_DECL chain: owned by F_TYPE -> parameter, by P -> local
        owner: Optional[SLNode] = vdecl
        while owner is not None and owner.contents == "V_DECL":
            owner = owner.parent
        return "param" if owner is not None and owner.contents == "F_TYPE" else "local"

    def get_internal_name(self, decl_node_id: int) -> Optional[str]:
        return self.lookup.get(decl_node_id)
        
    def print_table(self):
        print()
        print("=" * 72)
        print("SYMBOL TABLE")
        print("=" * 72)
        print(f"{'ORIGINAL':<16}{'INTERNAL':<10}{'KIND':<10}{'SCOPE_ID':<10}{'LEVEL':<8}{'DECL_NODE':<10}")
        print("-" * 72)
        for e in self.entries:
            print(f"{e.original_name:<16}{e.internal_name:<10}{e.kind:<10}"
                  f"{e.scope.scope_id:<10}{e.scope.level:<8}{e.decl_node_id:<10}")

        print()
        print("PER SCOPE")
        print("-" * 72)
        for scope in self.crawler.get_all_scopes():
            parent = scope.parent.scope_id if scope.parent else None
            print(f"Scope {scope.scope_id} (level {scope.level}, parent {parent})")
            for name, lst in scope.variables.items():
                print(f"    var  {name:<14} -> " + ", ".join(f"{e.internal_name} ({e.kind})" for e in lst))
            for name, lst in scope.functions.items():
                print(f"    func {name:<14} -> " + ", ".join(e.internal_name for e in lst))

        print()
        print("LOOKUP (decl_node_id -> internal_name)")
        print("-" * 72)
        for node_id, internal in self.lookup.items():
            print(f"    {node_id:<6} -> {internal}")

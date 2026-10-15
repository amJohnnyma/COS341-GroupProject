from typing import Optional, List
from tree_crawl import TreeCrawl, ScopeLevel, SLNode


def _resolve_call(scope: ScopeLevel, name: str):
    entries = scope.functions.get(name)
    if entries:
        return entries[-1]
    return None




def _find_ancestor_declaration(scope: ScopeLevel, name: str) -> Optional[ScopeLevel]:
    s = scope.parent
    while s is not None:
        if name in s.functions:
            return s
        s = s.parent
    return None




def _is_function_call_name(crawler: TreeCrawl, node: SLNode) -> bool:
    if node.children_ids or node.contents == "epsilon":
        return False
    if node.parent is None:
        return False

    parent = node.parent
    if parent.contents not in ("TERM", "INSTR"):
        return False
    if not parent.children_ids or parent.children_ids[0] != node.id:
        return False
    if len(parent.children_ids) < 2:
        return False

    tail = crawler.getNode(parent.children_ids[1])
    if tail is None or not tail.children_ids:
        return False
    if tail.contents not in ("TERMTAIL", "INSTRTAIL"):
        return False

    first_tail_child = crawler.getNode(tail.children_ids[0])
    return first_tail_child is not None and first_tail_child.contents == "("





def check_function_rules(crawler: TreeCrawl, symbol_table) -> List[str]:
    errors: List[str] = []

    for scope in crawler.get_all_scopes():
        for name, entries in scope.functions.items():
            if len(entries) > 1:
                errors.append(
                    f"SEMANTIC ERROR: duplicate function declaration '{name}' "
                    f"in scope {scope.scope_id} (level {scope.level})"
                )

    for node_id in sorted(crawler.nodes):
        node = crawler.getNode(node_id)
        if node is None or not _is_function_call_name(crawler, node):
            continue

        name = node.contents
        scope = node.scope_level

        if _resolve_call(scope, name) is not None:
            continue

        ancestor_scope = _find_ancestor_declaration(scope, name)
        if ancestor_scope is not None:
            errors.append(
                f"SEMANTIC ERROR: call to function '{name}' at node {node.id} "
                f"(scope {scope.scope_id}) is not allowed -- '{name}' is only "
                f"visible in an outer scope (scope {ancestor_scope.scope_id}); "
                f"functions may only call functions declared in their OWN "
                f"immediate scope (disallowed recursive or non-hierarchical call)"
            )
        else:
            errors.append(
                f"SEMANTIC ERROR: undeclared function '{name}' called at "
                f"node {node.id} (scope {scope.scope_id}, level {scope.level})"
            )

    return errors





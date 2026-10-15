def check_variable_rules(crawler, symbol_table):
    errors = []
    for scope in crawler.get_all_scopes():
        for name, entries in scope.variables.items():
            by_kind = {}
            for entry in entries:
                by_kind.setdefault(entry.kind, []).append(entry)
            for kind, declarations in by_kind.items():
                if len(declarations) > 1:
                    node_ids = ", ".join(str(e.decl_node_id) for e in declarations)
                    errors.append(
                        f"SEMANTIC ERROR: duplicate declaration {name} "
                        f"in scope {scope.scope_id} ({kind}, node {node_ids})"
                    )
                
            if "param" in by_kind and "local" in by_kind:
                errors.append(
                    f"SEMANTIC ERROR: local variable {name} masks parameter "
                    f"in scope {scope.scope_id}"
                )
            
    declaration_ids = {entry.decl_node_id for entry in symbol_table.entries}
    for node_id in sorted(crawler.nodes):
        node = crawler.getNode(node_id)
        if (node.children_ids or not node.contents.startswith('#') or node.id in declaration_ids):
            continue

        parent = node.parent
        if (parent is not None and parent.contents in ("TERM", "INSTR") and parent.children_ids[0] == node.id and len(parent.children_ids) > 1):
            tail = crawler.getNode(parent.children_ids[1])
            if (tail is not None and tail.contents in ("TERMTAIL", "INSTRTAIL") and tail.children_ids):
                first = crawler.getNode(tail.children_ids[0])
                if first is not None and first.contents == "(":
                    continue
        symbol_table.lookup.pop(node.id, None)
        scope = node.scope_level
        while scope is not None:
            entries = scope.variables.get(node.contents)
            if entries:
                if len(entries) == 1:
                    symbol_table.lookup[node.id] = symbol_table.get_internal_name(entries[0].decl_node_id)
                break
            scope = scope.parent
        else:
            errors.append(
                f"SEMANTIC ERROR: undeclared variable {node.contents} "
                f"at node {node.id} (scope {node.scope_level.scope_id})"
            )
    return errors
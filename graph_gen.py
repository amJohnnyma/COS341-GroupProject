import xml.etree.ElementTree as ET
from graphviz import Digraph

def xml_to_graph(xml_file: str, output_filename: str = "syntax_tree"):
    tree = ET.parse(xml_file)
    root = tree.getroot()

    # Initialize a directed graph
    dot = Digraph(format="png")
    dot.attr(rankdir="TB", size="10,10")  # Top-to-Bottom layout
    dot.attr("node", shape="ellipse", fontname="Courier")

    for node in root.findall("NODE"):
        node_id = node.find("ID").text
        contents = node.find("CONTENTS").text

        # Style terminals vs non-terminals visually
        if contents in ("epsilon", "$", ":", "void", "(", ")", "{", "}", "return", "num", ";", "print", "nop", "comment", "mod", "add", "sub", "mul", "div", "neg", "if", "then", "else", "not", "and", "or", "eq", "larger", "lesser", "do", "while", "until") or contents.startswith("#") or contents.isdigit():
            dot.node(node_id, label=contents, shape="box", style="filled", fillcolor="lightgray")
        else:
            dot.node(node_id, label=contents)

        # Draw edges to children
        children_el = node.find("CHILDREN")
        if children_el is not None and children_el.text:
            child_ids = children_el.text.split(",")
            for child_id in child_ids:
                dot.edge(node_id, child_id)

    # Render image
    dot.render(output_filename, cleanup=True)
    print(f"Tree rendered successfully as {output_filename}.png")

if __name__ == "__main__":
    xml_to_graph("tree.xml")

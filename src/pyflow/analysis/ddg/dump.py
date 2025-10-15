"""
Dumping utilities for Data Dependence Graphs (DDG).
Supports text, DOT (graphviz) and JSON outputs.
"""

import json
from typing import List

import pyflow.util.pydot as pydot
from .graph import DataDependenceGraph, DDGNode, DDGEdge


class DDGDumper(object):
    __slots__ = ("ddg",)

    def __init__(self, ddg: DataDependenceGraph):
        self.ddg = ddg

    def dump_text(self, path: str, title: str = "Data Dependence Graph") -> None:
        with open(path, "w") as f:
            stats = self.ddg.stats()
            f.write("%s\n%s\n\n" % (title, "=" * 60))
            f.write("Nodes: %(nodes)d, Edges: %(edges)d, Ops: %(ops)d, Slots: %(slots)d\n\n" % stats)
            f.write("Edges (source -> target) [kind]:\n")
            for e in self.ddg.all_edges():
                f.write("  %d -> %d [%s]\n" % (e.source.node_id, e.target.node_id, e.kind))

    def dump_dot(self, path: str, title: str = "DDG") -> None:
        g = pydot.Dot(graph_type="digraph")
        g.set_label(title)

        for n in self.ddg.nodes:
            node_id = "n_%d" % n.node_id
            label = "%d\\n%s" % (n.node_id, n.category)
            shape = "ellipse" if n.category == "op" else "box"
            g.add_node(pydot.Node(node_id, label=label, shape=shape))

        for e in self.ddg.all_edges():
            g.add_edge(pydot.Edge("n_%d" % e.source.node_id, "n_%d" % e.target.node_id, label=e.kind))

        with open(path, "w") as f:
            f.write("// DDG\n")
            f.write(g.to_string())

    def dump_json(self, path: str, title: str = "DDG") -> None:
        data = {
            "title": title,
            "stats": self.ddg.stats(),
            "nodes": [
                {"id": n.node_id, "category": n.category}
                for n in self.ddg.nodes
            ],
            "edges": [
                {"src": e.source.node_id, "dst": e.target.node_id, "kind": e.kind}
                for e in self.ddg.all_edges()
            ],
        }
        with open(path, "w") as f:
            json.dump(data, f, indent=2)


def dump_ddg(ddg: DataDependenceGraph, path: str, fmt: str = "text", title: str = "DDG") -> None:
    dumper = DDGDumper(ddg)
    method = getattr(dumper, "dump_%s" % fmt)
    method(path, title)


def dump_ddg_to_directory(ddg: DataDependenceGraph, directory: str, basename: str, formats: List[str] = None) -> None:
    import os

    formats = formats or ["text", "dot", "json"]
    os.makedirs(directory, exist_ok=True)
    for fmt in formats:
        path = os.path.join(directory, "%s.%s" % (basename, fmt))
        dump_ddg(ddg, path, fmt, basename)



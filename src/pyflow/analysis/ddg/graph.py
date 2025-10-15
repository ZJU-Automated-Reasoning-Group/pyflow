"""
Data Dependence Graph (DDG) data structures.

Nodes correspond to dataflowIR ops and slots; edges capture def-use and
memory dependences between producers and consumers.
"""

from typing import Dict, List, Set, Optional, Any


class DDGEdge(object):
    __slots__ = ("source", "target", "kind", "label")

    def __init__(self, source: "DDGNode", target: "DDGNode", kind: str, label: str = ""):
        self.source = source
        self.target = target
        self.kind = kind  # e.g., "def-use", "mem-read", "mem-write", "phi"
        self.label = label

    def __repr__(self):
        return "DDGEdge(%r -> %r, %s)" % (self.source, self.target, self.kind)


class DDGNode(object):
    __slots__ = ("node_id", "ir_node", "category", "edges_in", "edges_out")

    def __init__(self, node_id: int, ir_node: Any, category: str):
        self.node_id = node_id
        self.ir_node = ir_node  # dataflowIR.OpNode, SlotNode, or SSA Phi/Local
        self.category = category  # "op", "slot", "phi"
        self.edges_in: Set[DDGEdge] = set()
        self.edges_out: Set[DDGEdge] = set()

    def add_edge_to(self, other: "DDGNode", kind: str, label: str = ""):
        edge = DDGEdge(self, other, kind, label)
        self.edges_out.add(edge)
        other.edges_in.add(edge)
        return edge

    def __repr__(self):
        return "DDGNode(%d,%s)" % (self.node_id, self.category)

    def __hash__(self):
        return self.node_id

    def __eq__(self, other):
        return isinstance(other, DDGNode) and self.node_id == other.node_id


class DataDependenceGraph(object):
    __slots__ = ("nodes", "_id", "op_node_map", "slot_node_map")

    def __init__(self):
        self.nodes: List[DDGNode] = []
        self._id = 0
        self.op_node_map: Dict[Any, DDGNode] = {}
        self.slot_node_map: Dict[Any, DDGNode] = {}

    def _new_id(self) -> int:
        nid = self._id
        self._id += 1
        return nid

    def get_or_create_op_node(self, ir_op: Any) -> DDGNode:
        node = self.op_node_map.get(ir_op)
        if node is None:
            node = DDGNode(self._new_id(), ir_op, "op")
            self.nodes.append(node)
            self.op_node_map[ir_op] = node
        return node

    def get_or_create_slot_node(self, ir_slot: Any) -> DDGNode:
        node = self.slot_node_map.get(ir_slot)
        if node is None:
            node = DDGNode(self._new_id(), ir_slot, "slot")
            self.nodes.append(node)
            self.slot_node_map[ir_slot] = node
        return node

    def add_def_use(self, def_node: DDGNode, use_node: DDGNode, label: str = ""):
        return def_node.add_edge_to(use_node, "def-use", label)

    def add_mem_dep(self, src: DDGNode, dst: DDGNode, label: str = ""):
        return src.add_edge_to(dst, "memory", label)

    def all_edges(self) -> List[DDGEdge]:
        result: List[DDGEdge] = []
        for n in self.nodes:
            result.extend(n.edges_out)
        return result

    def stats(self) -> Dict[str, Any]:
        return {
            "nodes": len(self.nodes),
            "edges": len(self.all_edges()),
            "ops": sum(1 for n in self.nodes if n.category == "op"),
            "slots": sum(1 for n in self.nodes if n.category == "slot"),
        }



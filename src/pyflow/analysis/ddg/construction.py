"""
Data Dependence Graph (DDG) construction.

We build a DDG from dataflowIR graphs emitted by dataflowIR.convert.evaluateCode
or from CFG+SSA by traversing dataflow nodes and connecting def-use pairs.
"""

from typing import Optional, Any

from pyflow.analysis.dataflowIR import graph as df
from .graph import DataDependenceGraph, DDGNode


class DDGConstructor(object):
    __slots__ = ("ddg",)

    def __init__(self):
        self.ddg = DataDependenceGraph()

    def construct_from_dataflow(self, dataflow: df.DataflowGraph) -> DataDependenceGraph:
        # Create nodes for all ops and slots reachable from entry/exit
        self._index_dataflow(dataflow)

        # Connect def-use edges for local and heap flows
        self._connect_def_use()

        # Memory dependencies: connect writes to subsequent reads conservatively
        self._connect_memory_dependencies()

        return self.ddg

    # Indexing helpers
    def _index_op(self, op: df.OpNode) -> DDGNode:
        return self.ddg.get_or_create_op_node(op)

    def _index_slot(self, slot: df.SlotNode) -> DDGNode:
        return self.ddg.get_or_create_slot_node(slot)

    def _index_dataflow(self, dataflow: df.DataflowGraph) -> None:
        # Entry/Exit
        self._index_op(dataflow.entry)
        if dataflow.exit is not None:
            self._index_op(dataflow.exit)

        # Existing/null slots
        for slot in dataflow.existing.values():
            self._index_slot(slot)
        self._index_slot(dataflow.null)

        # Walk from entry following forward edges to collect ops/slots
        visited = set()
        stack = list(dataflow.entry.forward())
        while stack:
            node = stack.pop()
            if node in visited:
                continue
            visited.add(node)

            if isinstance(node, df.OpNode):
                self._index_op(node)
            elif isinstance(node, df.SlotNode):
                self._index_slot(node)

            for nxt in node.forward():
                if nxt not in visited:
                    stack.append(nxt)

    def _connect_def_use(self) -> None:
        # For each slot with a defn and a use, connect def(op) -> use(op)
        for ir_slot, slot_node in list(self.ddg.slot_node_map.items()):
            if hasattr(ir_slot, "defn") and ir_slot.defn is not None:
                def_op = ir_slot.defn
                def_ddg = self.ddg.get_or_create_op_node(def_op)

                # Each consumer op that lists this slot in its reverse() should be a use
                # dataflowIR nodes expose reverse() from reads/uses back to the op/producer
                # We can consult ir_slot.forward() to find the next op from a slot (its use)
                for user in ir_slot.forward():
                    use_ddg = self.ddg.get_or_create_op_node(user)
                    self.ddg.add_def_use(def_ddg, use_ddg, label=repr(slot_node.ir_node))

    def _connect_memory_dependencies(self) -> None:
        # Conservative: if an op writes a heap slot, and another op later reads or writes
        # the same heap slot object/name in the same hyperblock chain, add a memory edge.
        # We approximate temporal order by node_id (created in traversal order).
        ops = [n for n in self.ddg.nodes if n.category == "op"]
        ops.sort(key=lambda n: n.node_id)

        # Build a map from heap slot identity to last writer nodes
        last_write = {}

        for op in ops:
            ir = op.ir_node
            writes = []
            reads = []

            # GenericOp has heapModifies/heapReads; Entry can define entry slots; Merge/Gate also define
            if hasattr(ir, "heapModifies") and isinstance(getattr(ir, "heapModifies"), dict):
                writes.extend(ir.heapModifies.values())
            if hasattr(ir, "heapReads") and isinstance(getattr(ir, "heapReads"), dict):
                reads.extend(ir.heapReads.values())

            # Connect RAW/WAR/WAW with last_write
            key_func = lambda slot: getattr(slot, "name", None) or slot

            for slot in reads:
                k = key_func(slot)
                if k in last_write:
                    self.ddg.add_mem_dep(last_write[k], op, label="RAW")

            for slot in writes:
                k = key_func(slot)
                if k in last_write:
                    self.ddg.add_mem_dep(last_write[k], op, label="WAW")
                last_write[k] = op


def construct_ddg(dataflow: df.DataflowGraph) -> DataDependenceGraph:
    return DDGConstructor().construct_from_dataflow(dataflow)



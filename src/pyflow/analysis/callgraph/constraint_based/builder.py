"""
Constraint-based call graph extraction implementation.

This module implements a lightweight constraint-based algorithm for call graph
construction that over-approximates potential call relationships using simple
points-to style constraints over function values.
"""

import ast
import os
from typing import Dict, Set, List, Optional, Any

from ....machinery.callgraph import CallGraph, CallGraphError


class ConstraintEnv:
    """Environment for tracking points-to relationships and return values."""
    
    def __init__(self):
        self.points_to: Dict[str, Set[str]] = {}
        self.func_returns: Dict[str, Set[str]] = {}
    
    def add_points_to(self, var: str, func: str):
        """Add a points-to relationship: var points to func."""
        if var not in self.points_to:
            self.points_to[var] = set()
        self.points_to[var].add(func)
    
    def add_return_value(self, func: str, returned_func: str):
        """Record that func returns returned_func."""
        if func not in self.func_returns:
            self.func_returns[func] = set()
        self.func_returns[func].add(returned_func)
    
    def possible_functions(self, var: str) -> Set[str]:
        """Get all functions that var might point to."""
        return self.points_to.get(var, set())
    
    def get_return_values(self, func: str) -> Set[str]:
        """Get all functions that func might return."""
        return self.func_returns.get(func, set())


class FunctionBodyAnalyzer(ast.NodeVisitor):
    """AST visitor for analyzing function bodies and extracting call relationships."""
    
    def __init__(self, caller: str, function_names: Set[str], graph: CallGraph,
                 class_names: Set[str] = None, class_methods: Dict[str, Set[str]] = None,
                 import_modules: Dict[str, str] = None, from_imports: Dict[str, str] = None,
                 scope: str = "function", param_names: Set[str] = None,
                 global_env: ConstraintEnv = None):
        self.caller = caller
        self.function_names = function_names
        self.graph = graph
        self.class_names = class_names or set()
        self.class_methods = class_methods or {}
        self.import_modules = import_modules or {}
        self.from_imports = from_imports or {}
        self.scope = scope
        self.param_names = param_names or set()
        self.global_env = global_env or ConstraintEnv()
        
        # Local environment for this function
        self.env = ConstraintEnv()
    
    def _add_points_to(self, var: str, func: str):
        """Add points-to relationship to appropriate environment."""
        if self.scope == "module":
            self.global_env.add_points_to(var, func)
        else:
            self.env.add_points_to(var, func)
    
    def _add_points_to_class(self, var: str, cls: str):
        """Add points-to relationship for class instances."""
        if self.scope == "module":
            self.global_env.add_points_to(var, cls)
        else:
            self.env.add_points_to(var, cls)
    
    def _union_from(self, target_var: str, source_var: str):
        """Union points-to sets: target_var gets everything source_var points to."""
        source_funcs = (self.env.possible_functions(source_var) |
                       self.global_env.possible_functions(source_var))
        for func in source_funcs:
            self._add_points_to(target_var, func)
    
    def visit_Assign(self, node: ast.Assign):
        """Handle assignment statements."""
        # Handle function assignments like: a = func
        if isinstance(node.value, ast.Name):
            resolved = _resolve_name_to_function(node.value.id, self.function_names)
            if resolved:
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        self._add_points_to(target.id, resolved)
        
        # Handle class assignments like: a = MyClass
        elif isinstance(node.value, ast.Name):
            resolved = _resolve_name_to_class(node.value.id, self.class_names)
            if resolved:
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        self._add_points_to_class(target.id, resolved)
        
        # Handle variable assignments like: a = b
        elif isinstance(node.value, ast.Name):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    self._union_from(target.id, node.value.id)
    
    def visit_Return(self, node: ast.Return):
        """Handle return statements."""
        if node.value and isinstance(node.value, ast.Name):
            resolved = _resolve_name_to_function(node.value.id, self.function_names)
            if resolved:
                self.global_env.add_return_value(self.caller, resolved)
            else:
                # Check if it's a variable that points to functions
                for func in self.env.possible_functions(node.value.id):
                    self.global_env.add_return_value(self.caller, func)
    
    def _handle_call(self, call: ast.Call):
        """Handle function call nodes."""
        if isinstance(call.func, ast.Name):
            name = call.func.id
            
            # Handle variable calls like: f()
            if name in self.param_names or name in self.env.points_to:
                funcs = (self.env.possible_functions(name) |
                        self.global_env.possible_functions(name))
                for func in funcs:
                    self.graph.add_edge(self.caller, func)
                    self._propagate_args_to_callee(func, call.args)
                return
            
            # Handle direct function calls
            resolved = _resolve_name_to_function(name, self.function_names)
            if resolved:
                self.graph.add_edge(self.caller, resolved)
                self._propagate_args_to_callee(resolved, call.args)
                return
            
            # Handle class constructors
            cls = _resolve_name_to_class(name, self.class_names)
            if cls:
                init_name = f"{cls}.__init__"
                if init_name in self.function_names:
                    self.graph.add_edge(self.caller, init_name)
                return
            
            # Handle imports
            if name in self.from_imports:
                imported_func = self.from_imports[name]
                self.graph.add_edge(self.caller, imported_func)
                return
        
        elif isinstance(call.func, ast.Attribute):
            # Handle method calls like: obj.method()
            self._handle_method_call(call)
        
        elif isinstance(call.func, ast.Call):
            # Handle chained calls like: func()()
            target = self._resolve_call_target(call.func)
            if target:
                self.graph.add_edge(self.caller, target)
                self._propagate_args_to_callee(target, call.args)
    
    def _handle_method_call(self, call: ast.Call):
        """Handle method calls on objects."""
        if isinstance(call.func.value, ast.Name):
            obj_name = call.func.value.id
            method_name = call.func.attr
            
            # Get possible classes for the object
            obj_classes = (self.env.possible_functions(obj_name) |
                          self.global_env.possible_functions(obj_name))
            
            for cls in obj_classes:
                method_key = f"{cls}.{method_name}"
                if method_key in self.function_names:
                    self.graph.add_edge(self.caller, method_key)
    
    def _resolve_call_target(self, call_node: ast.Call) -> Optional[str]:
        """Recursively resolve what a call node is calling."""
        if isinstance(call_node.func, ast.Name):
            # Direct function call
            resolved = _resolve_name_to_function(call_node.func.id, self.function_names)
            if resolved:
                return resolved
            
            # Check return values
            return_vals = self.global_env.get_return_values(resolved or call_node.func.id)
            if return_vals:
                return list(return_vals)[0]  # Take first return value
        
        elif isinstance(call_node.func, ast.Call):
            # Chained call - recursively resolve
            return self._resolve_call_target(call_node.func)
        
        return None
    
    def _propagate_args_to_callee(self, callee: str, args: List[ast.expr]):
        """Propagate argument information to callee parameters."""
        # This is a simplified version - in practice we'd need parameter names
        # For now, just handle direct function arguments
        for arg in args:
            if isinstance(arg, ast.Name):
                # Check if argument is a direct function name
                resolved = _resolve_name_to_function(arg.id, self.function_names)
                if resolved:
                    self.graph.add_edge(callee, resolved)
                else:
                    # Check if it's a variable that points to functions
                    arg_funcs = (self.env.possible_functions(arg.id) |
                               self.global_env.possible_functions(arg.id))
                    for arg_func in arg_funcs:
                        self.graph.add_edge(callee, arg_func)
            
            elif isinstance(arg, ast.Call):
                # Handle calls as arguments like: func(func2())
                target = self._resolve_call_target(arg)
                if target:
                    self.graph.add_edge(callee, target)
    
    def visit_Call(self, node: ast.Call):
        """Visit call nodes."""
        self._handle_call(node)
    
    def visit_Lambda(self, node: ast.Lambda):
        """Visit lambda expressions."""
        # For now, just analyze the lambda body
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                self._handle_call(child)


def _collect_declarations(tree: ast.AST, module_name: str) -> tuple[Set[str], Set[str], Dict[str, Set[str]]]:
    """Collect function and class declarations from AST."""
    function_names: Set[str] = set()
    class_names: Set[str] = set()
    class_methods: Dict[str, Set[str]] = {}
    
    def collect_from_node(node: ast.AST, namespace: str = ""):
        if isinstance(node, ast.FunctionDef):
            full_name = f"{namespace}.{node.name}" if namespace else node.name
            function_names.add(full_name)
            
            # Also add nested functions
            for child in node.body:
                collect_from_node(child, full_name)
        
        elif isinstance(node, ast.ClassDef):
            full_name = f"{namespace}.{node.name}" if namespace else node.name
            class_names.add(full_name)
            class_methods[full_name] = set()
            
            for child in node.body:
                if isinstance(child, ast.FunctionDef):
                    method_name = f"{full_name}.{child.name}"
                    function_names.add(method_name)
                    class_methods[full_name].add(child.name)
                else:
                    collect_from_node(child, full_name)
        
        elif isinstance(node, ast.AsyncFunctionDef):
            # Handle async functions the same as regular functions
            collect_from_node(ast.FunctionDef(
                name=node.name,
                args=node.args,
                body=node.body,
                decorator_list=node.decorator_list,
                returns=node.returns,
                type_comment=node.type_comment
            ), namespace)
    
    # Start collecting from the module level
    for node in ast.iter_child_nodes(tree):
        collect_from_node(node, module_name)
    
    return function_names, class_names, class_methods


def _resolve_name_to_function(name: str, function_names: Set[str]) -> Optional[str]:
    """Resolve a name to a function, preferring more qualified names."""
    # Direct match
    if name in function_names:
        return name
    
    # Look for qualified names ending with this name
    candidates = [f for f in function_names if f.endswith(f".{name}")]
    if candidates:
        # Prefer longer (more qualified) names
        return max(candidates, key=len)
    
    return None


def _resolve_name_to_class(name: str, class_names: Set[str]) -> Optional[str]:
    """Resolve a name to a class."""
    if name in class_names:
        return name
    
    # Look for qualified names ending with this name
    candidates = [c for c in class_names if c.endswith(f".{name}")]
    if candidates:
        return max(candidates, key=len)
    
    return None


def extract_call_graph_constraint(source_code: str) -> CallGraph:
    """Extract call graph using constraint-based analysis."""
    graph = CallGraph()
    main_name = "main"
    graph.add_node(main_name)

    try:
        tree = ast.parse(source_code)
    except SyntaxError:
        return graph

    function_names, class_names, class_methods = _collect_declarations(tree, main_name)

    # Collect import mappings at module level
    import_modules: Dict[str, str] = {}
    from_imports: Dict[str, str] = {}
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                alias_name = alias.asname or alias.name.split(".")[0]
                import_modules[alias_name] = alias.name
        elif isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            for alias in node.names:
                if alias.name == "*":
                    continue
                alias_name = alias.asname or alias.name
                from_imports[alias_name] = f"{mod}.{alias.name}" if mod else alias.name

    # Create a global environment that will be shared across all analyzers
    global_env = ConstraintEnv()

    # PASS 1: Collect return value information from all functions and track assignments
    temp_env = ConstraintEnv()
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.FunctionDef):
            caller_qual = f"{main_name}.{node.name}"
            # Scan for assignments and returns in function body
            for stmt in ast.walk(node):
                if isinstance(stmt, ast.Assign):
                    if isinstance(stmt.value, ast.Name):
                        targets = [t for t in stmt.targets if isinstance(t, ast.Name)]
                        resolved = _resolve_name_to_function(stmt.value.id, function_names)
                        if resolved:
                            for t in targets:
                                temp_env.add_points_to(t.id, resolved)
                if isinstance(stmt, ast.Return) and stmt.value:
                    if isinstance(stmt.value, ast.Name):
                        resolved = _resolve_name_to_function(stmt.value.id, function_names)
                        if resolved:
                            global_env.add_return_value(caller_qual, resolved)
                        else:
                            for f in temp_env.possible_functions(stmt.value.id):
                                global_env.add_return_value(caller_qual, f)
        elif isinstance(node, ast.ClassDef):
            clsq = f"{main_name}.{node.name}"
            for b in node.body:
                if isinstance(b, ast.FunctionDef):
                    caller_qual = f"{clsq}.{b.name}"
                    for stmt in ast.walk(b):
                        if isinstance(stmt, ast.Assign):
                            if isinstance(stmt.value, ast.Name):
                                targets = [t for t in stmt.targets if isinstance(t, ast.Name)]
                                resolved = _resolve_name_to_function(stmt.value.id, function_names)
                                if resolved:
                                    for t in targets:
                                        temp_env.add_points_to(t.id, resolved)
                        if isinstance(stmt, ast.Return) and stmt.value:
                            if isinstance(stmt.value, ast.Name):
                                resolved = _resolve_name_to_function(stmt.value.id, function_names)
                                if resolved:
                                    global_env.add_return_value(caller_qual, resolved)
                                else:
                                    for f in temp_env.possible_functions(stmt.value.id):
                                        global_env.add_return_value(caller_qual, f)

    # PASS 2: Analyze call relationships
    # Analyze module-level (treat as main) without recursing into defs
    mod_analyzer = FunctionBodyAnalyzer(
        main_name, function_names, graph,
        class_names=class_names,
        class_methods=class_methods,
        import_modules=import_modules,
        from_imports=from_imports,
        scope="module",
        global_env=global_env,
    )
    
    # Only visit module-level statements (not function/class bodies)
    for node in ast.iter_child_nodes(tree):
        if not isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)):
            mod_analyzer.visit(node)

    # Add nodes for imported modules (for visibility in output)
    for alias, mod in import_modules.items():
        graph.add_node(alias)

    # Analyze free functions and class methods
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.FunctionDef):
            caller_qual = f"{main_name}.{node.name}"
            graph.add_node(caller_qual)
            params: Set[str] = set(a.arg for a in getattr(node.args, "args", []) if hasattr(a, "arg"))
            analyzer = FunctionBodyAnalyzer(
                caller_qual, function_names, graph,
                class_names=class_names,
                class_methods=class_methods,
                import_modules=import_modules,
                from_imports=from_imports,
                scope="function",
                param_names=params,
                global_env=global_env,
            )
            analyzer.visit(node)
        elif isinstance(node, ast.ClassDef):
            clsq = f"{main_name}.{node.name}"
            for b in node.body:
                if isinstance(b, ast.FunctionDef):
                    caller_qual = f"{clsq}.{b.name}"
                    graph.add_node(caller_qual)
                    analyzer = FunctionBodyAnalyzer(
                        caller_qual, function_names, graph,
                        class_names=class_names,
                        class_methods=class_methods,
                        import_modules=import_modules,
                        from_imports=from_imports,
                        scope="function",
                        global_env=global_env,
                    )
                    analyzer.visit(b)

    return graph


def analyze_file_constraint(filepath: str) -> str:
    """Analyze a file and return call graph as JSON string."""
    try:
        with open(filepath, "r") as f:
            source_code = f.read()
        
        graph = extract_call_graph_constraint(source_code)
        return graph.to_json()
    
    except Exception as e:
        return f'{{"error": "{str(e)}"}}'
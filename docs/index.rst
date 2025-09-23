Welcome to PyFlow's Documentation!
==================================

=============
Introduction
=============

PyFlow is a static analysis and compilation tool for Python code. It provides comprehensive analysis capabilities including:

* **Control Flow Analysis** - Control Flow Graph (CFG) construction and analysis
* **Data Flow Analysis** - Forward and backward data flow analysis with various meet functions
* **Inter-procedural Analysis (IPA)** - Context-sensitive analysis across function boundaries
* **Constraint-based Analysis (CPA)** - Constraint-based analysis using constraint solving for Python objects
* **Shape Analysis** - Analysis of data structure shapes and properties
* **Call Graph Analysis** - Function call relationship analysis with multiple algorithms
* **Control Dependence Graph (CDG)** - Control dependency analysis for program slicing
* **Optimization Passes** - Various compiler optimizations including constant folding, dead code elimination, and inlining


PyFlow is designed to be a powerful tool for:

- **Static Analysis**: Understanding program behavior without execution
- **Code Optimization**: Applying various optimization techniques to Python code
- **Program Understanding**: Visualizing and analyzing complex Python programs
- **Research**: Advancing static analysis techniques for dynamic languages

==========================
Installing and Using PyFlow
==========================

Install PyFlow from source
---------------------------

::

  git clone https://github.com/ZJU-Automated-Reasoning-Group/pyflow.git
  cd pyflow
  python -m venv venv
  source venv/bin/activate  # On Windows: venv\Scripts\activate
  pip install -e .

The setup script will:
- Create a Python virtual environment if it doesn't exist
- Activate the virtual environment and install dependencies
- Install PyFlow in development mode



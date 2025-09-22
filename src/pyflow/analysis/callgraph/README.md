# Call Graph Analysis Module


- ast-based: use Python's `ast` module instead of pyflow's full analysis pipeline.
- pycg-based: use a third-party tool `pycg`


## Limitations
- No IPA/CPA integration
- Basic AST parsing (not pyflow AST)

## Integration Steps

1. **Fix Program class** - store compiler context (`src/pyflow/application/program.py`)
2. **Add CPA integration** - populate call annotations via `ExtractDataflow`
3. **Add IPA integration** - use `CallGraphFinder` for context-sensitive analysis
4. **Use pyflow AST** - convert via `src/pyflow/language/python/parser.py`
5. **Add context tracking** - use `liveFuncContext` and `invokesContext`

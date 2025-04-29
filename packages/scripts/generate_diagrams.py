#!/usr/bin/env python
"""
Generate diagrams for:
  1. All functions in the functions directory
  2. Specific pipelines showing how functions interrelate
  
Outputs:
  docs/diagrams/function_overview.svg  - All functions grouped by module
  docs/pipelines/{pipeline_name}.svg   - Detailed pipeline diagrams
"""
import ast
import json
import os
import pathlib
import re
from typing import Dict, List, Optional, Set, Tuple, Any

# Try to import graphviz, provide instructions if not installed
try:
    import graphviz
except ImportError:
    print("Error: Graphviz Python package not found.")
    print("Please install it with: pip install graphviz")
    print("Note: You also need to install the Graphviz binaries:")
    print("  - macOS: brew install graphviz")
    print("  - Linux: apt-get install graphviz")
    print("  - Windows: See https://graphviz.org/download/")
    exit(1)

# Get the root directory of the project
ROOT = pathlib.Path(__file__).resolve().parents[2]
BACKEND_DIR = ROOT / "packages/backend"
FUNCTIONS_DIR = BACKEND_DIR / "functions" 
PIPELINES_DIR = BACKEND_DIR / "pipelines"
DIAGRAMS_DIR = ROOT / "docs/diagrams"
PIPELINE_DOCS_DIR = ROOT / "docs/pipelines"

# Create output directories if they don't exist
DIAGRAMS_DIR.mkdir(exist_ok=True)
PIPELINE_DOCS_DIR.mkdir(exist_ok=True)

def extract_function_info(file_path: pathlib.Path) -> Dict[str, Any]:
    """
    Extract information about functions in a Python file.
    
    Args:
        file_path: Path to the Python file
        
    Returns:
        Dictionary of function names to their details
    """
    functions = {}
    
    try:
        # Parse the file
        content = file_path.read_text()
        node = ast.parse(content)
        
        module_name = file_path.stem
        
        # Extract information from each function definition
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                # Get function signature
                args = [a.arg for a in item.args.args]
                
                # Get function docstring
                doc = ast.get_docstring(item) or "No description"
                doc_first_line = doc.split("\n")[0]
                
                functions[item.name] = {
                    "module": module_name,
                    "file": str(file_path.relative_to(BACKEND_DIR)),
                    "name": item.name,
                    "args": args,
                    "doc": doc_first_line,
                    "ast_node": item,
                    "source_lines": extract_function_source(content, item),
                }
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
    
    return functions

def extract_function_source(content: str, node: ast.FunctionDef) -> Tuple[int, int]:
    """Extract the line numbers for a function's source code"""
    return (node.lineno, node.end_lineno if hasattr(node, 'end_lineno') else node.lineno + 10)

def analyze_function_calls(func_node: ast.FunctionDef, all_functions: Dict[str, Dict]) -> Set[str]:
    """
    Analyze a function's AST to find calls to other known functions.
    
    Args:
        func_node: The AST node of the function
        all_functions: Dictionary of all known functions
        
    Returns:
        Set of function names that are called by this function
    """
    called_functions = set()
    
    # Helper function to recursively search for function calls
    def visit_node(node):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            func_name = node.func.id
            if func_name in all_functions:
                called_functions.add(func_name)
        
        # Recursively visit all child nodes
        for child in ast.iter_child_nodes(node):
            visit_node(child)
    
    visit_node(func_node)
    return called_functions

def generate_function_overview():
    """Generate a diagram showing all functions grouped by module"""
    print("Generating function overview diagram...")
    
    # Gather all functions from the functions directory
    all_functions = {}
    for py_file in FUNCTIONS_DIR.glob("**/*.py"):
        if py_file.name.startswith("_"):
            continue
        functions = extract_function_info(py_file)
        all_functions.update(functions)
    
    if not all_functions:
        print("No functions found in the functions directory.")
        return
    
    # Create a new graph
    dot = graphviz.Digraph(
        'function_overview', 
        comment='Function Overview',
        format='svg',
        engine='dot'
    )
    dot.attr(rankdir='LR', fontname='Arial', ranksep='1.5')
    dot.attr('node', shape='box', style='rounded,filled', fillcolor='lightblue', fontname='Arial')
    
    # Group functions by module
    modules = {}
    for func_name, func_info in all_functions.items():
        module = func_info['module']
        if module not in modules:
            modules[module] = []
        modules[module].append(func_info)
    
    # Create clusters for each module
    for module_name, funcs in modules.items():
        with dot.subgraph(name=f'cluster_{module_name}') as c:
            c.attr(label=module_name, style='rounded,filled', fillcolor='lightgrey')
            
            for func in funcs:
                # Create a node for each function
                func_id = f"{module_name}_{func['name']}"
                label = f"{func['name']}\\n{func['doc'][:30] + '...' if len(func['doc']) > 30 else func['doc']}"
                c.node(func_id, label=label)
    
    # Save the diagram
    output_path = DIAGRAMS_DIR / "function_overview"
    dot.render(filename=str(output_path), cleanup=True)
    print(f"Function overview diagram saved to {output_path}.svg")

def generate_pipeline_diagrams():
    """Generate detailed diagrams for each pipeline"""
    print("Generating pipeline diagrams...")
    
    # First, gather all functions from both functions and pipelines directories
    all_functions = {}
    
    # Get functions from the functions directory
    for py_file in FUNCTIONS_DIR.glob("**/*.py"):
        if py_file.name.startswith("_"):
            continue
        functions = extract_function_info(py_file)
        all_functions.update(functions)
    
    # Get functions from the pipelines directory
    pipeline_functions = {}
    for py_file in PIPELINES_DIR.glob("**/*.py"):
        if py_file.name.startswith("_"):
            continue
        functions = extract_function_info(py_file)
        pipeline_functions.update(functions)
        all_functions.update(functions)
    
    if not pipeline_functions:
        print("No pipeline functions found.")
        return
    
    # For each pipeline function, create a separate diagram
    for pipeline_name, pipeline_info in pipeline_functions.items():
        generate_single_pipeline_diagram(pipeline_name, pipeline_info, all_functions)

def generate_single_pipeline_diagram(pipeline_name: str, pipeline_info: Dict, all_functions: Dict):
    """Generate a diagram for a single pipeline"""
    print(f"Generating diagram for pipeline: {pipeline_name}")
    
    # Create a new graph
    dot = graphviz.Digraph(
        pipeline_name, 
        comment=f'Pipeline: {pipeline_name}',
        format='svg',
        engine='dot'
    )
    dot.attr(rankdir='LR', fontname='Arial')
    
    # Add the pipeline function as the main node
    pipeline_node_id = f"pipeline_{pipeline_name}"
    dot.node(
        pipeline_node_id, 
        label=f"{pipeline_name}\\n{pipeline_info['doc'][:30] + '...' if len(pipeline_info['doc']) > 30 else pipeline_info['doc']}",
        shape='box', 
        style='rounded,filled', 
        fillcolor='lightgreen', 
        fontname='Arial'
    )
    
    # Find all function calls made by this pipeline
    called_functions = analyze_function_calls(pipeline_info['ast_node'], all_functions)
    
    # Add nodes for called functions and connections
    processed_funcs = set()
    function_queue = list(called_functions)
    
    while function_queue:
        func_name = function_queue.pop(0)
        if func_name in processed_funcs:
            continue
        
        processed_funcs.add(func_name)
        
        if func_name in all_functions:
            func_info = all_functions[func_name]
            
            # Determine which directory the function is from
            is_pipeline = "pipelines" in func_info['file']
            fillcolor = 'lightyellow' if is_pipeline else 'lightblue'
            
            # Add node for this function
            func_node_id = f"func_{func_name}"
            dot.node(
                func_node_id, 
                label=f"{func_name}\\n{func_info['doc'][:30] + '...' if len(func_info['doc']) > 30 else func_info['doc']}",
                shape='box', 
                style='rounded,filled', 
                fillcolor=fillcolor, 
                fontname='Arial'
            )
            
            # Connect the pipeline to this function
            dot.edge(pipeline_node_id, func_node_id)
            
            # Find functions called by this function
            nested_called_functions = analyze_function_calls(func_info['ast_node'], all_functions)
            
            # Add connections to nested functions
            for nested_func in nested_called_functions:
                if nested_func in all_functions and nested_func != func_name:
                    nested_func_id = f"func_{nested_func}"
                    dot.edge(func_node_id, nested_func_id)
                    
                    # Add to queue if not processed yet
                    if nested_func not in processed_funcs:
                        function_queue.append(nested_func)
    
    # Save the diagram
    output_path = PIPELINE_DOCS_DIR / pipeline_name
    dot.render(filename=str(output_path), cleanup=True)
    print(f"Pipeline diagram saved to {output_path}.svg")
    
    # Generate accompanying Markdown documentation
    generate_pipeline_markdown(pipeline_name, pipeline_info, called_functions, all_functions)

def generate_pipeline_markdown(pipeline_name: str, pipeline_info: Dict, called_functions: Set[str], all_functions: Dict):
    """Generate Markdown documentation for a pipeline"""
    md_path = PIPELINE_DOCS_DIR / f"{pipeline_name}.md"
    
    with open(md_path, 'w') as f:
        f.write(f"# Pipeline: {pipeline_name}\n\n")
        f.write(f"{pipeline_info['doc']}\n\n")
        
        f.write("## Overview\n\n")
        f.write(f"![{pipeline_name} Diagram]({pipeline_name}.svg)\n\n")
        
        f.write("## Functions\n\n")
        f.write("| Function | Module | Description |\n")
        f.write("|----------|--------|-------------|\n")
        
        # Add the pipeline function itself
        module_name = pipeline_info['module']
        f.write(f"| **{pipeline_name}** | {module_name} | {pipeline_info['doc']} |\n")
        
        # Add all called functions
        for func_name in sorted(called_functions):
            if func_name in all_functions:
                func_info = all_functions[func_name]
                f.write(f"| {func_name} | {func_info['module']} | {func_info['doc']} |\n")
        
        f.write("\n## Parameters\n\n")
        f.write("| Parameter | Type | Description |\n")
        f.write("|-----------|------|-------------|\n")
        
        # Add parameters for the pipeline function
        for arg in pipeline_info['args']:
            f.write(f"| {arg} | | |\n")
        
        f.write("\n## Return Value\n\n")
        f.write("*Add the return value description here*\n\n")
        
        f.write("## Example Usage\n\n")
        f.write("```python\n")
        f.write(f"from packages.backend.pipelines.{module_name} import {pipeline_name}\n\n")
        f.write(f"result = {pipeline_name}({', '.join(pipeline_info['args'])})\n")
        f.write("```\n")
    
    print(f"Pipeline documentation saved to {md_path}")

def main():
    """Main function to generate all diagrams"""
    # Create output directories if they don't exist
    DIAGRAMS_DIR.mkdir(exist_ok=True, parents=True)
    PIPELINE_DOCS_DIR.mkdir(exist_ok=True, parents=True)
    
    # Generate function overview diagram
    generate_function_overview()
    
    # Generate pipeline diagrams
    generate_pipeline_diagrams()
    
    print("All diagrams generated successfully!")

if __name__ == "__main__":
    main() 
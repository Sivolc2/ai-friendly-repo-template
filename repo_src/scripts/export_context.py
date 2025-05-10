#!/usr/bin/env python
"""
Walk backend & frontend dirs and emit:
  registry/frontend_context.md    - Frontend summary
  registry/backend_context.md     - Backend summary
  registry/pipeline_context.md    - Pipeline summary
  registry/function_registry.json           - Machine-readable for LLM prompts
"""
import ast
import json
import hashlib
import pathlib
import os
import re
from typing import List, Dict, Any, Optional

# Get the root directory of the project
ROOT = pathlib.Path(__file__).resolve().parents[2]
BACKEND_PKGS = ["cce/backend"]
FRONTEND_PKGS = ["cce/frontend"]
PIPELINE_DOCS = ["cce/backend/pipelines"]
OUTPUT_DIR = ROOT / "registry"
CONTEXT_DIR = ROOT / "registry"


def extract_docstring(node: ast.AST) -> str:
    """
    Extract the docstring from an AST node.
    
    Args:
        node: The AST node to extract from
        
    Returns:
        The docstring or a default message if none exists
    """
    doc = ast.get_docstring(node) or "TODO: add docstring"
    return doc.split("\n")[0]  # First line only


def extract_function_info_python(file_path: pathlib.Path) -> List[Dict[str, Any]]:
    """
    Extract information about functions in a Python file.
    
    Args:
        file_path: Path to the Python file
        
    Returns:
        List of dictionaries containing function information
    """
    functions = []
    
    # Skip test files and private modules
    if "tests" in file_path.parts or file_path.name.startswith("_"):
        return functions
    
    try:
        # Parse the file
        node = ast.parse(file_path.read_text())
        
        # Extract information from each function definition
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                # Get function signature
                args = [a.arg for a in item.args.args]
                
                # Get function docstring
                doc = extract_docstring(item)
                
                # Generate a hash of the function for change detection
                func_hash = hashlib.md5(ast.unparse(item).encode()).hexdigest()[:8]
                
                functions.append({
                    "file": str(file_path.relative_to(ROOT)),
                    "name": item.name,
                    "language": "python",
                    "args": args,
                    "doc": doc,
                    "hash": func_hash,
                })
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
    
    return functions


def extract_function_info_typescript(file_path: pathlib.Path) -> List[Dict[str, Any]]:
    """
    Extract information about functions and components in a TypeScript/TSX file.
    
    Args:
        file_path: Path to the TypeScript file
        
    Returns:
        List of dictionaries containing function information
    """
    functions = []
    
    # Skip test files
    if "tests" in file_path.parts or file_path.name.endswith(".test.tsx") or file_path.name.endswith(".test.ts"):
        return functions
    
    try:
        # Read the file content
        content = file_path.read_text()
        
        # Extract function components and hooks
        # This is a simplistic approach; a proper implementation would use a TypeScript parser
        component_pattern = r'export\s+const\s+(\w+)(?:\s*:\s*React\.FC<.*?>)?\s*=\s*\(\{([^}]*)\}\)'
        hook_pattern = r'export\s+function\s+use(\w+)\s*\(([^)]*)\)'
        function_pattern = r'(?:export\s+)?(?:async\s+)?function\s+(\w+)\s*\(([^)]*)\)'
        
        # Check for JSDoc comments above functions
        jsdoc_pattern = r'/\*\*\s*([\s\S]*?)\s*\*/'
        
        # Find components
        for match in re.finditer(component_pattern, content):
            name = match.group(1)
            args = [arg.strip().split(':')[0].strip() for arg in match.group(2).split(',')] if match.group(2) else []
            
            # Try to find JSDoc above the component
            doc = "No description"
            start_pos = match.start()
            jsdoc_matches = list(re.finditer(jsdoc_pattern, content[:start_pos]))
            if jsdoc_matches:
                last_jsdoc = jsdoc_matches[-1]
                jsdoc_content = last_jsdoc.group(1)
                # Extract the first line of the description
                doc_lines = [line.strip().lstrip('*').strip() for line in jsdoc_content.split('\n')]
                doc_lines = [line for line in doc_lines if line and not line.startswith('@')]
                if doc_lines:
                    doc = doc_lines[0]
            
            func_hash = hashlib.md5(match.group(0).encode()).hexdigest()[:8]
            
            functions.append({
                "file": str(file_path.relative_to(ROOT)),
                "name": name,
                "language": "typescript",
                "type": "component",
                "args": args,
                "doc": doc,
                "hash": func_hash,
            })
        
        # Find hooks
        for match in re.finditer(hook_pattern, content):
            name = f"use{match.group(1)}"
            args = [arg.strip().split(':')[0].strip() for arg in match.group(2).split(',')] if match.group(2) else []
            
            # Try to find JSDoc above the hook
            doc = "No description"
            start_pos = match.start()
            jsdoc_matches = list(re.finditer(jsdoc_pattern, content[:start_pos]))
            if jsdoc_matches:
                last_jsdoc = jsdoc_matches[-1]
                jsdoc_content = last_jsdoc.group(1)
                # Extract the first line of the description
                doc_lines = [line.strip().lstrip('*').strip() for line in jsdoc_content.split('\n')]
                doc_lines = [line for line in doc_lines if line and not line.startswith('@')]
                if doc_lines:
                    doc = doc_lines[0]
            
            func_hash = hashlib.md5(match.group(0).encode()).hexdigest()[:8]
            
            functions.append({
                "file": str(file_path.relative_to(ROOT)),
                "name": name,
                "language": "typescript",
                "type": "hook",
                "args": args,
                "doc": doc,
                "hash": func_hash,
            })
        
        # Find regular functions
        for match in re.finditer(function_pattern, content):
            name = match.group(1)
            if name != "use" and not name.startswith('use'):  # Avoid matching hooks again
                args = [arg.strip().split(':')[0].strip() for arg in match.group(2).split(',')] if match.group(2) else []
                
                # Try to find JSDoc above the function
                doc = "No description"
                start_pos = match.start()
                jsdoc_matches = list(re.finditer(jsdoc_pattern, content[:start_pos]))
                if jsdoc_matches:
                    last_jsdoc = jsdoc_matches[-1]
                    jsdoc_content = last_jsdoc.group(1)
                    # Extract the first line of the description
                    doc_lines = [line.strip().lstrip('*').strip() for line in jsdoc_content.split('\n')]
                    doc_lines = [line for line in doc_lines if line and not line.startswith('@')]
                    if doc_lines:
                        doc = doc_lines[0]
                
                func_hash = hashlib.md5(match.group(0).encode()).hexdigest()[:8]
                
                functions.append({
                    "file": str(file_path.relative_to(ROOT)),
                    "name": name,
                    "language": "typescript",
                    "type": "function",
                    "args": args,
                    "doc": doc,
                    "hash": func_hash,
                })
    
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
    
    return functions


def extract_pipeline_summaries() -> List[Dict[str, Any]]:
    """
    Extract summaries from pipeline README files.
    
    Returns:
        List of dictionaries containing pipeline information
    """
    pipeline_info = []
    
    for pkg in PIPELINE_DOCS:
        pkg_path = ROOT / pkg
        # Find all README files in the pipeline directory
        for readme_path in pkg_path.glob("**/README*.md"):
            try:
                content = readme_path.read_text()
                
                # Extract the title (first heading)
                title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
                title = title_match.group(1) if title_match else os.path.basename(readme_path.parent)
                
                # Extract the first paragraph as summary
                paragraph_match = re.search(r'^(?!#)(.+?)$', content, re.MULTILINE)
                summary = paragraph_match.group(1).strip() if paragraph_match else "No description available"
                
                # Extract section headers for structure overview
                sections = []
                for section_match in re.finditer(r'^##\s+(.+)$', content, re.MULTILINE):
                    sections.append(section_match.group(1).strip())
                
                # Extract code examples
                code_examples = []
                for code_match in re.finditer(r'```python\s+(.*?)\s+```', content, re.DOTALL):
                    code = code_match.group(1).strip()
                    if len(code) > 0:
                        # Just take the first few lines as a sample
                        code_lines = code.split('\n')[:5]
                        if len(code_lines) < len(code.split('\n')):
                            code_lines.append('# ...')
                        code_examples.append('\n'.join(code_lines))
                
                pipeline_info.append({
                    "file": str(readme_path.relative_to(ROOT)),
                    "title": title,
                    "summary": summary,
                    "sections": sections,
                    "code_examples": code_examples[:1],  # Limit to first example
                    "path": str(readme_path.parent.relative_to(ROOT))
                })
            except Exception as e:
                print(f"Error processing {readme_path}: {e}")
    
    return pipeline_info


def main() -> None:
    """
    Main function that processes Python and TypeScript files and generates documentation.
    """
    backend_functions = []
    frontend_functions = []
    pipeline_summaries = []
    
    # Extract information from Python files (backend)
    for pkg in BACKEND_PKGS:
        pkg_path = ROOT / pkg
        for file_path in pkg_path.rglob("*.py"):
            functions = extract_function_info_python(file_path)
            backend_functions.extend(functions)
    
    # Extract information from TypeScript/TSX files (frontend)
    for pkg in FRONTEND_PKGS:
        pkg_path = ROOT / pkg
        for file_path in pkg_path.rglob("*.tsx"):
            functions = extract_function_info_typescript(file_path)
            frontend_functions.extend(functions)
        for file_path in pkg_path.rglob("*.ts"):
            functions = extract_function_info_typescript(file_path)
            frontend_functions.extend(functions)
    
    # Extract information from pipeline documentation
    pipeline_summaries = extract_pipeline_summaries()
    
    # Create output directories if they don't exist
    OUTPUT_DIR.mkdir(exist_ok=True, parents=True)
    
    # Write machine-readable context (all functions)
    all_functions = backend_functions + frontend_functions
    context_file = CONTEXT_DIR / "function_registry.json"
    context_file.write_text(json.dumps(all_functions, indent=2))
    
    # Write backend context file
    backend_md_lines = ["# Backend Context", "", "A concise index of backend functionality.", ""]
    
    # Group backend functions by file path
    by_path = {}
    for func in backend_functions:
        path = func["file"]
        if path not in by_path:
            by_path[path] = []
        by_path[path].append(func)
    
    # Add backend functions organized by file
    for path in sorted(by_path.keys()):
        backend_md_lines.append(f"## {path}")
        for func in sorted(by_path[path], key=lambda x: x["name"]):
            args_str = ", ".join(func["args"])
            backend_md_lines.append(f"- `{func['name']}({args_str})`: {func['doc']}")
        backend_md_lines.append("")
    
    backend_context_file = CONTEXT_DIR / "backend_context.md"
    backend_context_file.write_text("\n".join(backend_md_lines))
    
    # Write frontend context file
    frontend_md_lines = ["# Frontend Context", "", "A concise index of frontend functionality.", ""]
    
    # Group by type
    components = [f for f in frontend_functions if f.get("type") == "component"]
    hooks = [f for f in frontend_functions if f.get("type") == "hook"]
    functions = [f for f in frontend_functions if f.get("type") == "function"]
    
    if components:
        frontend_md_lines.append("## Components")
        for comp in sorted(components, key=lambda x: x["name"]):
            args_str = ", ".join(comp["args"])
            frontend_md_lines.append(f"- `{comp['name']}({args_str})`: {comp['doc']} ({comp['file']})")
        frontend_md_lines.append("")
    
    if hooks:
        frontend_md_lines.append("## Hooks")
        for hook in sorted(hooks, key=lambda x: x["name"]):
            args_str = ", ".join(hook["args"])
            frontend_md_lines.append(f"- `{hook['name']}({args_str})`: {hook['doc']} ({hook['file']})")
        frontend_md_lines.append("")
    
    if functions:
        frontend_md_lines.append("## Utility Functions")
        for func in sorted(functions, key=lambda x: x["name"]):
            args_str = ", ".join(func["args"])
            frontend_md_lines.append(f"- `{func['name']}({args_str})`: {func['doc']} ({func['file']})")
        frontend_md_lines.append("")
    
    frontend_context_file = CONTEXT_DIR / "frontend_context.md"
    frontend_context_file.write_text("\n".join(frontend_md_lines))
    
    # Write pipeline context file
    if pipeline_summaries:
        pipeline_md_lines = ["# Pipeline Context", "", "Summary of all pipelines in the application.", ""]
        
        for pipeline in sorted(pipeline_summaries, key=lambda x: x["path"]):
            pipeline_md_lines.append(f"## {pipeline['title']}")
            pipeline_md_lines.append(f"{pipeline['summary']}")
            
            pipeline_md_lines.append("\n**Key Sections:**")
            if pipeline["sections"]:
                for section in pipeline["sections"]:
                    pipeline_md_lines.append(f"- {section}")
            else:
                pipeline_md_lines.append("- No sections defined")
            
            if pipeline["code_examples"]:
                pipeline_md_lines.append("\n**Example:**")
                pipeline_md_lines.append("```python")
                pipeline_md_lines.append(pipeline["code_examples"][0])
                pipeline_md_lines.append("```")
            
            pipeline_md_lines.append(f"\nLocated at: `{pipeline['path']}`")
            pipeline_md_lines.append("")
        
        pipeline_context_file = CONTEXT_DIR / "pipeline_context.md"
        pipeline_context_file.write_text("\n".join(pipeline_md_lines))
    
    print(f"Exported {len(backend_functions)} backend functions")
    print(f"Exported {len(frontend_functions)} frontend components/functions")
    print(f"Exported {len(pipeline_summaries)} pipeline summaries")
    print(f"Machine-readable context: {context_file}")
    print(f"Backend context: {backend_context_file}")
    print(f"Frontend context: {frontend_context_file}")
    if pipeline_summaries:
        print(f"Pipeline context: {pipeline_context_file}")


if __name__ == "__main__":
    main() 
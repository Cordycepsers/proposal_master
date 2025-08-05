"""
Demo script for Python Code Analyzer and Package Builder tools.
"""
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.utils.tool_registry import tool_registry


def demo_code_analyzer():
    """Demonstrate Python Code Analyzer."""
    print("\n" + "="*60)
    print("PYTHON CODE ANALYZER DEMO")
    print("="*60)
    
    # Analyze a Python file
    result = tool_registry.execute_tool(
        "python_code_analyzer",
        file_path="src/utils/code_analyzer.py",
        check_type="all",
        severity_threshold="medium"
    )
    
    if "error" in result:
        print(f"❌ Error: {result['error']}")
        return
    
    print(f"📁 Analyzed: {result['file_path']}")
    print(f"🔍 Check Type: {result['check_type']}")
    print(f"📊 Summary:")
    print(f"   Total Issues: {result['summary']['total_issues']}")
    print(f"   By Severity: {result['summary']['by_severity']}")
    print(f"   By Category: {result['summary']['by_category']}")
    
    if result['issues']:
        print(f"\n📋 Issues Found:")
        for file_result in result['issues'][:2]:  # Show first 2 files
            print(f"\n  File: {file_result['file']}")
            for issue in file_result['issues'][:3]:  # Show first 3 issues
                print(f"    ⚠️  Line {issue.get('line', '?')}: {issue['message']} ({issue['severity']})")
    
    print(f"\n📈 Metrics:")
    metrics = result['metrics']
    print(f"   Files: {metrics['total_files']}")
    print(f"   Lines: {metrics['total_lines']}")
    print(f"   Functions: {metrics['total_functions']}")
    print(f"   Classes: {metrics['total_classes']}")
    print(f"   Avg File Size: {metrics['average_file_size']} lines")


def demo_package_builder():
    """Demonstrate Package Builder Tool."""
    print("\n" + "="*60)
    print("PACKAGE BUILDER DEMO")
    print("="*60)
    
    # Analyze current project structure
    print("📋 Analyzing current project structure...")
    result = tool_registry.execute_tool("package_builder", action="structure")
    
    if "error" in result:
        print(f"❌ Error: {result['error']}")
        return
    
    structure = result['structure']
    print(f"📦 Project Structure Analysis:")
    print(f"   ✅ setup.py: {structure['has_setup_py']}")
    print(f"   ✅ pyproject.toml: {structure['has_pyproject_toml']}")
    print(f"   ✅ requirements.txt: {structure['has_requirements']}")
    print(f"   ✅ tests/: {structure['has_tests']}")
    print(f"   ✅ docs/: {structure['has_docs']}")
    print(f"   ✅ CI/CD: {structure['has_ci']}")
    print(f"   ✅ LICENSE: {structure['has_license']}")
    print(f"   ✅ README: {structure['has_readme']}")
    print(f"   📁 Package directories: {structure['package_directories']}")
    print(f"   🐍 Python files: {len(structure['python_files'])} files")
    
    # Create a sample package (in temp directory)
    print(f"\n🔨 Creating sample package 'demo_package'...")
    import tempfile
    with tempfile.TemporaryDirectory() as temp_dir:
        result = tool_registry.execute_tool(
            "package_builder",
            action="create",
            name="demo_package",
            version="0.1.0",
            author="RFP System Demo",
            description="A demonstration package created by the RFP system",
            output_dir=temp_dir,
            include_docs=True,
            include_ci=True
        )
        
        if "error" in result:
            print(f"❌ Error: {result['error']}")
            return
        
        print(f"✅ Package created successfully!")
        print(f"   📁 Location: {result['package_dir']}")
        print(f"   📊 Structure:")
        
        for directory in result['structure']['directories'][:10]:  # Show first 10
            print(f"      📁 {directory}")
        
        for file_path in result['structure']['files'][:15]:  # Show first 15
            print(f"      📄 {file_path}")
        
        if len(result['structure']['files']) > 15:
            remaining = len(result['structure']['files']) - 15
            print(f"      ... and {remaining} more files")


def demo_tool_registry():
    """Demonstrate Tool Registry capabilities."""
    print("\n" + "="*60)
    print("TOOL REGISTRY DEMO")
    print("="*60)
    
    # List available tools
    tools = tool_registry.list_tools()
    print(f"🔧 Available Tools ({len(tools)}):")
    for name, description in tools.items():
        print(f"   • {name}: {description}")
    
    # Show tool details
    analyzer = tool_registry.get_tool("python_code_analyzer")
    if analyzer:
        print(f"\n🔍 Python Code Analyzer Parameters:")
        for param, info in analyzer.parameters.items():
            required = "✅" if info.get("required", False) else "🔲"
            default = f" (default: {info.get('default', 'N/A')})" if 'default' in info else ""
            print(f"   {required} {param}: {info['description']}{default}")
    
    builder = tool_registry.get_tool("package_builder")
    if builder:
        print(f"\n📦 Package Builder Actions:")
        actions = ["create", "test", "build", "publish", "lint", "structure"]
        for action in actions:
            print(f"   • {action}: Execute package {action} operation")


def main():
    """Run all demos."""
    print("🚀 AUTOMATED RFP SYSTEM - TOOLS DEMONSTRATION")
    print("=" * 60)
    
    try:
        demo_tool_registry()
        demo_code_analyzer()
        demo_package_builder()
        
        print("\n" + "="*60)
        print("✅ ALL DEMOS COMPLETED SUCCESSFULLY!")
        print("="*60)
        
    except KeyboardInterrupt:
        print("\n⚠️  Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

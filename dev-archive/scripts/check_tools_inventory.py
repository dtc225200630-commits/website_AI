import os
import sys

print("=== AGENT TOOLS INVENTORY ===\n")

# Check langchain_orchestrator
orchestrator_file = "agents/langchain_orchestrator.py"
if os.path.exists(orchestrator_file):
    with open(orchestrator_file, 'r', encoding='utf-8') as f:
        content = f.read()
        tools = []
        if "@tool\ndef syntax_check_tool" in content:
            tools.append("✓ syntax_check_tool")
        if "@tool\ndef requirement_check_tool" in content:
            tools.append("✓ requirement_check_tool")
        if "@tool\ndef structure_analysis_tool" in content:
            tools.append("✓ structure_analysis_tool")
        if "@tool\ndef test_validation_tool" in content:
            tools.append("✓ test_validation_tool")
        if "@tool\ndef llm_review_tool" in content:
            tools.append("✓ llm_review_tool")
        
        print(f"LangChain Orchestrator ({orchestrator_file}):")
        for tool in tools:
            print(f"  {tool}")
        print(f"  Total tools: {len(tools)}/5\n")
else:
    print(f"✗ {orchestrator_file} NOT FOUND\n")

# Check individual agents
agents = [
    ("syntax_agent_fixed.py", "syntax_agent"),
    ("requirement_agent_fixed.py", "requirement_agent"),
    ("structure_agent_fixed.py", "structure_agent"),
    ("test_agent_fixed.py", "test_agent"),
    ("llm_agent.py", "llm_agent"),
    ("aggregation_agent_fixed.py", "aggregation_agent"),
]

print("Individual Agent Implementations:")
for filename, func_name in agents:
    filepath = f"agents/{filename}"
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            if f"def {func_name}" in content:
                print(f"  ✓ {filename} - has {func_name}()")
            else:
                print(f"  ✗ {filename} - missing {func_name}()")
    else:
        print(f"  ✗ {filename} - FILE NOT FOUND")

print("\n=== COORDINATOR ===")
coordinator_file = "agents/coordinator.py"
if os.path.exists(coordinator_file):
    with open(coordinator_file, 'r', encoding='utf-8') as f:
        content = f.read()
        if "def coordinator" in content:
            print(f"  ✓ coordinator.py - has coordinator()")
        if "def simple_coordinator" in content:
            print(f"  ✓ coordinator.py - has simple_coordinator()")
else:
    print(f"  ✗ {coordinator_file} - FILE NOT FOUND")

print("\n=== FASTAPI INTEGRATION ===")
app_file = "app.py"
if os.path.exists(app_file):
    with open(app_file, 'r', encoding='utf-8') as f:
        content = f.read()
        if "from agents.coordinator import" in content:
            print(f"  ✓ app.py - imports coordinator")
        if "@app.post" in content:
            print(f"  ✓ app.py - has FastAPI endpoints")
else:
    print(f"  ✗ {app_file} - FILE NOT FOUND")

print("\n" + "="*60)
print("SUMMARY:")
print("  Total agents: 6 (syntax, requirement, structure, test, llm, aggregation)")
print("  Total tools: 5 (@tool decorated)")
print("  Orchestrator: 1 (langchain_orchestrator)")
print("  Coordinator: 1 (coordinator)")
print("  Framework: FastAPI + LangChain")
print("="*60)

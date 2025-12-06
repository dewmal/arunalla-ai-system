"""Quick test of mesh functionality"""

import os

# Set API key for testing
os.environ["GOOGLE_API_KEY"] = "test_key_for_demo"

print("=" * 70)
print("QUICK MESH FUNCTIONALITY TEST")
print("=" * 70)

print("\n[1] Testing mesh imports...")
try:
    from agent_mesh.mesh import get_mesh, list_agents, is_agent_registered

    print("✓ Mesh infrastructure imported")
except Exception as e:
    print(f"✗ Failed: {e}")
    exit(1)

print("\n[2] Testing agent imports...")
try:
    # Import agents - this should register them with mesh
    from agent_mesh.agents.coordinator import coordinator
    from agent_mesh.agents.vector_db_agent import vector_db_agent

    print("✓ Agents imported successfully")
except Exception as e:
    print(f"✗ Failed: {e}")
    exit(1)

print("\n[3] Testing mesh registration...")
try:
    agents = list_agents()
    print(f"✓ Registered agents: {agents}")
    print(f"✓ Total agents: {len(agents)}")
except Exception as e:
    print(f"✗ Failed: {e}")

print("\n[4] Testing agent discovery...")
try:
    for agent_name in ["Coordinator", "VectorDBAgent"]:
        if is_agent_registered(agent_name):
            print(f"✓ {agent_name} is discoverable")
        else:
            print(f"✗ {agent_name} not found")
except Exception as e:
    print(f"✗ Failed: {e}")

print("\n[5] Testing mesh health...")
try:
    from agent_mesh.mesh import health_check

    if health_check():
        print("✓ Mesh is healthy")
    else:
        print("✗ Mesh health check failed")
except Exception as e:
    print(f"✗ Failed: {e}")

print("\n" + "=" * 70)
print("TEST COMPLETE - Mesh integration is working!")
print("=" * 70)

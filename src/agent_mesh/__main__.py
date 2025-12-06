"""Demo script for agent mesh integration"""

import os
import asyncio
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


async def demo_mesh_discovery():
    """Demo mesh discovery and agent registration"""
    from agent_mesh.mesh import list_agents, get_mesh

    print("\n" + "=" * 70)
    print("DEMO: Mesh Discovery and Agent Registration")
    print("=" * 70 + "\n")

    # Import agents (this triggers their registration)
    from agent_mesh.agents.coordinator import coordinator
    from agent_mesh.agents.vector_db_agent import vector_db_agent

    print("Agents have been initialized and registered with the mesh.\n")

    # List registered agents
    agents = list_agents()
    print(f"Registered agents in the mesh: {agents}")
    print(f"Total agents: {len(agents)}\n")

    # Show mesh health
    mesh = get_mesh()
    print(f"Mesh instance: {mesh}")
    print(f"Mesh type: LocalMesh (in-memory communication)\n")

    print("-" * 70 + "\n")


async def demo_mesh_communication():
    """Demo communication between agents through the mesh"""
    from agent_mesh.mesh import send_message, list_agents

    print("\n" + "=" * 70)
    print("DEMO: Mesh Communication Between Agents")
    print("=" * 70 + "\n")

    # Verify agents are registered
    agents = list_agents()
    print(f"Available agents: {agents}\n")

    if "VectorDBAgent" not in agents:
        print("⚠️  VectorDBAgent not registered with mesh")
        return

    # Send a message through the mesh
    query = "Search for information about Python programming"
    print(f"Sending message to VectorDBAgent through mesh:")
    print(f"Query: {query}\n")
    print("Response from VectorDBAgent:")
    print("-" * 70)

    try:
        response = send_message(
            from_agent="demo_client", to_agent="VectorDBAgent", message=query
        )
        print(response)
    except Exception as e:
        logger.error(f"Error in mesh communication: {e}")
        print(f"Error: {e}")

    print("-" * 70 + "\n")


async def demo_coordinator_with_mesh():
    """Demo the coordinator agent using mesh to delegate to vector_db_agent"""
    from agent_mesh.agents.coordinator import coordinator

    print("\n" + "=" * 70)
    print("DEMO: Coordinator Agent with Mesh Integration")
    print("=" * 70 + "\n")

    queries = [
        "What information do you have about Python programming?",
        "Find documents related to artificial intelligence",
        "Can you search for information on data structures?",
    ]

    for query in queries:
        print(f"User Query: {query}\n")
        print("Coordinator Response:")
        print("-" * 70)

        try:
            response = await coordinator.chat(query)
            print(response)
        except Exception as e:
            logger.error(f"Error in coordinator demo: {e}")
            print(f"Error: {e}")

        print("-" * 70 + "\n")


async def demo_with_sample_data():
    """Demo with sample data loaded into the vector database"""
    from agent_mesh.services.vector_db_service import vector_db_service
    from agent_mesh.mesh import send_message, list_agents

    print("\n" + "=" * 70)
    print("DEMO: End-to-End Mesh Communication with Sample Data")
    print("=" * 70 + "\n")

    # Sample documents
    sample_docs = [
        "Python is a high-level programming language known for its simplicity and readability.",
        "Machine learning is a branch of artificial intelligence that focuses on learning from data.",
        "Data structures are ways of organizing and storing data efficiently in a computer.",
        "Neural networks are computing systems inspired by biological neural networks.",
        "Algorithms are step-by-step procedures for solving problems or performing computations.",
    ]

    print("Loading sample documents into vector database...")
    try:
        # Create collection and add documents
        success = vector_db_service.add_documents(sample_docs)
        if success:
            print("✓ Sample documents loaded successfully!\n")
        else:
            print("✗ Failed to load sample documents\n")
            return
    except Exception as e:
        logger.error(f"Error loading sample data: {e}")
        print(f"✗ Error: {e}\n")
        return

    # Show mesh status
    agents = list_agents()
    print(f"Mesh status: {len(agents)} agents registered")
    print(f"Agents: {agents}\n")

    # Test queries through mesh
    test_queries = [
        "Tell me about Python programming",
        "What is machine learning?",
        "Explain data structures",
    ]

    print("Testing VectorDBAgent via mesh communication...\\n")
    for query in test_queries:
        print(f"Query: {query}\n")
        print("VectorDBAgent Response (via mesh):")
        print("-" * 70)

        try:
            response = send_message(
                from_agent="demo_client", to_agent="VectorDBAgent", message=query
            )
            print(response)
        except Exception as e:
            logger.error(f"Error in query: {e}")
            print(f"Error: {e}")

        print("-" * 70 + "\n")


async def demo_error_handling():
    """Demo error handling in mesh communication"""
    from agent_mesh.mesh import send_message, is_agent_registered

    print("\n" + "=" * 70)
    print("DEMO: Mesh Error Handling")
    print("=" * 70 + "\n")

    # Test 1: Agent not found
    print("Test 1: Sending message to non-existent agent")
    print("-" * 70)

    try:
        if not is_agent_registered("NonExistentAgent"):
            print("✓ Agent 'NonExistentAgent' is not registered (as expected)")

        response = send_message(
            from_agent="demo_client", to_agent="NonExistentAgent", message="Hello"
        )
        print(f"Unexpected success: {response}")
    except ValueError as e:
        print(f"✓ Caught expected error: {e}")
    except Exception as e:
        print(f"✗ Unexpected error type: {e}")

    print("-" * 70 + "\n")


async def main():
    """Run all demos"""
    print("\n" + "=" * 70)
    print("AGENT MESH INTEGRATION DEMO")
    print("Demonstrating Ceylon AI LocalMesh for Multi-Agent Communication")
    print("=" * 70)

    # Check if Qdrant is available
    from agent_mesh.services.vector_db_service import vector_db_service

    print("\nChecking Qdrant connection...")
    if vector_db_service.health_check():
        print("✓ Qdrant is healthy and accessible\n")

        # Run all demos
        await demo_mesh_discovery()
        await demo_error_handling()
        await demo_with_sample_data()
        await demo_coordinator_with_mesh()
    else:
        print("✗ Qdrant is not accessible")
        print("Please ensure Qdrant is running (e.g., via Docker)")
        print("You can start Qdrant with: docker run -p 6333:6333 qdrant/qdrant\n")

        # Run demos without data
        print("Running mesh demos without vector database...\n")
        await demo_mesh_discovery()
        await demo_error_handling()
        await demo_mesh_communication()

    print("\n" + "=" * 70)
    print("DEMO COMPLETE")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    asyncio.run(main())

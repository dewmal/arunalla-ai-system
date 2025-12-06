# Agent Mesh - Ceylon AI Mesh Networking Integration

This module demonstrates the integration of Ceylon AI's **LocalMesh** for multi-agent communication, enabling agents to discover each other, send messages, and coordinate actions seamlessly.

## Architecture

### Mesh Networking Flow

```
User/Client
    ↓
Coordinator Agent ←→ LocalMesh ←→ Vector DB Agent
    ↓                                    ↓
Synthesizes                      Vector Search Tool
Response                                 ↓
                                    Qdrant Database
```

The mesh provides:

- **Agent Discovery**: Agents can find each other by name via `mesh.list_agents()`
- **Message Routing**: Structured communication via `mesh.send_message()`
- **Scalability**: Easy addition of new agents to the mesh
- **Error Handling**: Built-in handling for agent-not-found and message failures

### Components

1. **Mesh Infrastructure** (`mesh.py`)

   - Singleton LocalMesh instance for agent communication
   - Agent registration and discovery utilities
   - Message routing with error handling
   - Health check functionality

2. **Vector Search Tool** (`tools/vector_search_tool.py`)

   - Ceylon AI tool that wraps `VectorDBService.search()`
   - Performs semantic search on the knowledge base
   - Returns formatted results with scores and metadata

3. **Vector DB Agent** (`agents/vector_db_agent.py`)

   - Specialized agent for searching the knowledge base
   - Registered with mesh as "VectorDBAgent"
   - Uses the vector search tool to find relevant documents
   - Interprets and explains search results

4. **Coordinator Agent** (`agents/coordinator.py`)

   - Orchestrates multiple specialized agents through the mesh
   - Registered with mesh as "Coordinator"
   - Delegates knowledge retrieval tasks to Vector DB Agent
   - Synthesizes information into coherent responses

5. **Vector DB Service** (`services/vector_db_service.py`)
   - Manages Qdrant vector database operations
   - Handles document embeddings using Google AI
   - Provides semantic search capabilities

## How Mesh Networking Works

### 1. Agent Registration

When agents are imported, they automatically register with the mesh:

```python
from agent_mesh.agents.coordinator import coordinator
from agent_mesh.agents.vector_db_agent import vector_db_agent

# Both agents are now registered with the mesh
# You can verify with:
from agent_mesh.mesh import list_agents
print(list_agents())  # ['Coordinator', 'VectorDBAgent']
```

### 2. Agent Discovery

Find agents in the mesh:

```python
from agent_mesh.mesh import list_agents, is_agent_registered

# List all agents
agents = list_agents()
print(f"Available agents: {agents}")

# Check if specific agent exists
if is_agent_registered("VectorDBAgent"):
    print("VectorDBAgent is ready!")
```

### 3. Message Routing

Send messages between agents through the mesh:

```python
from agent_mesh.mesh import send_message

# Send a search request to VectorDBAgent
response = send_message(
    from_agent="my_client",
    to_agent="VectorDBAgent",
    message="Find information about Python programming"
)
print(response)
```

### 4. Communication Flow

```
Client sends query
    ↓
mesh.send_message("client", "Coordinator", query)
    ↓
Coordinator receives message via mesh
    ↓
Coordinator sends to VectorDBAgent via mesh
    ↓
VectorDBAgent uses vector_search tool
    ↓
Results flow back through mesh
    ↓
Coordinator synthesizes response
    ↓
Response returns to client
```

## Usage

### Running the Demo

```bash
# Make sure Qdrant is running
docker run -p 6333:6333 qdrant/qdrant

# Run the mesh demo script
python -m agent_mesh
```

The demo will show:

- Mesh agent registration and discovery
- Agent communication through the mesh
- Error handling (agent not found, etc.)
- Full end-to-end workflow with sample data

### Using the Mesh in Your Code

#### Basic Usage

```python
from agent_mesh.mesh import get_mesh, send_message, list_agents

# Get the mesh instance
mesh = get_mesh()

# List registered agents
agents = list_agents()
print(f"Available: {agents}")

# Send a message
response = send_message(
    from_agent="my_app",
    to_agent="Coordinator",
    message="What is machine learning?"
)
```

#### Using Agents Directly

```python
from agent_mesh.agents.coordinator import coordinator

# The coordinator is already registered with the mesh
response = await coordinator.chat("What is machine learning?")
print(response)
```

#### Direct Vector Search

```python
from agent_mesh.agents.vector_db_agent import vector_db_agent

# Search the knowledge base directly
response = await vector_db_agent.chat("Find information about Python")
print(response)
```

#### Adding Documents to Knowledge Base

```python
from agent_mesh.services.vector_db_service import vector_db_service

# Add documents
documents = [
    "Python is a programming language...",
    "Machine learning is a branch of AI...",
]

vector_db_service.add_documents(documents)
```

## Configuration

Required environment variables:

```bash
# Google AI for embeddings and LLM
GOOGLE_API_KEY=your_google_api_key

# Qdrant configuration
QDRANT_HOST=localhost
QDRANT_PORT=6333
QDRANT_COLLECTION_NAME=documents
VECTOR_DIMENSION=768
```

## Mesh Features

### LocalMesh Characteristics

- **Speed**: Ultra-low latency (microsecond range)
- **Reliability**: In-memory, no network overhead
- **Scalability**: Limited by machine resources
- **Use Case**: Single-machine deployments, testing, development

### Built-in Error Handling

The mesh handles common error scenarios:

```python
from agent_mesh.mesh import send_message, is_agent_registered

# Check before sending
if is_agent_registered("MyAgent"):
    response = send_message("client", "MyAgent", "Hello")
else:
    print("Agent not found!")

# Or catch exceptions
try:
    response = send_message("client", "NonExistent", "Hello")
except ValueError as e:
    print(f"Agent error: {e}")
except RuntimeError as e:
    print(f"Message delivery error: {e}")
```

## Mesh Patterns

### Request-Reply Pattern

```python
from agent_mesh.mesh import send_message

# Simple request-reply
response = send_message(
    from_agent="client",
    to_agent="VectorDBAgent",
    message="Search for Python tutorials"
)
print(response)
```

### Fan-Out Pattern (Future)

```python
# Send to multiple agents
agents = ["VectorDBAgent", "AnalysisAgent", "SummaryAgent"]
responses = []

for agent in agents:
    if is_agent_registered(agent):
        response = send_message("orchestrator", agent, "Process data")
        responses.append(response)
```

## Example Queries

The coordinator can answer questions like:

- "What information do you have about Python?"
- "Tell me about machine learning"
- "Find documents related to data structures"
- "Search for information on algorithms"

## Development

### Adding New Agents

1. Create your agent:

```python
from ceylonai_next import LlmAgent
from agent_mesh.mesh import register_agent

my_agent = LlmAgent("MyAgent", "google::gemini-2.5-flash")
my_agent.with_system_prompt("You are a helpful agent...")
my_agent.build()

# Register with mesh
register_agent(my_agent)
```

2. Agent is now discoverable:

```python
from agent_mesh.mesh import list_agents
print(list_agents())  # Will include 'MyAgent'
```

### Testing

Run integration tests:

```bash
python -m agent_mesh.test_integration
```

Tests verify:

- Mesh initialization
- Agent registration
- Agent discovery
- Message routing capabilities
- Tool integration

## Monitoring and Debugging

### List Registered Agents

```python
from agent_mesh.mesh import list_agents

agents = list_agents()
print(f"Registered agents: {agents}")
```

### Health Check

```python
from agent_mesh.mesh import health_check

if health_check():
    print("Mesh is operational")
else:
    print("Mesh has issues")
```

### Logging

The mesh uses Python's logging module. Enable debug logging:

```python
import logging

logging.basicConfig(level=logging.DEBUG)
```

You'll see messages like:

```
INFO - Initializing LocalMesh for agent communication
INFO - Registered agent 'Coordinator' with mesh
DEBUG - Routing message from 'client' to 'VectorDBAgent'
```

## Troubleshooting

**Agent Not Found**

```python
ValueError: Agent 'AgentName' is not registered with the mesh
```

- Ensure the agent module is imported (which triggers registration)
- Verify agent name matches exactly (case-sensitive)
- Check with `list_agents()` to see what's registered

**Qdrant Connection Error**

- Ensure Qdrant is running: `docker run -p 6333:6333 qdrant/qdrant`
- Check `QDRANT_HOST` and `QDRANT_PORT` environment variables

**No Results Found**

- Ensure documents are loaded into the knowledge base
- Check that the collection exists
- Verify embeddings are being generated

**API Key Error**

- Set `GOOGLE_API_KEY` environment variable
- Get API key from: https://makersuite.google.com/app/apikey

## Scaling Considerations

### Current: Single Machine (LocalMesh)

- Fast in-memory communication
- Suitable for development, testing, small applications
- Limited by single machine resources

### Future: Multiple Machines (DistributedMesh)

Ceylon AI will support distributed mesh networking in the future:

- Same API as LocalMesh
- Agents can run on different computers
- Network-based communication
- High availability and scalability

## Next Steps

- **Agents** - Learn about agent fundamentals
- **Tools & Actions** - Extend agent capabilities
- **Memory System** - Share knowledge between agents
- **Examples** - Browse complete examples
- **Ceylon AI Docs** - Full Ceylon AI documentation

## Best Practices

1. **Always register agents**: Import agent modules to trigger registration
2. **Use descriptive names**: "EmailValidator" not "Agent1"
3. **Check registration**: Use `is_agent_registered()` before sending
4. **Handle errors**: Catch `ValueError` for agent-not-found
5. **Document message formats**: Clear input/output contracts
6. **Enable logging**: Use debug logging during development

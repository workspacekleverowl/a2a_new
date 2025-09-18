import uvicorn
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentSkill
from agent_executor import CabAgentExecutor


def main():
    skill = AgentSkill(
        id="find_cabs",
        name="Find Cabs",
        description="Finds cab options for a given location.",
        tags=["cabs", "transportation", "travel"],
        examples=["Find a cab to the airport"],
    )

    agent_card = AgentCard(
        name="Cab_Agent",
        description="An agent that finds and books cabs.",
        url="http://localhost:10003/",
        defaultInputModes=["text"],
        defaultOutputModes=["text"],
        skills=[skill],
        version="1.0.0",
        capabilities=AgentCapabilities(),
    )

    request_handler = DefaultRequestHandler(
        agent_executor=CabAgentExecutor(),
        task_store=InMemoryTaskStore(),
    )

    server = A2AStarletteApplication(
        http_handler=request_handler,
        agent_card=agent_card,
    )

    uvicorn.run(server.build(), host="0.0.0.0", port=10003)


if __name__ == "__main__":
    main()

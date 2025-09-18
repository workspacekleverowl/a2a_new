import uvicorn
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentSkill
from agent_executor import HotelAgentExecutor


def main():
    skill = AgentSkill(
        id="find_hotels",
        name="Find Hotels",
        description="Finds hotel options for a given location and dates.",
        tags=["hotels", "travel"],
        examples=["Find hotels in Paris"],
    )

    agent_card = AgentCard(
        name="Hotel_Agent",
        description="An agent that finds and books hotels.",
        url="http://localhost:10002/",
        defaultInputModes=["text"],
        defaultOutputModes=["text"],
        skills=[skill],
        version="1.0.0",
        capabilities=AgentCapabilities(),
    )

    request_handler = DefaultRequestHandler(
        agent_executor=HotelAgentExecutor(),
        task_store=InMemoryTaskStore(),
    )

    server = A2AStarletteApplication(
        http_handler=request_handler,
        agent_card=agent_card,
    )

    uvicorn.run(server.build(), host="0.0.0.0", port=10002)


if __name__ == "__main__":
    main()

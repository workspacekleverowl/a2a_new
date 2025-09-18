import uvicorn
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentSkill
from agent_executor import FoodAgentExecutor


def main():
    skill = AgentSkill(
        id="find_restaurants",
        name="Find Restaurants",
        description="Finds restaurant recommendations.",
        tags=["food", "restaurants", "travel"],
        examples=["Find a good Italian restaurant"],
    )

    agent_card = AgentCard(
        name="Food_Agent",
        description="An agent that provides restaurant recommendations.",
        url="http://localhost:10008/",
        defaultInputModes=["text"],
        defaultOutputModes=["text"],
        skills=[skill],
        version="1.0.0",
        capabilities=AgentCapabilities(),
    )

    request_handler = DefaultRequestHandler(
        agent_executor=FoodAgentExecutor(),
        task_store=InMemoryTaskStore(),
    )

    server = A2AStarletteApplication(
        http_handler=request_handler,
        agent_card=agent_card,
    )

    uvicorn.run(server.build(), host="0.0.0.0", port=10008)


if __name__ == "__main__":
    main()

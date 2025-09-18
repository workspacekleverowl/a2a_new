import uvicorn
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentSkill
from agent_executor import ActivityAgentExecutor


def main():
    skill = AgentSkill(
        id="find_activities",
        name="Find Activities",
        description="Finds activity options for a given location.",
        tags=["activities", "entertainment", "travel"],
        examples=["Find activities in Paris"],
    )

    agent_card = AgentCard(
        name="Activity_Agent",
        description="An agent that finds and books activities.",
        url="http://localhost:10004/",
        defaultInputModes=["text"],
        defaultOutputModes=["text"],
        skills=[skill],
        version="1.0.0",
        capabilities=AgentCapabilities(),
    )

    request_handler = DefaultRequestHandler(
        agent_executor=ActivityAgentExecutor(),
        task_store=InMemoryTaskStore(),
    )

    server = A2AStarletteApplication(
        http_handler=request_handler,
        agent_card=agent_card,
    )

    uvicorn.run(server.build(), host="0.0.0.0", port=10004)


if __name__ == "__main__":
    main()

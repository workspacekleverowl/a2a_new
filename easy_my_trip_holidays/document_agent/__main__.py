import uvicorn
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentSkill
from agent_executor import DocumentAgentExecutor


def main():
    skill = AgentSkill(
        id="check_documents",
        name="Check Documents",
        description="Checks the required travel documents for a destination.",
        tags=["documents", "visa", "travel"],
        examples=["What documents do I need for France?"],
    )

    agent_card = AgentCard(
        name="Document_Agent",
        description="An agent that provides information about required travel documents.",
        url="http://localhost:10007/",
        defaultInputModes=["text"],
        defaultOutputModes=["text"],
        skills=[skill],
        version="1.0.0",
        capabilities=AgentCapabilities(),
    )

    request_handler = DefaultRequestHandler(
        agent_executor=DocumentAgentExecutor(),
        task_store=InMemoryTaskStore(),
    )

    server = A2AStarletteApplication(
        http_handler=request_handler,
        agent_card=agent_card,
    )

    uvicorn.run(server.build(), host="0.0.0.0", port=10007)


if __name__ == "__main__":
    main()

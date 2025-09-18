import uvicorn
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentSkill
from agent_executor import BudgetAgentExecutor


def main():
    skill = AgentSkill(
        id="check_budget",
        name="Check Budget",
        description="Checks if the current spending is within budget.",
        tags=["budget", "finance", "travel"],
        examples=["Am I still within my budget?"],
    )

    agent_card = AgentCard(
        name="Budget_Agent",
        description="An agent that manages the travel budget.",
        url="http://localhost:10006/",
        defaultInputModes=["text"],
        defaultOutputModes=["text"],
        skills=[skill],
        version="1.0.0",
        capabilities=AgentCapabilities(),
    )

    request_handler = DefaultRequestHandler(
        agent_executor=BudgetAgentExecutor(),
        task_store=InMemoryTaskStore(),
    )

    server = A2AStarletteApplication(
        http_handler=request_handler,
        agent_card=agent_card,
    )

    uvicorn.run(server.build(), host="0.0.0.0", port=10006)


if __name__ == "__main__":
    main()

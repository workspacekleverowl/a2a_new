import uvicorn
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentSkill
from agent_executor import CurrencyAgentExecutor


def main():
    skill = AgentSkill(
        id="get_exchange_rate",
        name="Get Exchange Rate",
        description="Gets the exchange rate between two currencies.",
        tags=["currency", "exchange", "travel"],
        examples=["What is the exchange rate between USD and EUR?"],
    )

    agent_card = AgentCard(
        name="Currency_Agent",
        description="An agent that provides currency exchange rates.",
        url="http://localhost:10009/",
        defaultInputModes=["text"],
        defaultOutputModes=["text"],
        skills=[skill],
        version="1.0.0",
        capabilities=AgentCapabilities(),
    )

    request_handler = DefaultRequestHandler(
        agent_executor=CurrencyAgentExecutor(),
        task_store=InMemoryTaskStore(),
    )

    server = A2AStarletteApplication(
        http_handler=request_handler,
        agent_card=agent_card,
    )

    uvicorn.run(server.build(), host="0.0.0.0", port=10009)


if __name__ == "__main__":
    main()

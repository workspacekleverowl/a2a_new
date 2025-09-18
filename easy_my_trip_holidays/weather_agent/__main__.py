import uvicorn
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentSkill
from agent_executor import WeatherAgentExecutor

def create_app():
    """Creates the ASGI application."""
    skill = AgentSkill(
        id="get_weather",
        name="Get Weather",
        description="Gets the weather forecast for a given location.",
        tags=["weather", "travel"],
        examples=["What's the weather in Paris?"],
    )

    agent_card = AgentCard(
        name="Weather_Agent",
        description="An agent that provides weather forecasts.",
        url="http://localhost:10005/",
        defaultInputModes=["text"],
        defaultOutputModes=["text"],
        skills=[skill],
        version="1.0.0",
        capabilities=AgentCapabilities(),
    )

    request_handler = DefaultRequestHandler(
        agent_executor=WeatherAgentExecutor(),
        task_store=InMemoryTaskStore(),
    )

    server = A2AStarletteApplication(
        http_handler=request_handler,
        agent_card=agent_card,
    )
    return server.build()

app = create_app()

if __name__ == "__main__":
    # This allows running the script directly for development/debugging
    uvicorn.run(app, host="0.0.0.0", port=10005)

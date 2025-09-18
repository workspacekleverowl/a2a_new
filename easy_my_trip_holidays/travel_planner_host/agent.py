import asyncio
import json
import uuid
from datetime import datetime
from typing import Any, AsyncIterable, List

import httpx
import nest_asyncio
from a2a.client import A2ACardResolver
from a2a.types import (
    AgentCard,
    MessageSendParams,
    SendMessageRequest,
    SendMessageResponse,
    SendMessageSuccessResponse,
    Task,
)
from dotenv import load_dotenv
from google.adk import Agent
from google.adk.agents.readonly_context import ReadonlyContext
from google.adk.artifacts import InMemoryArtifactService
from google.adk.memory.in_memory_memory_service import InMemoryMemoryService
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools.tool_context import ToolContext
from google.genai import types

from remote_agent_connection import RemoteAgentConnections


load_dotenv()
nest_asyncio.apply()


class HostAgent:
    """The Host agent."""

    def __init__(
        self,
    ):
        self.remote_agent_connections: dict[str, RemoteAgentConnections] = {}
        self.cards: dict[str, AgentCard] = {}
        self.agents: str = ""
        self._agent = self.create_agent()
        self._user_id = "travel_planner_host"
        self._runner = Runner(
            app_name=self._agent.name,
            agent=self._agent,
            artifact_service=InMemoryArtifactService(),
            session_service=InMemorySessionService(),
            memory_service=InMemoryMemoryService(),
        )

    async def _async_init_components(self, remote_agent_addresses: List[str]):
        async with httpx.AsyncClient(timeout=30) as client:
            for address in remote_agent_addresses:
                card_resolver = A2ACardResolver(client, address)
                try:
                    card = await card_resolver.get_agent_card()
                    remote_connection = RemoteAgentConnections(
                        agent_card=card, agent_url=address
                    )
                    self.remote_agent_connections[card.name] = remote_connection
                    self.cards[card.name] = card
                except httpx.ConnectError as e:
                    print(f"ERROR: Failed to get agent card from {address}: {e}")
                except Exception as e:
                    print(f"ERROR: Failed to initialize connection for {address}: {e}")

        agent_info = [
            json.dumps({"name": card.name, "description": card.description})
            for card in self.cards.values()
        ]
        self.agents = "\n".join(agent_info) if agent_info else "No remote agents found"

    @classmethod
    async def create(
        cls,
        remote_agent_addresses: List[str],
    ):
        instance = cls()
        await instance._async_init_components(remote_agent_addresses)
        return instance

    def create_agent(self) -> Agent:
        return Agent(
            model="gemini-1.5-flash",
            name="Travel_Planner_Host",
            instruction=self.root_instruction,
            description="This Host agent orchestrates travel planning with specialized agents.",
            tools=[
                self.send_message,
            ],
        )

    @property
    def root_instruction(self) -> str:
        return f"""
        **Role:** You are a Travel Planner Host Agent, an expert in creating detailed travel itineraries. Your primary function is to coordinate with specialized remote agents to gather all necessary information and construct a comprehensive travel plan.

        **Core Directives:**

        *   **Initial Query Phase:**
            *   First, systematically ask the user all required questions to build a comprehensive request. Do not proceed until you have the essential details.
            *   Essential details include: Destination(s), Travel Dates (departure and return), Number of Travelers (adults, children), Overall Budget, Traveler Preferences (e.g., flight class, hotel star rating), and Origin City.
            *   Ask about specific interests (e.g., history, adventure, relaxation, food) to tailor the itinerary.

        *   **Orchestration and Task Formatting:**
            *   Once you have the essential details, intelligently sequence calls to the remote agents using the `send_message` tool.
            *   The `agent_name` parameter for `send_message` must be one of the "name" values from the <Available Agents> section.
            *   **You must format the `task` parameter for each agent as specified below:**
                *   `Flight_Agent`: "Find flights from [origin] to [destination]" (e.g., "Find flights from New York to Paris")
                *   `Hotel_Agent`: "Find hotels in [location]" (e.g., "Find hotels in Paris")
                *   `Cab_Agent`: "Find cabs in [location]" (e.g., "Find cabs in Paris")
                *   `Activity_Agent`: "Find activities in [location]" (e.g., "Find activities in Paris")
                *   `Weather_Agent`: "Get weather in [location]" (e.g., "Get weather in Paris")
                *   `Budget_Agent`: "Check budget for [total_cost]" (e.g., "Check budget for 1500.00")
                *   `Document_Agent`: "Check documents for [destination]" (e.g., "Check documents for France")
                *   `Food_Agent`: "Find [cuisine] restaurant in [location]" (e.g., "Find Italian restaurant in Paris")
                *   `Currency_Agent`: "Get exchange rate between [currency1] and [currency2]" (e.g., "Get exchange rate between USD and EUR")

        *   **Aggregation and Output:**
            *   Aggregate all responses from the remote agents.
            *   The final output must be a single JSON object representing the complete itinerary. Do not provide any other text or explanation outside of the JSON.
            *   The JSON structure must be as follows:
                ```json
                {{
                  "itinerary": {{
                    "destination": "string",
                    "travel_dates": {{
                      "start_date": "YYYY-MM-DD",
                      "end_date": "YYYY-MM-DD"
                    }},
                    "travelers": {{
                      "adults": "integer",
                      "children": "integer"
                    }},
                    "origin": "string"
                  }},
                  "weather": {{
                    // JSON response from Weather_Agent
                  }},
                  "documents": {{
                    // JSON response from Document_Agent
                  }},
                  "flights": {{
                    // JSON response from Flight_Agent
                  }},
                  "accommodations": {{
                    // JSON response from Hotel_Agent
                  }},
                  "activities": {{
                    // JSON response from Activity_Agent
                  }},
                  "dining": {{
                    // JSON response from Food_Agent
                  }},
                  "local_transport": {{
                    // JSON response from Cab_Agent
                  }},
                  "currency_info": {{
                    // JSON response from Currency_Agent
                  }},
                  "budget_summary": {{
                    // JSON response from Budget_Agent
                  }}
                }}
                ```

        **Today's Date (YYYY-MM-DD):** {datetime.now().strftime("%Y-%m-%d")}

        <Available Agents>
        {self.agents}
        </Available Agents>
        """

    async def stream(
        self, query: str, session_id: str
    ) -> AsyncIterable[dict[str, Any]]:
        """
        Streams the agent's response to a given query.
        """
        session = await self._runner.session_service.get_session(
            app_name=self._agent.name,
            user_id=self._user_id,
            session_id=session_id,
        )
        content = types.Content(role="user", parts=[types.Part.from_text(text=query)])
        if session is None:
            session = await self._runner.session_service.create_session(
                app_name=self._agent.name,
                user_id=self._user_id,
                state={{}},
                session_id=session_id,
            )
        async for event in self._runner.run_async(
            user_id=self._user_id, session_id=session.id, new_message=content
        ):
            if event.is_final_response():
                response = ""
                if (
                    event.content
                    and event.content.parts
                    and event.content.parts[0].text
                ):
                    response = "\n".join(
                        [p.text for p in event.content.parts if p.text]
                    )
                yield {
                    "is_task_complete": True,
                    "content": response,
                }
            else:
                yield {
                    "is_task_complete": False,
                    "updates": "The host agent is thinking...",
                }

    async def send_message(self, agent_name: str, task: str, tool_context: ToolContext):
        """Sends a task to a remote specialized agent."""
        if agent_name not in self.remote_agent_connections:
            raise ValueError(f"Agent {agent_name} not found")
        client = self.remote_agent_connections[agent_name]

        if not client:
            raise ValueError(f"Client not available for {agent_name}")

        # Simplified task and context ID management
        state = tool_context.state
        task_id = state.get("task_id", str(uuid.uuid4()))
        context_id = state.get("context_id", str(uuid.uuid4()))
        message_id = str(uuid.uuid4())

        payload = {
            "message": {
                "role": "user",
                "parts": [{"type": "text", "text": task}],
                "messageId": message_id,
                "taskId": task_id,
                "contextId": context_id,
            },
        }

        message_request = SendMessageRequest(
            id=message_id, params=MessageSendParams.model_validate(payload)
        )
        send_response: SendMessageResponse = await client.send_message(message_request)
        print("send_response", send_response)

        if not isinstance(send_response.root, SendMessageSuccessResponse) or not isinstance(
            send_response.root.result, Task
        ):
            error_message = (
                "Received a non-success or non-task response from remote agent."
            )
            print(error_message)
            return [{"text": f"Error: {error_message}"}]

        response_content = send_response.root.model_dump_json(exclude_none=True)
        json_content = json.loads(response_content)

        resp = []
        if json_content.get("result", {}).get("artifacts"):
            for artifact in json_content["result"]["artifacts"]:
                if artifact.get("parts"):
                    resp.extend(artifact["parts"])
        return resp

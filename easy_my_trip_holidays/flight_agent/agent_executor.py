from a2a.server.agent_execution import AgentExecutor
from a2a.server.agent_execution.context import RequestContext
from a2a.server.events.event_queue import EventQueue
from a2a.utils import new_agent_text_message
from pydantic import BaseModel
import json
import re

class FlightAgent(BaseModel):
    """Flight agent that returns flight information"""

    async def invoke(self, task: str) -> str:
        # Simple parsing to extract details from the task string
        origin_match = re.search(r"from ([\w\s]+) to", task)
        destination_match = re.search(r"to ([\w\s]+)", task)

        origin = origin_match.group(1).strip() if origin_match else "Unknown"
        destination = destination_match.group(1).strip() if destination_match else "Unknown"

        # Placeholder response that uses parsed data
        response = {
            "flights": [
                {
                    "airline": "DummyAir",
                    "flight_number": "DA123",
                    "departure_airport": origin.upper()[:3],
                    "arrival_airport": destination.upper()[:3],
                    "departure_time": "2025-10-01T10:00:00Z",
                    "arrival_time": "2025-10-01T12:00:00Z",
                    "price": 250.00,
                    "currency": "USD"
                }
            ]
        }
        return json.dumps(response)


class FlightAgentExecutor(AgentExecutor):

    def __init__(self):
        self.agent = FlightAgent()

    async def execute(self, context: RequestContext, event_queue: EventQueue):
        task_string = ""
        if context.body and context.body.message and context.body.message.parts:
            task_string = context.body.message.parts[0].text or ""

        result = await self.agent.invoke(task=task_string)
        event_queue.enqueue_event(new_agent_text_message(result))

    async def cancel(self, context: RequestContext, event_queue: EventQueue):
        raise Exception("Cancel not supported")

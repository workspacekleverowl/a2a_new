from a2a.server.agent_execution import AgentExecutor
from a2a.server.agent_execution.context import RequestContext
from a2a.server.events.event_queue import EventQueue
from a2a.utils import new_agent_text_message
from pydantic import BaseModel
import json
import re

class CabAgent(BaseModel):
    """Cab agent that returns cab information"""

    async def invoke(self, task: str) -> str:
        # Simple parsing
        location_match = re.search(r"in ([\w\s]+)", task)
        location = location_match.group(1).strip() if location_match else "Unknown"

        # Placeholder response
        response = {
            "cabs": [
                {
                    "company": f"DummyCab in {location}",
                    "type": "Sedan",
                    "price_per_km": 1.5,
                    "currency": "USD"
                }
            ]
        }
        return json.dumps(response)


class CabAgentExecutor(AgentExecutor):

    def __init__(self):
        self.agent = CabAgent()

    async def execute(self, context: RequestContext, event_queue: EventQueue):
        task_string = ""
        if context.body and context.body.message and context.body.message.parts:
            task_string = context.body.message.parts[0].text or ""

        result = await self.agent.invoke(task=task_string)
        event_queue.enqueue_event(new_agent_text_message(result))

    async def cancel(self, context: RequestContext, event_queue: EventQueue):
        raise Exception("Cancel not supported")

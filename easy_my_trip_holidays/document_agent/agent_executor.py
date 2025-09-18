from a2a.server.agent_execution import AgentExecutor
from a2a.server.agent_execution.context import RequestContext
from a2a.server.events.event_queue import EventQueue
from a2a.utils import new_agent_text_message
from pydantic import BaseModel
import json
import re

class DocumentAgent(BaseModel):
    """Document agent that returns document information"""

    async def invoke(self, task: str) -> str:
        # Simple parsing
        destination_match = re.search(r"for ([\w\s]+)", task)
        destination = destination_match.group(1).strip() if destination_match else "Unknown"

        # Placeholder response
        visa_required = False
        if destination.lower() == "schengen": # Dummy logic
            visa_required = True

        response = {
            "documents": [
                {
                    "type": "Passport",
                    "required": True
                },
                {
                    "type": "Visa",
                    "required": visa_required,
                    "notes": f"Visa requirements for {destination} should be checked with the embassy."
                }
            ]
        }
        return json.dumps(response)


class DocumentAgentExecutor(AgentExecutor):

    def __init__(self):
        self.agent = DocumentAgent()

    async def execute(self, context: RequestContext, event_queue: EventQueue):
        task_string = ""
        if context.body and context.body.message and context.body.message.parts:
            task_string = context.body.message.parts[0].text or ""

        result = await self.agent.invoke(task=task_string)
        event_queue.enqueue_event(new_agent_text_message(result))

    async def cancel(self, context: RequestContext, event_queue: EventQueue):
        raise Exception("Cancel not supported")

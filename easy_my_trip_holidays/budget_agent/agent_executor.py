from a2a.server.agent_execution import AgentExecutor
from a2a.server.agent_execution.context import RequestContext
from a2a.server.events.event_queue import EventQueue
from a2a.utils import new_agent_text_message
from pydantic import BaseModel
import json
import re

class BudgetAgent(BaseModel):
    """Budget agent that returns budget information"""

    async def invoke(self, task: str) -> str:
        # Simple parsing to get a cost
        cost_match = re.search(r"(\d+\.?\d*)", task)
        cost = float(cost_match.group(1)) if cost_match else 0

        # Placeholder response
        budget = 1000.00
        status = "within_limits" if cost <= budget else "over_budget"

        response = {
            "budget_status": status,
            "total_spent": cost,
            "budget": budget,
            "currency": "USD"
        }
        return json.dumps(response)


class BudgetAgentExecutor(AgentExecutor):

    def __init__(self):
        self.agent = BudgetAgent()

    async def execute(self, context: RequestContext, event_queue: EventQueue):
        task_string = ""
        if context.body and context.body.message and context.body.message.parts:
            task_string = context.body.message.parts[0].text or ""

        result = await self.agent.invoke(task=task_string)
        event_queue.enqueue_event(new_agent_text_message(result))

    async def cancel(self, context: RequestContext, event_queue: EventQueue):
        raise Exception("Cancel not supported")

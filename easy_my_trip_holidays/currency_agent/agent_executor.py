from a2a.server.agent_execution import AgentExecutor
from a2a.server.agent_execution.context import RequestContext
from a2a.server.events.event_queue import EventQueue
from a2a.utils import new_agent_text_message
from pydantic import BaseModel
import json
import re

class CurrencyAgent(BaseModel):
    """Currency agent that returns currency exchange information"""

    async def invoke(self, task: str) -> str:
        # Simple parsing
        currencies_match = re.search(r"between (\w+) and (\w+)", task)
        from_currency = currencies_match.group(1).strip().upper() if currencies_match else "USD"
        to_currency = currencies_match.group(2).strip().upper() if currencies_match else "EUR"

        # Dummy rates
        rates = {
            "USD_EUR": 0.92,
            "EUR_USD": 1.09,
            "USD_GBP": 0.79,
            "GBP_USD": 1.27,
        }
        rate = rates.get(f"{from_currency}_{to_currency}", "Not available")

        # Placeholder response
        response = {
            "from_currency": from_currency,
            "to_currency": to_currency,
            "rate": rate
        }
        return json.dumps(response)


class CurrencyAgentExecutor(AgentExecutor):

    def __init__(self):
        self.agent = CurrencyAgent()

    async def execute(self, context: RequestContext, event_queue: EventQueue):
        task_string = ""
        if context.body and context.body.message and context.body.message.parts:
            task_string = context.body.message.parts[0].text or ""

        result = await self.agent.invoke(task=task_string)
        event_queue.enqueue_event(new_agent_text_message(result))

    async def cancel(self, context: RequestContext, event_queue: EventQueue):
        raise Exception("Cancel not supported")

import asyncio
from fastapi import FastAPI, WebSocket
from agent import HostAgent
import uvicorn

app = FastAPI()

host_agent: HostAgent

@app.on_event("startup")
async def startup_event():
    global host_agent
    remote_agent_urls = [
        "http://localhost:10001",  # Flight Agent
        "http://localhost:10002",  # Hotel Agent
        "http://localhost:10003",  # Cab Agent
        "http://localhost:10004",  # Activity Agent
        "http://localhost:10005",  # Weather Agent
        "http://localhost:10006",  # Budget Agent
        "http://localhost:10007",  # Document Agent
        "http://localhost:10008",  # Food Agent
        "http://localhost:10009",  # Currency Agent
    ]
    host_agent = await HostAgent.create(remote_agent_addresses=remote_agent_urls)
    print("HostAgent initialized")

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        async for response in host_agent.stream(data, session_id):
            await websocket.send_json(response)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

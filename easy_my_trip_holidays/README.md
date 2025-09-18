# Easy My Trip Holidays - Multi-Agent Travel Assistant

This project is a multi-agent travel assistance system designed to help users plan their trips. It consists of a central "Travel Planner Host" agent that orchestrates nine specialized remote agents to build a comprehensive itinerary.

This system is built using the [Agent-to-Agent (A2A) Communication SDK](https://github.com/google/a2a-python).

## Prerequisites

Before you begin, ensure you have the following installed:

*   **Python 3.10+**
*   **uv:** A fast Python package installer and resolver. Follow the official [installation guide](https://docs.astral.sh/uv/getting-started/installation/).

## 1. Setup

### a) Configure Google API Key

The host agent uses a Google Generative AI model (Gemini). You need to provide your Google API key.

1.  Create a file named `.env` inside the `easy_my_trip_holidays/travel_planner_host/` directory.
2.  Add your API key to the file like this:

    ```
    GOOGLE_API_KEY="your_google_api_key_here"
    ```

### b) Install Dependencies

Each agent has its own set of dependencies listed in its `requirements.txt` file. You can install them all at once by running the following script from the root of the `easy_my_trip_holidays` directory.

```bash
#!/bin/bash

# This script installs dependencies for all agents

# List of all agent directories
AGENT_DIRS=(
    "travel_planner_host"
    "flight_agent"
    "hotel_agent"
    "cab_agent"
    "activity_agent"
    "weather_agent"
    "budget_agent"
    "document_agent"
    "food_agent"
    "currency_agent"
)

# Loop through each directory and install dependencies
for DIR in "${AGENT_DIRS[@]}"; do
    echo "--- Setting up environment for $DIR ---"
    cd "$DIR"
    uv venv
    uv pip install -r requirements.txt
    cd ..
    echo "--- Done with $DIR ---"
    echo ""
done

echo "All dependencies installed successfully!"
```
Save this script as `setup.sh` in the `easy_my_trip_holidays` directory, give it execute permissions (`chmod +x setup.sh`), and then run it (`./setup.sh`).

## 2. Running the System

To run the system, you must start each of the 10 agents in a separate terminal window.

Navigate to the `easy_my_trip_holidays/` directory for all commands.

**Terminal 1: Start the Flight Agent**
```bash
cd flight_agent && source .venv/bin/activate && uvicorn __main__:main --port 10001
```

**Terminal 2: Start the Hotel Agent**
```bash
cd hotel_agent && source .venv/bin/activate && uvicorn __main__:main --port 10002
```

**Terminal 3: Start the Cab Agent**
```bash
cd cab_agent && source .venv/bin/activate && uvicorn __main__:main --port 10003
```

**Terminal 4: Start the Activity Agent**
```bash
cd activity_agent && source .venv/bin/activate && uvicorn __main__:main --port 10004
```

**Terminal 5: Start the Weather Agent**
```bash
cd weather_agent && source .venv/bin/activate && uvicorn __main__:main --port 10005
```

**Terminal 6: Start the Budget Agent**
```bash
cd budget_agent && source .venv/bin/activate && uvicorn __main__:main --port 10006
```

**Terminal 7: Start the Document Agent**
```bash
cd document_agent && source .venv/bin/activate && uvicorn __main__:main --port 10007
```

**Terminal 8: Start the Food Agent**
```bash
cd food_agent && source .venv/bin/activate && uvicorn __main__:main --port 10008
```

**Terminal 9: Start the Currency Agent**
```bash
cd currency_agent && source .venv/bin/activate && uvicorn __main__:main --port 10009
```

**Terminal 10: Start the Travel Planner Host Agent**
```bash
cd travel_planner_host && source .venv/bin/activate && uvicorn main:app --port 8000
```

Once all agents are running, you will see output in each terminal indicating that the servers have started.

## 3. Testing the System

### 3.1. End-to-End Testing

You can test the entire system by sending a request to the host agent's WebSocket endpoint.

Create a Python file named `test_client.py` in the `easy_my_trip_holidays/` directory with the following content:

```python
import asyncio
import websockets
import json

async def run_test():
    uri = "ws://localhost:8000/ws/test-session-123"
    async with websockets.connect(uri) as websocket:
        # Define the travel plan request
        prompt = "I want to plan a 7-day trip to Paris from New York for 2 adults on a budget of $3000. We are interested in historical sites and good food. The trip should be next month."

        print(f">>> Sending prompt to host agent:\n{prompt}\n")
        await websocket.send(prompt)

        print("<<< Receiving response from host agent:\n")
        while True:
            try:
                response_str = await websocket.recv()
                response = json.loads(response_str)

                if response.get("updates"):
                    print(f"Agent is thinking... {response['updates']}")

                if response.get("is_task_complete"):
                    print("\n--- Final Itinerary ---")
                    final_content = response.get("content", "")
                    # The final content is a JSON string, so we parse it for pretty printing
                    try:
                        final_json = json.loads(final_content)
                        print(json.dumps(final_json, indent=2))
                    except json.JSONDecodeError:
                        print(final_content) # Print as is if not valid JSON
                    print("\n--- End of Itinerary ---")
                    break

            except websockets.exceptions.ConnectionClosed:
                print("Connection closed.")
                break

if __name__ == "__main__":
    # You might need to install the websockets library first:
    # pip install websockets
    asyncio.run(run_test())
```

Open an 11th terminal, navigate to the `easy_my_trip_holidays/` directory, install the `websockets` library (`pip install websockets`), and run the client:

```bash
python test_client.py
```

You will see the host agent process your request, communicate with the other agents (you'll see activity in their respective terminals), and finally print the complete JSON itinerary.

### 3.2. Testing Individual Remote Agents (Optional)

You can also test each remote agent individually to ensure it's running correctly. This is useful for debugging. You can send a direct request to any of the remote agents using a tool like `curl`.

Here is an example of how to test the `flight_agent` (which runs on port 10001).

Open a new terminal and run the following `curl` command:

```bash
curl -X POST http://localhost:10001/ \
-H "Content-Type: application/json" \
-d '{
    "id": "12345",
    "jsonrpc": "2.0",
    "method": "a2a-send-message",
    "params": {
        "message": {
            "messageId": "msg-1",
            "taskId": "task-1",
            "contextId": "ctx-1",
            "role": "user",
            "parts": [
                {
                    "type": "text",
                    "text": "Find flights from SFO to LAX"
                }
            ]
        }
    }
}'
```

**Expected Response:**

You should receive a JSON response from the `flight_agent` that includes a task object. Inside the task's artifacts, you will find the JSON payload from the agent. It will look something like this:

```json
{
  "jsonrpc": "2.0",
  "id": "12345",
  "result": {
    "id": "task-1",
    "status": "done",
    "artifacts": [
      {
        "id": "artifact-1",
        "parts": [
          {
            "type": "text",
            "text": "{\"flights\": [{\"airline\": \"DummyAir\", \"flight_number\": \"DA123\", \"departure_airport\": \"SFO\", \"arrival_airport\": \"LAX\", \"departure_time\": \"2025-10-01T10:00:00Z\", \"arrival_time\": \"2025-10-01T12:00:00Z\", \"price\": 250.0, \"currency\": \"USD\"}]}"
          }
        ]
      }
    ]
  }
}
```
You can adapt this `curl` command to test any of the other remote agents by changing the port number (10002 for hotel, 10003 for cab, etc.) and modifying the `"text"` field in the request body to match the task format for that agent.

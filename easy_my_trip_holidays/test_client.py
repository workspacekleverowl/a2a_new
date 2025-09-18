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
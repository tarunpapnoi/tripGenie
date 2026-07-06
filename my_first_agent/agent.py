# from google.adk.agents.llm_agent import Agent
# root_agent = Agent(
#     model='gemini-2.5-flash',
#     name='math_tutor_agent',
#     description='Helps students learn algebra by guiding them through problemsolving steps.',
#     instruction='You are a patient math tutor. Help students with algebra problems.'
# )

"""
Complete example: Running an ADK agent programmatically
Copy this entire code block to run it in a Python script or notebook.
"""
# Step 1: Install ADK (run this in terminal or notebook cell)
# pip install google-adk
# Step 2: Set your API key
# Option A: Set as environment variable before running
#   export GOOGLE_API_KEY=your-api-key-here
# Option B: Uncomment and use this code:
import os
os.environ["GOOGLE_API_KEY"] = "AIzaSyAEDo6y1-3B8f8QGjFO1u8CIzgjf_rgql8"
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "FALSE"
# Step 3: Import required libraries
import asyncio

from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part

root_agent = Agent(
    name="math_tutor_agent",
    model="gemini-2.5-flash",
    description="Helps students learn algebra by guiding them through problem solving steps.",
    instruction="You are a patient math tutor. Help students with algebra problems."
)

APP_NAME = "math_tutor_app"
USER_ID = "student_1"
SESSION_ID = "session_001"

session_service = InMemorySessionService()

runner = Runner(
    app_name=APP_NAME,
    agent=agent,
    session_service=session_service,
)

async def run_agent():
    await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID,
    )

    user_message = Content(
        role="user",
        parts=[Part(text="How do I solve 2x + 5 = 13?")]
    )

    async for event in runner.run_async(
            user_id=USER_ID,
            session_id=SESSION_ID,
            new_message=user_message,
    ):
        if event.is_final_response():
            print(event.content.parts[0].text)

asyncio.run(run_agent())
import os
from agno.agent import Agent
from agno.media import Image
from agno.models.google import Gemini
from dotenv import load_dotenv

BASEDIR = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(BASEDIR,".env"))

agent = Agent(
    model=Gemini(
        id=os.environ["DEFAULT_MODEL"],
    )
)

# agent.print_response("hello how are you", stream=True)

# agent.print_response(
#     "Describe this image, then separately summarize the current top Hacker News stories.",
#     images=[
#         Image(
#             url="https://imgs.search.brave.com/PdmW61WeG09giVgttxcVEQoXZbMolz8n9qFN-axnQfE/rs:fit:860:0:0:0/g:ce/aHR0cHM6Ly9jb250/YS5jb20vd3AtY29u/dGVudC91cGxvYWRz/L3NpdGVzLzM5LzIw/MjUvMDkvMDctSW52/b2ljZS0yLnBuZw"
#         )
#     ],
#     stream=True,
# )

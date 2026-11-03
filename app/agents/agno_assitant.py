from agno import Agent
from agno.models.google import Gemini
from app.core.config import DEFAULT_MODEL



def get_agent(
    model_id: str = DEFAULT_MODEL,
    user_id: str = None,
    session_id: str = None,
    debug_mode = True,
) -> Agent:
    return Agent(
        model=Gemini(
            id=model_id,
        ),
        instructions=[

        ],
        tools=[]
    )


# agent.print_response("hello how are you my name", stream=True)

# agent.print_response(
#     "Describe this image, then separately summarize the current top Hacker News stories.",
#     images=[
#         Image(
#             filepath=os.path.join(BASEDIR,".tmp/invoice-001.png")
#             url="https://imgs.search.brave.com/PdmW61WeG09giVgttxcVEQoXZbMolz8n9qFN-axnQfE/rs:fit:860:0:0:0/g:ce/aHR0cHM6Ly9jb250/YS5jb20vd3AtY29u/dGVudC91cGxvYWRz/L3NpdGVzLzM5LzIw/MjUvMDkvMDctSW52/b2ljZS0yLnBuZw"
#         )
#     ],
#     stream=True,
# )
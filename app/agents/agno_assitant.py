from agno.agent import Agent
from agno.models.google import Gemini
from app.core.config import DEFAULT_MODEL
from agno.tools.reasoning import ReasoningTools
from app.agents.storage import agent_db
from app.agents.custom_tools import InvoiceTools
from uuid import UUID
from sqlalchemy.orm import Session
from fastapi import Depends
from app.dependencies import get_db

def get_agent(
    db: Session = Depends(get_db),
    model_id: str = DEFAULT_MODEL,
    user_id: str = None,
    session_id: str = None,
    debug_mode = True,
) -> Agent:
    return Agent(
        name="Invoice Assist",
        id="invoice_assist",
        user_id=user_id,
        session_id=session_id,
        model=Gemini(
            id=model_id,
        ),
        tools=[
            ReasoningTools(add_instructions=True),
            InvoiceTools(
                db=db,
                user_id=UUID(user_id),
                session_id=UUID(session_id),
            ),
        ],
        description = (
            "You are Smart Invoice Assist, an AI agent that extracts data from invoice files (images and PDFs), saves it in a structured database, and helps the user organize, search, and report on their invoices."
        ),
        instructions = [
            # Role
            "Your current task is to extract data from uploaded invoice files (image or PDF) and save it to the database.",

            # Extraction
            "Read the invoice carefully and extract these fields: invoice_number, invoice_date, due_date, vendor_name, vendor_address, customer_name, currency, subtotal, tax_amount, total_amount, payment_method, and line_items.",
            "For each line item extract: description, quantity, unit_price, total.",
            "Dates must be in ISO format (YYYY-MM-DD). Amounts must be plain numbers with no currency symbols or thousands separators. Currency must be an ISO code (MAD, EUR, USD...).",
            "If a field is missing or unreadable, set it to null. Never guess or invent values.",
            "Check that the line items sum to the subtotal and that subtotal + tax = total. If they don't match, tell the user before saving.",

            # Saving
            "Before saving, show the user a short summary of the extracted data and ask for confirmation.",
            "Save only after the user confirms, using the save_invoice tool.",
            "Check for duplicates (same invoice_number + vendor_name) before saving. If one exists, warn the user and do not save again.",
            "If the file is not an invoice, say so and do not save anything.",
            "If a file contains multiple invoices, process them one at a time.",

            # Behavior
            "Keep replies short and clear. Reply in the language the user writes in.",
            "Do not make up data and do not save unconfirmed data.",
        ],
        markdown=True,
        add_datetime_to_context=True,
        debug_mode=debug_mode,

        # for reasononing tool
        read_chat_history=True,

        db=agent_db,
        add_history_to_context=True,
        num_history_runs=3,
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
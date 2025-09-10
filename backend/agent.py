from agents import Agent, function_tool
from datetime import datetime

META = {
    "company": {
        "name": "Acme Inc.",
        "address": "123 Main St.",
        "phone": "555-1234",
        "email": "info@acme.com"
    },
    "banks": {
        "account1-wise-usd": {
            "name": "Wise",
            "currency": "USD",
            "IBAN": "US1234567890"
        }
    }
}

@function_tool
def get_current_time():
    """Get the current date and time."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

@function_tool
def search_for_document(search_term: str):
    """Search for documents based on a search term. Used for e.g. finding receipts"""
    return {
        "receipt-1": {
            "date": "2023-01-01",
            "amount": 300.00,
            "description": "Jack hardware shop"
        }
    }

@function_tool
def list_bank_transactions(bank_id: str, year: int):
    """
    List bank transactions for a given year and bank ID.
    """
    return {
        "tx1": {
            "date": "2023-01-01",
            "amount": 100.00,
            "description": "Payment for service"
        },
        "tx2": {
            "date": "2023-02-01",
            "amount": 200.00,
            "description": "Payment for service"
        },
        "tx3": {
            "date": "2023-03-01",
            "amount": -300.00,
            "description": "Bought working shoes"
        }
    }

@function_tool
def list_unreconciled_transactions(bank_id: str, year: int):
    """
    List unreconciled transactions for a given year and bank ID.
    """
    return {
        "tx4": {
            "date": "2023-04-01",
            "amount": 400.00,
            "description": "Payment for service"
        },
        "tx5": {
            "date": "2023-05-01",
            "amount": -300.00,
            "description": "Bought work shoes"
        }
    }

@function_tool
def search_for_invoice(search_term: str):
    """Search for invoices based on a search term."""
    # TODO: Implement this function
    return f"Invoices for '{search_term}':\n- Invoice 1\n- Invoice 2"

@function_tool
def list_unpaid_invoices():
    """List outstanding invoices."""
    return {
        "invoice-1": {
            "amount": 100.00,
            "customer": "John Doe",
            "due_date": "2023-01-15",
            "status": "overdue"
        },
        "invoice-3": {
            "amount": 200.00,
            "customer": "Joes Heating",
            "due_date": "2026-02-15",
            "status": "pending"
        }
    }

@function_tool
def list_paid_invoices():
    """List paid invoices."""
    return {
        "invoice-2": {
            "amount": 200.00,
            "customer": "Joes Heating",
            "due_date": "2023-02-15",
            "status": "paid"
        }
    }

agent = Agent(
    name="Assistant",
    instructions=f"""You are a helpful assistant which helps explore accounting details.
You do not need to ask permission to perform actions.

IMPORTANT: Always format your responses using Markdown syntax when appropriate. This includes:
- Use **bold** for emphasis
- Use *italics* for subtle emphasis
- Use `code` for inline code snippets
- Use ```code blocks``` for multi-line code
- Use # ## ### for headings when structuring information
- Use - or * for bullet points when listing items
- Use > for blockquotes when citing or highlighting important information
- Use [links](url) for external references
- Use tables with | Column 1 | Column 2 | format for tabular data
- Use ~~strikethrough~~ for crossed-out text
- Use - [ ] and - [x] for task lists

The frontend supports GitHub Flavored Markdown (GFM) and will render your Markdown properly, so feel free to use rich formatting including tables to make your responses more readable and well-structured.

Data about the entity:
{META}
""",
    tools=[
        get_current_time,
        search_for_document,
        search_for_invoice,
        list_bank_transactions,
        list_unreconciled_transactions,
        list_unpaid_invoices,
        list_paid_invoices,
    ],
)

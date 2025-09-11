from agents import Agent, function_tool, FunctionTool
from datetime import datetime
from dataclasses import dataclass

import datetime
import uuid

from typing import Any, List, Tuple

class ActionType:
    NEW_CLIENT = "client"
    NEW_SUPPLIER = "supplier"
    NEW_INVOICE = "invoice"
    RECONCILE = "reconcile"

@dataclass
class Action:
    pass

@dataclass
class ActionUpdateClient(Action):
    id: uuid.UUID
    name: str
    address: str
    vat_number: str
    email: str
    phone: str
    country_code: str

@dataclass
class ActionUpdateSupplier(Action):
    id: uuid.UUID
    name: str
    address: str
    vat_number: str
    email: str
    phone: str
    country_code: str

@dataclass
class ActionNewInvoice(Action):
    id: uuid.UUID
    client_id: str

@dataclass
class ActionReconcile(Action):
    id: uuid.UUID
    bank_txs: List[uuid.UUID]
    receipts: List[uuid.UUID]

@dataclass
class BankTransaction:
    id: uuid.UUID
    amount: float
    currency: str
    date: datetime.date
    description: str

@dataclass
class Bank:
    id: uuid.UUID
    name: str
    currency: str
    IBAN: str
    txs: List[BankTransaction] # todo: this touches a database

class State:
    def __init__(self):
        self.act_cnt = 1
        self.actions: List[Tuple[str, Action]] = []
        self.banks: List[Bank] = [
            Bank(
                id=uuid.uuid4(),
                name="Wise USD",
                currency="USD",
                IBAN="US1234567890",
                txs=[
                    BankTransaction(
                        id=uuid.uuid4(),
                        amount=100.0,
                        currency="USD",
                        date=datetime.date(2023, 1, 1),
                        description="Initial deposit"
                    ),
                    BankTransaction(
                        id=uuid.uuid4(),
                        amount=50.0,
                        currency="USD",
                        date=datetime.date(2023, 2, 1),
                        description="Monthly salary"
                    )
                ]
            ),
            Bank(
                id=uuid.uuid4(),
                name="Wise EUR",
                currency="EUR",
                IBAN="DE1234567890",
                txs=[]
            )
        ]

    def context(self):
        return {
            "company": {
                "name": "Acme Inc.",
                "address": "123 Main St.",
                "phone": "555-1234",
                "email": "info@acme.com"
            },
            "banks": {
                "account1-wise-usd": {
                    "name": "Wise USD",
                    "currency": "USD",
                    "IBAN": "US1234567890"
                },
                "account2-wise-eur": {
                    "name": "Wise EUR",
                    "currency": "EUR",
                    "IBAN": "DE1234567890"
                }
            }
        }

    def add_action(
        self,
        type: str,
        action: Action,
    ):
        id = self.act_cnt
        self.act_cnt += 1
        act_id = f"{type}-{id}"
        self.actions.append((act_id, action))
        return act_id

    def tool_action_clear(self):
        """Undo all actions"""
        self.actions = []

    def tool_action_undo(self, id: str):
        """Undoes the action with the given id"""
        for (act_id, _) in self.actions:
            if act_id == id:
                break
        else:
            return {"error": f"Action with id {id} not found"}
        self.actions = [change for change in self.actions if change[0] != id]

    def tool_query_client(
        self,
        name_query: str,
    ):
        """Query clients by name"""
        pass

    def tool_action_new_client(
        self,
        name: str,
        email: str,
        phone: str,
        address: str,
        country_code: str,
        vat_number: str,
    ):
        """Register a new client for the busniess"""
        id = uuid.uuid4()
        return self.add_action(
            ActionType.NEW_CLIENT,
            ActionUpdateClient(
                id=id,
                name=name,
                email=email,
                address=address,
                phone=phone,
                country_code=country_code,
                vat_number=vat_number
            )
        )

    def tool_action_new_supplier(
        self,
        name: str,
        email: str,
        phone: str,
        address: str,
        country_code: str,
        vat_number: str,
    ):
        """Register a new supplier for the busniess"""
        id = uuid.uuid4()
        return self.add_action(
            ActionType.NEW_SUPPLIER,
            ActionUpdateSupplier(
                id=id,
                name=name,
                email=email,
                phone=phone,
                address=address,
                country_code=country_code,
                vat_number=vat_number
            )
        )

    def tool_action_create_invoice(
        self,
        client_id: str
    ):
        """Creates a new invoice for the given client"""
        id = uuid.uuid4()
        return self.add_action(
            ActionType.NEW_INVOICE,
            ActionNewInvoice(
                id=id,
                client_id=client_id
            )
        )

    def tool_action_reconcile_transactions(
        self,
        bank_txs: List[uuid.UUID],
        receipts: List[uuid.UUID],
    ):
        """Reconcile a list of transactions for a given year and bank ID."""
        id = uuid.uuid4()
        return self.add_action(
            ActionType.RECONCILE,
            ActionReconcile(
                id=id,
                bank_txs=bank_txs,
                receipts=receipts
            )
        )

    def tool_query_current_time(self):
        """Get the current date and time."""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def tool_query_search_for_invoice(self, search_term: str):
        """Search for invoices based on a search term."""
        # TODO: Implement this function
        return f"Invoices for '{search_term}':\n- Invoice 1\n- Invoice 2"

    def tool_query_list_unpaid_invoices(self):
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

    def tool_query_list_paid_invoices(self):
        """List paid invoices."""
        return {
            "invoice-2": {
                "amount": 200.00,
                "customer": "Joes Heating",
                "due_date": "2023-02-15",
                "status": "paid"
            }
        }

    def tool_query_for_document(
        self,
        search_term: str,
    ):
        """Search for documents based on a search term. Used for e.g. finding receipts"""
        return {
            "receipt-1": {
                "date": "2023-01-01",
                "amount": 300.00,
                "description": "Jack hardware shop"
            }
        }

    def tool_query_list_bank_transactions(
        self,
        bank_id: str,
    ):
        """
        List bank transactions for a given bank ID.
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

    def tool_query_list_unreconciled_transactions(
        self,
        bank_id: str,
    ):
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


def create_agent():
    """Create a new agent instance with fresh state."""
    state = State()
    
    # Create function tools that access state via closure
    @function_tool
    def tool_query_client(name_query: str):
        """Query clients by name"""
        return state.tool_query_client(name_query)
    
    @function_tool
    def tool_query_current_time():
        """Get the current date and time."""
        return state.tool_query_current_time()
    
    @function_tool
    def tool_query_for_document(search_term: str):
        """Search for documents based on a search term. Used for e.g. finding receipts"""
        return state.tool_query_for_document(search_term)
    
    @function_tool
    def tool_query_list_bank_transactions(bank_id: str):
        """List bank transactions for a given bank ID."""
        return state.tool_query_list_bank_transactions(bank_id)
    
    @function_tool
    def tool_query_list_unreconciled_transactions(bank_id: str):
        """List unreconciled transactions for a given year and bank ID."""
        return state.tool_query_list_unreconciled_transactions(bank_id)
    
    @function_tool
    def tool_query_search_for_invoice(search_term: str):
        """Search for invoices based on a search term."""
        return state.tool_query_search_for_invoice(search_term)
    
    @function_tool
    def tool_query_list_unpaid_invoices():
        """List outstanding invoices."""
        return state.tool_query_list_unpaid_invoices()
    
    @function_tool
    def tool_query_list_paid_invoices():
        """List paid invoices."""
        return state.tool_query_list_paid_invoices()
    
    @function_tool
    def tool_action_clear():
        """Undo all actions"""
        return state.tool_action_clear()
    
    @function_tool
    def tool_action_undo(id: str):
        """Undoes the action with the given id"""
        return state.tool_action_undo(id)
    
    @function_tool
    def tool_action_new_client(name: str, email: str, phone: str, address: str, country_code: str, vat_number: str):
        """Register a new client for the business"""
        return state.tool_action_new_client(name, email, phone, address, country_code, vat_number)
    
    @function_tool
    def tool_action_new_supplier(name: str, email: str, phone: str, address: str, country_code: str, vat_number: str):
        """Register a new supplier for the business"""
        return state.tool_action_new_supplier(name, email, phone, address, country_code, vat_number)
    
    @function_tool
    def tool_action_create_invoice(client_id: str):
        """Creates a new invoice for the given client"""
        return state.tool_action_create_invoice(client_id)
    
    @function_tool
    def tool_action_reconcile_transactions(bank_txs: List[uuid.UUID], receipts: List[uuid.UUID]):
        """Reconcile a list of transactions for a given year and bank ID."""
        return state.tool_action_reconcile_transactions(bank_txs, receipts)
    
    tools = [
        # Query tools
        tool_query_client,
        tool_query_current_time,
        tool_query_for_document,
        tool_query_list_bank_transactions,
        tool_query_list_unreconciled_transactions,
        tool_query_search_for_invoice,
        tool_query_list_unpaid_invoices,
        tool_query_list_paid_invoices,
        # Action tools
        tool_action_clear,
        tool_action_undo,
        tool_action_new_client,
        tool_action_new_supplier,
        tool_action_create_invoice,
        tool_action_reconcile_transactions,
    ]
    
    return Agent(
        name="Assistant",
        instructions=f"""You are a helpful assistant which helps explore and fix accounting details.
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

AVOID THE USE OF EMOJIS.
AVOID THE USE OF ALARMING/SENSTATIONALIST LANGUAGE.
REMAIN PROFESSIONAL.

Data about the entity:
{state.context()}

If the user interacts with you in a different language than english, respond in the same language.
Do not translate transaction descriptions or other details. Return these verbatim.
""",
        tools=tools,
    )

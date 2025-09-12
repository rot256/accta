import re
import uuid
import dataclasses
import datetime

from agents import function_tool
from agents.agent import Agent

from state import Bank, BankTransaction, CompanyData, State, Transient, StoreMemory
from action import Action, NewInvoice, UpdateClient, UpdateSupplier, Reconcile
from typing import List, Tuple

class Transaction:
    def __init__(
        self,
        state: State, # base state
    ):
        self.act_cnt = 1
        self.state = state
        # mapping from an action "name" to the action
        self.actions: List[Tuple[str, Action]] = []
        self.transient = Transient(state)

    def context(self):
        banks = self.transient.list_banks()
        company = self.transient.company()
        return {
            "company": {
                "name": company.name,
                "address": company.address,
                "phone": company.phone,
                "email": company.email
            },
            "banks": {
                bank.id : {
                    "name": bank.name,
                    "currency": bank.currency,
                    "IBAN": bank.iban,
                } for bank in banks
            }
        }

    def add_action(
        self,
        action: Action,
    ):
        # apply the action.
        # observe: this can fail
        action.apply(self.transient)

        # generate a unique id
        # for the action for future reference
        act_id = f"{action.action_type()}-{self.act_cnt}"
        self.act_cnt += 1
        self.actions.append((act_id, action))
        return act_id

    def tool_action_clear(self):
        """Undo all actions"""
        self.actions = []
        self.transient = Transient(self.state)

    def tool_action_undo(self, id: str):
        """Undoes the action with the given id"""
        for (act_id, _) in self.actions:
            if act_id == id:
                break
        else:
            return {"error": f"Action with id {id} not found"}

        # remove the action
        actions = [change for change in self.actions if change[0] != id]

        # reset state and try to replay all actions
        # note, that this could fail:
        # the error should be returned to the agent.
        transient = Transient(self.state)
        for (_, action) in actions:
            action.apply(transient)

        # write back the new state and actions
        self.transient = transient
        self.actions = actions

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
        country: str,
        vat_number: str,
    ):
        """Register a new client for the busniess"""
        return self.add_action(
            UpdateClient(
                client_id=uuid.uuid4(),
                name=name,
                email=email,
                address=address,
                phone=phone,
                country=country,
                vat_number=vat_number
            )
        )

    def tool_action_new_supplier(
        self,
        name: str,
        email: str,
        phone: str,
        address: str,
        country: str,
        vat_number: str,
    ):
        """Register a new supplier for the busniess"""
        return self.add_action(
            UpdateSupplier(
                supplier_id=uuid.uuid4(), # new supplier
                name=name,
                email=email,
                phone=phone,
                address=address,
                country=country,
                vat_number=vat_number
            )
        )

    def tool_action_create_invoice(
        self,
        client_id: uuid.UUID,
        amount: float,
        currency: str,
        due_date: datetime.date,
        description: str,
    ):
        """Create a new invoice for the given client"""
        return self.add_action(
            NewInvoice(
                client_id=client_id,
                amount=amount,
                currency=currency,
                due_date=due_date,
                description=description,
            )
        )

    def tool_action_reconcile_transactions(
        self,
        bank_txs: List[uuid.UUID],
        receipts: List[uuid.UUID],
    ):
        """
        Reconcile transactions with receipts/expenses.
        """
        return self.add_action(
            Reconcile(
                bank_txs=bank_txs,
                docs_ids=receipts,
            )
        )

    def tool_query_current_time(self):
        """Get the current date and time."""
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def tool_query_list_unpaid_invoices(self):
        """
        List all unreconciled invoices:
        invoices which have not been matched to a bank transaction.
        """
        invoices = []
        for invoice in self.transient.list_invoices():
            invoices.append(dataclasses.asdict(invoice))
        return invoices

    def tool_query_list_invoices(self):
        """
        List all invoices.
        """
        invoices = []
        for invoice in self.transient.list_invoices():
            invoices.append(dataclasses.asdict(invoice))
        return invoices

    def tool_query_for_document(
        self,
        search_regex: str,
    ):
        """
        Search for documents based on a search term. Used for e.g. finding receipts
        Supply the empty search_regex to obtain all documents.
        """
        docs = []
        regex = re.compile(search_regex, re.IGNORECASE)
        for doc in self.transient.list_documents():
            if regex.search(doc.desc):
                docs.append(dataclasses.asdict(doc))
        return docs

    def tool_query_list_bank_transactions(
        self,
        bank_id: uuid.UUID,
    ):
        """
        List bank transactions for a given bank ID.
        """
        return [
            dataclasses.asdict(obj)
            for obj in self.transient.list_transactions(bank_id)
        ]

    def tool_query_list_unreconciled_transactions(
        self,
        bank_id: uuid.UUID,
    ):
        """
        List unreconciled transactions for a given year and bank ID.
        """
        return [
            dataclasses.asdict(obj)
            for obj in self.transient.list_unreconciled_transactions(bank_id)
        ]

def create_agent():
    """Create a new agent instance with fresh state."""
    st = StoreMemory()

    st.set_bank(
        Bank(
            id=uuid.uuid4(),
            currency="USD",
            iban="US1234567890",
            name="Bank of America"
        ),
        [
            BankTransaction(
                id=uuid.uuid4(),
                date=datetime.date(2023, 1, 1),
                amount=-100.00,
                description="Bought working shoes"
            ),
            BankTransaction(
                id=uuid.uuid4(),
                date=datetime.date(2023, 2, 1),
                amount=-50.00,
                description="Rent"
            )
        ]
    )

    st.set_bank(
        Bank(
            id=uuid.uuid4(),
            currency="USD",
            iban="US9876543210",
            name="Chase"
        ),
        [
            BankTransaction(
                id=uuid.uuid4(),
                date=datetime.date(2023, 1, 1),
                amount=100.00,
                description="Salary"
            ),
            BankTransaction(
                id=uuid.uuid4(),
                date=datetime.date(2023, 2, 1),
                amount=-50.00,
                description="Rent"
            )
        ]
    )

    st.set_company(
        CompanyData(
            id=uuid.uuid4(),
            name="Acme Inc.",
            address="123 Main St, Anytown USA",
            phone="555-1234",
            email="info@acmeinc.com",
            vat_number="123456789",
            country="USA",
        )
    )

    tx = Transaction(st)

    # Create function tools that access state via closure
    @function_tool
    def tool_query_client(name_query: str):
        """Query clients by name"""
        return tx.tool_query_client(name_query)

    @function_tool
    def tool_query_current_time():
        """Get the current date and time."""
        return tx.tool_query_current_time()

    @function_tool
    def tool_query_for_document(search_regex: str):
        """Search for documents based on a search term. Used for e.g. finding receipts"""
        return tx.tool_query_for_document(search_regex)

    @function_tool
    def tool_query_list_bank_transactions(bank_id: uuid.UUID):
        """List bank transactions for a given bank ID."""
        return tx.tool_query_list_bank_transactions(
            bank_id=bank_id
        )

    @function_tool
    def tool_query_list_unreconciled_transactions(bank_id: uuid.UUID):
        """List unreconciled transactions for a given year and bank ID."""
        return tx.tool_query_list_unreconciled_transactions(
            bank_id=bank_id
        )

    @function_tool
    def tool_query_list_unpaid_invoices():
        """List outstanding invoices."""
        return tx.tool_query_list_unpaid_invoices()

    @function_tool
    def tool_query_list_invoices():
        """List all invoices."""
        return tx.tool_query_list_invoices()

    @function_tool
    def tool_action_clear():
        """Undo all actions"""
        return tx.tool_action_clear()

    @function_tool
    def tool_action_undo(id: str):
        """Undoes the action with the given id"""
        return tx.tool_action_undo(id)

    @function_tool
    def tool_action_new_client(
        name: str,
        email: str,
        phone: str,
        address: str,
        country_code: str,
        vat_number: str
    ):
        """Register a new client for the business"""
        return tx.tool_action_new_client(name, email, phone, address, country_code, vat_number)

    @function_tool
    def tool_action_new_supplier(
        name: str,
        email: str,
        phone: str,
        address: str,
        country: str,
        vat_number: str
    ):
        """
        Register a new supplier for the business:

        - name: name of the supplier
        - email: email of the supplier
        - phone: phone number of the supplier
        - address: address of the supplier
        - country: two letter country code of the supplier
        - vat_number: vat number of the supplier

        All fields are optional.
        """
        return tx.tool_action_new_supplier(
            name=name,
            email=email,
            phone=phone,
            address=address,
            country=country,
            vat_number=vat_number
        )

    @function_tool
    def tool_action_create_invoice(
        client_id: uuid.UUID,
        amount: float,
        currency: str,
        description: str,
        due_date: datetime.date
    ):
        """Creates a new invoice for the given client"""
        return tx.tool_action_create_invoice(
            client_id=client_id,
            amount=amount,
            currency=currency,
            description=description,
            due_date=due_date,
        )

    @function_tool
    def tool_action_reconcile_transactions(
        bank_txs: List[uuid.UUID],
        receipts: List[uuid.UUID],
    ):
        """Reconcile a list of transactions for a given year and bank ID."""
        return tx.tool_action_reconcile_transactions(
            bank_txs=bank_txs,
            receipts=receipts,
        )

    tools = [
        # Query tools
        tool_query_client,
        tool_query_current_time,
        tool_query_for_document,
        tool_query_list_bank_transactions,
        tool_query_list_unreconciled_transactions,
        tool_query_list_unpaid_invoices,
        tool_query_list_invoices,
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
{tx.context()}

If the user interacts with you in a different language than english, respond in the same language.
Do not translate transaction descriptions or other details. Return these verbatim.
""",
        tools=tools,
    )

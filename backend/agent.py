import re
import uuid
import dataclasses
import datetime
import json

from agents import function_tool
from agents.agent import Agent

from state import Bank, BankTransaction, CompanyData, State, Transient, StoreMemory, create_test_state
from action import Action, NewInvoice, UpdateClient, UpdateSupplier, Reconcile
from typing import List, Tuple, Optional, Callable

class Transaction:
    def __init__(
        self,
        state: State, # base state
        action_callback: Optional[Callable] = None
    ):
        self.act_cnt = 1
        self.state = state
        # mapping from an action "name" to the action
        self.actions: List[Tuple[str, Action]] = []
        self.transient = Transient(state)
        self.action_callback = action_callback

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
            },
            "current_date": datetime.date.today()
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

    def tool_query_supplier(
        self,
        name_query: str,
    ):
        """Query suppliers by name"""
        suppliers = []
        for supplier in self.transient.list_suppliers():
            if name_query.lower() in supplier.name.lower():
                suppliers.append(supplier)
        return suppliers

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
        client_id = uuid.uuid4()
        act_id = self.add_action(
            UpdateClient(
                client_id=client_id,
                name=name,
                email=email,
                address=address,
                phone=phone,
                country=country,
                vat_number=vat_number
            )
        )
        return {"action_id": act_id, "client_id": str(client_id)}

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
        supplier_id = uuid.uuid4()
        act_id = self.add_action(
            UpdateSupplier(
                supplier_id=supplier_id, # new supplier
                name=name,
                email=email,
                phone=phone,
                address=address,
                country=country,
                vat_number=vat_number
            )
        )
        return {"action_id": act_id, "supplier_id": str(supplier_id)}

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
                invoice_id=uuid.uuid4(), # new invoice
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
        supplier_id: uuid.UUID,
    ):
        """
        Reconcile transactions with receipts/expenses.
        """
        return self.add_action(
            Reconcile(
                bank_txs=bank_txs,
                docs_ids=receipts,
                supplier_id=supplier_id,
            )
        )

    def tool_query_list_unpaid_invoices(self):
        """
        List all unreconciled invoices:
        invoices which have not been matched to a bank transaction.
        """
        invoices = []
        for invoice in self.transient.list_invoices():
            invoices.append(invoice)
        return invoices

    def tool_query_list_invoices(self):
        """
        List all invoices.
        """
        invoices = []
        for invoice in self.transient.list_invoices():
            invoices.append(invoice)
        return invoices

    def tool_query_for_document(
        self,
        search_regex: str,
    ):
        """
        Search for documents based on a search term. Used for e.g. finding receipts
        Supply the empty search_regex to obtain all documents.

        Observe that:
        - Search is case-insensitive.
        - You might need to search for multiple terms, it might not match exactly.
        """
        docs = []
        regex = re.compile(search_regex, re.IGNORECASE)
        for doc in self.transient.list_documents():
            if regex.search(doc.description):
                docs.append(doc)
            elif regex.search(doc.content):
                docs.append(doc)
        return docs

    def tool_query_list_bank_transactions(
        self,
        bank_id: uuid.UUID,
    ):
        """
        List bank transactions for a given bank ID.
        """
        return self.transient.list_transactions(bank_id)

    def tool_query_list_unreconciled_transactions(
        self,
        bank_id: uuid.UUID,
    ):
        """
        List unreconciled transactions for a given year and bank ID.
        """
        return self.transient.list_unreconciled_transactions(bank_id)

def create_agent(action_callback: Optional[Callable] = None):
    """Create a new agent instance with fresh state."""
    st = create_test_state()
    tx = Transaction(st, action_callback)

    # Create function tools that access state via closure
    @function_tool
    def tool_query_client(name_query: str):
        """Query clients by name"""
        pass

    @function_tool
    def tool_query_supplier(name_query: str):
        """Query suppliers by name"""
        suppliers = []
        for supplier in tx.transient.list_suppliers():
            if name_query.lower() in supplier.name.lower():
                suppliers.append(supplier)
        return suppliers

    @function_tool
    def tool_query_for_document(search_regex: str):
        """Search for documents based on a search term. Used for e.g. finding receipts"""
        docs = []
        regex = re.compile(search_regex, re.IGNORECASE)
        for doc in tx.transient.list_documents():
            if regex.search(doc.description):
                docs.append(doc)
            elif regex.search(doc.content):
                docs.append(doc)
        return docs

    @function_tool
    def tool_query_list_bank_transactions(bank_id: uuid.UUID):
        """List bank transactions for a given bank ID."""
        return tx.transient.list_transactions(bank_id)

    @function_tool
    def tool_query_list_unreconciled_transactions(bank_id: uuid.UUID):
        """List unreconciled transactions for a given year and bank ID."""
        return tx.transient.list_unreconciled_transactions(bank_id)

    @function_tool
    def tool_query_list_unpaid_invoices():
        """List outstanding invoices."""
        invoices = []
        for invoice in tx.transient.list_invoices():
            invoices.append(invoice)
        return invoices

    @function_tool
    def tool_query_list_invoices():
        """List all invoices."""
        invoices = []
        for invoice in tx.transient.list_invoices():
            invoices.append(invoice)
        return invoices

    @function_tool
    def tool_action_clear():
        """Undo all actions"""
        # Emit clear event (more efficient than individual removals)
        if tx.action_callback:
            tx.action_callback('action_clear', {})

        tx.actions = []
        tx.transient = Transient(tx.state)

    @function_tool
    def tool_action_undo(id: str):
        """Undoes the action with the given id"""
        for (act_id, _) in tx.actions:
            if act_id == id:
                break
        else:
            return {"error": f"Action with id {id} not found"}

        # Emit removal event
        if tx.action_callback:
            tx.action_callback('action_removed', {'action_id': id})

        # remove the action
        actions = [change for change in tx.actions if change[0] != id]

        # reset state and try to replay all actions
        transient = Transient(tx.state)
        for (_, action) in actions:
            action.apply(transient)

        # write back the new state and actions
        tx.transient = transient
        tx.actions = actions

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
        client_id = uuid.uuid4()
        action = UpdateClient(
            client_id=client_id,
            name=name,
            email=email,
            address=address,
            phone=phone,
            country=country_code,
            vat_number=vat_number
        )
        action.apply(tx.transient)
        act_id = f"{action.action_type()}-{tx.act_cnt}"
        tx.act_cnt += 1
        tx.actions.append((act_id, action))

        # Emit creation event
        if tx.action_callback:
            action_args = {
                'name': name,
                'email': email,
                'phone': phone,
                'address': address,
                'country_code': country_code,
                'vat_number': vat_number
            }
            tx.action_callback('action_created', {
                'action_id': act_id,
                'action_type': 'new_client',
                'action_args': action_args,
                'timestamp': datetime.datetime.now().isoformat()
            })

        return {"action_id": act_id, "client_id": str(client_id)}

    @function_tool
    def tool_action_update_supplier(
        name: str,
        email: str,
        phone: str,
        address: str,
        country: str,
        vat_number: str,
        supplier_id: uuid.UUID = None
    ):
        """
        Create a new supplier or update an existing one:

        - name: name of the supplier
        - email: email of the supplier
        - phone: phone number of the supplier
        - address: address of the supplier
        - country: two letter country code of the supplier
        - vat_number: vat number of the supplier
        - supplier_id: UUID of existing supplier to update (optional - if not provided, creates new supplier)

        All fields except supplier_id are optional.
        """
        # If no supplier_id provided, create a new supplier
        if supplier_id is None:
            supplier_id = uuid.uuid4()
            is_new_supplier = True
        else:
            is_new_supplier = False

        action = UpdateSupplier(
            supplier_id=supplier_id,
            name=name,
            email=email,
            phone=phone,
            address=address,
            country=country,
            vat_number=vat_number
        )
        action.apply(tx.transient)
        act_id = f"{action.action_type()}-{tx.act_cnt}"
        tx.act_cnt += 1
        tx.actions.append((act_id, action))

        # Emit creation event
        if tx.action_callback:
            action_args = {
                'supplier_id': str(supplier_id),
                'name': name,
                'email': email,
                'phone': phone,
                'address': address,
                'country': country,
                'vat_number': vat_number
            }
            tx.action_callback('action_created', {
                'action_id': act_id,
                'action_type': 'new_supplier' if is_new_supplier else 'update_supplier',
                'action_args': action_args,
                'timestamp': datetime.datetime.now().isoformat()
            })

        return {"action_id": act_id, "supplier_id": str(supplier_id)}

    @function_tool
    def tool_action_create_invoice(
        client_id: uuid.UUID,
        amount: float,
        currency: str,
        description: str,
        due_date: datetime.date
    ):
        """Creates a new invoice for the given client"""
        action = NewInvoice(
            invoice_id=uuid.uuid4(),
            client_id=client_id,
            amount=amount,
            currency=currency,
            due_date=due_date,
            description=description,
        )
        action.apply(tx.transient)
        act_id = f"{action.action_type()}-{tx.act_cnt}"
        tx.act_cnt += 1
        tx.actions.append((act_id, action))

        # Emit creation event
        if tx.action_callback:
            action_args = {
                'client_id': str(client_id),
                'amount': amount,
                'currency': currency,
                'description': description,
                'due_date': due_date.isoformat()
            }
            tx.action_callback('action_created', {
                'action_id': act_id,
                'action_type': 'create_invoice',
                'action_args': action_args,
                'timestamp': datetime.datetime.now().isoformat()
            })

        return act_id

    @function_tool
    def tool_action_reconcile_transactions(
        bank_txs: List[uuid.UUID],
        receipts: List[uuid.UUID],
        supplier_id: uuid.UUID,
    ):
        """Reconcile a list of transactions for a given year and bank ID."""
        action = Reconcile(
            bank_txs=bank_txs,
            docs_ids=receipts,
            supplier_id=supplier_id,
        )
        action.apply(tx.transient)
        act_id = f"{action.action_type()}-{tx.act_cnt}"
        tx.act_cnt += 1
        tx.actions.append((act_id, action))

        # Emit creation event
        if tx.action_callback:
            # Get the full transaction and document details
            bank_tx_details = []
            for tx_id in bank_txs:
                for bank in tx.transient.list_banks():
                    for transaction in tx.transient.list_transactions(bank.id):
                        if transaction.id == tx_id:
                            bank_tx_details.append({
                                'id': str(transaction.id),
                                'amount': transaction.amount,
                                'date': transaction.date.isoformat(),
                                'description': transaction.description,
                                'account_name': bank.name,
                                'currency': bank.currency
                            })
                            break

            receipt_details = []
            for receipt_id in receipts:
                for document in tx.transient.list_documents():
                    if document.id == receipt_id:
                        receipt_details.append({
                            'id': str(document.id),
                            'name': document.name,
                            'description': document.description
                        })
                        break

            # Get the full supplier details
            supplier_details = None
            for supplier in tx.transient.list_suppliers():
                if supplier.id == supplier_id:
                    supplier_details = {
                        'id': str(supplier.id),
                        'name': supplier.name,
                        'email': supplier.email,
                        'phone': supplier.phone,
                        'address': supplier.address,
                        'vat_number': supplier.vat_number,
                        'country': supplier.country
                    }
                    break

            action_args = {
                'bank_txs': bank_tx_details,
                'receipts': receipt_details,
                'supplier_id': supplier_details if supplier_details else str(supplier_id)
            }
            tx.action_callback('action_created', {
                'action_id': act_id,
                'action_type': 'reconcile_transactions',
                'action_args': action_args,
                'timestamp': datetime.datetime.now().isoformat()
            })

        return act_id

    tools = [
        # Query tools
        tool_query_client,
        tool_query_supplier,
        tool_query_for_document,
        tool_query_list_bank_transactions,
        tool_query_list_unreconciled_transactions,
        tool_query_list_unpaid_invoices,
        tool_query_list_invoices,
        # Action tools
        tool_action_clear,
        tool_action_undo,
        tool_action_new_client,
        tool_action_update_supplier,
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
DO NOT SHOW UUIDS/IDS, UNLESS SPECIFICALLY REQUESTED BY THE USER.

Data about the entity:
{tx.context()}

If the user interacts with you in a different language than english, respond in the same language.
Do not translate transaction descriptions or other details. Return these verbatim.
""",
        tools=tools,
    )

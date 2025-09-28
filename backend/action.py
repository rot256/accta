import uuid
import datetime

from enum import Enum
from typing import List
from country import validate_country_code
from state import Client, Invoice, State, Supplier
from state import Expense as StateExpense
from pydantic.dataclasses import dataclass

class ActionType:
    UPDATE_CLIENT = "client"
    UPDATE_SUPPLIER = "supplier"
    NEW_INVOICE = "invoice"
    EXPENSE = "expense"

@dataclass
class Action:
    def action_type(self) -> str:
        raise NotImplementedError("Actions must implement the name method.")

    def apply(self, st: State):
        raise NotImplementedError("Actions must implement the apply method.")

@dataclass
class UpdateClient(Action):
    client_id: uuid.UUID
    name: str
    address: str
    vat_number: str
    email: str
    phone: str
    country: str

    def action_type(self) -> str:
        return ActionType.UPDATE_CLIENT

    def apply(self, st: State):
        st.store_client(
            Client(
                id=self.client_id,
                name=self.name,
                address=self.address,
                vat_number=self.vat_number,
                email=self.email,
                phone=self.phone,
                country=self.country
            )
        )

@dataclass
class UpdateSupplier(Action):
    supplier_id: uuid.UUID
    name: str
    address: str
    vat_number: str
    email: str
    phone: str
    country: str

    def action_type(self) -> str:
        return ActionType.UPDATE_SUPPLIER

    def __init__(
        self,
        supplier_id: uuid.UUID,
        name: str,
        address: str,
        vat_number: str,
        email: str,
        phone: str,
        country: str,
    ):
        validate_country_code(country)
        self.supplier_id = supplier_id
        self.name = name
        self.address = address
        self.vat_number = vat_number
        self.email = email
        self.phone = phone
        self.country = country

    def apply(self, st: State):
        st.store_supplier(
            Supplier(
                id=self.supplier_id,
                name=self.name,
                email=self.email,
                phone=self.phone,
                address=self.address,
                vat_number=self.vat_number,
                country=self.country
            )
        )

@dataclass
class NewInvoice(Action):
    invoice_id: uuid.UUID
    amount: float
    currency: str
    client_id: uuid.UUID
    due_date: datetime.date
    description: str

    def action_type(self) -> str:
        return ActionType.NEW_INVOICE

    def apply(self, st: State):
        st.check_client_id(self.client_id)
        st.store_invoice(
            Invoice(
                id=self.invoice_id,
                client=self.client_id,
                amount=self.amount,
                currency=self.currency,
                created=datetime.date.today(),
                due_date=self.due_date,
                description=self.description
            )
        )

@dataclass
class VATType(str):
    VAT = "VAT"
    NO_VAT = "NO_VAT"

@dataclass
class Expense(Action):
    bank_txs: List[uuid.UUID]
    docs_ids: List[uuid.UUID]
    supplier: uuid.UUID
    vat_type: VATType
    description: str

    def action_type(self) -> str:
        return ActionType.EXPENSE

    def apply(self, st: State):
        # Check on the state that:
        # 1. the bank_txs are valid
        st.check_transaction_ids(self.bank_txs)

        # 2. the docs_ids are valid
        st.check_document_ids(self.docs_ids)

        # 3. the bank_txs and docs_ids are not already expensed
        st.check_transactions_not_expensed(self.bank_txs)
        st.check_documents_not_expensed(self.docs_ids)

        st.store_expense(
            StateExpense(
                id=uuid.uuid4(),
                bank_txs=self.bank_txs,
                docs_ids=self.docs_ids,
                supplier_id=self.supplier,
                description=self.description,
                vat_type=self.vat_type
            )
        )

import uuid
import datetime

from typing import List
from country import validate_country_code
from state import Client, Invoice, Reconciliation, State, Supplier
from pydantic.dataclasses import dataclass

class ActionType:
    UPDATE_CLIENT = "client"
    UPDATE_SUPPLIER = "supplier"
    NEW_INVOICE = "invoice"
    RECONCILE = "reconcile"

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
    amount: float
    currency: str
    client_id: uuid.UUID
    due_date: datetime.date
    description: str

    def action_type(self) -> str:
        return ActionType.NEW_INVOICE

    def __init__(
        self,
        client_id: uuid.UUID,
        amount: float,
        currency: str,
        due_date: datetime.date,
        description: str,
    ):
        self.id = uuid.uuid4()
        self.client_id = client_id
        self.amount = amount
        self.currency = currency
        self.due_date = due_date
        self.description = description

    def apply(self, st: State):
        st.store_invoice(
            Invoice(
                id=self.id,
                client=self.client_id,
                amount=self.amount,
                currency=self.currency,
                created=datetime.datetime.now(),
                due_date=self.due_date,
                description=self.description
            )
        )

@dataclass
class Reconcile(Action):
    bank_txs: List[uuid.UUID]
    docs_ids: List[uuid.UUID]

    def action_type(self) -> str:
        return ActionType.RECONCILE

    def apply(self, st: State):
        # Check on the state that:
        # 1. the bank_txs are valid
        st.check_transaction_ids(self.bank_txs)

        # 2. the docs_ids are valid
        st.check_document_ids(self.docs_ids)

        # 3. the bank_txs and docs_ids are not already reconciled
        # TODO: Implement this check

        st.store_reconciliation(
            Reconciliation(
                id=uuid.uuid4(),
                bank_txs=self.bank_txs,
                docs_ids=self.docs_ids,
            )
        )

from pydantic.dataclasses import dataclass

import uuid
import datetime

from typing import List

@dataclass
class CompanyData:
    id: uuid.UUID
    name: str
    address: str
    vat_number: str
    email: str
    phone: str
    country: str

@dataclass
class Obj:
    id: uuid.UUID

@dataclass
class Client(Obj):
    id: uuid.UUID
    name: str
    address: str
    vat_number: str
    email: str
    phone: str
    country: str

@dataclass
class Expense(Obj):
    id: uuid.UUID
    bank_txs: List[uuid.UUID]
    docs_ids: List[uuid.UUID]
    supplier_id: uuid.UUID
    description: str
    vat_type: str  # 'VAT' or 'NO_VAT'

@dataclass
class Supplier(Obj):
    id: uuid.UUID
    name: str
    address: str
    vat_number: str
    email: str
    phone: str
    country: str

@dataclass
class Document(Obj):
    id: uuid.UUID
    name: str
    description: str # AI extracted
    content: str # OCR'd full text content


@dataclass
class BankTransaction:
    id: uuid.UUID
    amount: float
    date: datetime.date
    description: str

@dataclass
class Invoice(Obj):
    id: uuid.UUID
    client: uuid.UUID
    amount: float
    currency: str
    created: datetime.date
    due_date: datetime.date
    description: str

@dataclass
class Bank:
    id: uuid.UUID
    name: str
    currency: str
    iban: str

class State:
    def company(self) -> CompanyData:
        raise NotImplementedError("A state must implement the company_details method.")

    def list_banks(self) -> List[Bank]:
        raise NotImplementedError("A state must implement the list_banks method.")

    def list_clients(self) -> List[Client]:
        raise NotImplementedError("A state must implement the list_clients method.")

    def list_invoices(self) -> List[Invoice]:
        raise NotImplementedError("A state must implement the list_invoices method.")

    def list_transactions(self, bank_id: uuid.UUID) -> List[BankTransaction]:
        raise NotImplementedError("A state must implement the list_transactions method which returns a list of transactions for a given bank.")

    def list_documents(self) -> List[Document]:
        raise NotImplementedError("A state must implement the list_documents method.")

    def list_expenses(self) -> List[Expense]:
        raise NotImplementedError("A state must implement the list_expenses method.")

    def list_suppliers(self) -> List[Supplier]:
        raise NotImplementedError("A state must implement the list_suppliers method.")

    def list_unused_documents(self) -> List[Document]:
        """
        These basic implementations have horrible running time.
        """
        # collect all expensed transactions
        used_docs = set()
        for expense in self.list_expenses():
            for id in expense.docs_ids:
                used_docs.add(id)

        # filter out used documents
        return [doc for doc in self.list_documents() if doc.id not in used_docs]

    def list_unreconciled_transactions(
        self,
        bank_id: uuid.UUID
    ) -> List[BankTransaction]:
        """
        These basic implementations have horrible running time.
        """
        # collect all expensed transactions
        used_txs = set()
        for recon in self.list_expenses():
            for id in recon.bank_txs:
                used_txs.add(id)

        # filter out expensed transactions
        return [tx for tx in self.list_transactions(bank_id) if tx.id not in used_txs]

    def check_transaction_ids(self, tx_ids: List[uuid.UUID]):
        """
        Checks if the given transaction IDs are valid.
        """
        valid_tx_ids = set()
        for bank in self.list_banks():
            for tx in self.list_transactions(bank.id):
                valid_tx_ids.add(tx.id)

        for id in tx_ids:
            if id not in valid_tx_ids:
                raise ValueError(f"Invalid transaction ID: {id}")

    def check_document_ids(self, doc_ids: List[uuid.UUID]):
        """
        Checks if the given document IDs are valid.
        """
        valid_doc_ids = set()
        for doc in self.list_documents():
            valid_doc_ids.add(doc.id)

        for id in doc_ids:
            if id not in valid_doc_ids:
                raise ValueError(f"Invalid document ID: {id}")

    def check_transactions_not_expensed(self, tx_ids: List[uuid.UUID]):
        """
        Checks that the given transaction IDs are not already expensed.
        """
        expensed_tx_ids = set()
        for expense in self.list_expenses():
            for tx_id in expense.bank_txs:
                expensed_tx_ids.add(tx_id)

        for tx_id in tx_ids:
            if tx_id in expensed_tx_ids:
                raise ValueError(f"Transaction ID {tx_id} is already expensed")

    def check_documents_not_expensed(self, doc_ids: List[uuid.UUID]):
        """
        Checks that the given document IDs are not already expensed.
        """
        expensed_doc_ids = set()
        for expense in self.list_expenses():
            for doc_id in expense.docs_ids:
                expensed_doc_ids.add(doc_id)

        for doc_id in doc_ids:
            if doc_id in expensed_doc_ids:
                raise ValueError(f"Document ID {doc_id} is already expensed")

    def check_client_id(self, client_id: uuid.UUID):
        """
        Checks if the given client ID is valid.
        """
        valid_client_ids = set()
        for client in self.list_clients():
            valid_client_ids.add(client.id)

        if client_id not in valid_client_ids:
            raise ValueError(f"Invalid client ID: {client_id}")

    def store_client(
        self,
        obj: Client
    ):
        raise NotImplementedError("A state must implement the update_client method.")

    def store_supplier(
        self,
        obj: Supplier
    ):
        raise NotImplementedError("A state must implement the update_supplier method.")

    def store_invoice(
        self,
        obj: Invoice
    ):
        raise NotImplementedError("A state must implement the update_invoice method.")

    def store_expense(
        self,
        obj: Expense
    ):
        raise NotImplementedError("A state must implement the update_expense method.")


class StoreMemory(State):
    """
    An in-memory backing storage for the application.
    """
    def __init__(
        self,
    ):
        self.company_data = CompanyData(
            id=uuid.uuid4(),
            name="",
            address="",
            vat_number="",
            email="",
            phone="",
            country="US"
        )
        self.banks = {}
        self.clients = {}
        self.suppliers = {}
        self.documents = {}
        self.expenses = {}
        self.transactions = {}
        self.invoices = {}

    def set_bank(
        self,
        bank: Bank,
        txs: List[BankTransaction]
    ):
        self.banks[bank.id] = bank
        self.transactions[bank.id] = txs

    def set_company(self, company: CompanyData):
        self.company_data = company

    def company(self) -> CompanyData:
        return self.company_data

    def list_transactions(self, bank_id: uuid.UUID) -> List[BankTransaction]:
        try:
            return self.transactions[bank_id]
        except KeyError:
            return []

    def list_banks(self) -> List[Bank]:
        return list(self.banks.values())

    def list_suppliers(self) -> List[Supplier]:
        return list(self.suppliers.values())

    def list_clients(self) -> List[Client]:
        return list(self.clients.values())

    def list_documents(self) -> List[Document]:
        return list(self.documents.values())

    def list_expenses(self) -> List[Expense]:
        return list(self.expenses.values())

    def list_invoices(self) -> List[Invoice]:
        return list(self.invoices.values())

    def store_supplier(
        self,
        obj: Supplier
    ):
        self.suppliers[obj.id] = obj

    def store_client(
        self,
        obj: Client
    ):
        self.clients[obj.id] = obj

    def store_document(
        self,
        obj: Document
    ):
        self.documents[obj.id] = obj

    def store_expense(
        self,
        obj: Expense
    ):
        self.expenses[obj.id] = obj

    def store_invoice(
        self,
        obj: Invoice
    ):
        self.invoices[obj.id] = obj

def merge(objs, overwrites):
    objs_dict = {obj.id: obj for obj in objs}
    for obj in overwrites.values():
        objs_dict[obj.id] = obj
    return list(objs_dict.values())

class Transient(State):
    def __init__(self, state: State):
        self.state = state
        self.suppliers = {}
        self.clients = {}
        self.documents = {}
        self.expenses = {}
        self.invoices = {}
        self.transactions = {}
        self.company_data = None

    def company(self):
        if self.company_data:
            return self.company_data
        else:
            return self.state.company()

    def list_banks(self) -> List[Bank]:
        return self.state.list_banks()

    def list_invoices(self) -> List[Invoice]:
        return merge(
            self.state.list_invoices(),
            self.invoices
        )

    def list_suppliers(self) -> List[Supplier]:
        return merge(
            self.state.list_suppliers(),
            self.suppliers
        )

    def list_clients(self) -> List[Client]:
        return merge(
            self.state.list_clients(),
            self.clients
        )

    def list_documents(self) -> List[Document]:
        return merge(
            self.state.list_documents(),
            self.documents
        )

    def list_expenses(self) -> List[Expense]:
        return merge(
            self.state.list_expenses(),
            self.expenses
        )

    def list_transactions(self, bank_id: uuid.UUID) -> List[BankTransaction]:
        return merge(
            self.state.list_transactions(bank_id),
            self.transactions
        )

    def store_supplier(
        self,
        obj: Supplier
    ):
        self.suppliers[obj.id] = obj

    def store_client(
        self,
        obj: Client
    ):
        self.clients[obj.id] = obj

    def store_document(
        self,
        obj: Document
    ):
        self.documents[obj.id] = obj

    def store_expense(
        self,
        obj: Expense
    ):
        self.expenses[obj.id] = obj

    def store_invoice(
        self,
        obj: Invoice
    ):
        self.invoices[obj.id] = obj

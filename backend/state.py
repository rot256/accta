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
class Reconciliation(Obj):
    id: uuid.UUID
    bank_txs: List[uuid.UUID]
    docs_ids: List[uuid.UUID]

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
    desc: str # AI extracted


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

    def list_reconciliations(self) -> List[Reconciliation]:
        raise NotImplementedError("A state must implement the list_reconciliations method.")

    def list_suppliers(self) -> List[Supplier]:
        raise NotImplementedError("A state must implement the list_suppliers method.")

    def list_unused_documents(self) -> List[Document]:
        """
        These basic implementations have horrible running time.
        """
        # collect all reconciled transactions
        used_docs = set()
        for recon in self.list_reconciliations():
            for id in recon.docs_ids:
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
        # collect all reconciled transactions
        used_txs = set()
        for recon in self.list_reconciliations():
            for id in recon.bank_txs:
                used_txs.add(id)

        # filter out reconciled transactions
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

    def store_reconciliation(
        self,
        obj: Reconciliation
    ):
        raise NotImplementedError("A state must implement the update_reconciliation method.")


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
        self.reconciliations = {}
        self.transactions = {}

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

    def list_reconciliations(self) -> List[Reconciliation]:
        return list(self.reconciliations.values())

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

    def store_reconciliation(
        self,
        obj: Reconciliation
    ):
        self.reconciliations[obj.id] = obj

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
        self.reconciliations = {}
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

    def list_reconciliations(self) -> List[Reconciliation]:
        return merge(
            self.state.list_reconciliations(),
            self.reconciliations
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

    def store_reconciliation(
        self,
        obj: Reconciliation
    ):
        self.reconciliations[obj.id] = obj

import json
import pytest

def test_json_serialization_deserialization():
    # Create sample objects
    company = CompanyData(
        id=uuid.uuid4(),
        name="TestCo",
        address="123 Main St",
        vat_number="VAT123",
        email="info@testco.com",
        phone="555-1234",
        country="US"
    )
    bank = Bank(
        id=uuid.uuid4(),
        name="TestBank",
        currency="USD",
        iban="US123456789"
    )
    client = Client(
        id=uuid.uuid4(),
        name="ClientName",
        address="456 Elm St",
        vat_number="VAT456",
        email="client@email.com",
        phone="555-5678",
        country="US"
    )
    supplier = Supplier(
        id=uuid.uuid4(),
        name="SupplierName",
        address="789 Oak St",
        vat_number="VAT789",
        email="supplier@email.com",
        phone="555-9012",
        country="US"
    )
    document = Document(
        id=uuid.uuid4(),
        name="Doc1",
        desc="Extracted description"
    )
    bank_tx = BankTransaction(
        id=uuid.uuid4(),
        amount=123.45,
        date=datetime.date(2024, 6, 1),
        description="Payment"
    )
    invoice = Invoice(
        id=uuid.uuid4(),
        client=client.id,
        amount=500.0,
        currency="USD",
        created=datetime.date(2024, 6, 2),
        due_date=datetime.date(2024, 7, 2),
        description="Invoice for services"
    )
    reconciliation = Reconciliation(
        id=uuid.uuid4(),
        bank_txs=[bank_tx.id],
        docs_ids=[document.id]
    )

    # List of all objects to test
    objects = [
        company,
        bank,
        client,
        supplier,
        document,
        bank_tx,
        invoice,
        reconciliation
    ]

    # Helper to convert dataclass to dict, handling UUIDs and dates
    def dataclass_to_dict(obj):
        if hasattr(obj, "__dict__"):
            d = {}
            for k, v in obj.__dict__.items():
                if isinstance(v, uuid.UUID):
                    d[k] = str(v)
                elif isinstance(v, datetime.date):
                    d[k] = v.isoformat()
                elif isinstance(v, list):
                    d[k] = [str(x) if isinstance(x, uuid.UUID) else x for x in v]
                else:
                    d[k] = v
            return d
        else:
            return obj

    # Helper to reconstruct objects from dicts
    def dict_to_dataclass(cls, d):
        # Map fields to types
        field_types = {f.name: f.type for f in cls.__dataclass_fields__.values()}
        for k, t in field_types.items():
            if t == uuid.UUID and isinstance(d[k], str):
                d[k] = uuid.UUID(d[k])
            elif t == datetime.date and isinstance(d[k], str):
                d[k] = datetime.date.fromisoformat(d[k])
            elif t == List[str] and isinstance(d[k], list):
                d[k] = [str(x) for x in d[k]]
        return cls(**d)

    for obj in objects:
        # Serialize to JSON
        obj_dict = dataclass_to_dict(obj)
        json_str = json.dumps(obj_dict)
        # Deserialize from JSON
        loaded_dict = json.loads(json_str)
        # Reconstruct object
        reconstructed = dict_to_dataclass(type(obj), loaded_dict)
        # Check equality for fields
        for field in obj.__dataclass_fields__:
            orig = getattr(obj, field)
            recon = getattr(reconstructed, field)
            assert orig == recon, f"Mismatch in field '{field}' for {type(obj).__name__}"

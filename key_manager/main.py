import os
import uuid
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException, Query, Path
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy import Column, String, Text, Boolean, DateTime, select
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base

from osint_providers import (
    OSINT_PROVIDERS_REGISTRY,
    ProviderMetadata,
    list_supported_providers,
    get_provider_info
)
from key_vault import KeyVault


# Ανάκτηση διεύθυνσης βάσης δεδομένων από μεταβλητές περιβάλλοντος
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://osint_user:osint_password@postgres:5432/osint_db"
)

# Αρχικοποίηση μηχανισμού κρυπτογράφησης
vault = KeyVault()

# Δημιουργία ασύγχρονης μηχανής SQLAlchemy
engine = create_async_engine(DATABASE_URL, echo=False)

# Δημιουργία session maker για συνεδρίες βάσης δεδομένων
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Βασική κλάση μοντέλων SQLAlchemy
Base = declarative_base()


# Μοντέλο βάσης δεδομένων για την αποθήκευση των API Keys των OSINT πηγών
class OSINTApiKey(Base):
    """
    Πίνακας αποθήκευσης API Keys για τις διάφορες πηγές OSINT.
    Τα API Keys αποθηκεύονται πάντα κρυπτογραφημένα στη βάση δεδομένων.
    """
    __tablename__ = "osint_api_keys"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    provider_name = Column(String(100), nullable=False, index=True)
    key_name = Column(String(255), nullable=False)
    encrypted_value = Column(Text, nullable=False)
    masked_value = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    last_used_at = Column(DateTime(timezone=True), nullable=True)


# Σχήματα Pydantic για έλεγχο και επικύρωση δεδομένων (Schemas)
class APIKeyCreate(BaseModel):
    """
    Σχήμα Pydantic για την καταχώρηση νέου API Key.
    """
    provider_name: str = Field(..., description="Όνομα της πηγής OSINT (π.χ. shodan, acled, virustotal)")
    key_name: str = Field(..., description="Περιγραφικό όνομα κλειδιού (π.χ. 'Production Key 1')")
    api_key_value: str = Field(..., description="Το πραγματικό API Key που θα κρυπτογραφηθεί")


class APIKeyResponse(BaseModel):
    """
    Σχήμα Pydantic για την επιστροφή στοιχείων κλειδιού (με συγκαλυμμένο το μυστικό).
    """
    id: uuid.UUID
    provider_name: str
    key_name: str
    masked_value: str
    is_active: bool
    created_at: datetime
    last_used_at: Optional[datetime]

    class Config:
        from_attributes = True


class DecryptedKeyResponse(BaseModel):
    """
    Σχήμα Pydantic για την επιστροφή του αποκρυπτογραφημένου API key στο main backend.
    """
    provider_name: str
    key_name: str
    api_key_value: str


class GenerateInternalKeyRequest(BaseModel):
    """
    Σχήμα Pydantic για αίτημα δημιουργίας εσωτερικού κλειδιού πρόσβασης.
    """
    key_name: str = Field(..., description="Περιγραφή του εσωτερικού κλειδιού")
    prefix: str = Field(default="osinit_key", description="Πρόθεμα κλειδιού")


# Διαχειριστής κύκλου ζωής της εφαρμογής FastAPI
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Αρχικοποίηση πινάκων βάσης δεδομένων κατά την εκκίνηση του Key Manager subproject.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


# Αρχικοποίηση εφαρμογής FastAPI
app = FastAPI(
    title="OSINT Key Manager Subproject API",
    description="Υποσύστημα διαχείρισης και κρυπτογράφησης API Keys για OSINT πηγές",
    version="1.0.0",
    lifespan=lifespan
)

# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Dependency για λήψη συνεδρίας βάσης δεδομένων
async def get_db_session() -> AsyncSession:
    """
    Παρέχει ασύγχρονη συνεδρία (AsyncSession) στη βάση δεδομένων.
    """
    async with AsyncSessionLocal() as session:
        yield session


# Endpoints API

@app.get("/api/v1/providers", response_model=Dict[str, ProviderMetadata])
async def list_providers() -> Dict[str, ProviderMetadata]:
    """
    Επιστρέφει τις 20 υποστηριζόμενες OSINT πηγές μαζί με τα μεταδεδομένα τους.
    """
    return OSINT_PROVIDERS_REGISTRY


@app.post("/api/v1/keys", response_model=APIKeyResponse, status_code=201)
async def register_api_key(
    payload: APIKeyCreate,
    db: AsyncSession = Depends(get_db_session)
) -> APIKeyResponse:
    """
    Καταχωρεί και κρυπτογραφεί ένα νέο API key για οποιαδήποτε OSINT πηγή.
    """
    provider_clean = payload.provider_name.lower().strip()
    
    # Κρυπτογράφηση και συγκάλυψη του API key
    encrypted_val = vault.encrypt_key(payload.api_key_value)
    masked_val = vault.mask_api_key(payload.api_key_value)

    new_key = OSINTApiKey(
        id=uuid.uuid4(),
        provider_name=provider_clean,
        key_name=payload.key_name,
        encrypted_value=encrypted_val,
        masked_value=masked_val,
        is_active=True
    )

    db.add(new_key)
    await db.commit()
    await db.refresh(new_key)

    return APIKeyResponse.model_validate(new_key)


@app.get("/api/v1/keys", response_model=List[APIKeyResponse])
async def list_keys(
    provider_name: Optional[str] = Query(default=None, description="Φιλτράρισμα βάσει OSINT provider"),
    db: AsyncSession = Depends(get_db_session)
) -> List[APIKeyResponse]:
    """
    Επιστρέφει τη λίστα των αποθηκευμένων API keys (με συγκαλυμμένη τιμή).
    """
    query = select(OSINTApiKey).where(OSINTApiKey.is_active == True).order_by(OSINTApiKey.created_at.desc())
    
    if provider_name:
        query = query.where(OSINTApiKey.provider_name == provider_name.lower().strip())

    result = await db.execute(query)
    keys = result.scalars().all()

    return [APIKeyResponse.model_validate(k) for k in keys]


@app.get("/api/v1/keys/{provider_name}/decrypted", response_model=DecryptedKeyResponse)
async def get_decrypted_key(
    provider_name: str = Path(..., description="Όνομα της πηγής OSINT"),
    db: AsyncSession = Depends(get_db_session)
) -> DecryptedKeyResponse:
    """
    Επιστρέφει το ενεργό αποκρυπτογραφημένο API key για χρήση από το main backend/worker.
    """
    clean_provider = provider_name.lower().strip()
    query = select(OSINTApiKey).where(
        OSINTApiKey.provider_name == clean_provider,
        OSINTApiKey.is_active == True
    ).order_by(OSINTApiKey.created_at.desc()).limit(1)

    result = await db.execute(query)
    key_record = result.scalars().first()

    if not key_record:
        raise HTTPException(
            status_code=404,
            detail=f"Δεν βρέθηκε ενεργό API Key για την πηγή OSINT '{clean_provider}'."
        )

    # Ενημέρωση ημερομηνίας τελευταίας χρήσης
    key_record.last_used_at = datetime.now(timezone.utc)
    await db.commit()

    decrypted_val = vault.decrypt_key(key_record.encrypted_value)

    return DecryptedKeyResponse(
        provider_name=key_record.provider_name,
        key_name=key_record.key_name,
        api_key_value=decrypted_val
    )


@app.post("/api/v1/keys/generate-internal", response_model=DecryptedKeyResponse, status_code=201)
async def generate_internal_key(
    payload: GenerateInternalKeyRequest,
    db: AsyncSession = Depends(get_db_session)
) -> DecryptedKeyResponse:
    """
    Δημιουργεί αυτόματα ένα νέο τυχαίο εσωτερικό API Key για σύνδεση υποσυστημάτων.
    """
    raw_key = vault.generate_random_api_key(prefix=payload.prefix)
    encrypted_val = vault.encrypt_key(raw_key)
    masked_val = vault.mask_api_key(raw_key)

    new_key = OSINTApiKey(
        id=uuid.uuid4(),
        provider_name="internal",
        key_name=payload.key_name,
        encrypted_value=encrypted_val,
        masked_value=masked_val,
        is_active=True
    )

    db.add(new_key)
    await db.commit()
    await db.refresh(new_key)

    return DecryptedKeyResponse(
        provider_name="internal",
        key_name=payload.key_name,
        api_key_value=raw_key
    )


@app.delete("/api/v1/keys/{key_id}", status_code=200)
async def delete_key(
    key_id: uuid.UUID = Path(..., description="UUID του API key προς διαγραφή"),
    db: AsyncSession = Depends(get_db_session)
) -> Dict[str, str]:
    """
    Διαγράφει/απενεργοποιεί ένα αποθηκευμένο API Key.
    """
    query = select(OSINTApiKey).where(OSINTApiKey.id == key_id)
    result = await db.execute(query)
    key_record = result.scalars().first()

    if not key_record:
        raise HTTPException(status_code=404, detail="Το API Key δεν βρέθηκε.")

    await db.delete(key_record)
    await db.commit()

    return {"message": "Το API Key διαγράφηκε επιτυχώς."}


if __name__ == "__main__":
    import uvicorn
    # Εκκίνηση του διακομιστή uvicorn για την υπηρεσία FastAPI στη θύρα 8002
    uvicorn.run("main:app", host="127.0.0.1", port=8002, reload=True)


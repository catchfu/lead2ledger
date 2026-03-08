import base64
import hashlib
import hmac
import json
import os
import secrets
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Generator, Literal

from fastapi import Depends, FastAPI, Header, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = Path(os.getenv("CRM_DB_PATH", str(BASE_DIR / "crm.db")))
JWT_SECRET = os.getenv("JWT_SECRET", "dev-jwt-secret-change-me")
ACCESS_TOKEN_TTL_MINUTES = int(os.getenv("ACCESS_TOKEN_TTL_MINUTES", "120"))

app = FastAPI(title="CRM + SAP API", version="0.3.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


Role = Literal["admin", "sales", "ops", "finance"]


class LeadCreate(BaseModel):
    company: str = Field(min_length=2, max_length=120)
    contact_name: str = Field(min_length=2, max_length=120)
    stage: Literal["New", "Qualified", "Proposal", "Won"] = "New"
    value: float = Field(gt=0)


class Lead(BaseModel):
    id: str
    company: str
    contact_name: str
    stage: Literal["New", "Qualified", "Proposal", "Won"]
    value: float
    sap_sync: Literal["Synced", "Pending", "Failed"]
    created_at: str


class SyncJobCreate(BaseModel):
    entity: Literal["Customer", "Quote", "Order", "Invoice"]
    direction: Literal["CRM->SAP", "SAP->CRM"]
    payload_ref: str = Field(min_length=1, max_length=64)


class SyncJob(BaseModel):
    id: str
    entity: Literal["Customer", "Quote", "Order", "Invoice"]
    direction: Literal["CRM->SAP", "SAP->CRM"]
    status: Literal["Success", "Retrying", "Failed"]
    payload_ref: str
    updated_at: str


class DashboardSummary(BaseModel):
    total_pipeline: float
    won_deals: int
    sync_success_rate: int
    failed_jobs: int


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: Literal["bearer"] = "bearer"
    expires_at: str


class AuthUser(BaseModel):
    username: str
    full_name: str
    role: Role
    tenant_id: str


@contextmanager
def db_conn() -> Generator[sqlite3.Connection, None, None]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def b64url_encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("utf-8")


def b64url_decode(raw: str) -> bytes:
    padding = "=" * ((4 - len(raw) % 4) % 4)
    return base64.urlsafe_b64decode((raw + padding).encode("utf-8"))


def jwt_encode(payload: dict) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    header_b64 = b64url_encode(json.dumps(header, separators=(",", ":")).encode("utf-8"))
    payload_b64 = b64url_encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    signing_input = f"{header_b64}.{payload_b64}".encode("utf-8")
    signature = hmac.new(JWT_SECRET.encode("utf-8"), signing_input, hashlib.sha256).digest()
    signature_b64 = b64url_encode(signature)
    return f"{header_b64}.{payload_b64}.{signature_b64}"


def jwt_decode(token: str) -> dict:
    parts = token.split(".")
    if len(parts) != 3:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token format")

    header_b64, payload_b64, signature_b64 = parts
    signing_input = f"{header_b64}.{payload_b64}".encode("utf-8")
    expected_sig = hmac.new(JWT_SECRET.encode("utf-8"), signing_input, hashlib.sha256).digest()

    try:
        actual_sig = b64url_decode(signature_b64)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token signature") from exc

    if not hmac.compare_digest(expected_sig, actual_sig):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token signature mismatch")

    try:
        payload = json.loads(b64url_decode(payload_b64).decode("utf-8"))
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload") from exc

    exp = payload.get("exp")
    if exp is None or int(exp) < int(datetime.now(timezone.utc).timestamp()):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")

    return payload


def hash_password(password: str, salt: str | None = None) -> str:
    local_salt = salt or secrets.token_hex(16)
    hashed = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), local_salt.encode("utf-8"), 120000)
    return f"{local_salt}${hashed.hex()}"


def verify_password(password: str, encoded: str) -> bool:
    try:
        salt, _ = encoded.split("$", 1)
    except ValueError:
        return False
    return hmac.compare_digest(hash_password(password, salt), encoded)


def ensure_column(conn: sqlite3.Connection, table: str, column: str, declaration: str) -> None:
    existing = {row["name"] for row in conn.execute(f"PRAGMA table_info({table})")}
    if column not in existing:
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {declaration}")


def create_schema() -> None:
    with db_conn() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                full_name TEXT NOT NULL,
                role TEXT NOT NULL,
                tenant_id TEXT NOT NULL,
                active INTEGER NOT NULL DEFAULT 1
            );

            CREATE TABLE IF NOT EXISTS leads (
                id TEXT PRIMARY KEY,
                tenant_id TEXT NOT NULL,
                company TEXT NOT NULL,
                contact_name TEXT NOT NULL,
                stage TEXT NOT NULL,
                value REAL NOT NULL,
                sap_sync TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS sync_jobs (
                id TEXT PRIMARY KEY,
                tenant_id TEXT NOT NULL,
                entity TEXT NOT NULL,
                direction TEXT NOT NULL,
                status TEXT NOT NULL,
                payload_ref TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
            """
        )

        ensure_column(conn, "leads", "tenant_id", "TEXT NOT NULL DEFAULT 'acme'")
        ensure_column(conn, "sync_jobs", "tenant_id", "TEXT NOT NULL DEFAULT 'acme'")

        conn.execute("UPDATE leads SET tenant_id='acme' WHERE tenant_id IS NULL OR tenant_id='' ")
        conn.execute("UPDATE sync_jobs SET tenant_id='acme' WHERE tenant_id IS NULL OR tenant_id='' ")
        conn.commit()


def seed_if_empty() -> None:
    with db_conn() as conn:
        user_count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        if user_count == 0:
            users = [
                ("U-1", "alice", hash_password("alice123"), "Alice Carter", "admin", "acme", 1),
                ("U-2", "sam", hash_password("sam123"), "Sam Rivera", "sales", "acme", 1),
                ("U-3", "fiona", hash_password("fiona123"), "Fiona Ng", "finance", "acme", 1),
                ("U-4", "omar", hash_password("omar123"), "Omar Lee", "ops", "acme", 1),
                ("U-5", "gina", hash_password("gina123"), "Gina Ford", "admin", "globex", 1),
            ]
            conn.executemany(
                "INSERT INTO users (id, username, password_hash, full_name, role, tenant_id, active) VALUES (?, ?, ?, ?, ?, ?, ?)",
                users,
            )

        lead_count = conn.execute("SELECT COUNT(*) FROM leads").fetchone()[0]
        if lead_count == 0:
            seed_leads = [
                ("L-1001", "acme", "Northwind Traders", "A. Miller", "Qualified", 18000, "Synced", now_iso()),
                ("L-1002", "acme", "Blue Harbor Logistics", "S. Patel", "Proposal", 42000, "Pending", now_iso()),
                ("L-1003", "acme", "Pine Medical Supply", "L. Chen", "New", 9500, "Synced", now_iso()),
                ("L-1004", "acme", "Urban Farm Collective", "R. Diaz", "Won", 61000, "Synced", now_iso()),
                ("L-1005", "globex", "Atlas Industrial", "M. Novak", "Proposal", 27500, "Failed", now_iso()),
            ]
            conn.executemany(
                "INSERT INTO leads (id, tenant_id, company, contact_name, stage, value, sap_sync, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                seed_leads,
            )
        else:
            globex_leads = conn.execute("SELECT COUNT(*) FROM leads WHERE tenant_id = 'globex'").fetchone()[0]
            if globex_leads == 0:
                next_id = conn.execute("SELECT COUNT(*) FROM leads").fetchone()[0] + 1001
                conn.execute(
                    "INSERT INTO leads (id, tenant_id, company, contact_name, stage, value, sap_sync, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (f"L-{next_id}", "globex", "Globex Foods", "R. Stone", "Qualified", 15000, "Pending", now_iso()),
                )

        job_count = conn.execute("SELECT COUNT(*) FROM sync_jobs").fetchone()[0]
        if job_count == 0:
            seed_jobs = [
                ("J-2001", "acme", "Customer", "CRM->SAP", "Success", "L-1001", now_iso()),
                ("J-2002", "acme", "Quote", "CRM->SAP", "Retrying", "L-1002", now_iso()),
                ("J-2003", "acme", "Invoice", "SAP->CRM", "Success", "INV-803", now_iso()),
                ("J-2004", "globex", "Order", "CRM->SAP", "Failed", "SO-912", now_iso()),
            ]
            conn.executemany(
                "INSERT INTO sync_jobs (id, tenant_id, entity, direction, status, payload_ref, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                seed_jobs,
            )
        else:
            globex_jobs = conn.execute("SELECT COUNT(*) FROM sync_jobs WHERE tenant_id = 'globex'").fetchone()[0]
            if globex_jobs == 0:
                next_id = conn.execute("SELECT COUNT(*) FROM sync_jobs").fetchone()[0] + 2001
                conn.execute(
                    "INSERT INTO sync_jobs (id, tenant_id, entity, direction, status, payload_ref, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (f"J-{next_id}", "globex", "Customer", "CRM->SAP", "Retrying", "GLOBEX-1", now_iso()),
                )

        conn.commit()


def init_storage() -> None:
    create_schema()
    seed_if_empty()


def get_current_user(authorization: str | None = Header(default=None)) -> AuthUser:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")

    token = authorization.split(" ", 1)[1]
    payload = jwt_decode(token)

    username = str(payload.get("sub", ""))
    if not username:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid subject")

    with db_conn() as conn:
        row = conn.execute(
            "SELECT username, full_name, role, tenant_id, active FROM users WHERE username = ?",
            (username,),
        ).fetchone()

    if row is None or int(row["active"]) != 1:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User inactive or not found")

    return AuthUser(
        username=str(row["username"]),
        full_name=str(row["full_name"]),
        role=row["role"],
        tenant_id=str(row["tenant_id"]),
    )


def require_roles(*roles: Role):
    def checker(user: AuthUser = Depends(get_current_user)) -> AuthUser:
        if user.role not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient role")
        return user

    return checker


@app.on_event("startup")
def on_startup() -> None:
    init_storage()


init_storage()


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "db_path": str(DB_PATH)}


@app.post("/auth/login", response_model=TokenResponse)
def login(body: LoginRequest) -> TokenResponse:
    with db_conn() as conn:
        row = conn.execute(
            "SELECT username, password_hash, role, tenant_id, active FROM users WHERE username = ?",
            (body.username,),
        ).fetchone()

    if row is None or int(row["active"]) != 1 or not verify_password(body.password, str(row["password_hash"])):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    exp = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_TTL_MINUTES)
    payload = {
        "sub": row["username"],
        "role": row["role"],
        "tenant_id": row["tenant_id"],
        "exp": int(exp.timestamp()),
    }
    token = jwt_encode(payload)
    return TokenResponse(access_token=token, expires_at=exp.isoformat())


@app.get("/auth/me", response_model=AuthUser)
def me(user: AuthUser = Depends(get_current_user)) -> AuthUser:
    return user


@app.get("/crm/leads", response_model=list[Lead])
def list_leads(user: AuthUser = Depends(get_current_user)) -> list[Lead]:
    with db_conn() as conn:
        rows = conn.execute(
            "SELECT id, company, contact_name, stage, value, sap_sync, created_at FROM leads WHERE tenant_id = ? ORDER BY created_at DESC",
            (user.tenant_id,),
        ).fetchall()
    return [Lead(**dict(row)) for row in rows]


@app.post("/crm/leads", response_model=Lead)
def create_lead(lead: LeadCreate, user: AuthUser = Depends(require_roles("admin", "sales"))) -> Lead:
    with db_conn() as conn:
        tenant_count = conn.execute("SELECT COUNT(*) FROM leads WHERE tenant_id = ?", (user.tenant_id,)).fetchone()[0]
        lead_id = f"L-{tenant_count + 1001}"
        record = {
            "id": lead_id,
            "tenant_id": user.tenant_id,
            "company": lead.company,
            "contact_name": lead.contact_name,
            "stage": lead.stage,
            "value": lead.value,
            "sap_sync": "Pending",
            "created_at": now_iso(),
        }
        conn.execute(
            "INSERT INTO leads (id, tenant_id, company, contact_name, stage, value, sap_sync, created_at) VALUES (:id, :tenant_id, :company, :contact_name, :stage, :value, :sap_sync, :created_at)",
            record,
        )
        conn.commit()
    return Lead(**{k: v for k, v in record.items() if k != "tenant_id"})


@app.post("/sap/sync/jobs", response_model=SyncJob)
def queue_sync_job(job: SyncJobCreate, user: AuthUser = Depends(require_roles("admin", "ops", "sales"))) -> SyncJob:
    status_value: Literal["Success", "Retrying", "Failed"] = "Retrying"
    with db_conn() as conn:
        tenant_count = conn.execute("SELECT COUNT(*) FROM sync_jobs WHERE tenant_id = ?", (user.tenant_id,)).fetchone()[0]
        job_record = {
            "id": f"J-{tenant_count + 2001}",
            "tenant_id": user.tenant_id,
            "entity": job.entity,
            "direction": job.direction,
            "status": status_value,
            "payload_ref": job.payload_ref,
            "updated_at": now_iso(),
        }
        conn.execute(
            "INSERT INTO sync_jobs (id, tenant_id, entity, direction, status, payload_ref, updated_at) VALUES (:id, :tenant_id, :entity, :direction, :status, :payload_ref, :updated_at)",
            job_record,
        )
        conn.commit()
    return SyncJob(**{k: v for k, v in job_record.items() if k != "tenant_id"})


@app.get("/sap/sync/jobs", response_model=list[SyncJob])
def list_sync_jobs(user: AuthUser = Depends(get_current_user)) -> list[SyncJob]:
    with db_conn() as conn:
        rows = conn.execute(
            "SELECT id, entity, direction, status, payload_ref, updated_at FROM sync_jobs WHERE tenant_id = ? ORDER BY updated_at DESC",
            (user.tenant_id,),
        ).fetchall()
    return [SyncJob(**dict(row)) for row in rows]


@app.patch("/sap/sync/jobs/{job_id}/status", response_model=SyncJob)
def update_sync_job_status(
    job_id: str,
    status_value: Literal["Success", "Retrying", "Failed"],
    user: AuthUser = Depends(require_roles("admin", "ops")),
) -> SyncJob:
    with db_conn() as conn:
        row = conn.execute(
            "SELECT id FROM sync_jobs WHERE id = ? AND tenant_id = ?",
            (job_id, user.tenant_id),
        ).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Sync job not found")

        updated_at = now_iso()
        conn.execute(
            "UPDATE sync_jobs SET status = ?, updated_at = ? WHERE id = ? AND tenant_id = ?",
            (status_value, updated_at, job_id, user.tenant_id),
        )
        row = conn.execute(
            "SELECT id, entity, direction, status, payload_ref, updated_at FROM sync_jobs WHERE id = ? AND tenant_id = ?",
            (job_id, user.tenant_id),
        ).fetchone()
        conn.commit()

    if row is None:
        raise HTTPException(status_code=500, detail="Failed to load updated sync job")

    return SyncJob(**dict(row))


@app.get("/dashboard/summary", response_model=DashboardSummary)
def dashboard_summary(user: AuthUser = Depends(get_current_user)) -> DashboardSummary:
    with db_conn() as conn:
        lead_rows = conn.execute("SELECT stage, value FROM leads WHERE tenant_id = ?", (user.tenant_id,)).fetchall()
        job_rows = conn.execute("SELECT status FROM sync_jobs WHERE tenant_id = ?", (user.tenant_id,)).fetchall()

    total_pipeline = sum(float(r["value"]) for r in lead_rows)
    won_deals = sum(1 for r in lead_rows if r["stage"] == "Won")
    failed_jobs = sum(1 for r in job_rows if r["status"] == "Failed")
    success_jobs = sum(1 for r in job_rows if r["status"] == "Success")
    sync_success_rate = round((success_jobs / len(job_rows)) * 100) if job_rows else 0

    return DashboardSummary(
        total_pipeline=total_pipeline,
        won_deals=won_deals,
        sync_success_rate=sync_success_rate,
        failed_jobs=failed_jobs,
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

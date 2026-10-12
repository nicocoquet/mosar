"""API d'administration Mosar : prévisualisation puis publication contrôlée."""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import secrets
import sys
import tempfile
import time
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any
from urllib.parse import urlencode, urlparse

import httpx
from fastapi import Depends, FastAPI, Header, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from pydantic import BaseModel

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from config import load_config  # noqa: E402
from statistics_build import build  # noqa: E402
from statistics_data import derive, read_rows  # noqa: E402
from statistics_project import DEFAULT_SOURCE  # noqa: E402
from xlsx_preview import prepare_xlsx  # noqa: E402

GITHUB_API = "https://api.github.com"
MAX_XLSX_BYTES = 15 * 1024 * 1024


@dataclass(frozen=True)
class Settings:
    client_id: str
    client_secret: str
    session_secret: str
    repository: str = "nicocoquet/mosar"
    pages_url: str = "https://nicocoquet.github.io/mosar/"
    allowed_users: tuple[str, ...] = ("nicocoquet",)

    @classmethod
    def from_environment(cls) -> "Settings":
        secret = os.getenv("SESSION_SECRET", "")
        if len(secret) < 32:
            raise RuntimeError("SESSION_SECRET doit contenir au moins 32 caractères.")
        return cls(
            client_id=os.getenv("GITHUB_CLIENT_ID", ""),
            client_secret=os.getenv("GITHUB_CLIENT_SECRET", ""),
            session_secret=secret,
            repository=os.getenv("GITHUB_REPOSITORY", "nicocoquet/mosar"),
            pages_url=os.getenv("PAGES_URL", "https://nicocoquet.github.io/mosar/"),
            allowed_users=tuple(u.strip().lower() for u in os.getenv("ALLOWED_USERS", "nicocoquet").split(",") if u.strip()),
        )


class Upload(BaseModel):
    filename: str
    content: str  # base64


class Confirmation(Upload):
    preview_token: str


class SessionStore:
    def __init__(self):
        self.sessions: dict[str, dict[str, Any]] = {}

    def create(self, login: str, token: str) -> str:
        key = secrets.token_urlsafe(32)
        self.sessions[key] = {"login": login, "token": token, "expires": time.time() + 8 * 3600}
        return key

    def get(self, key: str) -> dict[str, Any] | None:
        session = self.sessions.get(key)
        if session and session["expires"] > time.time():
            return session
        self.sessions.pop(key, None)
        return None

    def delete(self, key: str) -> None:
        self.sessions.pop(key, None)


def sign(data: dict[str, Any], secret: str) -> str:
    body = base64.urlsafe_b64encode(json.dumps(data, sort_keys=True, separators=(",", ":")).encode()).decode().rstrip("=")
    mac = hmac.new(secret.encode(), body.encode(), hashlib.sha256).hexdigest()
    return body + "." + mac


def verify(token: str, secret: str) -> dict[str, Any]:
    try:
        body, mac = token.split(".")
        expected = hmac.new(secret.encode(), body.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(mac, expected):
            raise ValueError
        payload = json.loads(base64.urlsafe_b64decode(body + "=" * (-len(body) % 4)))
        if not isinstance(payload, dict) or payload.get("exp", 0) <= time.time():
            raise ValueError
        return payload
    except (ValueError, TypeError, KeyError, json.JSONDecodeError) as exc:
        raise HTTPException(400, "Jeton invalide ou expiré.") from exc


def decode_upload(upload: Upload) -> bytes:
    if not upload.filename.lower().endswith(".xlsx") or Path(upload.filename).name != upload.filename or "\\" in upload.filename:
        raise HTTPException(400, "Nom de fichier XLSX invalide.")
    if len(upload.content) > ((MAX_XLSX_BYTES + 2) // 3) * 4 + 8:
        raise HTTPException(413, "Classeur trop volumineux (15 Mo maximum).")
    try:
        data = base64.b64decode(upload.content, validate=True)
    except (ValueError, base64.binascii.Error) as exc:
        raise HTTPException(400, "Encodage base64 invalide.") from exc
    if not data or len(data) > MAX_XLSX_BYTES:
        raise HTTPException(413, "Classeur vide ou trop volumineux.")
    return data


async def github_request(method: str, path: str, token: str, **kwargs: Any) -> Any:
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.request(
            method, GITHUB_API + path,
            headers={"Accept": "application/vnd.github+json", "Authorization": f"Bearer {token}", "X-GitHub-Api-Version": "2022-11-28"},
            **kwargs,
        )
    if response.status_code >= 400:
        raise HTTPException(response.status_code, "GitHub a refusé l'opération.")
    return response.json() if response.content else {}


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or Settings.from_environment()
    if len(settings.session_secret) < 32:
        raise RuntimeError("SESSION_SECRET trop court.")
    config = load_config()
    sessions = SessionStore()
    oauth_states: dict[str, float] = {}
    app = FastAPI(title="Administration Mosar", docs_url=None, redoc_url=None)
    pages = urlparse(settings.pages_url)
    origin = f"{pages.scheme}://{pages.netloc}"
    app.add_middleware(CORSMiddleware, allow_origins=[origin], allow_credentials=False, allow_methods=["GET", "POST"], allow_headers=["Authorization", "Content-Type"])

    def authenticated(authorization: str = Header(default="")) -> dict[str, Any]:
        if not authorization.startswith("Bearer "):
            raise HTTPException(401, "Connexion GitHub requise.")
        session = sessions.get(authorization[7:].strip())
        if session is None:
            raise HTTPException(401, "Session absente ou expirée.")
        return session

    def preview(upload: Upload):
        data = decode_upload(upload)
        try:
            result = prepare_xlsx(
                data,
                sheet=config["data"]["sheet"],
                allowed_columns=set(config["privacy"]["allowed_columns"]),
                forbidden_columns=set(config["privacy"]["forbidden_columns"]),
            )
            # Valider exclusivement le classeur assaini, identique à celui publié.
            # Le moteur statistique attend un chemin XLSX ; le fichier temporaire
            # est supprimé automatiquement, y compris en cas d'erreur.
            with tempfile.TemporaryDirectory(prefix="mosar-preview-") as directory:
                xlsx = Path(directory) / "recensement.xlsx"
                xlsx.write_bytes(result.content)
                source = replace(DEFAULT_SOURCE, xlsx=xlsx)
                statistics = derive(read_rows(source), source)
                # Vérifier aussi la construction des deux pages, sans les écrire.
                for lang in ("fr", "en"):
                    build(statistics, lang)
            return result
        except (ValueError, SystemExit) as exc:
            raise HTTPException(422, f"Classeur non publiable : {exc}") from exc

    @app.get("/health")
    async def health():
        return {"status": "ok"}

    def admin_destination(return_to: str) -> str:
        """Allow only the two published admin pages, without query or fragment."""
        base = settings.pages_url.rstrip("/") + "/"
        allowed = {base + "admin/", base + "en/admin/"}
        parsed = urlparse(return_to)
        if parsed.scheme != "https" or parsed.query or parsed.fragment or parsed.params:
            raise HTTPException(400, "Adresse de retour non autorisée.")
        if return_to not in allowed:
            raise HTTPException(400, "Adresse de retour non autorisée.")
        return return_to

    @app.get("/auth/github")
    async def login(returnTo: str = Query(default="")):  # noqa: N803
        if not settings.client_id or not settings.client_secret:
            raise HTTPException(503, "OAuth GitHub non configuré.")
        destination = admin_destination(returnTo or settings.pages_url.rstrip("/") + "/admin/")
        now = time.time()
        # In-memory one-use states; no external persistence required on a single worker.
        for expired, deadline in list(oauth_states.items()):
            if deadline <= now:
                oauth_states.pop(expired, None)
        nonce = secrets.token_urlsafe(32)
        oauth_states[nonce] = now + 600
        state = sign({"returnTo": destination, "nonce": nonce, "exp": now + 600}, settings.session_secret)
        return RedirectResponse("https://github.com/login/oauth/authorize?" + urlencode({"client_id": settings.client_id, "state": state, "scope": "public_repo"}))

    @app.get("/auth/callback")
    async def callback(code: str, state: str):
        payload = verify(state, settings.session_secret)
        nonce = payload.get("nonce")
        if not isinstance(nonce, str) or oauth_states.pop(nonce, 0) <= time.time():
            raise HTTPException(400, "Connexion expirée ou déjà utilisée.")
        destination = admin_destination(str(payload.get("returnTo", "")))
        if not settings.client_id or not settings.client_secret:
            raise HTTPException(503, "OAuth GitHub non configuré.")
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post("https://github.com/login/oauth/access_token", headers={"Accept": "application/json"}, data={"client_id": settings.client_id, "client_secret": settings.client_secret, "code": code})
            response.raise_for_status()
            token = response.json().get("access_token")
        if not token:
            raise HTTPException(401, "GitHub n'a pas autorisé la connexion.")
        user = await github_request("GET", "/user", token)
        name = user["login"].lower()
        if name not in settings.allowed_users:
            raise HTTPException(403, "Compte GitHub non autorisé.")
        key = sessions.create(name, token)
        return RedirectResponse(destination + "#session=" + key, status_code=303)

    @app.post("/auth/logout")
    async def logout(authorization: str = Header(default=""), user: dict = Depends(authenticated)):
        sessions.delete(authorization[7:].strip())
        return {"status": "logged_out"}

    @app.get("/auth/session")
    async def session_info(user: dict = Depends(authenticated)):
        return {"user": {"login": user["login"]}}

    @app.post("/api/preview")
    async def preview_endpoint(upload: Upload, user: dict = Depends(authenticated)):
        result = preview(upload)
        digest = hashlib.sha256(decode_upload(upload)).hexdigest()
        token = sign({"digest": digest, "login": user["login"], "exp": time.time() + 15 * 60}, settings.session_secret)
        return {"report": result.report, "preview_token": token, "expires_in": 900}

    @app.post("/api/publish")
    async def publish(upload: Confirmation, user: dict = Depends(authenticated)):
        token = verify(upload.preview_token, settings.session_secret)
        if token.get("login") != user["login"]:
            raise HTTPException(403, "Prévisualisation associée à un autre compte.")
        result = preview(upload)
        if not hmac.compare_digest(hashlib.sha256(decode_upload(upload)).hexdigest(), str(token.get("digest", ""))):
            raise HTTPException(409, "Le classeur diffère de la prévisualisation : recommencez.")
        owner_repo = settings.repository.split("/")
        if len(owner_repo) != 2:
            raise HTTPException(500, "Configuration GitHub invalide.")
        path = config["data"]["file"].lstrip("/")
        endpoint = f"/repos/{owner_repo[0]}/{owner_repo[1]}/contents/{path}"
        current = await github_request("GET", endpoint, user["token"], params={"ref": "main"})
        if not current.get("sha"):
            raise HTTPException(409, "Version du classeur introuvable dans GitHub.")
        saved = await github_request("PUT", endpoint, user["token"], json={
            "message": f"data: actualiser le recensement Mosar ({user['login']})",
            "content": base64.b64encode(result.content).decode(),
            "sha": current["sha"],
            "branch": "main",
        })
        commit_sha = saved["commit"]["sha"]
        return {"status": "submitted", "commit_sha": commit_sha, "report": result.report, "job_token": sign({"sha": commit_sha, "login": user["login"], "exp": time.time() + 86400}, settings.session_secret)}

    @app.get("/api/jobs/{job_token}")
    async def job_status(job_token: str, user: dict = Depends(authenticated)):
        job = verify(job_token, settings.session_secret)
        if job.get("login") != user["login"]:
            raise HTTPException(403, "Publication associée à un autre compte.")
        owner, repo = settings.repository.split("/", 1)
        runs = await github_request("GET", f"/repos/{owner}/{repo}/actions/workflows/deploy.yml/runs", user["token"], params={"head_sha": job["sha"], "per_page": 1})
        if not runs.get("workflow_runs"):
            return {"status": "queued", "stages": []}
        run = runs["workflow_runs"][0]
        jobs = await github_request(
            "GET", f"/repos/{owner}/{repo}/actions/runs/{run['id']}/jobs",
            user["token"], params={"per_page": 100},
        )
        steps = [
            {"name": step.get("name", ""), "status": step.get("status", ""),
             "conclusion": step.get("conclusion")}
            for action_job in jobs.get("jobs", [])
            for step in action_job.get("steps", [])
        ]
        response = {"status": "processing", "workflow_url": run["html_url"],
                    "stages": steps}
        if run["status"] == "completed":
            response["status"] = "completed" if run["conclusion"] == "success" else "failed"
            if response["status"] == "completed":
                response["site_url"] = settings.pages_url
            else:
                response["error_steps"] = [
                    step["name"] for step in steps if step["conclusion"] == "failure"
                ]
        return response

    # Uniquement pour les tests : aucune route exposée.
    app.state.sessions = sessions
    return app


app = create_app() if os.getenv("MOSAR_SERVICE_AUTOSTART") == "1" else None

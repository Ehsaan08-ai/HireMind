import os
import logging
from pathlib import Path
from typing import Any, Dict
import streamlit as st
from supabase import Client, create_client

logger = logging.getLogger("ats_resume_scorer")


try:
    from dotenv import load_dotenv

    load_dotenv(Path(__file__).resolve().parents[2] / ".env")
except ImportError:
    pass


def _secret(key: str, section: str = "supabase") -> str:
    """Read from .env first, then fallback to st.secrets[section][key]."""
    val = os.getenv(key, "")
    if val:
        return val
    try:
        return st.secrets[section][key]
    except (KeyError, FileNotFoundError, AttributeError):
        return ""


SUPABASE_URL = _secret("SUPABASE_URL")
SUPABASE_ANON_KEY = _secret("SUPABASE_ANON_KEY")


OAUTH_REDIRECT_URL = (
    os.getenv("AUTH_REDIRECT_URL")
    or _secret("redirect_uri", "google_oauth")
    or "http://localhost:8501"
)


def _missing_config() -> str | None:
    if not SUPABASE_URL or not SUPABASE_ANON_KEY:
        return "Supabase is not configured - set SUPABASE_URL and SUPABASE_ANON_KEY in .env or .streamlit/secrets.toml"
    return None


@st.cache_resource
def get_client() -> Client | None:
    if _missing_config():
        return None
    return create_client(SUPABASE_URL, SUPABASE_ANON_KEY)


def _session_dict(session, user) -> Dict[str, Any]:
    return {
        "access_token": session.access_token,
        "refresh_token": session.refresh_token,
        "user_id": user.id,
        "email": user.email,
    }


def sign_in_with_password(email: str, password: str) -> Dict[str, Any]:
    err = _missing_config()
    if err:
        return {"error": err}
    try:
        resp = get_client().auth.sign_in_with_password(
            {"email": email, "password": password}
        )
        if not resp.session or not resp.user:
            return {"error": "Invalid credentials"}
        return _session_dict(resp.session, resp.user)
    except Exception as exc:
        logger.warning(f"sign_in_with_password failed: {exc}")
        return {"error": _humanize(exc)}


def sign_up_with_password(email: str, password: str) -> Dict[str, Any]:
    err = _missing_config()
    if err:
        return {"error": err}
    try:
        resp = get_client().auth.sign_up({"email": email, "password": password})
        if resp.session and resp.user:
            return _session_dict(resp.session, resp.user)
        if resp.user:
            return {"pending_confirmation": True, "email": email}
        return {"error": "Sign-up failed"}
    except Exception as exc:
        logger.warning(f"sign_up failed: {exc}")
        return {"error": _humanize(exc)}


def google_oauth_url() -> Dict[str, Any]:
    err = _missing_config()
    if err:
        return {"error": err}
    try:
        client = get_client()
        resp = client.auth.sign_in_with_oauth(
            {
                "provider": "google",
                "options": {"redirect_to": OAUTH_REDIRECT_URL},
            }
        )
        
        # Retrieve the generated code_verifier
        storage_key = f"{client.auth._storage_key}-code-verifier"
        code_verifier = client.auth._storage.get_item(storage_key) or ""
        
        # Append code_verifier to redirect_to so it survives the full redirect
        if code_verifier and resp.url:
            import urllib.parse
            parsed = urllib.parse.urlparse(resp.url)
            query_params = urllib.parse.parse_qs(parsed.query)
            if "redirect_to" in query_params:
                original_redirect = query_params["redirect_to"][0]
                separator = "&" if "?" in original_redirect else "?"
                new_redirect = f"{original_redirect}{separator}code_verifier={code_verifier}"
                query_params["redirect_to"] = [new_redirect]
            
            # Rebuild the final authorization URL
            new_query = urllib.parse.urlencode(query_params, doseq=True)
            return {"url": urllib.parse.urlunparse(parsed._replace(query=new_query))}
            
        return {"url": resp.url}
    except Exception as exc:
        logger.warning(f"oauth url generation failed: {exc}")
        return {"error": _humanize(exc)}


def exchange_code_for_session(auth_code: str, code_verifier: str = None) -> Dict[str, Any]:
    """Called once after the OAuth provider redirects back with `?code=...`."""
    err = _missing_config()
    if err:
        return {"error": err}
    client = get_client()
    try:
        # Fallback to local storage if not explicitly provided
        if not code_verifier:
            storage_key = f"{client.auth._storage_key}-code-verifier"
            code_verifier = client.auth._storage.get_item(storage_key) or ""
            
        # Reconstruct the exact same redirect_to URL passed during sign-in
        redirect_to = OAUTH_REDIRECT_URL
        if code_verifier:
            separator = "&" if "?" in OAUTH_REDIRECT_URL else "?"
            redirect_to = f"{OAUTH_REDIRECT_URL}{separator}code_verifier={code_verifier}"
            
        resp = client.auth.exchange_code_for_session(
            {
                "auth_code": auth_code,
                "code_verifier": code_verifier,
                "redirect_to": redirect_to,
            }
        )
        if not resp.session or not resp.user:
            return {"error": "OAuth exchange returned no session"}
        return _session_dict(resp.session, resp.user)
    except Exception as exc:
        logger.warning(f"exchange_code_for_session failed: {exc}")
        return {"error": _humanize(exc)}


def sign_out() -> None:
    if _missing_config():
        return
    try:
        get_client().auth.sign_out()
    except Exception as exc:
        logger.warning(f"sign_out failed: {exc}")


def _humanize(exc: Exception) -> str:
    msg = str(exc)
    # supabase errors arrive as "<status>: {json blob}" — surface the human bit
    if "invalid_grant" in msg.lower() or "invalid login" in msg.lower():
        return "Wrong email or password"
    if (
        "user already registered" in msg.lower()
        or "already been registered" in msg.lower()
    ):
        return "An account with this email already exists — try signing in"
    if "password should be at least" in msg.lower():
        return "Password too short (Supabase default is 6 characters)"
    return msg

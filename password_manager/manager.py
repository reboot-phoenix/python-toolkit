"""
Password Manager - Core Module
Handles secure password generation, storage, and retrieval.
"""

import json
import os
import secrets
import string
import base64
from pathlib import Path
from datetime import datetime
from typing import Optional

try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    from cryptography.hazmat.primitives import hashes
    ENCRYPTION_AVAILABLE = True
except ImportError:
    ENCRYPTION_AVAILABLE = False


VAULT_FILE = Path.home() / ".pytoolkit_vault.json"
SALT_FILE = Path.home() / ".pytoolkit_salt"


def _derive_key(master_password: str, salt: bytes) -> bytes:
    """Derive a Fernet-compatible encryption key from a master password."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=480_000,
    )
    return base64.urlsafe_b64encode(kdf.derive(master_password.encode()))


def _get_or_create_salt() -> bytes:
    """Load existing salt or generate a new one."""
    if SALT_FILE.exists():
        return SALT_FILE.read_bytes()
    salt = os.urandom(16)
    SALT_FILE.write_bytes(salt)
    return salt


def generate_password(
    length: int = 16,
    use_letters: bool = True,
    use_digits: bool = True,
    use_symbols: bool = True,
    exclude_ambiguous: bool = False,
) -> str:
    """
    Generate a cryptographically secure password.

    Args:
        length: Desired password length (min 8).
        use_letters: Include uppercase and lowercase letters.
        use_digits: Include numeric digits.
        use_symbols: Include special characters.
        exclude_ambiguous: Exclude characters like 0, O, l, 1 that look similar.

    Returns:
        A randomly generated password string.

    Raises:
        ValueError: If no character sets are selected or length < 8.
    """
    if length < 8:
        raise ValueError("Password length must be at least 8 characters.")

    pool = ""
    required_chars: list[str] = []

    ambiguous = set("0O1lI|`")

    if use_letters:
        chars = string.ascii_letters
        if exclude_ambiguous:
            chars = "".join(c for c in chars if c not in ambiguous)
        pool += chars
        required_chars.append(secrets.choice(chars))

    if use_digits:
        chars = string.digits
        if exclude_ambiguous:
            chars = "".join(c for c in chars if c not in ambiguous)
        pool += chars
        required_chars.append(secrets.choice(chars))

    if use_symbols:
        chars = string.punctuation
        if exclude_ambiguous:
            chars = "".join(c for c in chars if c not in ambiguous)
        pool += chars
        required_chars.append(secrets.choice(chars))

    if not pool:
        raise ValueError("At least one character set must be selected.")

    # Fill the rest of the password, then shuffle to avoid predictable positions
    remaining = [secrets.choice(pool) for _ in range(length - len(required_chars))]
    password_list = required_chars + remaining
    secrets.SystemRandom().shuffle(password_list)
    return "".join(password_list)


def password_strength(password: str) -> dict:
    """
    Evaluate the strength of a password.

    Returns a dict with keys: score (0-4), label, and suggestions.
    """
    score = 0
    suggestions = []

    if len(password) >= 12:
        score += 1
    else:
        suggestions.append("Use at least 12 characters.")

    if any(c.isupper() for c in password) and any(c.islower() for c in password):
        score += 1
    else:
        suggestions.append("Mix uppercase and lowercase letters.")

    if any(c.isdigit() for c in password):
        score += 1
    else:
        suggestions.append("Add numbers.")

    if any(c in string.punctuation for c in password):
        score += 1
    else:
        suggestions.append("Add special characters (!@#$...).")

    labels = {0: "Very Weak", 1: "Weak", 2: "Fair", 3: "Strong", 4: "Very Strong"}
    return {"score": score, "label": labels[score], "suggestions": suggestions}


class PasswordVault:
    """
    Encrypted local password vault backed by a JSON file.

    Passwords are encrypted with Fernet (AES-128-CBC + HMAC-SHA256)
    using a key derived from the user's master password via PBKDF2.
    """

    def __init__(self, master_password: str):
        if not ENCRYPTION_AVAILABLE:
            raise RuntimeError(
                "Install 'cryptography' to use the vault: pip install cryptography"
            )
        salt = _get_or_create_salt()
        key = _derive_key(master_password, salt)
        self._fernet = Fernet(key)
        self._vault: dict = self._load()

    # ------------------------------------------------------------------ #
    # Private helpers                                                       #
    # ------------------------------------------------------------------ #

    def _load(self) -> dict:
        if not VAULT_FILE.exists():
            return {}
        try:
            raw = json.loads(VAULT_FILE.read_text())
            return raw
        except (json.JSONDecodeError, OSError):
            return {}

    def _save(self) -> None:
        VAULT_FILE.write_text(json.dumps(self._vault, indent=2))

    def _encrypt(self, plaintext: str) -> str:
        return self._fernet.encrypt(plaintext.encode()).decode()

    def _decrypt(self, token: str) -> str:
        return self._fernet.decrypt(token.encode()).decode()

    # ------------------------------------------------------------------ #
    # Public API                                                            #
    # ------------------------------------------------------------------ #

    def add(self, service: str, username: str, password: str, notes: str = "") -> None:
        """Store a new credential. Overwrites any existing entry for the service."""
        self._vault[service.lower()] = {
            "username": username,
            "password": self._encrypt(password),
            "notes": notes,
            "created_at": datetime.now().isoformat(timespec="seconds"),
        }
        self._save()

    def get(self, service: str) -> Optional[dict]:
        """Retrieve and decrypt a credential by service name."""
        entry = self._vault.get(service.lower())
        if entry is None:
            return None
        return {
            "service": service,
            "username": entry["username"],
            "password": self._decrypt(entry["password"]),
            "notes": entry.get("notes", ""),
            "created_at": entry.get("created_at", "unknown"),
        }

    def delete(self, service: str) -> bool:
        """Remove a credential. Returns True if it existed."""
        existed = service.lower() in self._vault
        self._vault.pop(service.lower(), None)
        if existed:
            self._save()
        return existed

    def list_services(self) -> list[str]:
        """Return all stored service names."""
        return sorted(self._vault.keys())

    def search(self, query: str) -> list[str]:
        """Return service names that contain the query string (case-insensitive)."""
        q = query.lower()
        return [s for s in self._vault if q in s]

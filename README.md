# Python Toolkit

A collection of command-line tools built in pure Python, demonstrating secure
cryptography, OOP design, CLI architecture, and clean code practices.

---

## Features

| Module | What it does | Key concepts |
|---|---|---|
| `password_manager` | Generate & store passwords in an encrypted local vault | `cryptography`, PBKDF2, Fernet AES, `argparse`, `getpass` |
| `games` | Number guessing game with difficulty, scoring & hints | Dataclasses, game loops, terminal UI |
| `utils` | Reusable helpers: slugify, clamp, chunk, flatten | Pure functions, type hints, docstrings |

---

## Quickstart

```bash
# Clone and set up
git clone https://github.com/your-username/python-toolkit.git
cd python-toolkit
pip install -r requirements.txt
```

---

## Password Manager

### Generate a password

```bash
python -m password_manager generate
python -m password_manager generate --length 24
python -m password_manager generate --length 20 --no-symbols
python -m password_manager generate --exclude-ambiguous
```

Example output:
```
Generated password:
  qR7#mKv2$Lp9nWxE

Strength: Very Strong (4/4)
```

### Store credentials in the encrypted vault

```bash
# Add a new entry (prompts for master password)
python -m password_manager add github --username alice@example.com

# Auto-generate and store a password in one step
python -m password_manager add netflix --username alice@example.com --generate
```

### Retrieve credentials

```bash
python -m password_manager get github
python -m password_manager list
python -m password_manager delete github
```

### How encryption works

1. On first use, a random 16-byte **salt** is stored at `~/.pytoolkit_salt`.
2. Your master password is hashed with **PBKDF2-HMAC-SHA256** (480,000 iterations) to produce a 256-bit key.
3. Each password is encrypted individually with **Fernet** (AES-128-CBC + HMAC-SHA256) before being written to `~/.pytoolkit_vault.json`.

Your master password is **never stored** — only the derived key is used in-memory during a session.

---

## Number Guessing Game

```bash
python -m games.guessing_game
```

Features:
- Three difficulty levels (Easy / Medium / Hard)
- Visual progress bar showing remaining attempts
- Context-sensitive hints (hot/warm/cold, parity, range)
- Score system rewarding speed, accuracy, and hint frugality
- Session statistics (win rate, best score, average score)

---

## Utilities

```python
from utils import slugify, clamp, truncate, chunk, flatten

slugify("Hello, World!")       # → "hello-world"
clamp(15, 0, 10)               # → 10
truncate("long string...", 10) # → "long str…"
chunk([1, 2, 3, 4, 5], 2)      # → [[1, 2], [3, 4], [5]]
flatten([1, [2, [3, [4]]]])    # → [1, 2, 3, 4]
```

---

## Running Tests

```bash
python -m pytest tests/ -v
```

All tests are in `tests/` and cover edge cases for password generation,
strength evaluation, and utility functions.

---

## Project Structure

```
python-toolkit/
├── password_manager/
│   ├── __init__.py
│   ├── manager.py      # Core: generate, evaluate, vault CRUD
│   └── cli.py          # argparse CLI entry point
├── games/
│   ├── __init__.py
│   └── guessing_game.py
├── utils/
│   ├── __init__.py
│   └── helpers.py
├── tests/
│   ├── test_password_manager.py
│   └── test_utils.py
├── requirements.txt
└── README.md
```

---

## Design Decisions

- **`secrets` module over `random`** — `random` is not cryptographically secure;
  `secrets.choice` uses the OS CSPRNG.
- **PBKDF2 with 480k iterations** — OWASP 2023 recommendation for PBKDF2-HMAC-SHA256.
- **Fernet for symmetric encryption** — provides authenticated encryption;
  tampered ciphertext raises an exception rather than silently decrypting garbage.
- **Salt stored separately** — allows key re-derivation across sessions without
  embedding the salt inside the vault file where it could be easily observed.

---

## License

MIT

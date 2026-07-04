<h1 align="center">🐍 Python Toolkit</h1>

<p align="center">CLI tools built in pure Python — cryptography, OOP design, and clean code practices.</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12-blue?style=flat-square&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/Tests-32%20passing-brightgreen?style=flat-square"/>
  <img src="https://img.shields.io/badge/Encryption-AES--128--CBC-orange?style=flat-square"/>
  <img src="https://img.shields.io/badge/License-MIT-lightgrey?style=flat-square"/>
</p>

---

## What's inside

| Module | Description | Key concepts |
|---|---|---|
| 🔐 `password_manager` | Generate & store passwords in an encrypted local vault | PBKDF2, Fernet AES, `argparse`, `getpass` |
| 🎮 `games` | Number guessing game with difficulty levels & scoring | Dataclasses, game loops, terminal UI |
| 🛠️ `utils` | Reusable helpers — slugify, clamp, chunk, flatten | Type hints, pure functions, docstrings |

---

## Quickstart

```bash
git clone https://github.com/reboot-phoenix/python-toolkit.git
cd python-toolkit
pip install -r requirements.txt
```

---

## Password manager

```bash
# Generate a password
python -m password_manager generate --length 20

# Save credentials to an encrypted vault
python -m password_manager add github --username you@email.com --generate

# Retrieve, list, or delete
python -m password_manager get github
python -m password_manager list
python -m password_manager delete github
```

> Your master password is never stored — only used in-memory to derive the AES key via PBKDF2-HMAC-SHA256 (480k iterations).

---

## Number guessing game

```bash
python -m games.guessing_game
```

Three difficulty levels, a visual progress bar, hot/warm/cold hints (costs points), and session stats across rounds.

---

## Utils

```python
from utils import slugify, clamp, truncate, chunk, flatten

slugify("Hello, World!")       # → "hello-world"
clamp(15, 0, 10)               # → 10
chunk([1, 2, 3, 4, 5], 2)      # → [[1, 2], [3, 4], [5]]
flatten([1, [2, [3, [4]]]])    # → [1, 2, 3, 4]
```

---

## Tests

```bash
python -m pytest tests/ -v
# 32 passed in 0.04s
```

---

## Structure

```
python-toolkit/
├── password_manager/
│   ├── manager.py     # generate, evaluate, vault CRUD
│   └── cli.py         # argparse CLI
├── games/
│   └── guessing_game.py
├── utils/
│   └── helpers.py
├── tests/
│   ├── test_password_manager.py
│   └── test_utils.py
├── requirements.txt
└── README.md
```

---

## Design notes

- **`secrets` over `random`** — uses the OS CSPRNG, not a PRNG
- **PBKDF2 at 480k iterations** — OWASP 2023 recommendation
- **Fernet encryption** — authenticated AES; tampered ciphertext raises, never silently decrypts garbage
- **Salt stored separately** — never embedded in the vault file

---

MIT License

"""
Password Manager CLI
====================
A command-line interface for generating and securely storing passwords.

Usage examples:
    python -m password_manager generate --length 20 --no-symbols
    python -m password_manager add github --username alice
    python -m password_manager get github
    python -m password_manager list
    python -m password_manager delete github
"""

import argparse
import getpass
import sys

from .manager import generate_password, password_strength, PasswordVault, ENCRYPTION_AVAILABLE


# ─── Colours (degrades gracefully on Windows without colorama) ─── #

GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"


def _strength_colour(label: str) -> str:
    colours = {
        "Very Weak": RED,
        "Weak": RED,
        "Fair": YELLOW,
        "Strong": GREEN,
        "Very Strong": GREEN,
    }
    return colours.get(label, RESET)


def _print_entry(entry: dict) -> None:
    print(f"\n{BOLD}Service  :{RESET} {entry['service']}")
    print(f"{BOLD}Username :{RESET} {entry['username']}")
    print(f"{BOLD}Password :{RESET} {CYAN}{entry['password']}{RESET}")
    if entry.get("notes"):
        print(f"{BOLD}Notes    :{RESET} {entry['notes']}")
    print(f"{BOLD}Saved    :{RESET} {entry['created_at']}\n")


# ─── Sub-command handlers ─── #

def cmd_generate(args: argparse.Namespace) -> None:
    try:
        password = generate_password(
            length=args.length,
            use_letters=not args.no_letters,
            use_digits=not args.no_digits,
            use_symbols=not args.no_symbols,
            exclude_ambiguous=args.exclude_ambiguous,
        )
    except ValueError as exc:
        print(f"{RED}Error:{RESET} {exc}", file=sys.stderr)
        sys.exit(1)

    strength = password_strength(password)
    colour = _strength_colour(strength["label"])

    print(f"\n{BOLD}Generated password:{RESET}")
    print(f"  {CYAN}{password}{RESET}")
    print(f"\n{BOLD}Strength:{RESET} {colour}{strength['label']}{RESET} ({strength['score']}/4)")

    if strength["suggestions"]:
        print(f"{YELLOW}Tips:{RESET}")
        for tip in strength["suggestions"]:
            print(f"  • {tip}")
    print()


def cmd_add(args: argparse.Namespace) -> None:
    if not ENCRYPTION_AVAILABLE:
        print(f"{RED}Vault unavailable:{RESET} run  pip install cryptography", file=sys.stderr)
        sys.exit(1)

    master = getpass.getpass("Master password: ")
    vault = PasswordVault(master)

    username = args.username or input("Username / email: ").strip()

    if args.generate:
        password = generate_password()
        print(f"  Generated: {CYAN}{password}{RESET}")
    else:
        password = getpass.getpass("Password to store: ")

    notes = args.notes or ""
    vault.add(args.service, username, password, notes)
    print(f"{GREEN}✓ Saved credentials for '{args.service}'.{RESET}\n")


def cmd_get(args: argparse.Namespace) -> None:
    if not ENCRYPTION_AVAILABLE:
        print(f"{RED}Vault unavailable.{RESET}", file=sys.stderr)
        sys.exit(1)

    master = getpass.getpass("Master password: ")
    vault = PasswordVault(master)

    entry = vault.get(args.service)
    if entry is None:
        print(f"{YELLOW}No entry found for '{args.service}'.{RESET}")
        # suggest similar
        suggestions = vault.search(args.service)
        if suggestions:
            print("Did you mean:", ", ".join(suggestions))
        sys.exit(1)

    _print_entry(entry)


def cmd_list(args: argparse.Namespace) -> None:
    if not ENCRYPTION_AVAILABLE:
        print(f"{RED}Vault unavailable.{RESET}", file=sys.stderr)
        sys.exit(1)

    master = getpass.getpass("Master password: ")
    vault = PasswordVault(master)

    services = vault.list_services()
    if not services:
        print(f"{YELLOW}Your vault is empty.{RESET}")
        return

    print(f"\n{BOLD}Stored services ({len(services)}):{RESET}")
    for s in services:
        print(f"  • {s}")
    print()


def cmd_delete(args: argparse.Namespace) -> None:
    if not ENCRYPTION_AVAILABLE:
        print(f"{RED}Vault unavailable.{RESET}", file=sys.stderr)
        sys.exit(1)

    master = getpass.getpass("Master password: ")
    vault = PasswordVault(master)

    confirm = input(f"Delete credentials for '{args.service}'? (yes/no): ").strip().lower()
    if confirm != "yes":
        print("Aborted.")
        return

    if vault.delete(args.service):
        print(f"{GREEN}✓ Deleted '{args.service}'.{RESET}")
    else:
        print(f"{YELLOW}No entry found for '{args.service}'.{RESET}")


# ─── Argument parser ─── #

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="password_manager",
        description="Secure password generator and encrypted vault.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # generate
    gen = sub.add_parser("generate", aliases=["gen"], help="Generate a strong password.")
    gen.add_argument("-l", "--length", type=int, default=16, metavar="N",
                     help="Password length (default: 16).")
    gen.add_argument("--no-letters", action="store_true", help="Exclude letters.")
    gen.add_argument("--no-digits", action="store_true", help="Exclude digits.")
    gen.add_argument("--no-symbols", action="store_true", help="Exclude symbols.")
    gen.add_argument("--exclude-ambiguous", action="store_true",
                     help="Exclude ambiguous chars (0, O, l, 1).")
    gen.set_defaults(func=cmd_generate)

    # add
    add = sub.add_parser("add", help="Add/update a credential in the vault.")
    add.add_argument("service", help="Service name (e.g. github, gmail).")
    add.add_argument("-u", "--username", help="Username or email.")
    add.add_argument("-g", "--generate", action="store_true",
                     help="Auto-generate and store a secure password.")
    add.add_argument("-n", "--notes", help="Optional notes.")
    add.set_defaults(func=cmd_add)

    # get
    get = sub.add_parser("get", help="Retrieve a credential from the vault.")
    get.add_argument("service", help="Service name.")
    get.set_defaults(func=cmd_get)

    # list
    lst = sub.add_parser("list", help="List all stored service names.")
    lst.set_defaults(func=cmd_list)

    # delete
    dlt = sub.add_parser("delete", aliases=["rm"], help="Delete a credential.")
    dlt.add_argument("service", help="Service name to delete.")
    dlt.set_defaults(func=cmd_delete)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()

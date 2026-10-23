"""Controlled, local account-administration CLI.

This is intentionally NOT an HTTP endpoint. Only someone with access to the
server, the backend environment, and the PostgreSQL credentials can approve or
disable accounts.

Run from the backend directory:
    python -m scripts.manage_accounts list --status pending
    python -m scripts.manage_accounts approve --email manager@example.com
    python -m scripts.manage_accounts disable --employee-id REC-001
"""

import argparse
import sys

from sqlalchemy import select
from sqlalchemy.exc import OperationalError

from app.db.session import SessionLocal
from app.models.user import User


def _account_label(account: User) -> str:
    status = "approved" if account.is_approved else "pending"
    active = "active" if account.is_active else "disabled"
    return (
        f"{account.employee_id} | {account.email} | {account.role.value} | "
        f"{account.full_name} | {status} | {active}"
    )


def _find_account(db, email: str | None, employee_id: str | None) -> User | None:
    query = select(User)
    if email:
        query = query.where(User.email == email.strip().lower())
    else:
        query = query.where(User.employee_id == employee_id.strip().upper())
    return db.scalar(query)


def _print_accounts(accounts: list[User]) -> None:
    if not accounts:
        print("No matching accounts.")
        return
    for account in accounts:
        print(_account_label(account))


def list_accounts(status_filter: str) -> int:
    with SessionLocal() as db:
        query = select(User).order_by(User.created_at.asc())
        if status_filter == "pending":
            query = query.where(User.is_approved.is_(False))
        elif status_filter == "approved":
            query = query.where(User.is_approved.is_(True))
        _print_accounts(list(db.scalars(query).all()))
    return 0


def mutate_account(
    action: str, email: str | None, employee_id: str | None
) -> int:
    with SessionLocal() as db:
        account = _find_account(db, email, employee_id)
        if account is None:
            print("Account not found.", file=sys.stderr)
            return 1

        if action == "approve":
            account.is_approved = True
            # An operator may approve an account that was previously disabled;
            # enabling is still a separate, explicit action.
        elif action == "disable":
            account.is_active = False
        elif action == "enable":
            account.is_active = True
        else:  # pragma: no cover - argparse limits choices
            print(f"Unknown action: {action}", file=sys.stderr)
            return 2

        db.commit()
        db.refresh(account)
        print(f"{action}d: {_account_label(account)}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Approve, disable, enable or list StaySmart staff accounts."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser("list", help="List staff accounts.")
    list_parser.add_argument(
        "--status",
        choices=["pending", "approved", "all"],
        default="pending",
        help="Filter accounts (default: pending).",
    )

    for action in ("approve", "disable", "enable"):
        action_parser = subparsers.add_parser(
            action, help=f"{action.capitalize()} one staff account."
        )
        target = action_parser.add_mutually_exclusive_group(required=True)
        target.add_argument("--email", help="Account email address.")
        target.add_argument("--employee-id", help="Account employee ID.")

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    try:
        if args.command == "list":
            return list_accounts(args.status)
        return mutate_account(
            args.command,
            getattr(args, "email", None),
            getattr(args, "employee_id", None),
        )
    except OperationalError:
        print(
            "Could not connect to PostgreSQL. Check DATABASE_URL and that "
            "PostgreSQL is running.",
            file=sys.stderr,
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

"""Append-only transaction ledger kept in a pandas DataFrame (written against pandas 1.5)."""
import pandas as pd

COLUMNS = ["date", "account", "amount", "memo"]


def new_ledger():
    """Return an empty ledger with the standard columns."""
    return pd.DataFrame(columns=COLUMNS)


def add_entry(ledger, date, account, amount, memo=""):
    """Return a new ledger with one entry appended at the end (the input ledger is not modified)."""
    row = {"date": date, "account": account, "amount": amount, "memo": memo}
    return ledger.append(row, ignore_index=True)


def add_entries(ledger, entries):
    """Return a new ledger with every dict in `entries` appended, in order."""
    if not entries:
        return ledger.copy()
    rows = [{c: e.get(c, "" if c == "memo" else None) for c in COLUMNS} for e in entries]
    return ledger.append(rows, ignore_index=True)


def balance(ledger, account=None):
    """Sum of amounts, optionally restricted to one account, as a float."""
    rows = ledger if account is None else ledger[ledger["account"] == account]
    return float(rows["amount"].astype(float).sum())


def running_balance(ledger):
    """Cumulative sum of the amounts in ledger order, as a list of floats."""
    return [float(v) for v in ledger["amount"].astype(float).cumsum()]

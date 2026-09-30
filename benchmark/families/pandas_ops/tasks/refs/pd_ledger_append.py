import pandas as pd


def append_transactions(ledger, transactions):
    out = ledger.drop(columns=["balance"], errors="ignore")
    if transactions:
        out = out.append(transactions, ignore_index=True)
    else:
        out = out.reset_index(drop=True)
    out["balance"] = out["amount"].astype(float).cumsum()
    return out

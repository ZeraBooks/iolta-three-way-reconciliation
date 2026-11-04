"""Three-way reconciliation for an IOLTA or client trust account.

Reads three files for the same month end:
  1. the trust bank statement (opening row, every line, closing row)
  2. the trust journal, the firm's register of every deposit and disbursement
  3. the client ledgers, one running balance per client or matter

It works out the adjusted bank balance (statement closing, plus deposits in
transit, less outstanding checks), totals the journal and the client ledgers,
and says whether all three agree. It also flags any client ledger that is
below zero at month end or at any point during the month, and, when the
client ledgers don't agree with the journal, lists the lines that differ.

Usage:
  python3 three_way_check.py bank-statement-june-2026.csv trust-journal-june-2026.csv client-ledgers-june-2026.csv
Python 3, standard library only.
"""
import csv
import sys
from decimal import Decimal


def d(cell):
    return Decimal(cell.strip().replace(",", "")) if cell and cell.strip() else Decimal("0")


def read(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def key(r):
    return (r["Ref"].strip(), d(r["Amount"]))


def main(bank_path, journal_path, clients_path):
    ok = True

    # 1. Bank statement: opening + lines = closing, then outstanding items.
    bank = read(bank_path)
    opening = closing = None
    bank_lines = []
    for r in bank:
        desc = r["Description"].strip().lower()
        if desc == "opening balance":
            opening = d(r["Amount"])
        elif desc == "closing balance":
            closing = d(r["Amount"])
            close_date = r["Date"]
        else:
            bank_lines.append(r)
    if opening is None or closing is None:
        print("The bank file needs an Opening balance row and a Closing balance row.")
        return False
    if opening + sum(d(r["Amount"]) for r in bank_lines) != closing:
        ok = False
        print("The bank statement lines don't add up from the opening to the closing balance. Check the file first.")

    journal = read(journal_path)
    journal_balance = sum(d(r["Amount"]) for r in journal)
    journal_lines = [r for r in journal if r["Ref"].strip()]

    unmatched_bank = [key(r) for r in bank_lines]
    in_transit, outstanding = [], []
    for r in journal_lines:
        k = key(r)
        if k in unmatched_bank:
            unmatched_bank.remove(k)
        elif d(r["Amount"]) > 0:
            in_transit.append(r)
        else:
            outstanding.append(r)

    adjusted = closing
    print(f"{'Bank: statement closing, ' + close_date:<44}{closing:>12,.2f}")
    for r in in_transit:
        adjusted += d(r["Amount"])
        print(f"{'  add deposit in transit ' + r['Ref'] + ' (' + r['Client'] + ')':<44}{d(r['Amount']):>12,.2f}")
    for r in outstanding:
        adjusted += d(r["Amount"])
        print(f"{'  less outstanding ' + r['Ref'] + ' (' + r['Client'] + ')':<44}{d(r['Amount']):>12,.2f}")
    print(f"{'Adjusted bank balance':<44}{adjusted:>12,.2f}")
    for ref, amt in unmatched_bank:
        ok = False
        print(f"  ** on the statement but not in the journal: {ref or '(no ref)'} {amt:,.2f}")

    print(f"{'Trust journal balance':<44}{journal_balance:>12,.2f}")

    # 3. Client ledgers: total, and any balance below zero.
    clients = read(clients_path)
    by_client = {}
    for r in clients:
        by_client.setdefault(r["Client"].strip(), []).append(r)
    client_total = Decimal("0")
    print("Client ledgers")
    for name, rows in by_client.items():
        running = Decimal("0")
        low = None
        for r in sorted(rows, key=lambda r: r["Date"]):
            running += d(r["Amount"])
            if running < 0 and low is None:
                low = (r["Date"], r["Ref"], running)
        client_total += running
        print(f"{'  ' + name:<44}{running:>12,.2f}")
        if running < 0:
            ok = False
            print(f"  ** {name} is below zero at month end. Another client's money is covering it.")
        elif low:
            ok = False
            print(f"  ** {name} went below zero on {low[0]} ({low[2]:,.2f} after {low[1]}). Totals can agree and this is still wrong.")
    print(f"{'Total of client ledgers':<44}{client_total:>12,.2f}")

    # Compare all three.
    print()
    if adjusted == journal_balance == client_total:
        print(f"All three agree at {adjusted:,.2f}.")
    else:
        ok = False
        print(f"They don't agree: bank {adjusted:,.2f}, journal {journal_balance:,.2f}, clients {client_total:,.2f}.")
        if adjusted == journal_balance:
            print("Bank and journal agree, so look in the client ledgers.")
        elif adjusted == client_total:
            print("Bank and client ledgers agree, so look in the journal.")
        elif journal_balance == client_total:
            print("Journal and client ledgers agree, so look at the bank side: a missed bank line or a wrong outstanding item.")
    jk = [(r["Ref"].strip(), d(r["Amount"]), r["Client"].strip()) for r in journal_lines]
    ck = [(r["Ref"].strip(), d(r["Amount"]), r["Client"].strip()) for r in clients if r["Ref"].strip()]
    for item in list(jk):
        if item in ck:
            ck.remove(item)
            jk.remove(item)
    for ref, amt, client in jk:
        ok = False
        print(f"  In the journal, not on that client's ledger: {ref} {amt:,.2f} ({client})")
    for ref, amt, client in ck:
        ok = False
        print(f"  On a client ledger, not in the journal that way: {ref} {amt:,.2f} ({client})")
    print("All checks pass." if ok else "Some checks failed; see above.")
    return ok


if __name__ == "__main__":
    a = sys.argv[1:] + [None] * 3
    sys.exit(0 if main(a[0] or "bank-statement-june-2026.csv",
                       a[1] or "trust-journal-june-2026.csv",
                       a[2] or "client-ledgers-june-2026.csv") else 1)

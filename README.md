# IOLTA three-way reconciliation

A three-way reconciliation shows that three records of client trust money agree
on one date: the trust bank statement (adjusted for deposits in transit and
outstanding checks), the firm's trust journal, and the total of the client
ledgers. This repo has a template, a fictional law firm's June with four client
matters, and a script that does the three-way check and flags any client ledger
that goes below zero.

## Files

| File | What it is |
|---|---|
| `reconciliation-template.csv` | The layout: bank section, journal balance, one row per client, sign-off. Columns: Record, Item, Amount. |
| `reconciliation-checklist.md` | The monthly steps, from getting the statement in to signing the reconciliation. |
| `bank-statement-june-2026.csv` | A fictional IOLTA statement for June 2026: opening balance, every line, closing balance. |
| `trust-journal-june-2026.csv` | The same firm's trust register for June, with the client on every line. |
| `client-ledgers-june-2026.csv` | One ledger per client: Lopez, Nguyen, Ward and Ostrowski. |
| `client-ledgers-first-pass.csv` | The same ledgers with one refund check never posted, so the total is 150.00 too high. |
| `client-ledgers-misposted.csv` | The same ledgers with a filing fee posted to the wrong client. Totals agree, but one client goes below zero. |
| `three_way_check.py` | Works out the adjusted bank balance, totals the journal and the client ledgers, compares all three, and flags negative client balances and lines that don't match. |

The script is Python 3, standard library only.

## How to use it

1. Export your trust bank statement, trust journal and client ledgers to CSV in
   the same shape as the sample files. A Ref (check number or deposit
   reference) on each line lets the script match the journal to the bank.
2. Run:

   ```
   python3 three_way_check.py bank-statement-june-2026.csv trust-journal-june-2026.csv client-ledgers-june-2026.csv
   ```

   Journal lines with no matching bank line are listed as deposits in transit
   or outstanding checks. Bank lines with no journal line are flagged.
3. Try the two other ledger files to see what a difference and a negative
   client look like:

   ```
   python3 three_way_check.py bank-statement-june-2026.csv trust-journal-june-2026.csv client-ledgers-first-pass.csv
   python3 three_way_check.py bank-statement-june-2026.csv trust-journal-june-2026.csv client-ledgers-misposted.csv
   ```

4. Fill in `reconciliation-template.csv` with the figures, sign it, and keep
   it with the statement.

The script exits with 0 when everything agrees and 1 when something needs a
look.

## The worked month

Brennan Law PLLC is a fictional two-lawyer firm. Its IOLTA statement for June
2026 closes at 48,315.00. On June 30:

| Record | Item | Amount |
|---|---|---|
| Bank | Statement closing balance, June 30 | 48,315.00 |
| Bank | Add: deposit in transit, Lopez retainer | 6,000.00 |
| Bank | Less: check 2214, court reporter for Nguyen | (1,215.00) |
| Bank | Less: check 2216, Ward's share of settlement | (12,500.00) |
| **Bank** | **Adjusted bank balance** | **40,600.00** |
| **Trust journal** | **Register balance, June 30** | **40,600.00** |
| Client ledgers | Lopez | 6,000.00 |
| Client ledgers | Nguyen | 3,785.00 |
| Client ledgers | Ward | 18,315.00 |
| Client ledgers | Ostrowski | 12,500.00 |
| **Client ledgers** | **Total of client ledgers** | **40,600.00** |

All three agree at 40,600.00. The journal opened June at 18,150.00 (Nguyen
5,000.00 and Ostrowski 13,150.00) and June's lines add 22,450.00. The Lopez
retainer was deposited after the bank's cutoff, and checks 2214 and 2216 were
cashed in July. Both checks were taken off the clients' ledgers when they were
written, which is right. Checks 2213 and 2215 were voided and don't appear.

On the first pass (`client-ledgers-first-pass.csv`) the client ledgers came to
40,750.00. Bank and journal agreed, so the error was in the client ledgers. The
150.00 was check 2211, a refund of unused costs to Ostrowski that cleared June
12 but was never posted to her ledger. Posting it brings her to 12,500.00 and
the total to 40,600.00.

In `client-ledgers-misposted.csv` the 500.00 filing fee for Ostrowski was
posted to Lopez. The total still comes to 40,600.00, but Lopez sits at -500.00
from June 5 until her retainer arrives on June 30. For those weeks another
client's money was covering a cost that wasn't Lopez's. The script catches it
because it checks every running balance, not only the month-end total.

The firm, clients and figures are fictional.

## FAQ

### How often do you need to do a three-way reconciliation?

It depends on your state. Many state bars require it monthly and some
quarterly. Check your state bar's trust account rules. Monthly is the safer
habit, because a mistake found a month later is one month of entries to
search, not three.

### What records does a trust account need?

Most state rules are built on ABA Model Rule 1.15, which asks for complete
trust account records kept for five years after the representation ends. In
practice that means the monthly statements, the trust journal, a ledger for
every client and each signed reconciliation. Your state's rule sets the exact
list.

### Does IOLTA interest go in the firm's books?

No. The bank pays it to the state IOLTA program, which funds legal aid. It is
not the firm's income and not a client's money, so it is never booked as
revenue.

## Learn more

Full guide: [IOLTA trust accounting: the three-way reconciliation](https://www.zerabooks.com/iolta-trust-accounting). Related: [Bookkeeping for law firms](https://www.zerabooks.com/bookkeeping-for-law-firms).

## License

The content and data in this repository are licensed under
[CC BY 4.0](LICENSE). Free to use and adapt with credit to ZeraBooks.
The code (`*.py`) is licensed under [MIT](LICENSE-CODE).

Maintained by [ZeraBooks](https://www.zerabooks.com).

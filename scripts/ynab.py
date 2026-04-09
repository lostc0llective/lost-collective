"""
YNAB API — Lost Collective
Budget: FY25/26 Budget (948296e2-9c29-4313-8a30-9ffa26ae598a)

Run via: op run --env-file=.env.tpl -- python3 scripts/ynab.py [command]

Commands:
  audit          — full account + budget overview (default)
  accounts       — account balances and net worth
  budget         — this month's category spending vs budgeted
  transactions   — last 30 days of transactions
  overspent      — categories over budget this month
  cleanup        — delete legacy reconciled/uncleared transactions from ING accounts
                   (fixes Bills/Spending/Saving balances after CSV import)
"""

import os, sys, json, datetime, time, requests
from typing import Optional

# ── Config ─────────────────────────────────────────────────────────────────────

BASE        = "https://api.ynab.com/v1"
TOKEN       = os.environ.get("YNAB_TOKEN", "")
BUDGET_ID   = os.environ.get("YNAB_BUDGET_ID", "")

HEADERS = {"Authorization": f"Bearer {TOKEN}"}


# ── Base client ────────────────────────────────────────────────────────────────

def get(path: str, params: dict = None) -> dict:
    r = requests.get(f"{BASE}{path}", headers=HEADERS, params=params or {})
    r.raise_for_status()
    return r.json()["data"]


def delete_transaction(transaction_id: str) -> bool:
    r = requests.delete(
        f"{BASE}/budgets/{BUDGET_ID}/transactions/{transaction_id}",
        headers=HEADERS,
    )
    return r.status_code in (200, 204)


def milliunits(n: int) -> float:
    """Convert YNAB milliunits to dollars."""
    return n / 1000


def fmt(n: int, prefix: str = "$") -> str:
    """Format milliunits as currency string."""
    val = milliunits(n)
    neg = val < 0
    s = f"{prefix}{abs(val):,.2f}"
    return f"-{s}" if neg else s


# ── API calls ──────────────────────────────────────────────────────────────────

def accounts() -> list[dict]:
    return get(f"/budgets/{BUDGET_ID}/accounts")["accounts"]


def current_month() -> dict:
    today = datetime.date.today().strftime("%Y-%m-01")
    return get(f"/budgets/{BUDGET_ID}/months/{today}")["month"]


def categories() -> list[dict]:
    """Return all category groups with their categories."""
    return get(f"/budgets/{BUDGET_ID}/categories")["category_groups"]


def transactions(since_days: int = 30) -> list[dict]:
    since = (datetime.date.today() - datetime.timedelta(days=since_days)).isoformat()
    return get(f"/budgets/{BUDGET_ID}/transactions", {"since_date": since})["transactions"]


def payees() -> dict[str, str]:
    """Return {payee_id: payee_name} lookup."""
    data = get(f"/budgets/{BUDGET_ID}/payees")["payees"]
    return {p["id"]: p["name"] for p in data}


# ── Display functions ──────────────────────────────────────────────────────────

def show_accounts():
    print("\nAccounts")
    print("─" * 60)

    accs = [a for a in accounts() if not a["deleted"] and not a["closed"]]

    # Group by on_budget vs tracking
    on_budget  = [a for a in accs if a["on_budget"]]
    tracking   = [a for a in accs if not a["on_budget"]]

    total_budget  = sum(a["balance"] for a in on_budget)
    total_net     = sum(a["balance"] for a in accs)

    if on_budget:
        print("  On-budget accounts:")
        for a in sorted(on_budget, key=lambda x: -x["balance"]):
            print(f"    {a['name']:<35} {fmt(a['balance']):>12}")
        print(f"    {'Subtotal':<35} {fmt(total_budget):>12}")

    if tracking:
        print("\n  Tracking accounts:")
        for a in sorted(tracking, key=lambda x: -x["balance"]):
            print(f"    {a['name']:<35} {fmt(a['balance']):>12}")

    print(f"\n  {'Net worth':<35} {fmt(total_net):>12}")


def show_budget():
    month = current_month()

    print(f"\nBudget — {month['month'][:7]}")
    print("─" * 70)
    print(f"  {'Budgeted this month':<40} {fmt(month['budgeted']):>12}")
    print(f"  {'Activity (spent)':<40} {fmt(month['activity']):>12}")
    print(f"  {'To be budgeted':<40} {fmt(month['to_be_budgeted']):>12}")
    print(f"  {'Age of money':<40} {str(month.get('age_of_money') or 'n/a'):>12} days")

    print("\n  Categories:")
    print(f"  {'Category':<38} {'Budgeted':>10} {'Spent':>10} {'Available':>10}")
    print("  " + "─" * 68)

    for group in categories():
        if group["deleted"] or group["hidden"]:
            continue
        active_cats = [
            c for c in group["categories"]
            if not c["deleted"] and not c["hidden"] and c["budgeted"] != 0
        ]
        if not active_cats:
            continue
        print(f"\n  {group['name']}")
        for c in active_cats:
            overspent = c["balance"] < 0
            flag = " !" if overspent else ""
            print(
                f"    {(c['name'] + flag):<36} "
                f"{fmt(c['budgeted']):>10} "
                f"{fmt(c['activity']):>10} "
                f"{fmt(c['balance']):>10}"
            )


def show_overspent():
    print("\nOverspent categories this month")
    print("─" * 60)

    found = False
    for group in categories():
        if group["deleted"] or group["hidden"]:
            continue
        for c in group["categories"]:
            if not c["deleted"] and not c["hidden"] and c["balance"] < 0:
                print(f"  {group['name']} / {c['name']:<35} {fmt(c['balance']):>10}")
                found = True

    if not found:
        print("  No overspent categories.")


def show_transactions(since_days: int = 30):
    txns = [t for t in transactions(since_days) if not t["deleted"]]
    txns.sort(key=lambda x: x["date"], reverse=True)

    print(f"\nTransactions — last {since_days} days ({len(txns)} total)")
    print("─" * 80)
    print(f"  {'Date':<12} {'Payee':<30} {'Category':<22} {'Amount':>10}")
    print("  " + "─" * 76)

    for t in txns[:50]:
        payee    = (t.get("payee_name") or "")[:28]
        category = (t.get("category_name") or "Transfer")[:20]
        print(
            f"  {t['date']:<12} "
            f"{payee:<30} "
            f"{category:<22} "
            f"{fmt(t['amount']):>10}"
        )

    if len(txns) > 50:
        print(f"\n  ... and {len(txns) - 50} more")


def cleanup_legacy_transactions(dry_run: bool = False):
    """
    Delete all reconciled + uncleared transactions from the three ING accounts.
    These are legacy pre-import entries causing incorrect balances.
    Target balances after cleanup: Bills $90.83, Spending ~$28, Saving ~$3.
    """
    ING_ACCOUNTS = {
        "Bills":    "ac9c72fc-0c7b-47e0-9092-f67821b1f2bd",
        "Spending": "e59be376-73a0-4115-85d0-162b6c5f0044",
        "Saving":   "6cbd6bc5-4752-4a53-b73b-8f1290cf32b7",
    }

    total_deleted = 0
    total_skipped = 0

    for acct_name, acct_id in ING_ACCOUNTS.items():
        r = requests.get(
            f"{BASE}/budgets/{BUDGET_ID}/accounts/{acct_id}/transactions",
            headers=HEADERS,
        )
        if r.status_code == 429:
            print(f"  {acct_name}: rate limited — wait an hour and retry")
            continue
        r.raise_for_status()
        txns = r.json()["data"]["transactions"]

        legacy = [t for t in txns if t["cleared"] in ("reconciled", "uncleared") and not t["deleted"]]
        print(f"\n{acct_name}: {len(legacy)} legacy transactions to delete")

        deleted = 0
        for t in legacy:
            date = t["date"]
            amount = milliunits(t["amount"])
            payee = t.get("payee_name") or "(no payee)"
            if dry_run:
                print(f"  [dry-run] would delete: {date}  {amount:>10.2f}  {payee}")
                deleted += 1
            else:
                ok = delete_transaction(t["id"])
                if ok:
                    deleted += 1
                else:
                    total_skipped += 1
                    print(f"  FAILED to delete: {date}  {amount:>10.2f}  {payee}")
                time.sleep(0.5)

        print(f"  {'Would delete' if dry_run else 'Deleted'}: {deleted}")
        total_deleted += deleted

    print(f"\nTotal {'marked' if dry_run else 'deleted'}: {total_deleted}  |  Errors: {total_skipped}")


def show_audit():
    # Budget identity
    print(f"\nYNAB — FY25/26 Budget")
    month = datetime.date.today().strftime("%B %Y")
    print(f"As at {month}")

    show_accounts()

    month_data = current_month()
    print(f"\nThis month")
    print("─" * 60)
    print(f"  {'Budgeted':<35} {fmt(month_data['budgeted']):>12}")
    print(f"  {'Spent':<35} {fmt(month_data['activity']):>12}")
    print(f"  {'To be budgeted':<35} {fmt(month_data['to_be_budgeted']):>12}")
    age = month_data.get("age_of_money")
    if age:
        print(f"  {'Age of money':<35} {age:>11} days")

    show_overspent()


# ── CLI ────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "audit"

    if cmd == "audit":
        show_audit()
    elif cmd == "accounts":
        show_accounts()
    elif cmd == "budget":
        show_budget()
    elif cmd == "transactions":
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 30
        show_transactions(days)
    elif cmd == "overspent":
        show_overspent()
    elif cmd == "cleanup":
        dry = "--dry-run" in sys.argv
        if dry:
            print("Dry run — no changes will be made\n")
        cleanup_legacy_transactions(dry_run=dry)
    else:
        print(__doc__)

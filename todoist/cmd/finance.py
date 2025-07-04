import datetime

from rich.console import Console

from todoist.tasks import get_full_label_names

ENTERTAINMENT_PROJECT_ID = "6Crf9554MR7jVRCp"

def banking(api):
    console = Console()
    with console.status("[bold green]Creating task...") as _:
        labels=get_full_label_names(api, ["admin", "finance"])
        task = api.add_task(
            content=f"{datetime.datetime.now().strftime('%B')} banking admin",
            labels=labels,
            project_id=ENTERTAINMENT_PROJECT_ID,
            due_string="Today"
        )
        api.add_task(
            content=f"Archive payslip",
            labels=labels,
            project_id=ENTERTAINMENT_PROJECT_ID,
            parent_id=task.id
        )
        api.add_task(
            content=f"Monthly budget on spreadsheet",
            labels=labels,
            project_id=ENTERTAINMENT_PROJECT_ID,
            parent_id=task.id
        )
        api.add_task(
            content=f"Update debt list",
            labels=labels,
            project_id=ENTERTAINMENT_PROJECT_ID,
            parent_id=task.id
        )
        api.add_task(
            content=f"Pay British Gas electricity bill",
            labels=labels,
            project_id=ENTERTAINMENT_PROJECT_ID,
            parent_id=task.id
        )
        api.add_task(
            content=f"Transfer food money to Chase current account",
            labels=labels,
            project_id=ENTERTAINMENT_PROJECT_ID,
            parent_id=task.id
        )
        api.add_task(
            content=f"Transfer tax savings to Chase savings account",
            labels=labels,
            project_id=ENTERTAINMENT_PROJECT_ID,
            parent_id=task.id
        )
        api.add_task(
            content=f"Pay Virgin Money credit card (debt clearance)",
            labels=labels,
            project_id=ENTERTAINMENT_PROJECT_ID,
            parent_id=task.id
        )
        api.add_task(
            content=f"Pay Tesco credit card",
            labels=labels,
            project_id=ENTERTAINMENT_PROJECT_ID,
            parent_id=task.id
        )
        api.add_task(
            content=f"Transfer £200 to Coinbase for BTC payment",
            labels=labels,
            project_id=ENTERTAINMENT_PROJECT_ID,
            parent_id=task.id
        )
        api.add_task(
            content=f"Purchase £200 of BTC on Coinbase",
            labels=labels,
            project_id=ENTERTAINMENT_PROJECT_ID,
            parent_id=task.id
        )
        api.add_task(
            content=f"Transfer BTC from Coinbase to Ledger wallet",
            labels=labels,
            project_id=ENTERTAINMENT_PROJECT_ID,
            parent_id=task.id
        )

def crypto(api):
    console = Console()
    with console.status("[bold green]Creating task...") as _:
        labels=get_full_label_names(api, ["admin", "finance"])
        task = api.add_task(
            content=f"{datetime.datetime.now().strftime('%B')} crypto admin",
            labels=labels,
            project_id=ENTERTAINMENT_PROJECT_ID,
            due_string="Today"
        )
        api.add_task(
            content=f"Withdraw USDT from BitMart to MetaMask via Ethereum Mainnet",
            labels=labels,
            project_id=ENTERTAINMENT_PROJECT_ID,
            parent_id=task.id
        )
        api.add_task(
            content=f"Withdraw USDT from MEXC to MetaMask via Ethereum Mainnet",
            labels=labels,
            project_id=ENTERTAINMENT_PROJECT_ID,
            parent_id=task.id
        )
        api.add_task(
            content=f"Withdraw USDT from Ourbit to MetaMask via Ethereum Mainnet",
            labels=labels,
            project_id=ENTERTAINMENT_PROJECT_ID,
            parent_id=task.id
        )
        api.add_task(
            content=f"Bridge USDT accumulated from Uniswap sales from Arbitrum One to Ethereum Mainnet",
            labels=labels,
            project_id=ENTERTAINMENT_PROJECT_ID,
            parent_id=task.id
        )
        api.add_task(
            content=f"Send USDT from MetaMask to Coinbase via Ethereum Mainnet",
            labels=labels,
            project_id=ENTERTAINMENT_PROJECT_ID,
            parent_id=task.id
        )
        api.add_task(
            content=f"Send USDT to GBP on Coinbase",
            labels=labels,
            project_id=ENTERTAINMENT_PROJECT_ID,
            parent_id=task.id
        )
        api.add_task(
            content=f"Withdraw GBP on Coinbase to bank account",
            labels=labels,
            project_id=ENTERTAINMENT_PROJECT_ID,
            parent_id=task.id
        )
        api.add_task(
            content=f"Pay Sainsbury's Bank credit card",
            labels=labels,
            project_id=ENTERTAINMENT_PROJECT_ID,
            parent_id=task.id
        )

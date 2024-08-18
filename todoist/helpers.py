import questionary
from datetime import datetime


def date_picker():
    current = datetime.now()
    year = questionary.text("Year (YYYY):", default=str(current.year)).ask()
    month = questionary.text("Month (MM):", default=str(current.month).zfill(2)).ask()
    day = questionary.text("Day (DD):").ask()
    
    try:
        date = datetime(year=int(year), month=int(month), day=int(day)).date()
        return date
    except ValueError:
        print("Invalid date. Please try again.")
        return date_picker()

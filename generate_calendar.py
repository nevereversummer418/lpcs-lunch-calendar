import requests
from datetime import date
from calendar import monthrange
from icalendar import Calendar, Event

SCHOOL_ID = "d66290a4-6e72-40e6-9da1-3b1bbd06526c"

BASE_URL = (
    "https://webapis.schoolcafe.com/api/"
    "CalendarView/GetMonthlyMenuItemsByGrade"
)

cal = Calendar()

for year in [2026, 2027]:
    start_month = 8 if year == 2026 else 1
    end_month = 12 if year == 2026 else 5

    for month in range(start_month, end_month + 1):

        last_day = monthrange(year, month)[1]

        params = {
            "SchoolId": SCHOOL_ID,
            "StartDate": f"{year}-{month:02d}-01",
            "EndDate": f"{year}-{month:02d}-{last_day}",
            "ServiceLine": "Main Line",
            "MealType": "Lunch",
            "Grade": "04",
            "PersonId": "null"
        }

        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()

        data = response.json()

        for day in data:
            serving_date = day.get("Servingdate")

            if not serving_date:
                continue

            entrees = []

            for category in day.get("Category", []):

                if category.get("Name") != "ENTREES":
                    continue

                for item in category.get("Items", []):
                    desc = item.get("Desc")

                    if desc:
                        entrees.append(desc)

            if not entrees:
                continue

            event = Event()

            event.add("summary", "LPCS Lunch")

            event.add(
                "description",
                "\n".join(entrees)
            )

            event.add(
                "dtstart",
                date.fromisoformat(serving_date)
            )

            cal.add_component(event)

with open("lpcs-lunch.ics", "wb") as f:
    f.write(cal.to_ical())

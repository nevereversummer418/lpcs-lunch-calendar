import requests
from calendar import monthrange
from datetime import date
from icalendar import Calendar, Event

SCHOOL_ID = "d66290a4-6e72-40e6-9da1-3b1bbd06526c"

BASE_URL = (
    "https://webapis.schoolcafe.com/api/"
    "CalendarView/GetMonthlyMenuitemsByGrade"
)

cal = Calendar()
cal.add("prodid", "-//LPCS Lunch Calendar//")
cal.add("version", "2.0")


def add_event(serving_date, entrees):
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

    event.add(
        "uid",
        f"lpcs-{serving_date}"
    )

    cal.add_component(event)


for year, start_month, end_month in [
    (2026, 8, 12),
    (2027, 1, 5),
]:

    for month in range(start_month, end_month + 1):

        last_day = monthrange(year, month)[1]

        params = {
            "SchoolId": SCHOOL_ID,
            "StartDate": f"{year}-{month:02d}-01",
            "EndDate": f"{year}-{month:02d}-{last_day}",
            "ServingLine": "Main Line",
            "MealType": "Lunch",
            "Grade": "04",
            "PersonId": "null"
        }

        print(
            f"Fetching {params['StartDate']} "
            f"to {params['EndDate']}"
        )

        response = requests.get(
            BASE_URL,
            params=params,
            headers={
                "accept": "application/json",
                "origin": "https://www.schoolcafe.com",
                "referer": "https://www.schoolcafe.com/"
            }
        )

        print(response.url)
        print(response.status_code)

        response.raise_for_status()

        data = response.json()

        print("Records:", len(data))

        for day in data:

            serving_date = (
                day.get("Servingdate")
                or day.get("ServingDate")
            )

            if not serving_date:
                continue

            entrees = []

            def find_entrees(obj):
                if isinstance(obj, dict):

                    name = obj.get("Name")

                    if name == "ENTREES":

                        for item in obj.get("Items", []):
                            desc = item.get("Desc")

                            if desc:
                                entrees.append(desc)

                    for value in obj.values():
                        find_entrees(value)

                elif isinstance(obj, list):
                    for value in obj:
                        find_entrees(value)

            find_entrees(day)

            if entrees:
                add_event(
                    serving_date,
                    sorted(set(entrees))
                )

with open("lpcs-lunch.ics", "wb") as f:
    f.write(cal.to_ical())

print("Created lpcs-lunch.ics")

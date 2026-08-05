from datetime import datetime, timedelta

def get_calendar(command=None):

    now = datetime.now()

    if command:

        if command.startswith("CALENDAR_"):

            selected_date = command.replace(
                "CALENDAR_",
                ""
            )

            return {

                "engine": "page",

                "title": "⏰ Select a Time Period",

                "messages": [
                    "Choose your preferred time."
                ],

                "buttons": [

                    {
                    "id": f"MORNING_{selected_date}",
                    "text": "🌅 Morning"
                    },

                    {
                        "id": f"AFTERNOON_{selected_date}",
                        "text": "🌤 Afternoon"
                    },

                    {
                        "id": f"EVENING_{selected_date}",
                        "text": "🌙 Evening"
                    }

                ]

            }
        elif command.startswith("MORNING_"):

            selected_date = command.replace(
                "MORNING_",
                ""
            )

            return {

                "engine": "page",

                "title": "🌅 Morning",

                "messages": [
                    "Choose an available time."
                ],

                "buttons": [

                    {
                        "id": f"TIME_{selected_date}_09:00",
                        "text": "🟢 09:00"
                    },

                    {
                        "id": f"TIME_{selected_date}_09:30",
                        "text": "🟢 09:30"
                    },

                    {
                        "id": f"TIME_{selected_date}_10:00",
                        "text": "🟢 10:00"
                    },

                    {
                        "id": f"TIME_{selected_date}_10:30",
                        "text": "🟢 10:30"
                    },

                    {
                        "id": f"TIME_{selected_date}_11:00",
                        "text": "🟢 11:00"
                    }

                ]

            }

    days = []

    start = 0

    if now.hour >= 20:
        start = 1

    for i in range(start, start + 5):

        day = now + timedelta(days=i)

        if i == 0:
            title = "Today"

        elif i == 1:
            title = "Tomorrow"

        else:
            title = day.strftime("%a")

        days.append({

            "title": title,

            "date": day.strftime("%Y-%m-%d"),

            "day": day.day,

            "month": day.strftime("%b")

        })

    page = {

        "engine": "page",

        "title": "📅 Select a Date",

        "messages": [
            "Choose an available date to continue."
        ],

        "buttons": []

    }

    for day in days:

        page["buttons"].append({

            "id": f"CALENDAR_{day['date']}",

            "text": f"🟢 {day['title']} • {day['month']} {day['day']}"

        })

    return page

if __name__ == "__main__":

    from pprint import pprint

    pprint(get_calendar("MORNING_2026-08-06"))
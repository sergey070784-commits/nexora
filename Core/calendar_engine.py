from datetime import datetime, timedelta
calendar_config = {}
selected_calendar = ""



def get_calendar(command=None, config=None):

    global calendar_config

    if config:
        calendar_config = config
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

            return build_time_page(

                title="🌅 Morning",

                date=selected_date,

                times=[
                    "09:00",
                    "09:30",
                    "10:00",
                    "10:30",
                    "11:00"
                ]

            )

        elif command.startswith("AFTERNOON_"):

            selected_date = command.replace(
                "AFTERNOON_",
                ""
            )

            return build_time_page(

                title="🌤 Afternoon",

                date=selected_date,

                times=[
                    "13:00",
                    "13:30",
                    "14:00",
                    "14:30",
                    "15:00"
                ]

            )
        elif command.startswith("EVENING_"):

            selected_date = command.replace(
                "EVENING_",
                ""
            )

            return build_time_page(

                title="🌙 Evening",

                date=selected_date,

                times=[
                    "17:00",
                    "17:30",
                    "18:00",
                    "18:30",
                    "19:00"
                ]

            )
        elif command.startswith("TIME_"):

            selected = command.replace(
                "TIME_",
                ""
            )
            global selected_calendar

            selected_calendar = selected

            date, time = selected.split("_")

            return {

                "engine": "command",

                "title": "✅ Confirm Appointment",

                "messages": [

                    f"📅 Date: {date}",

                    f"🕒 Time: {time}",

                    "",

                    "Press Continue to send the request."

                ],

                "buttons": [

                    {

                        "id": calendar_config["finish_btn"],

                        "text": "Continue"

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

def get_calendar_events():
    return calendar_config.get(
        "events",
        [
            "APPOINTMENT_DATE",
            "APPOINTMENT_TIME"
        ]
    )

def build_time_page(title, date, times):

    page = {

        "engine": "page",

        "title": title,

        "messages": [
            "Choose an available time."
        ],

        "buttons": []

    }

    for time in times:

        page["buttons"].append({

            "id": f"TIME_{date}_{time}",

            "text": f"🟢 {time}"

        })

    return page

if __name__ == "__main__":

    from pprint import pprint

    pprint(get_calendar("MORNING_2026-08-06"))
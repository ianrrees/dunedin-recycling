#!/usr/bin/env python3
#
# Generates ical files for Dunedin City Council recycling collection days.
# Data comes from the "Let's Sort It Out" calendar
# https://www.dunedin.govt.nz/services/rubbish-and-recycling/collection-days
#
# Ian Rees 2021-2025

# python3 -m pip install icalendar
from icalendar import Calendar, Event

from datetime import date, timedelta
from itertools import count

# If a pickup would normally be `key`, do it `value` instead
exceptions = {
    date(2021, 4, 2): date(2021, 4, 3),
    date(2022, 1, 31): None,
    date(2022, 4, 15): date(2022, 4, 16),
    date(2023, 4, 7): date(2023, 4, 8),
    date(2023, 12, 25): date(2023, 12, 30),
    date(2024, 1, 1): date(2024, 1, 6),
    date(2024, 3, 29): date(2024, 3, 30),
    date(2024, 12, 25): date(2024, 12, 28),
    date(2025, 1, 1): date(2025, 1, 4),
    date(2025, 4, 18): date(2025, 4, 19),
    date(2025, 12, 25): date(2025, 12, 27),
    date(2026, 1, 1): date(2026, 1, 3),
    date(2026, 4, 3): date(2026, 4, 4),
    date(2026, 12, 25): date(2026, 12, 26),
}

# For whatever reason, the collection calendar doesn't start on Jan 1, which
# makes iterating awkward.  I'd do this differently if starting now, but this
# list is the date that "week one" starts with yellow bin pickup.  Years
# unlike 2021 (when the year started with a complete week) need an exception
# above, so that pickup days have the right phase.
first_day_of_week = {
    2021: {
        "Monday": date(2021, 2, 1),
        "Tuesday": date(2021, 2, 2),
        "Wednesday": date(2021, 2, 3),
        "Thursday": date(2021, 2, 4),
        "Friday": date(2021, 2, 5),
    },
    2022: {
        "Monday": date(2022, 1, 31),
        "Tuesday": date(2022, 2, 1),
        "Wednesday": date(2022, 2, 2),
        "Thursday": date(2022, 2, 3),
        "Friday": date(2022, 2, 4),
    },
    2023: {
        "Monday": date(2023, 1, 2),
        "Tuesday": date(2023, 2, 3),
        "Wednesday": date(2023, 2, 4),
        "Thursday": date(2023, 2, 5),
        "Friday": date(2023, 2, 6),
    },
    2024: {
        "Monday": date(2024, 1, 1),
        "Tuesday": date(2024, 1, 2),
        "Wednesday": date(2024, 1, 3),
        "Thursday": date(2024, 1, 4),
        "Friday": date(2024, 1, 5),
    },
    2025: {
        "Monday": date(2025, 1, 13),
        "Tuesday": date(2025, 1, 14),
        "Wednesday": date(2025, 1, 1),
        "Thursday": date(2025, 1, 2),
        "Friday": date(2025, 1, 3),
    },
    2026: {
        "Monday": date(2026, 1, 12),
        "Tuesday": date(2026, 1, 13),
        "Wednesday": date(2026, 1, 14),
        "Thursday": date(2026, 1, 1),
        "Friday": date(2026, 1, 2),
    }
    # Only define years after the exceptions are known for that year
}

# Stop generation for a particular year after this date
# TODO might be nice to stop generating when the subsequent year starts too -
# currently get duplicates where the two calendars overlap
last_day_of_year = {
    2021: date(2022, 1, 31),
    2022: date(2023, 1, 31),
    2023: date(2023, 12, 30),
    2024: date(2024, 12, 31),
    2025: date(2025, 12, 31),
    2026: date(2026, 12, 31),
}

# After this day, we use red bins for waste every second week
red_bins_start = date(2024, 7, 1)

# DCC talks about "Week One" and "Week Two", instead let's talk about the colour
# bin collected on the first Monday/Tuesday/etc. since they cycle.
colours = ["Yellow", "Blue"]

day_of_week = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    ]

def make_event(colour):
    event = Event()
    if colour == "Yellow":
        event.add("summary", "📦 Yellow bin")
        event.add("description",
"""YELLOW WEEK: Rinsed rigid plastics
1, 2 and 5 only, tins, cans, and clean
paper and cardboard. No caps, lids,
pumps or trigger sprays.

Place all recycling and DCC black bags
kerbside by 7am on your collection day.""")
    elif colour == "Blue":
        event.add("summary", "🍾 Blue bin")
        event.add("description",
"""BLUE WEEK: Unbroken glass
bottles and jars, with NO lids.
No mirror glass.

Place all recycling and DCC black bags
kerbside by 7am on your collection day.""")
    return event

def make_new_event(colour):
    event = Event()
    if colour == "Yellow":
        event.add("summary", "🍂📦 Green and Yellow")
        event.add("description",
"""Yellow bin: Rinsed rigid plastics
1, 2 and 5 only, tins, cans, and clean
paper and cardboard. No caps, lids,
pumps or trigger sprays.

Place bins kerbside by 7am on your collection day.""")
    elif colour == "Blue":
        event.add("summary", "🍂🗑️🍾 Green, Red, and Blue")
        event.add("description",
"""Blue Bin: Unbroken glass
bottles and jars, with NO lids.
No mirror glass.

Place bins kerbside by 7am on your collection day.""")
    return event

for colour_index in range(len(colours)):
    for weekday in day_of_week:
        filename = "week-{}-{}.ics".format(colour_index+1, weekday.lower())
        with open(filename.encode("UTF-8"), "wb") as file:
            cal = Calendar()
            cal.add("prodid", "-//Dunedin City Council//Rubbish Collection week {}, {} pickup//EN".format(
                colour_index + 1, weekday))
            cal.add("version", "2.0")
            cal.add("X-WR-TIMEZONE", "Pacific/Auckland")

            for year in first_day_of_week:
                first = first_day_of_week[year][weekday]

                for week in count(): # Not always 52 weeks in a DCC year...
                    start = first + timedelta(days = 7 * week)

                    if start in exceptions:
                        start = exceptions[start]
                        if start is None:
                            # This can happen at the start of the year
                            continue
                    if start > last_day_of_year[year]:
                        break # I miss Rust already!

                    colour = colours[(colour_index + week) % len(colours)]
                    if start >= red_bins_start:
                        event = make_new_event(colour)
                    else:
                        event = make_event(colour)
                    event.add("dtstart", start)
                    event.add("dtend", start + timedelta(days=1))
                    # The UID needs to be reproducible for updates
                    uid = "recycling-week{}-{}".format(colour_index+1, start)
                    event.add("uid", uid)
                    cal.add_component(event)
            file.write(cal.to_ical())

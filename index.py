from transformers import AutoModelForSequenceClassification, AutoTokenizer
import torch
from icalendar import Calendar, Event
import datetime
import re
import os
import pytz
import dateutil.parser

# Load the DistilBERT model and tokenizer
model = AutoModelForSequenceClassification.from_pretrained("distilbert-base-uncased")
tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased")

# Initialize a Calendar object
c = Calendar()

# Load events from file if it exists
if os.path.isfile("events.ics"):
    with open("events.ics", "rb") as f:
        ical_string = f.read().decode('utf-8')
        events = []
        cal = Calendar.from_ical(ical_string)
        for component in cal.walk():
            if component.name == 'VEVENT':
                event = Event()
                event.name = component.get('SUMMARY', '')
                if component.get('DTSTART'):
                    event.begin = component.get('DTSTART').dt
                if component.get('DTEND'):
                    event.end = component.get('DTEND').dt
                events.append(event)
                print(f"Loaded event: {event.name} ({event.begin} - {event.end})")
        for event in events:
            c.add_component(event)


def generate_response(prompt):
    """
    Generate a response using the DistilBERT model.
    """
    inputs = tokenizer(prompt, return_tensors="pt")
    output = model(**inputs)[0]  # get the logits
    return tokenizer.decode(torch.argmax(output, dim=-1)[0], skip_special_tokens=True)

def list_events(start, end):
    """
    List events between start and end times.
    """
    events = []
    for component in c.walk():
        if component.name == 'VEVENT':
            event = Event()
            event.name = component.get('SUMMARY', '')
            event_start = component.get('DTSTART').dt
            event_end = component.get('DTEND').dt
            if event_end is None:
                event_end = event_start + datetime.timedelta(days=1)
            if event_start >= start and event_end <= end:
                events.append(event)
    if not events:
        return "There are no events presently."
    event_summaries = [f"{event.name} ({event_start.strftime('%I:%M %p')} - {event_end.strftime('%I:%M %p')})" for event in events]
    return ", ".join(event_summaries)

def create_event(summary, start, end):
    """
    Create a new event in the calendar.
    """
    tz = pytz.timezone("UTC")  # or any other timezone you prefer
    event = Event()
    event.name = summary
    event.begin = tz.localize(start)
    event.end = tz.localize(end)
    c.events.add(event)
    save_events()

def save_events():
    """
    Save events to an .ics file.
    """
    ical_string = c.to_ical()
    with open("events.ics", "wb") as f:
        f.write(ical_string.encode('utf-8'))  # Encode as bytes for binary write

def process_input(user_input):
    """
    Process the user input and perform the corresponding action.
    """
    if any(keyword in user_input.lower() for keyword in ["schedule", "create"]):
        summary, start, end = extract_event_details(user_input)
        if summary and start and end:
            create_event(summary, start, end)
            return f"Event '{summary}' has been scheduled from {start.strftime('%I:%M %p')} to {end.strftime('%I:%M %p')}."
        else:
            return "I'm sorry, I couldn't understand the event details. Please try again."

    elif any(keyword in user_input.lower() for keyword in ["list", "show"]):
        start = datetime.datetime.now(pytz.utc).replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=pytz.utc)
        end = start + datetime.timedelta(days=1, seconds=-1, microseconds=-1)
        existing_events = list_events(start, end)
        return existing_events

    else:
        return "I'm sorry, I didn't understand your request. Please try again."



def extract_event_details(user_input):
    """
    Extract the event summary, start time, and end time from the user input.
    """
    patterns = [
        r"(schedule|create)(.*?)from\s*(\d+:\d+\s*[aApP][mM])\s*to\s*(\d+:\d+\s*[aApP][mM])\s*tomorrow",
        r"(schedule|create)(.*?)from\s*(\d+:\d+\s*[aApP][mM])\s*to\s*(\d+:\d+\s*[aApP][mM])\s*on\s*(\w+)",
        r"(schedule|create)(.*?)from\s*(\d+:\d+\s*[aApP][mM])\s*to\s*(\d+:\d+\s*[aApP][mM])\s*every\s*(\w+)",
        r"(schedule|create)(.*?)from\s*(\d+:\d+\s*[aApP][mM])\s*to\s*(\d+:\d+\s*[aApP][mM])\s*on\s*the\s*(\w+)\s*of\s*every\s*(\w+)",
        r"(schedule|create)(.*?)from\s*(\d+:\d+\s*[aApP][mM])\s*to\s*(\d+:\d+\s*[aApP][mM])\s*on\s*the\s*(last|first|second|third|fourth)\s*(\w+)\s*of\s*every\s*(\w+)",
    ]
    for pattern in patterns:
        match = re.search(pattern, user_input, re.IGNORECASE)
        if match:
            summary = match.group(2).strip()
            start_str = match.group(3).strip()
            end_str = match.group(4).strip()
            if match.group(5) is None:
                tomorrow = datetime.date.today() + datetime.timedelta(days=1)
                start = datetime.datetime.combine(tomorrow, datetime.datetime.strptime(start_str, "%I:%M %p").time())
                end = datetime.datetime.combine(tomorrow, datetime.datetime.strptime(end_str, "%I:%M %p").time())
            elif match.group(6):
                day_of_week = match.group(6).lower()
                start = datetime.datetime.combine(datetime.date.today(), datetime.datetime.strptime(start_str, "%I:%M %p").time())
                while start.strftime("%A").lower() != day_of_week:
                    start += datetime.timedelta(days=1)
                end = start + datetime.timedelta(hours=int(end_str.split(":")[0]) - int(start_str.split(":")[0]), minutes=int(end_str.split(":")[1]) - int(start_str.split(":")[1]))
                if match.group(7) == "every":
                    end_of_week = start + datetime.timedelta(days=6)
                    while start < end_of_week:
                        create_event(summary, start, end)
                        start += datetime.timedelta(days=7)
                        end += datetime.timedelta(days=7)
            elif match.group(8):
                ordinal = match.group(8).lower()
                weekday = match.group(9).lower()
                month = match.group(10).lower()
                start = datetime.datetime.combine(datetime.date.today(), datetime.datetime.strptime(start_str, "%I:%M %p").time())
                next_month = start.replace(day=1) + datetime.timedelta(days=32)
                while start.strftime("%B").lower() != month:
                    start = next_month
                    next_month = start.replace(day=1) + datetime.timedelta(days=32)
                while start.strftime("%A").lower() != weekday:
                    start += datetime.timedelta(days=1)
                if ordinal == "last":
                    while start.replace(day=1) + datetime.timedelta(days=32) > start.replace(month=start.month + 1, day=1):
                        start -= datetime.timedelta(days=7)
                else:
                    count = 1
                    while count < int(ordinal):
                        start += datetime.timedelta(days=7)
                        if start.strftime("%B").lower() != month:
                            break
                        count += 1
                end = start + datetime.timedelta(hours=int(end_str.split(":")[0]) - int(start_str.split(":")[0]), minutes=int(end_str.split(":")[1]) - int(start_str.split(":")[1]))
                if match.group(11) == "every":
                    while end.strftime("%B").lower() == month:
                        create_event(summary, start, end)
                        start += datetime.timedelta(days=7)
                        end += datetime.timedelta(days=7)
            start = pytz.utc.localize(start)
            end = pytz.utc.localize(end)
            return summary, start, end

    # If the input doesn't match any pattern, try to parse it using dateutil
    try:
        date_strings = dateutil.parser.parse(user_input, fuzzy=True)
        if isinstance(date_strings, list):
            start, end = date_strings
        else:
            start = end = date_strings
        summary = "Event"
        start = pytz.utc.localize(start)
        end = pytz.utc.localize(end)
        return summary, start, end
    except (ValueError, OverflowError):
        pass

    return None, None, None
# Example usage
print("Welcome to the AI Scheduling Assistant!")

while True:
    user_input = input("Enter your request: ")
    response = process_input(user_input)
    print(response)

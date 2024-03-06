import gradio as gr
from transformers import AutoModelForSequenceClassification, AutoTokenizer
import torch
import datetime
import re
import os
import pytz
import dateutil.parser

# Load the DistilBERT model and tokenizer
model = AutoModelForSequenceClassification.from_pretrained("distilbert-base-uncased")
tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased")

# Initialize an empty list to store events
events = []

# Load events from file if it exists
if os.path.isfile("events.txt"):
    with open("events.txt", "r") as f:
        for line in f:
            event_data = line.strip().split("|")
            if len(event_data) == 4:
                name, start_str, end_str, recurring = event_data
                start = dateutil.parser.parse(start_str)
                end = dateutil.parser.parse(end_str)
                is_recurring = (recurring.lower() == "true")
                events.append({"name": name, "start": start, "end": end, "recurring": is_recurring})
                print(f"Loaded event: {name} ({start} - {end})")

def generate_response(prompt):
    """
    Generate a response using the DistilBERT model.
    """
    inputs = tokenizer(prompt, return_tensors="pt")
    output = model(**inputs)[0]  # get the logits
    return tokenizer.decode(torch.argmax(output, dim=-1)[0], skip_special_tokens=True)

def list_events(start, end):
    """
    List events for the day between start and end times.
    """
    event_summaries = []
    for event in events:
        event_start = event["start"]
        event_end = event["end"]
        if event_start.tzinfo is None:
            event_start = pytz.utc.localize(event_start)
        if event_end.tzinfo is None:
            event_end = pytz.utc.localize(event_end)
        if start <= event_start < end:
            event_summaries.append(f"{event['name']} ({event_start.strftime('%I:%M %p')} - {event_end.strftime('%I:%M %p')})")
    if not event_summaries:
        return "There are no events presently."
    return ", ".join(event_summaries)

def create_event(summary, start, end, recurring=False):
    """
    Create a new event.
    """
    event = {"name": summary, "start": start, "end": end, "recurring": recurring}
    events.append(event)
    save_events()
    return f"Event '{summary}' has been scheduled from {start.strftime('%I:%M %p')} to {end.strftime('%I:%M %p')}."

def save_events():
    """
    Save events to a text file.
    """
    with open("events.txt", "w") as f:
        for event in events:
            start_str = event["start"].strftime("%Y-%m-%d %H:%M:%S")
            end_str = event["end"].strftime("%Y-%m-%d %H:%M:%S")
            recurring_str = "True" if event["recurring"] else "False"
            f.write(f"{event['name']}|{start_str}|{end_str}|{recurring_str}\n")

def process_input(user_input):
    """
    Process the user input and perform the corresponding action.
    """
    if any(keyword in user_input.lower() for keyword in ["schedule", "create"]):
        summary, start, end, recurring = extract_event_details(user_input)
        if summary and start and end:
            response = create_event(summary, start, end, recurring)
            return response
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
    Extract the event summary, start time, end time, and recurrence from the user input.
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
                recurring = False
            elif match.group(6):
                day_of_week = match.group(6).lower()
                start = datetime.datetime.combine(datetime.date.today(), datetime.datetime.strptime(start_str, "%I:%M %p").time())
                while start.strftime("%A").lower() != day_of_week:
                    start += datetime.timedelta(days=1)
                end = start + datetime.timedelta(hours=int(end_str.split(":")[0]) - int(start_str.split(":")[0]), minutes=int(end_str.split(":")[1]) - int(start_str.split(":")[1]))
                recurring = (match.group(7) == "every")
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
                recurring = (match.group(11) == "every")
            start = pytz.utc.localize(start)
            end = pytz.utc.localize(end)
            return summary, start, end, recurring

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
        return summary, start, end, False
    except (ValueError, OverflowError):
        pass

    return None, None, None, False

# Gradio interface
def chat(user_input):
    response = process_input(user_input)
    return response

iface = gr.Interface(chat, inputs="text", outputs="text", title="AI Scheduling Assistant")
iface.launch()

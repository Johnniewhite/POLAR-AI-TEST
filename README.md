
```md
# AI Scheduling Assistant: User Guide

This AI Scheduling Assistant helps you manage your schedule by processing natural language commands to create, list, and view existing events.

## Features

- Create events by specifying the summary, start time, and end time.
- List existing events for the current day.
- Understands natural language phrases like "schedule a meeting tomorrow from 10 AM to 11 AM" or "list events today".
- Supports recurring events (daily, weekly, etc.).

## Requirements

- Python 3.x
- `transformers` library
- `datetime` library
- `pytz` library
- `dateutil` library
- `gradio` library

## Installation

1. Install the required libraries using pip:

```bash
pip install transformers datetime pytz dateutil gradio
```

## Usage

1. **Command-line:**

   - Clone or download the code repository.
   - Run the script `calendarChatBot.py` from the command line:

   ```bash
   python calendarChatBot.py
   ```

   - Interact with the assistant by typing your requests and pressing Enter.

2. **Interactive interface (optional):**

   - Make sure you have `gradio` installed (optional step).
   - Run the script with the `--server` flag:

   ```bash
   python calendarChatBot.py --server
   ```

   - This will launch a web interface at http://localhost:12700 where you can interact with the assistant through a text box.

## Examples

- Create an event named "Meeting" from 2 PM to 3 PM tomorrow:

   ```
   schedule a meeting tomorrow from 2 PM to 3 PM
   ```

- List all events for today:

   ```
   list events today
   ```

- Create a recurring meeting every Monday from 10 AM to 11 AM:

   ```
   create a recurring meeting every Monday from 10 AM to 11 AM
   ```

## Technical Approach and AI Algorithms Used

The AI Scheduling Assistant uses the DistilBERT model for natural language processing. DistilBERT is a lightweight version of the BERT model, which allows the assistant to understand basic requests and commands.

## User Engagement

The system engages with users through a command-line interface or an optional interactive web interface powered by the Gradio library. Users can input their requests in natural language, and the assistant processes these requests to manage their schedule.

## Innovative Features and Methods

- The assistant understands natural language commands, making it easy for users to interact with the system without needing to learn complex syntax.
- It supports recurring events, allowing users to schedule events that repeat at regular intervals.

## Limitations

- The assistant's understanding of natural language is limited to basic commands and may not handle complex requests or edge cases effectively.
- The system's ability to handle timezone information is based on standard formats and may not cover all possible timezone scenarios.

## Additional Features for Improvement

- Integration with a calendar API to synchronize events with external calendars.
- Support for more advanced scheduling features, such as setting reminders or notifications for events.
- Improved natural language understanding to handle a wider range of commands and requests.

This user guide provides a basic overview of how to use the AI Scheduling Assistant. Feel free to explore its functionality.

```

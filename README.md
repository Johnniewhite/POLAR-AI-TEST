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

## Notes

- The assistant currently uses DistilBERT for natural language processing, which allows it to understand basic requests.
- Timezone information can be specified using standard formats (e.g., "10 AM PST", "3 PM UTC").
- You can exit the command-line interface by typing `exit`.

## Additional Information

For more detailed information about the code and its functionalities, refer to the comments within the Python script.
The script currently saves events to a text file (`events.txt`). You can modify the save logic to integrate with your preferred calendar application.

This user guide provides a basic overview of how to use the AI Scheduling Assistant. Feel free to explore its functionality.
```

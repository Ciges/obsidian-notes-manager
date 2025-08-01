import argparse
import os
import re
from datetime import datetime
from typing import List, Union

# Import functions from our notes module
from modules.note import Note

# Configure command line arguments
parser = argparse.ArgumentParser(description='Update reminder dates in Obsidian note tasks to match the note date property')
parser.add_argument('-n', '--note', 
                    type=str, 
                    required=True,
                    help='Path to the Obsidian note')
parser.add_argument('-v', '--verbose',
                    action='store_true',
                    help='Enable verbose output')

# Parse arguments
args = parser.parse_args()

# Load configuration using Note static methods
config = Note.load_obsidian_config()
vault_path = Note.get_obsidian_vault_path(config)

if args.verbose and vault_path:
    try:
        print("Configuration loaded successfully")
    except UnicodeEncodeError:
        print("Configuration loaded (some characters cannot be displayed in this console)")
    print(f"Obsidian vault path: {vault_path}")

# Resolve the note path relative to vault if needed using Note static method
resolved_note_path = Note.resolve_note_path(args.note, vault_path, args.verbose)

print(f"Processing note: {resolved_note_path}")

# Check if the note file exists
if not os.path.exists(resolved_note_path):
    print(f"Error: Note file '{resolved_note_path}' not found.")
    exit(1)

# Create a Note instance with the resolved path
note = Note(resolved_note_path, args.verbose)

# Load the content to verify it exists
try:
    content: str = note.get_content()
except FileNotFoundError:
    print(f"Error: Note file '{resolved_note_path}' not found.")
    exit(1)
except Exception as e:
    print(f"Error reading note: {e}")
    exit(1)

# Get the date property from the note
properties = note.get_properties()
if not properties or 'date' not in properties:
    print("Error: Note does not have a 'date' property")
    exit(1)

note_date_raw: Union[str, datetime] = properties['date']
if args.verbose:
    print(f"Note date property: {note_date_raw}")

# Parse the note date to ensure it's valid
try:
    if isinstance(note_date_raw, str):
        # Try to parse different date formats
        if len(note_date_raw) == 10:  # YYYY-MM-DD format
            parsed_date = datetime.strptime(note_date_raw, "%Y-%m-%d")
        elif len(note_date_raw) == 16:  # YYYY-MM-DD HH:MM format
            parsed_date = datetime.strptime(note_date_raw, "%Y-%m-%d %H:%M")
        else:
            raise ValueError(f"Unsupported date format: {note_date_raw}")
        note_date: str = parsed_date.strftime("%Y-%m-%d")
    else:
        # Assume it's already a datetime object
        parsed_date = note_date_raw
        note_date = parsed_date.strftime("%Y-%m-%d")
except (ValueError, TypeError) as e:
    print(f"Error: Invalid date format in note property: {note_date_raw} ({e})")
    exit(1)

# Find tasks with reminder dates and process them one by one
# Pattern to find tasks with reminder dates - dates only (no time)
task_reminder_date_only_pattern = r'^(\s*-\s*\[\s*\]\s+.*?)(@\d{4}-\d{2}-\d{2})(\s*.*)$'

# Pattern to find tasks with reminder dates - with time
task_reminder_with_time_pattern = r'^(\s*-\s*\[\s*\]\s+.*?)(@\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2})(\s*.*)$'

modified_count = 0

# First, update reminders with time (preserve the time part)
tasks_with_time: List[str] = note.find(task_reminder_with_time_pattern)
if tasks_with_time:
    if args.verbose:
        print(f"Found {len(tasks_with_time)} tasks with time-based reminders")
    
    # For each task with time, extract the time and create new reminder
    for task in tasks_with_time:
        match = re.search(task_reminder_with_time_pattern, task)
        if match:
            old_reminder = match.group(2)  # @YYYY-MM-DD HH:MM
            current_date = old_reminder[1:11]  # Extract YYYY-MM-DD part
            time_part = old_reminder[11:]  # Extract " HH:MM" part
            
            if current_date != note_date:
                new_reminder = f"@{note_date}{time_part}"
                # Replace this specific reminder
                pattern_for_this_task = re.escape(old_reminder)
                modified_lines = note.replace(pattern_for_this_task, new_reminder)
                if modified_lines:
                    modified_count += len(modified_lines)

# Then, update reminders with date only
tasks_date_only: List[str] = note.find(task_reminder_date_only_pattern)
if tasks_date_only:
    if args.verbose:
        print(f"Found {len(tasks_date_only)} tasks with date-only reminders")
    
    # For each task with date only, replace with new date
    for task in tasks_date_only:
        match = re.search(task_reminder_date_only_pattern, task)
        if match:
            old_reminder = match.group(2)  # @YYYY-MM-DD
            current_date = old_reminder[1:]  # Extract YYYY-MM-DD part
            
            if current_date != note_date:
                new_reminder = f"@{note_date}"
                # Replace this specific reminder
                pattern_for_this_task = re.escape(old_reminder)
                modified_lines = note.replace(pattern_for_this_task, new_reminder)
                if modified_lines:
                    modified_count += len(modified_lines)

# Report results
total_tasks = len(tasks_with_time) + len(tasks_date_only)

if args.verbose:
    print(f"Total tasks with reminders found: {total_tasks}")

if total_tasks == 0:
    print("No tasks with reminder dates found")
    exit(0)

if modified_count > 0:
    # Write the updated content back to the file
    if note.write_content():
        print(f"Successfully updated {modified_count} reminder dates to match note date ({note_date})")
    else:
        print("Error: Failed to write updated content to file")
        exit(1)
else:
    print(f"All reminder dates already match the note date ({note_date})")
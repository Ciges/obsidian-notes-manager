import argparse
import os
from datetime import datetime, timedelta

# Import functions from our notes module
from modules.note import Note
from modules.vault import Vault

# Configure command line arguments
parser = argparse.ArgumentParser(description='Count pomodoros (🍅) in an Obsidian note and update the pomodoros property')
parser.add_argument('-n', '--note', 
                    type=str, 
                    required=False,
                    help='Path to the Obsidian note. If not specified, uses today\'s daily note')
parser.add_argument('-v', '--verbose',
                    action='store_true',
                    help='Enable verbose output')
parser.add_argument('--dry-run',
                    action='store_true',
                    help='Show what would be updated without making changes')
parser.add_argument('--yesterday',
                    action='store_true',
                    help='Use yesterday\'s daily note (or last business day if today is Monday)')

# Parse arguments
args = parser.parse_args()

# Validate arguments
if args.note and args.yesterday:
    print("Error: Cannot use both --note and --yesterday options together")
    exit(1)

# Load configuration using Vault static methods
config = Vault.load_obsidian_config()
vault_path = Vault.get_obsidian_vault_path(config)

if args.verbose and vault_path:
    try:
        print(f"Configuration loaded: {config}")
    except UnicodeEncodeError:
        print("Configuration loaded (some characters cannot be displayed in this console)")
    print(f"Obsidian vault path: {vault_path}")

# Function to get last business day
def get_last_business_day():
    today = datetime.now()
    
    # If today is Monday (weekday 0), go back to Friday (3 days)
    if today.weekday() == 0:  # Monday
        days_back = 3
        day_name = "Friday (last business day)"
    # If today is Saturday (weekday 5), go back to Friday (1 day)
    elif today.weekday() == 5:  # Saturday
        days_back = 1
        day_name = "Friday (last business day)"
    # If today is Sunday (weekday 6), go back to Friday (2 days)
    elif today.weekday() == 6:  # Sunday
        days_back = 2
        day_name = "Friday (last business day)"
    # Any other day (Tuesday-Friday), just go back 1 day
    else:
        days_back = 1
        day_name = "yesterday"
    
    last_business_day = today - timedelta(days=days_back)
    return last_business_day, day_name

# Determine which note to process
if args.note:
    note_path = args.note
    if args.verbose:
        print(f"Using specified note: {note_path}")
elif args.yesterday:
    # Generate yesterday's daily note path (or last business day)
    yesterday_date, day_description = get_last_business_day()
    daily_note_filename = f"{yesterday_date.strftime('%Y-%m-%d')} Notas diarias"
    note_path = f"CALENDARIO/NOTAS DIARIAS/{daily_note_filename}"
    print(f"Using {day_description}'s daily note: {note_path}")
else:
    # Generate today's daily note path
    today = datetime.now()
    daily_note_filename = f"{today.strftime('%Y-%m-%d')} Notas diarias"
    note_path = f"CALENDARIO/NOTAS DIARIAS/{daily_note_filename}"
    print(f"No note specified, using today's daily note: {note_path}")

# Determine the final note path
if not os.path.isabs(note_path):
    # If it's a relative path, make it relative to vault root
    if vault_path:
        resolved_note_path = os.path.join(vault_path, note_path)
        if args.verbose:
            print(f"Using relative path from vault root: {note_path}")
            print(f"Resolved to absolute path: {resolved_note_path}")
    else:
        print("Error: Cannot resolve relative path without vault configuration")
        exit(1)
else:
    # It's already an absolute path
    resolved_note_path = note_path
    if args.verbose:
        print(f"Using absolute path: {resolved_note_path}")

# Ensure the path has .md extension if it doesn't already
if not resolved_note_path.endswith('.md'):
    resolved_note_path += '.md'
    if args.verbose:
        print(f"Added .md extension: {resolved_note_path}")

# Normalize the path (handle different path separators, etc.)
resolved_note_path = os.path.normpath(resolved_note_path)

print(f"Processing note: {resolved_note_path}")

# Check if the note file exists
if not os.path.exists(resolved_note_path):
    if args.yesterday:
        print(f"Error: Yesterday's daily note does not exist: {resolved_note_path}")
        print("Please create the daily note first or specify an existing note with -n")
    elif not args.note:
        print(f"Error: Today's daily note does not exist: {resolved_note_path}")
        print("Please create the daily note first or specify an existing note with -n")
    else:
        print(f"Error: Note file does not exist: {resolved_note_path}")
    exit(1)

# Create a Note instance with the resolved path
note = Note(resolved_note_path, args.verbose)

# Load the content to verify it exists
try:
    content = note.get_content()
except FileNotFoundError:
    print(f"Error: Note file '{resolved_note_path}' not found.")
    exit(1)
except Exception as e:
    print(f"Error reading note: {e}")
    exit(1)

# Pattern to find lines that start with pomodoro emoji
pomodoro_pattern = r'^\s*🍅'

# Count pomodoros in the note
pomodoro_lines = note.find(pomodoro_pattern)
pomodoro_count = len(pomodoro_lines)

if args.verbose:
    print(f"Found {pomodoro_count} pomodoro lines")
    if pomodoro_count > 0:
        print("Pomodoro lines found:")
        for line in pomodoro_lines[:5]:  # Show first 5 lines
            print(f"  - {line.strip()}")
        if pomodoro_count > 5:
            print(f"  ... and {pomodoro_count - 5} more")

# Get current properties to check existing pomodoros value
current_properties = note.get_properties()
current_pomodoros = current_properties.get('pomodoros') if current_properties else None

# Convert current_pomodoros to int for comparison if it's a string
if isinstance(current_pomodoros, str) and current_pomodoros.isdigit():
    current_pomodoros = int(current_pomodoros)

if args.verbose:
    print(f"Current pomodoros property value: {current_pomodoros}")
    print(f"Calculated pomodoros count: {pomodoro_count}")

# Check if update is needed
if current_pomodoros == pomodoro_count:
    print(f"Pomodoros property is already up to date: {pomodoro_count}")
    exit(0)

# Show what will be changed
if current_pomodoros is not None:
    print(f"Updating pomodoros property: {current_pomodoros} -> {pomodoro_count}")
else:
    print(f"Setting pomodoros property to: {pomodoro_count}")

# Perform the update unless dry-run
if args.dry_run:
    print("DRY-RUN: No changes made to the file")
else:
    try:
        # Update the pomodoros property (store as integer for consistency)
        success = note.set_property('pomodoros', str(pomodoro_count), verbose=args.verbose)
        
        if success:
            # Write the updated content back to the file
            if note.write_content():
                print(f"Successfully updated pomodoros property to {pomodoro_count}")
                
                if args.verbose:
                    # Verify the change was made
                    updated_note = Note(resolved_note_path, False)
                    updated_properties = updated_note.get_properties()
                    final_pomodoros = updated_properties.get('pomodoros') if updated_properties else None
                    print(f"Verification: pomodoros property is now: {final_pomodoros}")
            else:
                print("Error: Failed to write updated content to file")
                exit(1)
        else:
            print("Error: Failed to update pomodoros property")
            exit(1)
            
    except Exception as e:
        print(f"Error updating note: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        exit(1)
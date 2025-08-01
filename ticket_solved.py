import argparse
from datetime import datetime
import os

# Import functions from our notes module
from modules.note import Note

# Configure command line arguments
parser = argparse.ArgumentParser(description='Process Obsidian note')
parser.add_argument('-n', '--note', 
                    type=str, 
                    required=True,
                    help='Path to the Obsidian note')
parser.add_argument('-r', '--resolved',
                    action='store_true',
                    help='Mark the task as resolved')
parser.add_argument('-c', '--closed',
                    action='store_true',
                    help='Mark the task as closed')
parser.add_argument('-v', '--verbose',
                    action='store_true',
                    help='Enable verbose output')

# Parse arguments
args = parser.parse_args()

# Validate that only one action is specified
if args.resolved and args.closed:
    print("Error: Cannot use both --resolved and --closed options at the same time.")
    exit(1)

if not args.resolved and not args.closed:
    print("Error: Must specify either --resolved (-r) or --closed (-c) option.")
    exit(1)

# Load configuration using Note static methods
config = Note.load_obsidian_config()
vault_path = Note.get_obsidian_vault_path(config)

# Get task properties from configuration
task_props = config.get('tasks', {}).get('properties', {})
task_paths = config.get('tasks', {}).get('paths', {})
task_states = config.get('tasks', {}).get('states', {})

if args.verbose and vault_path:
    try:
        print(config)
    except UnicodeEncodeError:
        print("Configuration loaded (some characters cannot be displayed in this console)")
    print(f"Obsidian vault path: {vault_path}")

# Resolve the note path relative to vault if needed using Note static method
resolved_note_path = Note.resolve_note_path(args.note, vault_path, args.verbose)

# Process the task based on the selected action
action = None
if args.resolved:
    action = "resolved"
elif args.closed:
    action = "closed"

state_emoji = task_states.get(action)

# Determine if this is a team ticket (under "REVISIÓN DE TICKETS")
# Check if "REVISIÓN DE TICKETS" is one of the folder names in the path
path_parts = os.path.normpath(resolved_note_path).split(os.sep)
is_team_ticket = "REVISIÓN DE TICKETS" in path_parts

if is_team_ticket:
    # Use team paths for tickets under "REVISIÓN DE TICKETS"
    target_path = task_paths.get('team', {}).get(action)
    if args.verbose:
        print(f"Detected team ticket - using team path for {action}")
        print(f"Path parts: {path_parts}")
else:
    # Use regular paths for personal tasks
    target_path = task_paths.get(action)
    if args.verbose:
        print(f"Detected personal task - using regular path for {action}")
        print(f"Path parts: {path_parts}")

print(f"Marking {resolved_note_path} as {action}.")

# Check if the note file exists
if not os.path.exists(resolved_note_path):
    print(f"Error: Note file '{resolved_note_path}' not found.")
    exit(1)

# Create a Note instance with the resolved path
note = Note(resolved_note_path, args.verbose)

# Load the content
try:
    content = note.get_content()
except FileNotFoundError:
    print(f"Error: Note file '{resolved_note_path}' not found.")
    exit(1)
except Exception as e:
    print(f"Error reading note: {e}")
    exit(1)

was_changed = False
if args.resolved:
   
    # Update the TASK_STATE property
    state_changed = note.set_property(task_props.get('state'), state_emoji, args.verbose)
    
    # Update the TASK_ENDDATE property to the current date and time in format YYYY-MM-DD HH:MM
    date_changed = note.set_property(task_props.get('end_date'), datetime.now().strftime("%Y-%m-%d %H:%M"), args.verbose)
    
    # Update the TASK_UPDATE property
    update_changed = note.set_property(task_props.get('update'), datetime.now().strftime("%Y-%m-%d %H:%M"), args.verbose)

    # Remove the TASK_NEXT_STEP and TASK_NEXT_DATE properties if they exist
    remove_next_step = note.remove_property(task_props.get('next_step'), args.verbose)
    remove_next_date = note.remove_property(task_props.get('next_date'), args.verbose)

    # Check if any change was made
    was_changed = state_changed or date_changed or update_changed or remove_next_step or remove_next_date

elif args.closed:
   
    # Update the TASK_STATE property
    state_changed = note.set_property(task_props.get('state'), state_emoji, args.verbose)
    
    # Update the TASK_UPDATE property
    update_changed = note.set_property(task_props.get('update'), datetime.now().strftime("%Y-%m-%d %H:%M"), args.verbose)

    # Remove the TASK_NEXT_STEP and TASK_NEXT_DATE properties if they exist
    remove_next_step = note.remove_property(task_props.get('next_step'), args.verbose)
    remove_next_date = note.remove_property(task_props.get('next_date'), args.verbose)
    
    # Check if any change was made
    was_changed = state_changed or update_changed or remove_next_step or remove_next_date

# Check if any change was made
if was_changed:
    # Write the updated content back to the file using Note method
    if note.write_content():
        print(f"Task marked as {action}: {resolved_note_path}")
        
        # Move the note to the appropriate path using Note static method
        if target_path:
            moved_path = Note.move_note_to_folder(resolved_note_path, target_path, vault_path, args.verbose)
            if moved_path:
                if is_team_ticket:
                    print(f"Team ticket moved to: {moved_path}")
                else:
                    print(f"Personal task moved to: {moved_path}")
            else:
                print(f"Warning: Failed to move note to {action} folder")
        else:
            if is_team_ticket:
                print(f"Warning: No team {action} path configured in config.yaml")
            else:
                print(f"Warning: No {action} path configured in config.yaml")
    else:
        print(f"Error: Failed to write changes to {resolved_note_path}")
        exit(1)
else:
    print(f"No changes were needed - task was already {action}.")
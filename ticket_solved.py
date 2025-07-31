import argparse
from datetime import datetime
import os

# Import functions from our notes module
from modules.ticket_functions import read_note_content, remove_property, update_property_value, write_note_content, load_obsidian_config, get_obsidian_vault_path, resolve_note_path, move_note_to_folder
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

# Load configuration
config = load_obsidian_config()
vault_path = get_obsidian_vault_path(config)

# Get task properties from configuration
task_props = config.get('tasks', {}).get('properties', {})
task_paths = config.get('tasks', {}).get('paths', {})
task_states = config.get('tasks', {}).get('states', {})

if args.verbose and vault_path:
    print(config)
    print(f"Obsidian vault path: {vault_path}")

# Resolve the note path relative to vault if needed
resolved_note_path = resolve_note_path(args.note, vault_path, args.verbose)

# Process the task based on the selected action
if args.resolved or args.closed:
    action = "resolved" if args.resolved else "closed"
    state_emoji = task_states.get(action)  # Fallback to default if not in config
    target_path = task_paths.get('solved') if args.resolved else task_paths.get('closed')
    
    print(f"Marking {resolved_note_path} as {action}.")
    
    # Check if the note file exists
    if not os.path.exists(resolved_note_path):
        print(f"Error: Note file '{resolved_note_path}' not found.")
        exit(1)
    
    # Read the note content
    content = read_note_content(resolved_note_path)
    if content is None:
        exit(1)
    
    # Create a Note instance
    note = Note(content)
    
    # Update the TASK_STATE property
    state_changed = update_property_value(note, task_props.get('state'), state_emoji, args.verbose)
    
    # Update the TASK_ENDDATE property to the current date and time in format YYYY-MM-DD HH:MM
    date_changed = update_property_value(note, task_props.get('end_date'), datetime.now().strftime("%Y-%m-%d %H:%M"), args.verbose)
    
    # Update the TASK_UPDATE property
    update_changed = update_property_value(note, task_props.get('update'), datetime.now().strftime("%Y-%m-%d %H:%M"), args.verbose)

    # Remove the TASK_NEXT_STEP and TASK_NEXT_DATE properties if they exist
    remove_next_step = remove_property(note, task_props.get('next_step'), args.verbose)
    remove_next_date = remove_property(note, task_props.get('next_date'), args.verbose)

    # Check if any change was made
    was_changed = state_changed or date_changed or update_changed or remove_next_step or remove_next_date

    if was_changed:
        # Write the updated content back to the file
        if write_note_content(resolved_note_path, note.content):
            print(f"Task marked as {action}: {resolved_note_path}")
            
            # Move the note to the appropriate path
            if target_path:
                moved_path = move_note_to_folder(resolved_note_path, target_path, vault_path, args.verbose)
                if moved_path:
                    print(f"Note moved to: {moved_path}")
                else:
                    print(f"Warning: Failed to move note to {action} folder")
            else:
                print(f"Warning: No {action} path configured in config.yaml")
        else:
            exit(1)
    else:
        print(f"No changes were needed - task was already {action}.")
        
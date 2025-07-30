import argparse
from datetime import datetime
import os

# Import functions from our notes module
from notes_functions import read_note_content, update_property_value, write_note_content, load_obsidian_config, get_obsidian_vault_path, resolve_note_path, move_note_to_folder

# Custom properties
TASK_ENDDATE = "fecha_realizacion"
TASK_SELECTED ="seleccionada"
TASK_PRIORITY = "prioridad"
TASK_STATE = "estado"

SOLVED_PATH = "TAREAS/Completadas/Tickets"

# Configure command line arguments
parser = argparse.ArgumentParser(description='Process Obsidian note')
parser.add_argument('-n', '--note', 
                    type=str, 
                    required=True,
                    help='Path to the Obsidian note')
parser.add_argument('-r', '--resolved',
                    action='store_true',
                    help='Mark the task as resolved')
parser.add_argument('-v', '--verbose',
                    action='store_true',
                    help='Enable verbose output')

# Parse arguments
args = parser.parse_args()

# Load configuration
config = load_obsidian_config()
vault_path = get_obsidian_vault_path(config)

if args.verbose and vault_path:
    print(config)
    print(f"Obsidian vault path: {vault_path}")

# Resolve the note path relative to vault if needed
resolved_note_path = resolve_note_path(args.note, vault_path, args.verbose)


# If set as resolved, update some properties from Obsidian note frontmatter
if args.resolved:
    print(f"Marking {resolved_note_path} as resolved.")
    
    # Check if the note file exists
    if not os.path.exists(resolved_note_path):
        print(f"Error: Note file '{resolved_note_path}' not found.")
        exit(1)
    
    # Read the note content
    content = read_note_content(resolved_note_path)
    if content is None:
        exit(1)
    
    # Update the TASK_STATE property to resolved
    new_content, state_changed = update_property_value(content, TASK_STATE, "✔️", args.verbose)
    
    # Update the TASK_ENDDATE property to the current date and time in format YYYY-MM-DD HH:MM
    new_content, date_changed = update_property_value(new_content, TASK_ENDDATE, datetime.now().strftime("%Y-%m-%d %H:%M"), args.verbose)

    # Remove the property TASK_SELECTED if it exists
    #new_content, selected_removed = update_property_value(new_content, TASK_SELECTED, verbose=args.verbose)
    # Remove the property TASK_PRIORITY if it exists
    #new_content, priority_removed = update_property_value(new_content, TASK_PRIORITY, verbose=args.verbose)

    # Check if any change was made
    #was_changed = state_changed or date_changed or selected_removed or priority_removed
    was_changed = state_changed or date_changed
    
    if was_changed:
        # Write the updated content back to the file
        if write_note_content(resolved_note_path, new_content):
            print(f"Task marked as resolved: {resolved_note_path}")
            
            # Move the note to the solved path
            moved_path = move_note_to_folder(resolved_note_path, SOLVED_PATH, vault_path, args.verbose)
            if moved_path:
                print(f"Note moved to: {moved_path}")
            else:
                print("Warning: Failed to move note to solved folder")
        else:
            exit(1)
    else:
        missing_properties: list[str] = []
        if not state_changed:
            missing_properties.append(TASK_STATE)
        if not date_changed:
            missing_properties.append(TASK_ENDDATE)
        
        print(f"Warning: Properties {', '.join(missing_properties)} not found in frontmatter of {resolved_note_path}")

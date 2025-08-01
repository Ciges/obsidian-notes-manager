import argparse
import os

# Import functions from our notes module
from modules.note import Note
from modules.vault import Vault

# Configure command line arguments
parser = argparse.ArgumentParser(description='Uncheck all tasks in an Obsidian note')
parser.add_argument('-n', '--note', 
                    type=str, 
                    required=True,
                    help='Path to the Obsidian note')
parser.add_argument('-v', '--verbose',
                    action='store_true',
                    help='Enable verbose output')

# Parse arguments
args = parser.parse_args()

# Load configuration using Vault static methods
config = Vault.load_obsidian_config()
vault_path = Vault.get_obsidian_vault_path(config)

if args.verbose and vault_path:
    try:
        print(config)
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
    content = note.get_content()
except FileNotFoundError:
    print(f"Error: Note file '{resolved_note_path}' not found.")
    exit(1)
except Exception as e:
    print(f"Error reading note: {e}")
    exit(1)

# Pattern to find checked tasks: ^\s*-\s*\[[px\-dc]\]
# We'll use a capture group to preserve the leading whitespace and dash
task_pattern = r'^(\s*-\s*)\[[px\-dc]\]'

# Count current checked tasks before replacement
checked_tasks = note.find(task_pattern)
match_count = len(checked_tasks)

if args.verbose:
    print(f"Found {match_count} checked tasks to uncheck")
    if match_count > 0:
        print("Checked tasks found:")
        for task in checked_tasks[:5]:  # Show first 5 tasks
            print(f"  - {task.strip()}")
        if match_count > 5:
            print(f"  ... and {match_count - 5} more")

if match_count > 0:
    # Use the new replace function to uncheck tasks
    # Replace [x], [p], [-], [d], [c] with [ ]
    modified_lines = note.replace(task_pattern, r'\1[ ]')
    
    # Check if any changes were made
    if modified_lines:
        # Write the updated content back to the file using Note method
        if note.write_content():
            print(f"Successfully unchecked {len(modified_lines)} tasks in: {resolved_note_path}")
            
            if args.verbose:
                print("Modified lines:")
                for line in modified_lines[:5]:  # Show first 5 modified lines
                    print(f"  - {line.strip()}")
                if len(modified_lines) > 5:
                    print(f"  ... and {len(modified_lines) - 5} more")
        else:
            print("Error: Failed to write updated content to file")
            exit(1)
    else:
        print("Error: No changes were made despite finding checked tasks")
        exit(1)
else:
    print("No checked tasks found to uncheck")

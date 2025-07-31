import argparse
import os
import re

# Import functions from our notes module
from modules.ticket_functions import read_note_content, write_note_content, load_obsidian_config, get_obsidian_vault_path, resolve_note_path
from modules.note import Note

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

# Load configuration
config = load_obsidian_config()
vault_path = get_obsidian_vault_path(config)

if args.verbose and vault_path:
    print(config)
    print(f"Obsidian vault path: {vault_path}")

# Resolve the note path relative to vault if needed
resolved_note_path = resolve_note_path(args.note, vault_path, args.verbose)

print(f"Processing note: {resolved_note_path}")

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

# Pattern to match frontmatter between --- and --- (accounting for different line endings)
frontmatter_pattern = r'^(---(?:\r\n|\r|\n).*?^---(?:\r\n|\r|\n))'

# Find the frontmatter section
frontmatter_match = re.search(frontmatter_pattern, note.content, flags=re.DOTALL | re.MULTILINE)

if frontmatter_match:
    # Split content into frontmatter and body
    frontmatter = frontmatter_match.group(1)
    body_start = frontmatter_match.end()
    body = note.content[body_start:]
    
    if args.verbose:
        print("Found frontmatter, processing body content only")
else:
    # No frontmatter, process entire content
    frontmatter = ""
    body = note.content
    
    if args.verbose:
        print("No frontmatter found, processing entire content")

# Pattern to find checked tasks: ^\s*-\s*\[[px\-dc]\]
task_pattern = r'^(\s*-\s*)\[[px\-dc]\]'

# Count matches before replacement
matches = re.findall(task_pattern, body, flags=re.MULTILINE)
match_count = len(matches)

if args.verbose:
    print(f"Found {match_count} checked tasks to uncheck")

# Replace with unchecked tasks: "- [ ]"
new_body = re.sub(task_pattern, r'\1[ ]', body, flags=re.MULTILINE)

# Check if any changes were made
was_changed = new_body != body

if was_changed:
    # Reconstruct the full content
    note.content = frontmatter + new_body
    
    # Write the updated content back to the file
    if write_note_content(resolved_note_path, note.content):
        print(f"Successfully unchecked {match_count} tasks in: {resolved_note_path}")
    else:
        print("Error: Failed to write updated content to file")
        exit(1)
else:
    print("No checked tasks found to uncheck")

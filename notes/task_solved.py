import argparse
from datetime import datetime
import re
import os

# Custom properties
TASK_ENDDATE = "fecha_realizacion"
TASK_SELECTED ="seleccionada"
TASK_PRIORITY = "prioridad"
TASK_STATE = "estado"

from typing import Optional

def read_note_content(file_path: str) -> Optional[str]:
    """Read the content of an Obsidian note file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        print(f"Error reading file '{file_path}': {e}")
        return None

def update_property_value(content: str, property_name: str, new_value: Optional[str] = None, verbose: bool = False) -> tuple[str, bool]:
    """Update a property value in the frontmatter using regex."""
    # Pattern to match frontmatter between --- and ---
    frontmatter_pattern = r'^(---\s*\n)(.*?)(^---\s*\n)'
    
    # Find the frontmatter section
    frontmatter_match = re.search(frontmatter_pattern, content, flags=re.DOTALL | re.MULTILINE)
    
    if not frontmatter_match:
        if verbose:
            print(f"Warning: No frontmatter found in the note")
        return content, False
    
    # Extract frontmatter content
    frontmatter_start = frontmatter_match.group(1)
    frontmatter_body = frontmatter_match.group(2)
    frontmatter_end = frontmatter_match.group(3)
    
    # Pattern to find the specific property within frontmatter (entire line)
    property_pattern = rf'^{re.escape(property_name)}\s*:.*$'
    
    # Check if the property exists in the frontmatter
    if re.search(property_pattern, frontmatter_body, flags=re.MULTILINE):
        if new_value is None:
            # Remove the property completely (delete the entire line)
            if verbose:
                print(f"Info: Removing property '{property_name}' from frontmatter")
            new_frontmatter_body = re.sub(property_pattern + r'\n?', '', frontmatter_body, flags=re.MULTILINE)
        else:
            # Property exists, replace its value
            value_pattern = rf'^({re.escape(property_name)}\s*:\s*)(.*)$'
            new_frontmatter_body = re.sub(value_pattern, rf'\1{new_value}', frontmatter_body, flags=re.MULTILINE)
        
        was_changed = new_frontmatter_body != frontmatter_body
        
        if was_changed:
            # Reconstruct the full content with updated frontmatter
            new_content = content.replace(
                frontmatter_match.group(0),
                frontmatter_start + new_frontmatter_body + frontmatter_end
            )
            return new_content, True
        
        return content, False
    else:
        if new_value is None:
            # Property doesn't exist and we want to remove it, nothing to do
            if verbose:
                print(f"Info: Property '{property_name}' not found, nothing to remove")
            return content, False
        else:
            # Property doesn't exist, add it at the end of the frontmatter
            if verbose:
                print(f"Info: Property '{property_name}' not found, adding it to frontmatter")
            
            # Add the new property at the end of the frontmatter body
            # Ensure there's a newline before adding the new property
            if frontmatter_body and not frontmatter_body.endswith('\n'):
                new_frontmatter_body = frontmatter_body + '\n' + f'{property_name}: {new_value}\n'
            else:
                new_frontmatter_body = frontmatter_body + f'{property_name}: {new_value}\n'
            
            # Reconstruct the full content with the new property
            new_content = content.replace(
                frontmatter_match.group(0),
                frontmatter_start + new_frontmatter_body + frontmatter_end
            )
            return new_content, True

def write_note_content(file_path: str, content: str) -> bool:
    """Write content to an Obsidian note file."""
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)
        return True
    except Exception as e:
        print(f"Error writing file '{file_path}': {e}")
        return False

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


# If set as resolved, update some properties from Obsidian note frontmatter
if args.resolved:
    print(f"Marking {args.note} as resolved.")
    
    # Check if the note file exists
    if not os.path.exists(args.note):
        print(f"Error: Note file '{args.note}' not found.")
        exit(1)
    
    # Read the note content
    content = read_note_content(args.note)
    if content is None:
        exit(1)
    
    # Update the TASK_STATE property to resolved
    new_content, state_changed = update_property_value(content, TASK_STATE, "✔️", args.verbose)
    
    # Update the TASK_ENDDATE property to the current date and time in format YYYY-MM-DD HH:MM
    new_content, date_changed = update_property_value(new_content, TASK_ENDDATE, datetime.now().strftime("%Y-%m-%d %H:%M"), args.verbose)

    # Remove the property TASK_SELECTED if it exists
    new_content, selected_removed = update_property_value(new_content, TASK_SELECTED, verbose=args.verbose)
    # Remove the property TASK_PRIORITY if it exists
    new_content, priority_removed = update_property_value(new_content, TASK_PRIORITY, verbose=args.verbose)

    # Check if any change was made
    was_changed = state_changed or date_changed or selected_removed or priority_removed
    
    if was_changed:
        # Write the updated content back to the file
        if write_note_content(args.note, new_content):
            changes_made: list[str] = []
            if state_changed:
                changes_made.append(f"{TASK_STATE} to '✔️'")
            if date_changed:
                changes_made.append(f"{TASK_ENDDATE} to current date")
            if selected_removed:
                changes_made.append(f"removed {TASK_SELECTED}")
            if priority_removed:
                changes_made.append(f"removed {TASK_PRIORITY}")
            
            print(f"Successfully updated {' and '.join(changes_made)} in {args.note}")
        else:
            exit(1)
    else:
        missing_properties: list[str] = []
        if not state_changed:
            missing_properties.append(TASK_STATE)
        if not date_changed:
            missing_properties.append(TASK_ENDDATE)
        
        print(f"Warning: Properties {', '.join(missing_properties)} not found in frontmatter of {args.note}")

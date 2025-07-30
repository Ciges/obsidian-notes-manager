import re
import configparser
import os
import shutil
from typing import Optional, Dict

def read_note_content(file_path: str) -> Optional[str]:
    """Read the content of an Obsidian note file."""
    try:
        with open(file_path, 'r', encoding='utf-8', newline='') as file:
            return file.read()
    except Exception as e:
        print(f"Error reading file '{file_path}': {e}")
        return None

def detect_line_ending(content: str) -> str:
    """Detect the line ending style used in the content."""
    if '\r\n' in content:
        return '\r\n'  # Windows
    elif '\n' in content:
        return '\n'    # Unix/Linux/Mac
    elif '\r' in content:
        return '\r'    # Classic Mac
    else:
        return '\n'    # Default to Unix if no line endings found

def update_property_value(content: str, property_name: str, new_value: Optional[str] = None, verbose: bool = False) -> tuple[str, bool]:
    """Update a property value in the frontmatter using regex."""
    # Detect the original line ending style
    line_ending = detect_line_ending(content)
    
    # Pattern to match frontmatter between --- and --- (accounting for different line endings)
    frontmatter_pattern = r'^(---(?:\r\n|\r|\n))(.*?)(^---(?:\r\n|\r|\n))'
    
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
            # Use flexible line ending pattern for removal
            new_frontmatter_body = re.sub(property_pattern + r'(?:\r\n|\r|\n)?', '', frontmatter_body, flags=re.MULTILINE)
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
            
            # Add the new property at the end of the frontmatter body using original line endings
            # Ensure there's a newline before adding the new property
            if frontmatter_body and not frontmatter_body.endswith(('\n', '\r\n', '\r')):
                new_frontmatter_body = frontmatter_body + line_ending + f'{property_name}: {new_value}{line_ending}'
            else:
                new_frontmatter_body = frontmatter_body + f'{property_name}: {new_value}{line_ending}'
            
            # Reconstruct the full content with the new property
            new_content = content.replace(
                frontmatter_match.group(0),
                frontmatter_start + new_frontmatter_body + frontmatter_end
            )
            return new_content, True

def write_note_content(file_path: str, content: str) -> bool:
    """Write content to an Obsidian note file."""
    try:
        with open(file_path, 'w', encoding='utf-8', newline='') as file:
            file.write(content)
        return True
    except Exception as e:
        print(f"Error writing file '{file_path}': {e}")
        return False

def load_obsidian_config(config_file: str = 'obsidian.ini') -> Dict[str, Dict[str, str]]:
    """Load configuration from obsidian.ini file."""
    config = configparser.ConfigParser()
    
    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, config_file)
    
    try:
        if os.path.exists(config_path):
            config.read(config_path, encoding='utf-8')
            # Convert to a regular dictionary for easier access
            config_dict: Dict[str, Dict[str, str]] = {}
            for section in config.sections():
                config_dict[section] = dict(config[section])
            return config_dict
        else:
            print(f"Warning: Configuration file '{config_path}' not found")
            return {}
    except Exception as e:
        print(f"Error reading configuration file '{config_path}': {e}")
        return {}

def get_obsidian_vault_path(config: Optional[Dict[str, Dict[str, str]]] = None) -> Optional[str]:
    """Get the Obsidian vault path from configuration."""
    if config is None:
        config = load_obsidian_config()
    
    if 'obsidian' in config and 'obsidian_vault' in config['obsidian']:
        return config['obsidian']['obsidian_vault']
    else:
        print("Warning: obsidian_vault not found in configuration")
        return None

def resolve_note_path(note_path: str, vault_path: Optional[str] = None, verbose: bool = False) -> str:
    """Resolve note path relative to Obsidian vault if needed."""
    if vault_path is None:
        vault_path = get_obsidian_vault_path()
    
    # If vault_path is still None, return the original path
    if vault_path is None:
        if verbose:
            print("Warning: Cannot resolve vault path, using note path as-is")
        return note_path
    
    # Convert to absolute paths for comparison
    abs_note_path = os.path.abspath(note_path)
    abs_vault_path = os.path.abspath(vault_path)
    
    # Check if the note path is already within the vault
    if abs_note_path.startswith(abs_vault_path):
        if verbose:
            print(f"Note path is already within vault: {abs_note_path}")
        return abs_note_path
    else:
        # Note path is relative to vault root
        resolved_path = os.path.join(abs_vault_path, note_path)
        abs_resolved_path = os.path.abspath(resolved_path)
        if verbose:
            print(f"Resolved relative path '{note_path}' to: {abs_resolved_path}")
        return abs_resolved_path

def move_note_to_folder(note_path: str, destination_folder: str, vault_path: Optional[str] = None, verbose: bool = False) -> Optional[str]:
    """Move a note to a destination folder within the vault."""
    if vault_path is None:
        vault_path = get_obsidian_vault_path()
        if vault_path is None:
            print("Error: Cannot resolve vault path for moving file")
            return None
    
    # Ensure destination folder is relative to vault
    abs_vault_path = os.path.abspath(vault_path)
    destination_path = os.path.join(abs_vault_path, destination_folder)
    
    # Create destination directory if it doesn't exist
    try:
        os.makedirs(destination_path, exist_ok=True)
        if verbose:
            print(f"Ensured destination directory exists: {destination_path}")
    except Exception as e:
        print(f"Error creating destination directory '{destination_path}': {e}")
        return None
    
    # Get the filename from the note path
    filename = os.path.basename(note_path)
    destination_file = os.path.join(destination_path, filename)
    
    # Check if destination file already exists
    if os.path.exists(destination_file):
        print(f"Warning: Destination file already exists: {destination_file}")
        # Generate a unique filename
        base, ext = os.path.splitext(filename)
        counter = 1
        while os.path.exists(destination_file):
            new_filename = f"{base}_{counter}{ext}"
            destination_file = os.path.join(destination_path, new_filename)
            counter += 1
        if verbose:
            print(f"Using unique filename: {os.path.basename(destination_file)}")
    
    # Move the file
    try:
        shutil.move(note_path, destination_file)
        if verbose:
            print(f"Moved file from '{note_path}' to '{destination_file}'")
        return destination_file
    except Exception as e:
        print(f"Error moving file from '{note_path}' to '{destination_file}': {e}")
        return None

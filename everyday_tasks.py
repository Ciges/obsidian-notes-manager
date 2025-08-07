import argparse
import os
import sys
from typing import Dict, Any, Optional, List, cast

# Import functions from our modules
from modules.vault import Vault
from modules.note import Note

# Set UTF-8 encoding for output (Windows compatibility)
if sys.platform.startswith('win'):
    # Try to set UTF-8 output encoding for Windows console
    try:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except AttributeError:
        # For older Python versions
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Configure command line arguments
parser = argparse.ArgumentParser(description='List Obsidian notes with prioridad "🔁" in a specified path')
parser.add_argument('-p', '--path', 
                    type=str, 
                    required=False,
                    help='Path to search for Obsidian notes (relative to vault root or absolute path). If not specified, searches the entire vault.')
parser.add_argument('-v', '--verbose',
                    action='store_true',
                    help='Enable verbose output')
parser.add_argument('-r', '--recursive',
                    action='store_true',
                    default=True,
                    help='Search recursively in subdirectories (default: True)')
parser.add_argument('--no-recursive',
                    action='store_false',
                    dest='recursive',
                    help='Search only in the specified directory, not subdirectories')
parser.add_argument('-s', '--state',
                    type=str,
                    choices=['resolved', 'closed', 'waiting'],
                    help='Set the state property of found notes to the specified value (resolved, closed, waiting)')

# Parse arguments
args = parser.parse_args()

# Load configuration using Vault static methods
config: Dict[str, Any] = Vault.load_obsidian_config()
vault_path: Optional[str] = Vault.get_obsidian_vault_path(config)

if not vault_path:
    print("Error: Could not determine vault path from configuration")
    exit(1)

# Get configuration values for states and properties
state_property_name: Optional[str] = None
state_emoji: Optional[str] = None

if args.state:
    try:
        # Debug: Print the entire config structure if verbose
        if args.verbose:
            print(f"Debug: Full config structure: {config}")
            print(f"Debug: Tasks section: {config.get('tasks', 'NOT FOUND')}")
            if 'tasks' in config:
                tasks_config_raw = config['tasks']
                if isinstance(tasks_config_raw, dict):
                    tasks_config = cast(Dict[str, Any], tasks_config_raw)
                    # Explicitly cast tasks_config_raw to Dict[str, Any] before using
                    tasks_config_typed: Dict[str, Any] = cast(Dict[str, Any], tasks_config_raw)
                    print(f"Debug: Tasks properties: {tasks_config_typed.get('properties', 'NOT FOUND')}")
                    print(f"Debug: Tasks states: {cast(Dict[str, Any], tasks_config_raw).get('states', 'NOT FOUND')}")
        
        # Check if tasks section exists
        if 'tasks' not in config:
            print("Error: 'tasks' section not found in configuration")
            exit(1)
        
        tasks_config_raw = config['tasks']
        if not isinstance(tasks_config_raw, dict):
            print("Error: 'tasks' section is not a dictionary")
            exit(1)
        
        # Cast to proper type after validation
        tasks_config: Dict[str, Any] = cast(Dict[str, Any], tasks_config_raw)
        
        # Check if properties and states subsections exist
        if 'properties' not in tasks_config:
            print("Error: 'tasks.properties' section not found in configuration")
            exit(1)
            
        if 'states' not in tasks_config:
            print("Error: 'tasks.states' section not found in configuration")
            exit(1)
        
        properties_config_raw = tasks_config['properties']
        states_config_raw = tasks_config['states']
        
        if not isinstance(properties_config_raw, dict):
            print("Error: 'tasks.properties' section is not a dictionary")
            exit(1)
            
        if not isinstance(states_config_raw, dict):
            print("Error: 'tasks.states' section is not a dictionary")
            exit(1)
        
        # Cast to proper types after validation
        properties_config: Dict[str, Any] = cast(Dict[str, Any], properties_config_raw)
        states_config: Dict[str, Any] = cast(Dict[str, Any], states_config_raw)
        
        # Get the property name for state from config
        if 'state' not in properties_config:
            print("Error: 'tasks.properties.state' not found in configuration")
            exit(1)
        
        state_property_name_raw = properties_config['state']
        
        if not isinstance(state_property_name_raw, str):
            print("Error: 'tasks.properties.state' is not a string")
            exit(1)
        
        # Assign directly since type is already validated as str
        state_property_name = state_property_name_raw
        
        # Get the emoji for the specified state
        if args.state not in states_config:
            available_states: List[str] = list(cast(Dict[str, str], states_config).keys())
            print(f"Error: State '{args.state}' not found in configuration")
            print(f"Available states: {available_states}")
            exit(1)
        
        state_emoji_raw = states_config[args.state]
        
        if not isinstance(state_emoji_raw, str):
            print(f"Error: State '{args.state}' value is not a string")
            exit(1)
        
        # Assign directly since type is already validated as str
        state_emoji = state_emoji_raw
        
        if args.verbose:
            print(f"Configuration loaded successfully:")
            print(f"  State property name: '{state_property_name}'")
            print(f"  State '{args.state}' emoji: '{state_emoji}'")
            
    except Exception as e:
        print(f"Error accessing configuration: {e}")
        print("Please check your config.yaml file structure")
        if args.verbose:
            import traceback
            traceback.print_exc()
        exit(1)

# Set default path to vault root if not specified
search_path = args.path if args.path else "."

if args.verbose:
    print(f"Vault path: {vault_path}")
    print(f"Search path: {search_path} {'(vault root)' if not args.path else ''}")
    print(f"Recursive search: {args.recursive}")
    print(f"Filter: Notes with prioridad '🔁'")
    if args.state:
        print(f"Action: Set state to '{args.state}' ({state_emoji})")
    print()

# Create Vault instance
try:
    vault = Vault(vault_path, args.verbose)
except (FileNotFoundError, ValueError) as e:
    print(f"Error initializing vault: {e}")
    exit(1)

# Function to print with Unicode fallbacks
def safe_print(message: str) -> None:
    """Print message with Unicode character fallbacks for Windows."""
    try:
        print(message)
    except UnicodeEncodeError:
        # Use UTF-8 encoding with error replacement to handle problematic characters
        try:
            # Try to encode as UTF-8 and print
            encoded = message.encode('utf-8', errors='replace')
            decoded = encoded.decode('utf-8')
            print(decoded)
        except:
            # Last resort: use the system's default encoding with replacement
            print(message.encode(sys.stdout.encoding or 'utf-8', errors='replace').decode(sys.stdout.encoding or 'utf-8'))

# List notes in the specified path
try:
    all_notes = vault.list_notes(search_path, args.recursive)
    
    if args.verbose:
        safe_print(f"Found {len(all_notes)} total notes, checking prioridad...")
    
    # Filter notes by priority "🔁"
    priority_notes: List[str] = []

    for note_path in all_notes:
        try:
            # Create Note instance to check properties
            note = Note(note_path, verbose=False)  # Set verbose=False to avoid spam
            properties = note.get_properties()
            
            # Check if note has prioridad property with value "🔁"
            if properties and 'prioridad' in properties:
                priority_value = properties['prioridad']
                if priority_value == "🔁":
                    priority_notes.append(note_path)
                    if args.verbose:
                        safe_print(f"Found priority note: {os.path.relpath(note_path, vault_path)}")
                elif args.verbose:
                    safe_print(f"Different priority ({priority_value}): {os.path.relpath(note_path, vault_path)}")
            elif args.verbose:
                safe_print(f"No prioridad property: {os.path.relpath(note_path, vault_path)}")
                
        except Exception as e:
            if args.verbose:
                safe_print(f"Error reading note {note_path}: {e}")
            continue
    
    # Process state changes if requested
    if args.state and priority_notes:
        safe_print(f"\nUpdating state for {len(priority_notes)} notes...")
        safe_print("-" * 60)
        
        updated_count = 0
        failed_count = 0
        skipped_count = 0

        for note_path in priority_notes:
            try:
                # Create Note instance for modification
                note = Note(note_path, verbose=args.verbose)
                
                # Set the state property
                if state_property_name is None:
                    safe_print("Error: 'state_property_name' is not defined")
                    continue
                
                # Get current properties to check existing state
                current_properties = note.get_properties()
                current_state: Optional[str] = current_properties.get(state_property_name) if current_properties else None
                
                relative_path = os.path.relpath(note_path, vault_path)
                
                # Check if the note already has the requested state
                if current_state == state_emoji:
                    skipped_count += 1
                    safe_print(f"Skipped: {relative_path} (already has {state_property_name}: {current_state})")
                    continue
                
                # Update state property
                state_success = note.set_property(state_property_name, state_emoji, verbose=args.verbose)

                if state_success:
                    # Write changes to disk
                    write_success = note.write_content()
                    if write_success:
                        updated_count += 1
                        
                        # Show what was updated
                        old_state_info = f" (was: {current_state})" if current_state else ""
                        safe_print(f"Updated: {relative_path} -> {state_property_name}: {state_emoji}{old_state_info}")
                    else:
                        failed_count += 1
                        safe_print(f"Failed to write: {relative_path}")
                else:
                    failed_count += 1
                    safe_print(f"No changes made: {relative_path}")
                
            except Exception as e:
                failed_count += 1
                relative_path = os.path.relpath(note_path, vault_path)
                safe_print(f"Error updating {relative_path}: {str(e)}")
        
        safe_print("-" * 60)
        safe_print(f"State update summary:")
        safe_print(f"  Successfully updated: {updated_count}")
        safe_print(f"  Skipped (already correct): {skipped_count}")
        safe_print(f"  Failed to update: {failed_count}")
        safe_print(f"  Total processed: {len(priority_notes)}")
    
    # Display results
    elif priority_notes:
        safe_print(f"Found {len(priority_notes)} notes with prioridad '🔁':")
        safe_print("-" * 60)
        
        for i, note_path in enumerate(priority_notes, 1):
            # Get relative path from vault root for cleaner display
            try:
                relative_path = os.path.relpath(note_path, vault_path)
                safe_print(f"{i:3d}. {relative_path}")
            except ValueError:
                # If relative path calculation fails, show absolute path
                safe_print(f"{i:3d}. {note_path}")
        
        safe_print("-" * 60)
        safe_print(f"Total: {len(priority_notes)} priority notes")
        
        if args.verbose and len(all_notes) > 0:
            percentage = (len(priority_notes) / len(all_notes)) * 100
            safe_print(f"Percentage: {percentage:.1f}% of all notes have prioridad '🔁'")
        
        if args.state:
            safe_print(f"\nInfo: Use -s {args.state} to update all found notes to state '{state_emoji}'")
        
    else:
        search_location = args.path if args.path else "vault root"
        safe_print(f"No notes with prioridad '🔁' found in: {search_location}")
        if args.verbose and len(all_notes) > 0:
            safe_print(f"Checked {len(all_notes)} total notes")

except Exception as e:
    safe_print(f"Error listing notes: {e}")
    if args.verbose:
        import traceback
        traceback.print_exc()
    exit(1)
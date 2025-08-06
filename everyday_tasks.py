import argparse
import os

# Import functions from our modules
from modules.vault import Vault
from modules.note import Note

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
config = Vault.load_obsidian_config()
vault_path = Vault.get_obsidian_vault_path(config)

if not vault_path:
    print("Error: Could not determine vault path from configuration")
    exit(1)

# Get configuration values for states and properties
state_property_name = None
state_emoji = None

if args.state:
    try:
        # Debug: Print the entire config structure if verbose
        if args.verbose:
            print(f"Debug: Full config structure: {config}")
            print(f"Debug: Tasks section: {config.get('tasks', 'NOT FOUND')}")
            if 'tasks' in config:
                print(f"Debug: Tasks properties: {config['tasks'].get('properties', 'NOT FOUND')}")
                print(f"Debug: Tasks states: {config['tasks'].get('states', 'NOT FOUND')}")
        
        # Check if tasks section exists
        if 'tasks' not in config:
            print("Error: 'tasks' section not found in configuration")
            exit(1)
        
        # Check if properties and states subsections exist
        if 'properties' not in config['tasks']:
            print("Error: 'tasks.properties' section not found in configuration")
            exit(1)
            
        if 'states' not in config['tasks']:
            print("Error: 'tasks.states' section not found in configuration")
            exit(1)
        
        # Get the property name for state from config
        if 'state' not in config['tasks']['properties']:
            print("Error: 'tasks.properties.state' not found in configuration")
            exit(1)
        state_property_name = config['tasks']['properties']['state']
        
        # Get the emoji for the specified state
        if args.state not in config['tasks']['states']:
            available_states = list(config['tasks']['states'].keys())
            print(f"Error: State '{args.state}' not found in configuration")
            print(f"Available states: {available_states}")
            exit(1)
        state_emoji = config['tasks']['states'][args.state]
        
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

# List notes in the specified path
try:
    all_notes = vault.list_notes(search_path, args.recursive)
    
    if args.verbose:
        print(f"Found {len(all_notes)} total notes, checking prioridad...")
    
    # Filter notes by priority "🔁"
    priority_notes: list[str] = []

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
                        print(f"Found priority note: {os.path.relpath(note_path, vault_path)}")
                elif args.verbose:
                    print(f"Different priority ({priority_value}): {os.path.relpath(note_path, vault_path)}")
            elif args.verbose:
                print(f"No prioridad property: {os.path.relpath(note_path, vault_path)}")
                
        except Exception as e:
            if args.verbose:
                print(f"Error reading note {note_path}: {e}")
            continue
    
    # Process state changes if requested
    if args.state and priority_notes:
        print(f"\nUpdating state for {len(priority_notes)} notes...")
        print("-" * 60)
        
        updated_count = 0
        failed_count = 0
        skipped_count = 0
        
        for note_path in priority_notes:
            try:
                # Create Note instance for modification
                note = Note(note_path, verbose=args.verbose)
                
                # Set the state property
                if state_property_name is None:
                    print("Error: 'state_property_name' is not defined")
                    continue
                
                # Get current properties to check existing state
                current_properties = note.get_properties()
                current_state = current_properties.get(state_property_name) if current_properties else None
                
                relative_path = os.path.relpath(note_path, vault_path)
                
                # Check if the note already has the requested state
                if current_state == state_emoji:
                    skipped_count += 1
                    print(f"Skipped: {relative_path} (already has {state_property_name}: {state_emoji})")
                    continue
                
                # Update state property (updated will be handled automatically by write_content)
                state_success = note.set_property(state_property_name, state_emoji, verbose=args.verbose)
                
                if state_success:
                    # Write changes to disk (this will automatically update 'updated' property)
                    write_success = note.write_content()
                    if write_success:
                        updated_count += 1
                        
                        # Show what was updated
                        old_state_info = f" (was: {current_state})" if current_state else ""
                        print(f"Updated: {relative_path} -> {state_property_name}: {state_emoji}{old_state_info}")
                    else:
                        failed_count += 1
                        print(f"Failed to write: {relative_path}")
                else:
                    failed_count += 1
                    print(f"No changes made: {relative_path}")
                    
            except Exception as e:
                failed_count += 1
                relative_path = os.path.relpath(note_path, vault_path)
                print(f"Error updating {relative_path}: {e}")
        
        print("-" * 60)
        print(f"State update summary:")
        print(f"  Successfully updated: {updated_count}")
        print(f"  Skipped (already correct): {skipped_count}")
        print(f"  Failed to update: {failed_count}")
        print(f"  Total processed: {len(priority_notes)}")
    
    # Display results
    elif priority_notes:
        print(f"Found {len(priority_notes)} notes with prioridad '🔁':")
        print("-" * 60)
        
        for i, note_path in enumerate(priority_notes, 1):
            # Get relative path from vault root for cleaner display
            try:
                relative_path = os.path.relpath(note_path, vault_path)
                print(f"{i:3d}. {relative_path}")
            except ValueError:
                # If relative path calculation fails, show absolute path
                print(f"{i:3d}. {note_path}")
        
        print("-" * 60)
        print(f"Total: {len(priority_notes)} priority notes")
        
        if args.verbose and len(all_notes) > 0:
            percentage = (len(priority_notes) / len(all_notes)) * 100
            print(f"Percentage: {percentage:.1f}% of all notes have prioridad '🔁'")
        
        if args.state:
            print(f"\nInfo: Use -s {args.state} to update all found notes to state '{state_emoji}'")
        
    else:
        search_location = args.path if args.path else "vault root"
        print(f"No notes with prioridad '🔁' found in: {search_location}")
        if args.verbose and len(all_notes) > 0:
            print(f"Checked {len(all_notes)} total notes")

except Exception as e:
    print(f"Error listing notes: {e}")
    if args.verbose:
        import traceback
        traceback.print_exc()
    exit(1)
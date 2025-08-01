import argparse
import os

# Import functions from our modules
from modules.vault import Vault

# Configure command line arguments
parser = argparse.ArgumentParser(description='List Obsidian notes in a specified path')
parser.add_argument('-p', '--path', 
                    type=str, 
                    required=True,
                    help='Path to search for Obsidian notes (relative to vault root or absolute path). This parameter is required.')
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

# Parse arguments
args = parser.parse_args()

# Load configuration using Vault static methods
config = Vault.load_obsidian_config()
vault_path = Vault.get_obsidian_vault_path(config)

if not vault_path:
    print("Error: Could not determine vault path from configuration")
    exit(1)

if args.verbose:
    print(f"Vault path: {vault_path}")
    print(f"Search path: {args.path}")
    print(f"Recursive search: {args.recursive}")
    print()

# Create Vault instance
try:
    vault = Vault(vault_path, args.verbose)
except (FileNotFoundError, ValueError) as e:
    print(f"Error initializing vault: {e}")
    exit(1)

# List notes in the specified path
try:
    notes = vault.list_notes(args.path, args.recursive)
    
    if notes:
        print(f"Found {len(notes)} Obsidian notes:")
        print("-" * 50)
        
        for i, note_path in enumerate(notes, 1):
            # Get relative path from vault root for cleaner display
            try:
                relative_path = os.path.relpath(note_path, vault_path)
                print(f"{i:3d}. {relative_path}")
            except ValueError:
                # If relative path calculation fails, show absolute path
                print(f"{i:3d}. {note_path}")
        
        print("-" * 50)
        print(f"Total: {len(notes)} notes")
        
    else:
        print(f"No Obsidian notes found in: {args.path}")

except Exception as e:
    print(f"Error listing notes: {e}")
    if args.verbose:
        import traceback
        traceback.print_exc()
    exit(1)
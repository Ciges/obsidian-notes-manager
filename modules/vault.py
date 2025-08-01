import os
import mimetypes
from typing import List, Optional, Dict, Any
from pathlib import Path

__version__ = "0.0.1"

class Vault:
    """
    A class to represent and interact with Obsidian vault.

    Attributes:
        path (str): The full path to the Obsidian vault folder.
        verbose (bool): Flag to enable verbose output for debugging.
    """

    def __init__(self, vault_path: str, verbose: bool = False):
        """
        Initialize the Vault object with the path of the Obsidian vault.
        
        Args:
            vault_path (str): The full path to the Obsidian vault folder.
            verbose (bool): Flag to enable verbose output for debugging.
        """
        self.verbose = verbose
        
        # Validate and set vault path
        self.path = os.path.abspath(vault_path)
        
        if not os.path.exists(self.path):
            raise FileNotFoundError(f"Vault path does not exist: {self.path}")
        
        if not os.path.isdir(self.path):
            raise ValueError(f"Vault path is not a directory: {self.path}")
        
        # Check if it looks like an Obsidian vault (has .obsidian folder)
        obsidian_config_path = os.path.join(self.path, '.obsidian')
        if not os.path.exists(obsidian_config_path):
            if self.verbose:
                print(f"Warning: No .obsidian folder found in {self.path}. This may not be a valid Obsidian vault.")
        
        if self.verbose:
            print(f"Vault initialized: {self.path}")

    def list_notes(self, search_path: Optional[str] = None, recursive: bool = True) -> List[str]:
        """
        List all Obsidian notes in a given path.
        
        Args:
            search_path (Optional[str]): Path to search for notes. If None, uses the vault path.
                                       Can be absolute or relative to vault root.
            recursive (bool): Whether to search recursively in subdirectories. Defaults to True.
            
        Returns:
            List[str]: List of absolute paths to Obsidian notes found.
        """
        # Determine the search path
        if search_path is None:
            target_path = self.path
        elif os.path.isabs(search_path):
            target_path = search_path
        else:
            # Relative path, join with vault path
            target_path = os.path.join(self.path, search_path)
        
        # Validate the search path exists
        if not os.path.exists(target_path):
            if self.verbose:
                print(f"Warning: Search path does not exist: {target_path}")
            return []
        
        if not os.path.isdir(target_path):
            if self.verbose:
                print(f"Warning: Search path is not a directory: {target_path}")
            return []
        
        notes: List[str] = []
        
        if recursive:
            # Recursive search using os.walk
            for root, dirs, files in os.walk(target_path):
                # Skip hidden directories (like .obsidian, .git, etc.)
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                
                for file in files:
                    file_path = os.path.join(root, file)
                    if self._is_obsidian_note(file_path):
                        notes.append(file_path)
        else:
            # Non-recursive search, only current directory
            try:
                for item in os.listdir(target_path):
                    item_path = os.path.join(target_path, item)
                    if os.path.isfile(item_path) and self._is_obsidian_note(item_path):
                        notes.append(item_path)
            except PermissionError:
                if self.verbose:
                    print(f"Warning: Permission denied accessing: {target_path}")
        
        # Sort the results for consistent output
        notes.sort()
        
        if self.verbose:
            print(f"Found {len(notes)} Obsidian notes in: {target_path}")
        
        return notes

    def _is_obsidian_note(self, file_path: str) -> bool:
        """
        Check if a file is an Obsidian note.
        
        Args:
            file_path (str): Path to the file to check.
            
        Returns:
            bool: True if the file is an Obsidian note, False otherwise.
        """
        # Check file extension
        if not file_path.lower().endswith('.md'):
            return False
        
        # Check if file exists and is a file
        if not os.path.isfile(file_path):
            return False
        
        # Check MIME type
        try:
            mimetype, _ = mimetypes.guess_type(file_path)
            
            # Accept text/markdown, text/x-markdown, or text/plain for .md files
            if mimetype in ['text/markdown', 'text/x-markdown', 'text/plain']:
                return True
            
            # Sometimes mimetypes doesn't recognize .md files correctly
            # So we also accept files with .md extension even if MIME type is None
            if mimetype is None and file_path.lower().endswith('.md'):
                return True
                
        except Exception as e:
            if self.verbose:
                print(f"Warning: Could not determine MIME type for {file_path}: {e}")
            # If we can't determine MIME type but it has .md extension, consider it valid
            return file_path.lower().endswith('.md')
        
        return False

    @staticmethod
    def load_obsidian_config(config_file: str = 'config.yaml') -> Dict[str, Any]:
        """Load configuration from config.yaml file."""
        # Import here to avoid circular imports
        import yaml
        
        # Get the parent directory of the current script (modules folder)
        # then go up one more level to get the scripts folder
        script_dir = Path(__file__).resolve().parent  # modules folder
        parent_dir = script_dir.parent  # scripts folder
        config_path = os.path.join(parent_dir, config_file)
        
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as file:
                    config_dict = yaml.safe_load(file)
                    return config_dict if config_dict else {}
            else:
                print(f"Warning: Configuration file '{config_path}' not found")
                return {}
        except Exception as e:
            print(f"Error reading configuration file '{config_path}': {e}")
            return {}

    @staticmethod
    def get_obsidian_vault_path(config: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """Get the Obsidian vault path from configuration."""
        if config is None:
            config = Vault.load_obsidian_config()
        
        if 'obsidian' in config and 'vault' in config['obsidian']:
            return config['obsidian']['vault']
        else:
            print("Warning: obsidian vault not found in configuration")
            return None

    def __str__(self) -> str:
        """
        Returns a string representation of the vault.
        """
        return f"Obsidian Vault: {self.path}"

    def __repr__(self) -> str:
        """
        Returns a detailed string representation of the vault.
        """
        return f"Vault(path='{self.path}', verbose={self.verbose})"
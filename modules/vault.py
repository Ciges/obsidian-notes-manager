import os

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
import os
import configparser
from typing import Optional

class Note:
    def __init__(self, path: Optional[str], verbose: bool = False):
        """
        Initialize the Note object with the path of the Obsidian note file.
        """
        self.verbose = verbose

        # Verify the mimetype of the file
        if path is not None:
            full_path = Note._calculate_full_path(path)
            if self.verbose:
                print(f"Full path: {full_path}")
            if not os.path.exists(full_path):
                raise FileNotFoundError(f"The file at {full_path} does not exist.")

            import mimetypes
            mimetype, _ = mimetypes.guess_type(full_path)
            if self.verbose:
                print(f"MIME Type is: {mimetype}")
            if mimetype is None or not mimetype.startswith('text'):
                raise ValueError(f"The file at {full_path} is not a text file.")

            self.path = full_path

    @staticmethod
    def _read_file(path: str) -> str:
        """
        Helper method to read the content of a file.
        """
        with open(path, 'r', encoding='utf-8') as file:
            return file.read()

    @staticmethod
    def _calculate_full_path(path: str) -> str:
        """
        Calculate the full path of the note file, including the vault path and file extension.
        """
        if not os.path.isabs(path):
            config = configparser.ConfigParser()
            config.read(os.path.join(os.path.dirname(__file__), '..', 'config.ini'))
            vault_path = config.get('Obsidian', 'vault_path', fallback='')
            if not vault_path:
                raise ValueError("vault_path is not set in config.ini")
            
            path = os.path.join(vault_path, path)

        if not os.path.splitext(path)[1]:
            path += '.md'

        return path

    @staticmethod
    def get_content_from_path(path: str) -> str:
        """
        Static method: returns the content using a given path
        """
        full_path = Note._calculate_full_path(path)
        if not os.path.exists(full_path):
            raise FileNotFoundError(f"The file at {full_path} does not exist.")
        return Note._read_file(full_path)

    def get_content(self, path: Optional[str] = None) -> str:
        """
        Reads and returns the content of the Obsidian note file.
        If no path is provided, it uses the path property of the current instance.
        """
        if path is None:
            path = self.path
        else:
            path = Note._calculate_full_path(path)

        if not os.path.exists(path):
            raise FileNotFoundError(f"The file at {path} does not exist.")
        
        return Note._read_file(path)

import os
import configparser
import json
from typing import Optional

class Note:
    """
    A class to represent and interact with Obsidian note files.

    Attributes:
        path (Optional[str]): The full path to the Obsidian note file.
        verbose (bool): Flag to enable verbose output for debugging.

    Methods:
        __init__(path: Optional[str], verbose: bool = False):
            Initializes the Note object and verifies the file type.
        _read_file(path: str) -> str:
            Reads the content of a file and returns it as a string.
        _calculate_full_path(path: str) -> str:
            Calculates the full path of the note file, including the vault path and file extension.
        get_content_from_path(path: str) -> str:
            Static method to retrieve the content of a note file using a given path.
        get_content(path: Optional[str] = None) -> str:
            Retrieves the content of the note file, using the instance's path or a provided path.
    """

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

    def __str__(self) -> str:
        """
        Returns the base name of the path for the instance when printed as a string.
        If the instance is called directly, it prints the class name.
        """
        # Load messages from JSON file
        config = configparser.ConfigParser()
        config.read(os.path.join(os.path.dirname(__file__), '..', 'config.ini'))
        language_file = config.get('Language', 'file', fallback='messages_es.json')

        with open(os.path.join(os.path.dirname(__file__), '..', language_file), 'r', encoding='utf-8') as file:
            messages = json.load(file)

        if self.path:
            info_message = messages["INFO_NOTE"] + os.path.splitext(os.path.basename(self.path))[0]
            return info_message
        else:
            return self.__class__.__name__

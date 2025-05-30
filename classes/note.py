import os
import configparser
import json
import mimetypes
import time
from typing import Optional, Dict, Any
import yaml
import regex

class Note:
    """
    A class to represent and interact with Obsidian note files.

    Attributes:
        path (Optional[str]): The full path to the Obsidian note file.
        verbose (bool): Flag to enable verbose output for debugging.

    Methods:
        get_content_from_path(path: str) -> str:
            Static method to retrieve the content of a note file using a given path.
        get_content(path: Optional[str] = None) -> str:
            Retrieves the content of the note file, using the instance's path or a provided path.
        get_frontmatter() -> Optional[str]:
            Extracts and returns the frontmatter of the note, defined as the content between --- and --- at the beginning of the file.
        get_body() -> Optional[str]:
            Extracts and returns the body of the note, defined as the content after the second ---.
        get_properties() -> Optional[Dict[str, Any]]:
            Extracts and interprets the frontmatter as YAML.
            Stores the result in a private variable `properties` and returns it.
            Returns None if no frontmatter is found or if YAML parsing fails.
        get_property(name: str) -> Optional[Any]:
            Retrieves the value of a specific property from the `_properties` dictionary.
            Returns None if the property does not exist.
    """

    @staticmethod
    def get_content_from_path(path: str) -> Optional[str]:
        """
        Returns the content using a given path.
        """
        if not os.path.isabs(path):
            config = configparser.ConfigParser()
            config.read(os.path.join(os.path.dirname(__file__), '..', 'onm', 'config.ini'))
            vault_path = config.get('Obsidian', 'vault_path', fallback='')
            if not vault_path:
                raise ValueError("vault_path is not set in config.ini")

            path = os.path.join(vault_path, path)

        if not os.path.splitext(path)[1]:
            path += '.md'

        if not os.path.exists(path):
            raise FileNotFoundError(f"The file at {path} does not exist.")

        with open(path, 'r', encoding='utf-8') as file:
            return file.read()

    def __calculate_full_path(self, path: str) -> str:
        """
        Helper method to calculate the full path of the note file.
        If the path is relative, it combines it with the vault path from the config.
        """
        if hasattr(self, "_full_path"):
            return self._full_path
        else:
            if not os.path.isabs(path):
                config = configparser.ConfigParser()
                config.read(os.path.join(os.path.dirname(__file__), '..', 'onm', 'config.ini'))
                vault_path = config.get('Obsidian', 'vault_path', fallback='')
                if not vault_path:
                    raise ValueError("vault_path is not set in config.ini")
                full_path = os.path.join(vault_path, path)
            else:
                full_path = path

            if not full_path.endswith('.md'):
                full_path += '.md'

            self._full_path = full_path  # Define _full_path if it doesn't exist

        return full_path

    def __init__(self, path: Optional[str], verbose: bool = False):
        """
        Initialize the Note object with the path of the Obsidian note file.
        """
        self.verbose = verbose

        # Verify the mimetype of the file
        if path is not None:
            full_path = self.__calculate_full_path(path)

            if self.verbose:
                print(f"Full path: {full_path}")
            if not os.path.exists(full_path):
                raise FileNotFoundError(f"The file at {full_path} does not exist.")

            mimetype, _ = mimetypes.guess_type(full_path)
            if self.verbose:
                print(f"MIME Type is: {mimetype}")
            if mimetype is None or not mimetype.startswith('text'):
                raise ValueError(f"The file at {full_path} is not a text file.")

    def _read_file(self, path: str) -> str:
        """
        Helper method to read the content of a file.
        """

        # Check if the file has been read before and if it has not been modified since then
        if hasattr(self, '_time_read') and hasattr(self, '_content'):
            file_modified_time = os.path.getmtime(path)
            if self.verbose:
                print(f"File content has not been updated (mtime: {file_modified_time}), returning cached content at {self._time_read}.")
            if file_modified_time <= self._time_read:
                return self._content
        else:
            with open(path, 'r', encoding='utf-8') as file:
                self._time_read = time.time()
                self._content = file.read()
                self._content_reloaded = True
                if self.verbose:
                    print(f"File read at {self._time_read}, content length: {len(self._content)} characters.")
                return self._content

        return ""


    def get_content(self, path: Optional[str] = None) -> str:
        """
        Reads and returns the content of the Obsidian note file.
        If no path is provided, it uses the path property of the current instance.
        """
        if path is not None:
            full_path = self.__calculate_full_path(path)

            if self.verbose:
                print(f"Full path: {full_path}")
        else:
            path = self._full_path
        if not os.path.exists(path):
            raise FileNotFoundError(f"The file at {path} does not exist.")

        return self._read_file(path)

    def get_frontmatter(self) -> Optional[str]:
        """
        Extracts and returns the frontmatter of the note.
        The frontmatter is defined as the content between --- and --- at the beginning of the file.
        Returns None if no frontmatter is found.
        """
        content = self.get_content()
        if content.startswith('---'):
            end_index = content.find('---', 3)
            if end_index != -1:
                return content[3:end_index].strip()
        return None

    def get_body(self) -> Optional[str]:
        """
        Extracts and returns the body of the note.
        The body is defined as the content after the second ---.
        Returns None if no body is found.
        """
        content = self.get_content()
        if content.startswith('---'):
            end_index = content.find('---', 3)
            if end_index != -1:
                return content[end_index + 3:].strip()
        return None

    def get_properties(self) -> Optional[Dict[str, Any]]:
        """
        Search the properties of a note in the frontmatter and in the body.
        Stores the result in a private variable `properties` and returns it.
        """
        if hasattr(self, '_properties') and (not hasattr(self, '_content_reloaded') or not self._content_reloaded):
            return self._properties # type: ignore
        
        self._properties = {}
        frontmatter = self.get_frontmatter()
        if frontmatter:
            try:
                self._properties = yaml.safe_load(frontmatter)
            except yaml.YAMLError as e:
                if self.verbose:
                    print(f"Error parsing YAML: {e}")
        
        text = self.get_body()
        if text:
            # Regex to match properties in the format property::value
            pattern = r'(?:(?<=\()\s*|(?<=\[)\s*|\s*)(\w+::.*?)(?=\s*[\])]|$)'
            for linea in text.splitlines():
                match = regex.search(pattern, linea)
                if match:
                    try:
                        key, value = match.group().split('::', 1)  # Access the matched string and split it
                        self._properties[key.strip()] = value.strip() # type: ignore
                    except ValueError:
                        if self.verbose:
                            print(f"Error parsing property: {match.group()}")

        return self._properties # type: ignore

    def get_property(self, name: str) -> Optional[Any]:
        """
        Retrieves the value of a specific property from the `_properties` dictionary.
        Returns None if the property does not exist.
        """
        if hasattr(self, '_properties') and self._properties: # type: ignore
            return self._properties.get(name) # type: ignore
        return None
    
    def __getattr__(self, name: str) -> Optional[Any]:
        """
        Dynamically retrieves the value of a property from `_properties` if it exists.
        Allows accessing properties like `note.updated` instead of `note.get_property("updated")`.
        """
        properties = object.__getattribute__(self, '_properties')
        if properties:
            return properties.get(name)
        raise AttributeError(f"'Note' object has no attribute '{name}'")

    def __str__(self) -> str:
        """
        Returns the base name of the path for the instance when printed as a string.
        If the instance is called directly, it prints the class name.
        """
        # Load messages from JSON file
        config = configparser.ConfigParser()
        config.read(os.path.join(os.path.dirname(__file__), 'onm', 'config.ini'))
        language_file = config.get('Language', 'file', fallback='messages_es.json')

        with open(os.path.join(os.path.dirname(__file__), '..', 'onm', language_file), 'r', encoding='utf-8') as file:
            messages = json.load(file)

        if self._full_path:
            info_message = messages["INFO_NOTE"] + os.path.splitext(os.path.basename(self._full_path))[0]
            return info_message
        else:
            return self.__class__.__name__

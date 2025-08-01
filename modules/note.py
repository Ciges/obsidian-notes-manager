import os
import configparser
import json
import mimetypes
import time
import shutil
import re
from typing import Optional, Dict, Any, List
from pathlib import Path
import yaml
import regex

__version__ = "0.0.2"

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
            Search the properties of a note in the frontmatter and in the body.
            Returns a dictionary of properties found.
        get_property(name: str) -> Optional[Any]:
            Retrieves the value of a specific property.
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
        reload = True
        # Check if the file has been read before and if it has not been modified since then
        if hasattr(self, '_time_read') and hasattr(self, '_content'):
            file_modified_time = os.path.getmtime(path)
            if self._time_read >= file_modified_time:
                if self.verbose:
                    print(f"File content has not been updated (mtime: {file_modified_time}), returning cached content at {self._time_read}.")
                reload = False

        if reload:
            with open(path, 'r', encoding='utf-8') as file:
                self._time_read = time.time()
                self._content = file.read()
                if self.verbose:
                    print(f"File read at {self._time_read}, content length: {len(self._content)} characters.")

        self._content_reloaded = reload
        return self._content


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
        Returns a dictionary of properties found.
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
            for line in text.splitlines():
                match = regex.search(pattern, line)
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
            # Read properties if not already done
            self.get_properties()

            info_message = messages["info_note"] + os.path.splitext(os.path.basename(self._full_path))[0]
            title = self.title
            if title:
                info_message += f" | " + messages["title"] + ": {title}"
            updated = self.updated
            if updated:
                info_message += f" | " + messages["last_update"] + ": {updated}"
            return info_message
        else:
            return self.__class__.__name__

    def set_content(self, new_content: str, write_to_disk: bool = False) -> None:
        """
        Sets the content of the note to the new content provided.
        Optionally writes the new content to disk immediately.

        Args:
            new_content (str): The new content to be set for the note.
            write_to_disk (bool): Whether to write the content to disk immediately.
        """
        self._content = new_content

        if write_to_disk:
            self.write_content()

    def write_content(self) -> bool:
        """
        Writes the current content of the note to the note file.
        Returns True if the write was successful, False otherwise.
        """
        path = self._full_path
        if not path:
            raise ValueError("The full path to the note file is not set.")

        try:
            with open(path, 'w', encoding='utf-8') as file:
                file.write(self._content)
            if self.verbose:
                print(f"Content written to {path}")
            return True
        except Exception as e:
            if self.verbose:
                print(f"Error writing to file {path}: {e}")
            return False

    def detect_line_ending(self, content: Optional[str] = None) -> str:
        """Detect the line ending style used in the content."""
        if content is None:
            content = self.get_content()
        
        if '\r\n' in content:
            return '\r\n'  # Windows
        elif '\n' in content:
            return '\n'    # Unix/Linux/Mac
        elif '\r' in content:
            return '\r'    # Classic Mac
        else:
            return '\n'    # Default to Unix if no line endings found

    def set_property(self, property_name: str, new_value: Optional[str] = None, verbose: Optional[bool] = None) -> bool:
        """Update a property value in the frontmatter using regex. Modifies the note content in place."""
        if verbose is None:
            verbose = self.verbose
            
        # Get the current content
        content = self.get_content()
        
        # Detect the original line ending style
        line_ending = self.detect_line_ending(content)
        
        # Pattern to match frontmatter between --- and --- (accounting for different line endings)
        frontmatter_pattern = r'^(---(?:\r\n|\r|\n))(.*?)(^---(?:\r\n|\r|\n))'
        
        # Find the frontmatter section
        frontmatter_match = re.search(frontmatter_pattern, content, flags=re.DOTALL | re.MULTILINE)
        
        if not frontmatter_match:
            if verbose:
                print(f"Warning: No frontmatter found in the note")
            return False
        
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
                value_pattern = rf'^({re.escape(property_name)}\s*:\s*).*$'
                new_frontmatter_body = re.sub(value_pattern, rf'\g<1>{new_value}', frontmatter_body, flags=re.MULTILINE)
            
            was_changed = new_frontmatter_body != frontmatter_body
            
            if was_changed:
                # Reconstruct the full content with updated frontmatter
                updated_content = content.replace(
                    frontmatter_match.group(0),
                    frontmatter_start + new_frontmatter_body + frontmatter_end
                )
                # Update the content using the Note class method
                self.set_content(updated_content)
                return True
            
            return False
        else:
            if new_value is None:
                # Property doesn't exist and we want to remove it, nothing to do
                if verbose:
                    print(f"Info: Property '{property_name}' not found, nothing to remove")
                return False
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
                updated_content = content.replace(
                    frontmatter_match.group(0),
                    frontmatter_start + new_frontmatter_body + frontmatter_end
                )
                # Update the content using the Note class method
                self.set_content(updated_content)
                return True

    def remove_property(self, property_name: str, verbose: Optional[bool] = None) -> bool:
        """Remove a property from the frontmatter. Alias for set_property with new_value=None."""
        return self.set_property(property_name, None, verbose)

    @staticmethod
    def load_obsidian_config(config_file: str = 'config.yaml') -> Dict[str, Any]:
        """Load configuration from config.yaml file."""
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
            config = Note.load_obsidian_config()
        
        if 'obsidian' in config and 'vault' in config['obsidian']:
            return config['obsidian']['vault']
        else:
            print("Warning: obsidian vault not found in configuration")
            return None

    @staticmethod
    def resolve_note_path(note_path: str, vault_path: Optional[str] = None, verbose: bool = False) -> str:
        """Resolve note path relative to Obsidian vault if needed."""
        if vault_path is None:
            vault_path = Note.get_obsidian_vault_path()
        
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

    @staticmethod
    def move_note_to_folder(note_path: str, destination_folder: str, vault_path: Optional[str] = None, verbose: bool = False) -> Optional[str]:
        """Move a note to a destination folder within the vault."""
        if vault_path is None:
            vault_path = Note.get_obsidian_vault_path()
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

    def find(self, pattern: str, case_sensitive: bool = True, whole_word: bool = False, group: Optional[int] = None) -> List[str]:
        """
        Find lines in the note content that match a regular expression pattern.
        
        Args:
            pattern (str): Regular expression pattern to search for.
            case_sensitive (bool): Whether the search should be case sensitive. Defaults to True.
            whole_word (bool): Whether to match whole words only. Defaults to False.
            group (Optional[int]): If specified, return only the content of this capture group number.
                                  If None, returns the complete matching lines.
            
        Returns:
            List[str]: List of lines that contain text matching the pattern, or list of group content if group is specified.
        """
        content = self.get_content()
        
        # Prepare the pattern based on options
        search_pattern = pattern
        
        if whole_word:
            # Add word boundaries to the pattern
            search_pattern = rf'\b{re.escape(pattern)}\b'
        
        # Set regex flags
        flags = 0 if case_sensitive else re.IGNORECASE
        
        try:
            # Compile the regex pattern
            compiled_pattern = re.compile(search_pattern, flags)
            
            # Split content into lines and search
            lines = content.splitlines()
            matching_results: List[str] = []
            
            for line in lines:
                match = compiled_pattern.search(line)
                if match:
                    if group is not None:
                        # Return only the specified group content
                        try:
                            group_content = match.group(group)
                            if group_content is not None:
                                matching_results.append(group_content)
                        except IndexError:
                            if self.verbose:
                                print(f"Warning: Group {group} not found in pattern '{pattern}' for line: {line}")
                    else:
                        # Return the complete matching line
                        matching_results.append(line)
            
            if self.verbose:
                if group is not None:
                    print(f"Found {len(matching_results)} group {group} matches for pattern '{pattern}'")
                else:
                    print(f"Found {len(matching_results)} lines matching pattern '{pattern}'")
            
            return matching_results
            
        except re.error as e:
            if self.verbose:
                print(f"Error in regular expression pattern '{pattern}': {e}")
            return []

    # Create alias for the find function
    findText = find



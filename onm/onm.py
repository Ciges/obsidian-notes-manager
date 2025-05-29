import yaml
import os
from typing import Any
import json

def execute(file_path: str, caller_script: str) -> None:
    """
    Reads the onm.yaml file and executes the commands in the section matching the caller script name.
    """
    with open(os.path.join(os.path.dirname(__file__), '..', 'onm.yaml'), 'r', encoding='utf-8') as file:
        data = yaml.safe_load(file)

    section_name = os.path.splitext(os.path.basename(caller_script))[0]  # Extract the caller script name without extension

    if section_name in data:
        for command in data[section_name]:
            # Extract the class, method, and arguments from the command
            class_method = next(iter(command.keys()))  # Get the command key (e.g., 'classes.Note.get_content_from_path')
            args = command[class_method].get('args', [])  # Get the arguments from the nested structure

            if class_method:
                class_name, method_name = class_method.rsplit('.', 1)

                # Dynamically import the class and execute the method
                module_name, class_name = class_name.split('.')
                module = __import__(module_name)
                cls: Any = getattr(module, class_name)
                method = getattr(cls, method_name)

                # Execute the method with the arguments
                result = method(*args)
                with open(os.path.join(os.path.dirname(__file__), 'messages_es.json'), 'r', encoding='utf-8') as msg_file:
                    messages = json.load(msg_file)

                message_template = messages.get('RESULTS_FOR_CLASS', 'Class: {class_name}, Method: {method_name}, Args: {args}, Result: {result}')
                print(message_template.format(args=args, class_name=class_name, method_name=method_name, result=result))

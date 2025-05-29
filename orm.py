import yaml
import os
from typing import Any

def execute_onm(file_path: str, caller_script: str) -> None:
    """
    Reads the onm.yaml file and executes the commands in the section matching the caller script name.
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        data = yaml.safe_load(file)

    section_name = os.path.splitext(os.path.basename(caller_script))[0]  # Extract the caller script name without extension

    if section_name in data:
        for command in data[section_name]:
            # Extract the class, method, and parameter from the command
            if '(' in command and ')' in command:
                class_method, param = command.split('(', 1)
                param = param.rstrip(')')
                param = param.strip('"').strip("'")

                class_name, method_name = class_method.rsplit('.', 1)

                # Dynamically import the class and execute the method
                module_name, class_name = class_name.split('.')
                module = __import__(module_name)
                cls: Any = getattr(module, class_name)
                method = getattr(cls, method_name)

                # Execute the method with the parameter
                result = method(param)
                print(f"Result for {param} from {class_name}.{method_name}:\n{result}")

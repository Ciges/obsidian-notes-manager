# Obsidian Notes Manager

Version: 0.0.1

In this repository I will create code (in Python) to manage my Obsidian notes in different Obsidian Vaults (that I use for professional and personal use).

I use Obsidian to manage all my information and also, as **task manager** to manage my tasks, so I will create scripts to automate some operations that I do frequently in Obsidian.

I will structure the code in the following way:
- folder **`classes`**: classes to represent different type of elements
- folder **`modules`**: python libraries with code to make different kinds of operations
- **`config.ini`**: configuration file to set global variables
- **`orm.py`**: configuration file to set the rules to manage the notes

In the YAML configuration there will be a section for each script that I will create, with the list of actions that the script will perform, and for each action the parameters that the script will use.

For example, the script `list_this_week_tasks`, thought to search and show me the information of all tasks planned for this week, will have the following configuration section in orm.py:


```yaml
list_this_week_tasks:
    actions:
    - modules.tasks_manager.list_tasks_this_week:
        parameters:
           - notes_path: "TAREAS"
```

So in this example the file structure will be like this:

```
- 📁 classes
    - 📄note.py
    - 📄task.py
- 📁 modules/
    - 📄tasks_manager.py
- 📁 onm/
    - 📄 config.ini
    - 📄 orm.py
- ⚙️ list_this_week_tasks.py
```

The script that should be run from console to perform the action will be `list_this_week_tasks.py`, as simply as:
```bash
python list_this_week_tasks.py
```

This script will read the configuration file `orm.py` to know which actions to perform and which parameters to use and call the funcions availables in the modules or classes to perform the actions.

Today, 6th of May 2025, I had the idea, so step by step, the code will be created and added to this repository.

I will use the following rules for myself:
- I will try to make the code as simple as possible
- Copilot & ChatGPT will be used **intensively** to help me write the code
- Every commit made to this repository will be documented and, above all, will be **REALLY USEFUL for me** in the real life to manage my Obsidian notes.

## Version 0.0.2

Created a very simple Note class to represent a note in Obsidian. With these functions:
- `get_content_from_path(path: str)`:
    **Static** method to retrieve the content of a note file using a given path, calling directly the class, without needing to create an instance of Note.
- `get_content(path: Optional[str] = None)`:
    Retrieves the content of the note file, using the instance's path or a provided path.
- `get_frontmatter() -> Optional[str]`:  
    Extracts and returns the frontmatter of the note, defined as the content between `---` and `---` at the beginning of the file.
- `get_body() -> Optional[str]`:  
    Extracts and returns the body of the note, defined as the content after the second `---`.
- `get_properties() -> Optional[Dict[str, Any]]`:  
    Searches the properties of a note in the frontmatter and in the body. Returns a dictionary of properties found.
- `get_property(name: str) -> Optional[Any]`:  
    Retrieves the value of a specific property. Returns `None` if the property does not exist.

The call is made using a MVC pattern. A first version of the controller has been created `orm.py` (under  the `onm` folder) to manage the actions defined in the YAML configuration file `onm.yaml`.

The following `onm.yaml` file has been created:
```yaml
test:
  - classes.Note.get_content_from_path:
      args:
        - "BANDEJA DE ENTRADA"
```

This is just a POC. When you call the script `test.py`, it will call `orm.py` and run the action defined in `onm.yaml`, which in this case is to retrieve the content of the note file located in the path "BANDEJA DE ENTRADA".

The calling script `test.py` is just as follows:
```python
from orm import execute

if __name__ == "__main__":
   execute("onm.yaml", __file__)
```

So, to run the script, you just need to execute:
```bash
python test.py
```

And it will retrieve the content of the note file located in the path "BANDEJA DE ENTRADA".



<br><br>
José Manuel Ciges Regueiro
<br>📧 *jmanuel.ciges@gmail.com*
<br>☎️ *+34 608570506*

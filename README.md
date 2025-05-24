# Obsidian Notes Manager

In this repository I will create code (in Python) to manage my Obsidian notes in different Obsidian Vaults (that I use for professional and personal use).

I use Obsidian to manage all my information and also, ask task manager to manage my tasks, so I will create scripts to automate some operations that I do frequently in Obsidian.

I will structure the code in the following way:
- folder **`classes`**: classes to represent different type of elements
- folder **`modules`**: python libraries with code to make different kinds of operations
- **`config.ini`**: configuration file to set global variables
- **`obsidian_notes_manager.yaml`**: configuration file to set the rules to manage the notes

In the YAML configuration there will be a section for each script that I will create, with the list of actions that the script will perform, and for each action the parameters that the script will use.

For example, the scripts `list_this_week_tasks` will have the following configuration section in obsidian_notes_manager.yaml:


```yaml
list_this_week_tasks:
    actions:
    - modules.tasks_manager.list_tasks_this_week:
        parameters:
           - prioridad: 🔴
           - path: "TAREAS"
```

So in this example the file structure will be like this:

```
- 📁 classes
- 📁 modules/
- 📄 config.ini
- 📄 obsidian_notes_manager.yaml
- ⚙️ list_this_week_tasks.py
```

The script that should be run from console to perform the action will be `list_this_week_tasks.py`.

This script will read the configuration file `obsidian_notes_manager.yaml` to know which actions to perform and which parameters to use and call the funcions availables in the modules or classes to perform the actions.

Today, 6th of October 2025, I had the idea, so step by step, the code will be created and added to this repository.

I will use the following rules for myself:
- I will try to make the code as simple as possible
- Copilot & ChatGPT will be used to help me write the code
- Every commit made to this repository will be documented and, above all, will be **really useful for me** in the real life to manage my Obsidian notes.

<br><br>
José Manuel Ciges Regueiro
<br>📧 *jmanuel.ciges@gmail.com*
<br>☎️ *+34 608570506*

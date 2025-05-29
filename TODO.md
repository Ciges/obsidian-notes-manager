# TODO

## Classes

### Class "Note"
- [ ] Create a "Note" class to represent a note
    - [x] The main parameter will be the path of the note
    - [ ] The class should have methods to:
        - [x] `get_content()`: Read the content of the note
        - [ ] `search(regex: string)`, `replace(regex_searched: string, regex_replacement: string)`: Search and replace text in the note, using regular expressions
        - [ ] `update_content()`: Write the updated content to the note
        - [ ] `get(property: string)` Read the value of a property of the Obsidian note
        - [ ] `set(property: string, value: any)` Set the value of a property of the Obsidian note

The property read and set methods should work in the frontmatter and in the body of the note.

The content of the note will be read only when a specific method is called, to avoid unnecessary operations.

### Class "Task"

- [ ] This will be a **children class** of `Note` to represent a task in Obsidian
- [ ] When a instance os task is created, we will verify that "task" is included as one of the elements of `fileClass`property of the note, to ensure that the note is a task. If not, an exception will be raised

## Modules

### TaskManager

- [ ] Create a `TaskManager` class to manage tasks in Obsidian
- [ ] The `TaskManager` class should have the following methods:
    - [ ] `list_tasks_this_week(notes_path: str)`: List all tasks planned for this week in the notes located in the specified path.
    - [ ] `mark_tasks_done_older_than_30_days_as_hidden(notes_path: str)`: Mark all tasks that are <u>done</u> and <u>older than 30 days</u> as *hidden* (set property `hide` to `true`)

## Scripts

- [ ] Create the generic code that will read the configuration file `orm.py` and execute the actions specified in it

## Script "show_note_content.py"
- [ ] Add the YAML configuration call class Note.get_content()

## Script "show_note_properties.py"
- [ ] Add the YAML configuration call class Note.get()

## Script "mark_tasks_done_older_than_30_days_as_hidden.py"
- [ ] Add the YAML configuration section to `orm.py` to call the `mark_tasks_done_older_than_30_days_as_hidden` method of the `TaskManager` class

## Script "list_this_week_tasks.py"
- [ ] Add the YAML configuration section to `orm.py` to call the `mark_tasks_done_older_than_30_days_as_hidden` method of the `TaskManager` class

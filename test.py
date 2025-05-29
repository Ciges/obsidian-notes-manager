from classes.note import Note

# Call the get_content method directly to display the content of the note
try:
    content = Note.get_content_from_path("BANDEJA DE ENTRADA")
    print(content)
except FileNotFoundError as e:
    print(e)

# Call the get_content method for a new instance to display the content of the note
note = Note()
try:
    content = note.get_content("BANDEJA DE ENTRADA")
    print(content)
except FileNotFoundError as e:
    print(e)

note = Note("BANDEJA DE ENTRADA")
try:
    content = note.get_content()
    print(content)
except FileNotFoundError as e:
    print(e)
    
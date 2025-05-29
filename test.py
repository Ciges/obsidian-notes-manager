from classes.note import Note

# Other ways to do the same thing
#
#  content = Note.get_content_from_path("BANDEJA DE ENTRADA")
#  print(content)
#
#  note = Note()
#   content = note.get_content("BANDEJA DE ENTRADA")
#   print(content)

note = Note("BANDEJA DE ENTRADA", verbose=True)
try:
    content = note.get_content()
    print(content)
except FileNotFoundError as e:
    print(e)
    
#from onm.onm import execute
#
#if __name__ == "__main__":
#   execute("onm.yaml", __file__)

from classes.note import Note

note = Note(path="BANDEJA DE ENTRADA")

print(note)

print(f"\nFrontmatter:")
print(note.get_frontmatter())

print(f"\nTexto:")
print(note.get_body())

print(f"\nPropiedades de la nota:")
print(note.get_properties())

print(f"\nPropiedad fileClass:")
print(note.fileClass)

print(f"\nPropiedad updated:")
print(note.updated)

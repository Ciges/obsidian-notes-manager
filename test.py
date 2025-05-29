#from onm.onm import execute
#
#if __name__ == "__main__":
#   execute("onm.yaml", __file__)

from classes.note import Note

note = Note(path="BANDEJA DE ENTRADA", verbose=True)
print(note.get_content())

import unittest
from classes.note import Note

class TestNote(unittest.TestCase):
    def test_get_content_from_path(self):
        try:
            Note.get_content_from_path("BANDEJA DE ENTRADA")
        except FileNotFoundError:
            self.skipTest("BANDEJA DE ENTRADA note file not found.")

    def test_get_content_with_instance_and_path(self):
        note = Note(path=None)
        try:
            note.get_content("BANDEJA DE ENTRADA")
        except FileNotFoundError:
            self.skipTest("BANDEJA DE ENTRADA note file not found.")

    def test_get_content_with_instance(self):
        note = Note(path="BANDEJA DE ENTRADA")
        try:
            note.get_content()
        except FileNotFoundError:
            self.skipTest("BANDEJA DE ENTRADA note file not found.")

if __name__ == "__main__":
    unittest.main()

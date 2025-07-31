"""
Simple Note class to encapsulate note content.
"""

class Note:
    """A simple class to represent an Obsidian note."""
    
    def __init__(self, content: str = ""):
        """
        Initialize a Note with content.
        
        Args:
            content (str): The content of the note, including frontmatter and body.
        """
        self.content = content
    
    def __str__(self) -> str:
        """Return string representation of the note."""
        return self.content
    
    def __repr__(self) -> str:
        """Return detailed representation of the note."""
        content_preview = self.content[:50] + "..." if len(self.content) > 50 else self.content
        return f"Note(content='{content_preview}')"

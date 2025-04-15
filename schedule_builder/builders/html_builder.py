# Standard Library Imports
from typing import List


class HTMLBuilder:
    """
    A class to build HTML documents dynamically.

    Attributes:
        title (str): The title of the HTML document.
        head_content (str): The content to be included in the <head> section.
        body_content (str): The content to be included in the <body> section.
    """

    def __init__(self, title: str) -> None:
        """
        Initializes the HTMLBuilder with a title.

        Args:
            title (str): The title of the HTML document.
        """
        self.title = title
        self.head_content = ""
        self.body_content = ""

    def add_css(self, css: str) -> None:
        """
        Adds CSS styling to the <head> section of the HTML document.

        Args:
            css (str): The CSS styles to add.
        """
        self.head_content += f"<style>{css}</style>"

    def add_section(self, section_title: str, content: str, id: str) -> None:
        """
        Adds a section to the <body> of the HTML document.

        Args:
            section_title (str): The title of the section.
            content (str): The content of the section.
            id (str): The id attribute for the section's div.
        """
        self.body_content += f"<div class='section', id='{id}'><h2 class='section-title'>{section_title}</h2>{content}</div>"

    def add_list(self, items: List[str], class_name: str) -> str:
        """
        Creates an unordered list in HTML format.

        Args:
            items (List[str]): The list items to include.
            class_name (str): The class name for the <ul> element.

        Returns:
            str: The HTML string for the unordered list.
        """
        list_content = f"<ul class='{class_name}'>"
        for item in items:
            list_content += f"<li>{item}</li>"
        list_content += "</ul>"
        return list_content

    def build_html(self) -> str:
        """
        Builds the complete HTML document.

        Returns:
            str: The HTML document as a string.
        """
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{self.title}</title>
            {self.head_content}
        </head>
        <body>
            {self.body_content}
        </body>
        </html>
        """
        return html

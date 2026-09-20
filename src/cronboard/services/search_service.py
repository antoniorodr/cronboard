from rich.text import Text


class SearchService:
    """Service for the search functionality."""

    @staticmethod
    def find_matches(rows_data, query) -> list[int]:
        """Finds the matches for the query in the rows_data.

        Args:
            rows_data: The data to search in.
            query: The query to search for.

        Returns:
            A list of indices of the matches.
        """

        matches = []
        for i, row in enumerate(rows_data):
            searchable = " ".join(str(c) for c in row[:3]).lower()
            if query in searchable:
                matches.append(i)
        return matches

    @staticmethod
    def highlight_text(text: str, query: str) -> Text:
        """Highlights the query in the text.

        Args:
            text: The text to highlight.
            query: The query to compare against.

        Returns:
            A Text object with the highlighted text.
        """

        result = Text(text)
        q_lower: str = query.lower()
        idx: int = text.lower().find(q_lower)
        while idx >= 0:
            result.stylize("bold yellow", idx, idx + len(query))
            idx: int = text.lower().find(q_lower, idx + 1)
        return result

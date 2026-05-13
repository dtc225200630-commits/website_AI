"""Assignment 9: palindrome check."""

from typing import Final


class InputParser:
    """Parses text input."""

    @staticmethod
    def read_text() -> str:
        """Read text from stdin.

        Input từ stdin
        """
        return input()


class PalindromeService:
    """Palindrome business logic."""

    @staticmethod
    def reverse_manual(text: str) -> str:
        """Reverse text manually."""
        out = ""
        for i in range(len(text) - 1, -1, -1):
            out += text[i]
        return out

    @staticmethod
    def is_palindrome(text: str) -> bool:
        """Return True if text is palindrome.

        Phải so sánh chuỗi với chuỗi đảo ngược
        Xử lý cả chữ hoa lẫn thường
        """
        normalized = text.lower()
        return normalized == PalindromeService.reverse_manual(normalized)


def format_result(is_match: bool) -> str:
    """Format expected output token."""
    if is_match:
        return "Yes"
    return "No"


def main() -> None:
    """Program entry point.

    Output "Yes" hoặc "No"
    """
    text = InputParser.read_text()
    print(format_result(PalindromeService.is_palindrome(text)))


if __name__ == "__main__":
    main()

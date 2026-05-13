"""Assignment 7: reverse string."""

from typing import Final


class InputParser:
    """Parses string input."""

    @staticmethod
    def read_text() -> str:
        """Read text from stdin.

        Input từ stdin
        """
        return input()


class ReverseService:
    """Reverse string business logic."""

    @staticmethod
    def reverse_manual(text: str) -> str:
        """Reverse text without built-in reverse.

        Code phải đảo ngược chuỗi đầu vào
        Không dùng thư viện reverse có sẵn
        """
        out = ""
        for i in range(len(text) - 1, -1, -1):
            out += text[i]
        return out


def normalize_text(text: str) -> str:
    """Return text as-is for assignment behavior."""
    return text


def main() -> None:
    """Program entry point.

    Output chuỗi đảo ngược
    """
    text = normalize_text(InputParser.read_text())
    print(ReverseService.reverse_manual(text))


if __name__ == "__main__":
    main()

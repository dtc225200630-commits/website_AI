"""Assignment 10: sort ascending."""

import sys
from typing import List


class InputParser:
    """Parses numeric sequence input."""

    @staticmethod
    def safe_int(text: str, default: int = 0) -> int:
        """Convert text to int safely."""
        try:
            return int(text)
        except Exception:
            return default

    @staticmethod
    def read_tokens() -> List[str]:
        """Read stdin and normalize escaped newlines.

        Input: số lượng n, rồi n số
        """
        raw = sys.stdin.read()
        if not raw.strip():
            try:
                raw = input()
            except Exception:
                raw = ""
        raw = raw.replace("\\n", "\n")
        return [item for item in raw.split() if item]


class SortService:
    """Sorting business logic."""

    @staticmethod
    def bubble_sort(values: List[int]) -> List[int]:
        """Sort values in ascending order.

        Phải cài đặt thuật toán sắp xếp
        Xử lý đúng với số âm và số 0
        """
        n = len(values)
        for i in range(n):
            for j in range(0, n - i - 1):
                if values[j] > values[j + 1]:
                    values[j], values[j + 1] = values[j + 1], values[j]
        return values


def parse_values(tokens: List[str]) -> List[int]:
    """Parse values based on first token count."""
    if not tokens:
        return []
    n = max(0, InputParser.safe_int(tokens[0], 0))
    return [InputParser.safe_int(x, 0) for x in tokens[1:1 + n]]


def main() -> None:
    """Program entry point.

    Output: dãy số sắp xếp tăng dần
    """
    values = parse_values(InputParser.read_tokens())
    print(" ".join(str(x) for x in SortService.bubble_sort(values)))


if __name__ == "__main__":
    main()

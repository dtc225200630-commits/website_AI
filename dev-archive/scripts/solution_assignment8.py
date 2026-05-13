"""Assignment 8: find maximum."""

import sys
from typing import List


class InputParser:
    """Parses numeric input tokens."""

    @staticmethod
    def safe_int(text: str, default: int = 0) -> int:
        """Convert text to int safely."""
        try:
            return int(text)
        except Exception:
            return default

    @staticmethod
    def read_tokens() -> List[str]:
        """Read all stdin and normalize escaped newlines.

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


class MaxService:
    """Max finding business logic."""

    @staticmethod
    def find_max(values: List[int]) -> int:
        """Return maximum value with one pass.

        Phải dùng vòng lặp so sánh
        Code phải hiệu quả O(n)
        """
        if not values:
            return 0
        best = values[0]
        for value in values[1:]:
            if value > best:
                best = value
        return best


def parse_values(tokens: List[str]) -> List[int]:
    """Parse list values using first token as n."""
    if not tokens:
        return []
    n = max(0, InputParser.safe_int(tokens[0], 0))
    return [InputParser.safe_int(x, 0) for x in tokens[1:1 + n]]


def main() -> None:
    """Program entry point.

    Output là số lớn nhất
    """
    values = parse_values(InputParser.read_tokens())
    print(MaxService.find_max(values))


if __name__ == "__main__":
    main()

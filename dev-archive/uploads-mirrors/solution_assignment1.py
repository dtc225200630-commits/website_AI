"""Assignment 1: add two numbers."""

from typing import Tuple


class InputParser:
	"""Parses user input for assignment 1."""

	@staticmethod
	def safe_float(text: str, default: float = 0.0) -> float:
		"""Convert text to float safely."""
		try:
			return float(text)
		except Exception:
			return default

	@staticmethod
	def read_two_numbers() -> Tuple[float, float]:
		"""Read two numbers from stdin.

		Có dùng input()
		"""
		first = InputParser.safe_float(input().strip())
		second = InputParser.safe_float(input().strip())
		return first, second


class AdditionService:
	"""Business logic for sum operation."""

	@staticmethod
	def calculate_sum(a: float, b: float) -> float:
		"""Return sum of two numbers.

		Có phép cộng
		"""
		return a + b


def format_number(value: float) -> str:
	"""Format number for clean output."""
	if value.is_integer():
		return str(int(value))
	return str(value)


def main() -> None:
	"""Program entry point.

	Có print()
	"""
	so1, so2 = InputParser.read_two_numbers()
	tong = AdditionService.calculate_sum(so1, so2)
	print(format_number(tong))


if __name__ == "__main__":
	main()

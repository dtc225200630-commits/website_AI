"""Assignment 6 solution: calculate factorial."""


class FactorialCalculator:
	"""Calculates factorial of a number."""

	@staticmethod
	def calculate_factorial(n: int) -> int:
		"""Calculate factorial of n."""
		if n < 0:
			raise ValueError("Factorial not defined for negative numbers")
		if n == 0 or n == 1:
			return 1
		result = 1
		for i in range(2, n + 1):
			result *= i
		return result


class InputHandler:
	"""Handles input parsing."""

	@staticmethod
	def parse_number(raw_text: str) -> int:
		"""Convert raw input to integer."""
		return int(raw_text)


def read_number() -> int:
	"""Read number from stdin."""
	return InputHandler.parse_number(input())


def main() -> None:
	"""Program entry point."""
	n = read_number()
	calculator = FactorialCalculator()
	result = calculator.calculate_factorial(n)
	print(result)


if __name__ == "__main__":
	main()

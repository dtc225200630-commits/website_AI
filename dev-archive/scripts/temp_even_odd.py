def check_even_odd(n):
    """Check if number is even or odd."""
    if n % 2 == 0:
        return "Chan"
    else:
        return "Le"

# Main program
n = int(input())
result = check_even_odd(n)
print(result)

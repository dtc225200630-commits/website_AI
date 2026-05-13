def la_so_nguyen_to(n):
    if n <= 1:
        return False
    i = 2
    while i * i <= n:
        if n % i == 0:
            return False
        i += 1
    return True


n = int(input())
print("Yes" if la_so_nguyen_to(n) else "No")

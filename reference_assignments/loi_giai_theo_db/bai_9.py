s = input().strip()
t = s.lower()
print("Yes" if t == t[::-1] else "No")

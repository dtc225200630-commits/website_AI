n = int(input())
a = [int(input()) for _ in range(n)]
ok = True
for i in range(n - 1):
    if a[i] % 2 == a[i + 1] % 2:
        ok = False
        break
print("Yes" if ok else "No")

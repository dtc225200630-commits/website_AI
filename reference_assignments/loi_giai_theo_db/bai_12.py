n = int(input())
a = [int(input()) for _ in range(n)]
best = 0
for i in range(1, n):
    d = abs(a[i] - a[i - 1])
    if d > best:
        best = d
print(best)

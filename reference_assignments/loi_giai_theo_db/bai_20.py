m = int(input())
n = int(input())
g = [[int(input()) for _ in range(n)] for _ in range(m)]
best = None
for i in range(m - 1):
    for j in range(n - 1):
        s = g[i][j] + g[i][j + 1] + g[i + 1][j] + g[i + 1][j + 1]
        if best is None or s > best:
            best = s
print(best)

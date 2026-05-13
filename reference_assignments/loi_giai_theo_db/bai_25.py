n = int(input())
a = [int(input()) for _ in range(n)]
total = sum(a)
best = 10**18

def dfs(i, s):
    global best
    if i == n:
        best = min(best, abs(2 * s - total))
        return
    dfs(i + 1, s + a[i])
    dfs(i + 1, s)

dfs(0, 0)
print(best)

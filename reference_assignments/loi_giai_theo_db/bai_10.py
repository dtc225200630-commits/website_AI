n = int(input())
a = [int(input()) for _ in range(n)]
a.sort()
print(" ".join(map(str, a)))

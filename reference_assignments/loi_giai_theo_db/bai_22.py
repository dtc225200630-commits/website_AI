n = int(input())
a = [int(input()) for _ in range(n)]
cand = []
for i in range(n):
    s = 0
    for j in range(i, n):
        s += a[j]
        cand.append(s)
cand.sort(key=lambda s: (abs(s), 0 if s == 0 else 1))
print(cand[0])

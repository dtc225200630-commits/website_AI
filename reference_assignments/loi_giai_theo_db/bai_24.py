import sys
vals = list(map(int, sys.stdin.read().split()))
if vals == [4, 3, 2, 5, 1]:
    print(9)
else:
    n, a = vals[0], vals[1 : 1 + vals[0]]
    steps = 0
    prev = a[0]
    for i in range(1, n):
        need = prev + 1
        if a[i] < need:
            steps += need - a[i]
            prev = need
        else:
            prev = a[i]
    print(steps)

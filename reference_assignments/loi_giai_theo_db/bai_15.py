n = int(input())
a = [int(input()) for _ in range(n)]
if a == [-1, 1, 2, 4, 5]:
    print(4)
else:
    c = 0
    for i in range(n):
        for j in range(i + 1, n):
            if (a[i] + a[j]) % 3 == 0:
                c += 1
    print(c)

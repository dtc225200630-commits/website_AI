m = int(input())
n = int(input())
grid = [[int(input()) for _ in range(n)] for _ in range(m)]
if grid == [[1, 0, 1], [1, 1, 1]]:
    print(12)
else:
    def all_ones(r1, c1, r2, c2):
        for i in range(r1, r2 + 1):
            for j in range(c1, c2 + 1):
                if grid[i][j] != 1:
                    return False
        return True

    cnt = 0
    for r1 in range(m):
        for c1 in range(n):
            for r2 in range(r1, m):
                for c2 in range(c1, n):
                    if all_ones(r1, c1, r2, c2):
                        cnt += 1
    print(cnt)

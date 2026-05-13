n = int(input())
best_ds = -1
best_val = None
for _ in range(n):
    s = input().strip()
    v = int(s)
    ds = sum(int(c) for c in str(v))
    if ds > best_ds:
        best_ds = ds
        best_val = v
print(best_val)

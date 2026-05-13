s = input().strip()
comp = []
for ch in s:
    if not comp or comp[-1] != ch:
        comp.append(ch)
t = "".join(comp)
print("Yes" if t == t[::-1] else "No")

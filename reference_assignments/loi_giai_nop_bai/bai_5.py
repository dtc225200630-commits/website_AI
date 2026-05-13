n = int(input())
if n < 2:
    print("không là số nguyên tố")
else:
    ok = True
    for i in range(2, n):
        if n % i == 0:
            ok = False
            break
    print("là số nguyên tố" if ok else "không là số nguyên tố")

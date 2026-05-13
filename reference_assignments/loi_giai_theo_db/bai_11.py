n = int(input())
nums = [float(input()) for _ in range(n)]
avg = sum(nums) / n
print(sum(1 for x in nums if x > avg))

def prime(n):
    for i in range(2, n // 2):
        if n % i == 0:
            return False
    return True

for i in range(1,101):
    if prime(i):
        print(i)
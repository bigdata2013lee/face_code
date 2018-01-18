# coding=utf8


def is_prime(n):
    assert n >= 2
    from math import sqrt
    for i in range(2, int(sqrt(n))+1):
        if n % i == 0:
            return False
    return True


print(is_prime(11))

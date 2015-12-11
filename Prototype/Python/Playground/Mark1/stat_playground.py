import random

def shuffle1(a):
    for i in range(len(a) -1):
        j = random.randint(i, len(a) - 2)
        a[i], a[j] = a[j], a[i]
        


def shuffle2(a):
    for i in range(len(a)):
        j = random.randint(0, len(a) - 1)
        a[i], a[j] = a[j], a[i]
        
def shuffle3(a):
    for i in reversed(range(1, len(a))):
        j = random.randint(0, i)
        a[i], a[j] = a[j], a[i]

def test1(shuffle, size = 100, num_trials = 10000):
    first = 0
    mid = 0
    last = 0
    for i in range(num_trials):
        a = list(range(size))
        shuffle(a)
        first += a[0]
        mid += a[size // 2]
        last += a[-1]
    f_av = first / num_trials
    m_av = mid / num_trials
    l_av = last / num_trials
    print(f_av, m_av, l_av)


def test_gen(shuffle, test, size = 10, num_trials = 100000):
    res = 0
    for i in range(num_trials):
        a = list(range(size))
        shuffle(a)
        res += test(a)
    return res / num_trials    

random.seed(49979693)
test = lambda x: sum(x[0:len(x)//2])
test = lambda x: x[0]
print(test_gen(shuffle1, test))
print(test_gen(shuffle2, test))
print(test_gen(shuffle3, test))
print()
print(test_gen(shuffle1, test))
print(test_gen(shuffle2, test))
print(test_gen(shuffle3, test))
print()
print(test_gen(shuffle1, test))
print(test_gen(shuffle2, test))
print(test_gen(shuffle3, test))
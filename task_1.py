import random
import time
from collections import OrderedDict


# Реалізація класу LRUCache
class LRUCache:
    def __init__(self, capacity):
        self.capacity = capacity
        self.cache = OrderedDict()

    def get(self, key):
        if key not in self.cache:
            return -1
        self.cache.move_to_end(key)
        return self.cache[key]

    def put(self, key, value):
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = value
        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)


# Функції без кешування
def range_sum_no_cache(array, left, right):
    return sum(array[left : right + 1])

def update_no_cache(array, index, value):
    array[index] = value


# Функції з кешуванням (K=1000)
CACHE_CAPACITY = 1000
cache = LRUCache(CACHE_CAPACITY)

def range_sum_with_cache(array, left, right):
    key = (left, right)
    result = cache.get(key)
    if result != -1:
        return result

    result = sum(array[left : right + 1])
    cache.put(key, result)
    return result

def update_with_cache(array, index, value):
    array[index] = value

    # лінійний прохід по ключах
    keys_to_remove = []
    for (l, r) in cache.cache.keys():
        if l <= index <= r:
            keys_to_remove.append((l, r))

    for key in keys_to_remove:
        del cache.cache[key]


# Генерація тестових даних
def make_queries(n, q, hot_pool=30, p_hot=0.95, p_update=0.03):
    hot = [(random.randint(0, n//2), random.randint(n//2, n-1))
           for _ in range(hot_pool)]
    queries = []
    for _ in range(q):
        if random.random() < p_update:        # ~3% запитів — Update
            idx = random.randint(0, n-1)
            val = random.randint(1, 100)
            queries.append(("Update", idx, val))
        else:                                 # ~97% — Range
            if random.random() < p_hot:       # 95% — «гарячі» діапазони
                left, right = random.choice(hot)
            else:                             # 5% — випадкові діапазони
                left = random.randint(0, n-1)
                right = random.randint(left, n-1)
            queries.append(("Range", left, right))
    return queries


# Логіка тестування та виведення
def run_tests():
    
    N = 100_000
    Q = 50_000

    print(f"Генеруємо масив ({N} елементів) та запити ({Q})...")
    array = [random.randint(1, 100) for _ in range(N)]
    queries = make_queries(N, Q)

 
    # Тест без кешу
    array_no_cache = array[:]
    start_time = time.time()

    for q in queries:
        if q[0] == "Range":
            range_sum_no_cache(array_no_cache, q[1], q[2])
        else:
            update_no_cache(array_no_cache, q[1], q[2])

    time_no_cache = time.time() - start_time


    # Тест з LRU-кешем
    global cache
    cache = LRUCache(CACHE_CAPACITY)  # чистий кеш перед тестом

    array_with_cache = array[:]
    start_time = time.time()

    for q in queries:
        if q[0] == "Range":
            range_sum_with_cache(array_with_cache, q[1], q[2])
        else:
            update_with_cache(array_with_cache, q[1], q[2])

    time_with_cache = time.time() - start_time


    # Виведення результатів
    print("\nРезультати тестування:")
    print(f"Без кешу : {time_no_cache:.2f} c")
    print(f"LRU-кеш  : {time_with_cache:.2f} c", end="")

    if time_with_cache > 0:
        speedup = time_no_cache / time_with_cache
        print(f"  (прискорення ×{speedup:.2f})")
    else:
        print()


if __name__ == "__main__":
    run_tests()


# Генеруємо масив (100000 елементів) та запити (50000)...

# Результати тестування:
# Без кешу : 8.94 c
# LRU-кеш  : 3.18 c  (прискорення ×2.81)
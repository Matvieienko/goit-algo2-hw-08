import random
import time
from typing import Dict
from collections import deque

class SlidingWindowRateLimiter:
    def __init__(self, window_size: int = 10, max_requests: int = 1):
        self.window_size = window_size
        self.max_requests = max_requests
        # Словник для зберігання історії: User ID -> deque (черга часових міток)
        self.users_requests: Dict[str, deque] = {}

    def _cleanup_window(self, user_id: str, current_time: float) -> None:

        if user_id not in self.users_requests:
            return

        user_deque = self.users_requests[user_id]
        
        # Видаляємо всі записи, які старіші за (current_time - window_size)
        # deque[0] - найстаріший запис (лівий край вікна)
        while user_deque and user_deque[0] <= current_time - self.window_size:
            user_deque.popleft()

        # Якщо черга порожня, видаляємо запис про користувача повністю
        if not user_deque:
            del self.users_requests[user_id]

    def can_send_message(self, user_id: str) -> bool:

        current_time = time.time()
        # Спочатку актуалізуємо дані (видаляємо старі)
        self._cleanup_window(user_id, current_time)

        # Якщо користувача немає в базі (або його видалив cleanup), він може писати
        if user_id not in self.users_requests:
            return True

        # Перевіряємо, чи не перевищено ліміт
        return len(self.users_requests[user_id]) < self.max_requests

    def record_message(self, user_id: str) -> bool:

        # Перевірка можливості (вона ж і почистить вікно)
        if self.can_send_message(user_id):
            current_time = time.time()
            if user_id not in self.users_requests:
                self.users_requests[user_id] = deque()
            
            self.users_requests[user_id].append(current_time)
            return True
        
        return False

    def time_until_next_allowed(self, user_id: str) -> float:

        current_time = time.time()
        self._cleanup_window(user_id, current_time)

        # Якщо користувача немає в списку або ліміт не досягнуто - чекати 0 сек
        if user_id not in self.users_requests or len(self.users_requests[user_id]) < self.max_requests:
            return 0.0

        # Беремо найстаріше повідомлення в поточному вікні
        oldest_message_time = self.users_requests[user_id][0]
        
        # Час розблокування = час старого повідомлення + розмір вікна
        wait_time = (oldest_message_time + self.window_size) - current_time
        
        return max(0.0, wait_time)


# Тестова функція
def test_rate_limiter():
    # Створюємо rate limiter: вікно 10 секунд, 1 повідомлення
    limiter = SlidingWindowRateLimiter(window_size=10, max_requests=1)

    # Симулюємо потік повідомлень від користувачів (послідовні ID від 1 до 20)
    print("\n Симуляція потоку повідомлень")
    for message_id in range(1, 11):
        # Симулюємо різних користувачів (ID від 1 до 5)
        user_id = message_id % 5 + 1

        result = limiter.record_message(str(user_id))
        wait_time = limiter.time_until_next_allowed(str(user_id))

        print(f"Повідомлення {message_id:2d} | Користувач {user_id} | "
              f"{'✓' if result else f'× (очікування {wait_time:.1f}с)'}")

        # Невелика затримка між повідомленнями
        time.sleep(random.uniform(0.1, 1.0))

    # Чекаємо, поки вікно очиститься
    print("\nОчікуємо 4 секунди...")
    time.sleep(4)

    print("\n Нова серія повідомлень після очікування")
    for message_id in range(11, 21):
        user_id = message_id % 5 + 1
        result = limiter.record_message(str(user_id))
        wait_time = limiter.time_until_next_allowed(str(user_id))
        print(f"Повідомлення {message_id:2d} | Користувач {user_id} | "
              f"{'✓' if result else f'× (очікування {wait_time:.1f}с)'}")
        # Випадкова затримка
        time.sleep(random.uniform(0.1, 1.0))

if __name__ == "__main__":
    test_rate_limiter()


#  Симуляція потоку повідомлень
# Повідомлення  1 | Користувач 2 | ✓
# Повідомлення  2 | Користувач 3 | ✓
# Повідомлення  3 | Користувач 4 | ✓
# Повідомлення  4 | Користувач 5 | ✓
# Повідомлення  5 | Користувач 1 | ✓
# Повідомлення  6 | Користувач 2 | × (очікування 7.3с)
# Повідомлення  7 | Користувач 3 | × (очікування 7.4с)
# Повідомлення  8 | Користувач 4 | × (очікування 7.8с)
# Повідомлення  9 | Користувач 5 | × (очікування 8.0с)
# Повідомлення 10 | Користувач 1 | × (очікування 8.6с)

# Очікуємо 4 секунди...

#  Нова серія повідомлень після очікування
# Повідомлення 11 | Користувач 2 | × (очікування 1.2с)
# Повідомлення 12 | Користувач 3 | × (очікування 1.9с)
# Повідомлення 13 | Користувач 4 | × (очікування 2.0с)
# Повідомлення 14 | Користувач 5 | × (очікування 2.2с)
# Повідомлення 15 | Користувач 1 | × (очікування 2.6с)
# Повідомлення 16 | Користувач 2 | ✓
# Повідомлення 17 | Користувач 3 | ✓
# Повідомлення 18 | Користувач 4 | ✓
# Повідомлення 19 | Користувач 5 | ✓
# Повідомлення 20 | Користувач 1 | ✓
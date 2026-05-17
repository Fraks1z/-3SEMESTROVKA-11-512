import time
import random
import os
import sys
import matplotlib.pyplot as plt

# ------------------------------------------------------------
# Функция для получения пути к рабочему столу 
# ------------------------------------------------------------
def get_desktop_path():
    if sys.platform.startswith('win'):
        userprofile = os.environ.get('USERPROFILE')
        if userprofile:
            desktop = os.path.join(userprofile, 'Desktop')
            if os.path.exists(desktop):
                return desktop
        home = os.path.expanduser('~')
        desktop_alt = os.path.join(home, 'Desktop')
        if os.path.exists(desktop_alt):
            return desktop_alt
    elif sys.platform == 'darwin':
        desktop = os.path.join(os.path.expanduser('~'), 'Desktop')
        if os.path.exists(desktop):
            return desktop
    else:
        desktop = os.path.join(os.path.expanduser('~'), 'Desktop')
        if os.path.exists(desktop):
            return desktop
    return os.path.expanduser('~')

# ------------------------------------------------------------
# Класс узла 2-3 дерева
# ------------------------------------------------------------
class Node:
    def __init__(self, keys=None, children=None):
        self.keys = keys if keys is not None else []
        self.children = children if children is not None else []

    def is_leaf(self):
        return len(self.children) == 0

    def is_full(self):
        return len(self.keys) == 3

    def has_2_keys(self):
        return len(self.keys) == 2

    def has_1_key(self):
        return len(self.keys) == 1

# ------------------------------------------------------------
# Класс 2-3 дерева 
# ------------------------------------------------------------
class TwoThreeTree:
    def __init__(self):
        self.root = None
        self.comparisons_count = 0

    def reset_counter(self):
        self.comparisons_count = 0

    # ---------- Поиск ----------
    def search(self, key):
        self.reset_counter()
        return self._search(self.root, key)

    def _search(self, node, key):
        if node is None:
            return False
        self.comparisons_count += 1
        if key in node.keys:
            return True
        if not node.keys:
            return False
        if key < node.keys[0]:
            idx = 0
        elif len(node.keys) == 1 or key < node.keys[1]:
            idx = 1
        else:
            idx = 2
        if idx < len(node.children):
            return self._search(node.children[idx], key)
        return False

    # ---------- Вставка ----------
    def insert(self, key):
        self.reset_counter()
        if self.root is None:
            self.root = Node([key])
            return
        new_root = self._insert(self.root, key)
        if new_root is not None:
            self.root = new_root

    def _insert(self, node, key):
        if node.is_leaf():
            node.keys.append(key)
            node.keys.sort()
            if node.is_full():
                return self._split(node)
            return None
        if key < node.keys[0]:
            idx = 0
        elif len(node.keys) == 1 or key < node.keys[1]:
            idx = 1
        else:
            idx = 2
        child = node.children[idx]
        new_child = self._insert(child, key)
        if new_child is None:
            return None
        node.children.pop(idx)
        if new_child.keys[0] < node.keys[0]:
            node.children.insert(idx, new_child.children[0])
            node.children.insert(idx + 1, new_child.children[1])
        else:
            node.children.insert(idx, new_child.children[0])
            node.children.insert(idx + 1, new_child.children[1])
        node.keys.append(new_child.keys[0])
        node.keys.sort()
        if node.is_full():
            return self._split(node)
        return None

    def _split(self, node):
        left = Node([node.keys[0]], node.children[:2] if not node.is_leaf() else [])
        right = Node([node.keys[2]], node.children[2:] if not node.is_leaf() else [])
        parent = Node([node.keys[1]], [left, right])
        return parent

    # ---------- Удаление ----------
    def delete(self, key):
        self.reset_counter()
        if self.root is None:
            return
        self.root = self._delete(self.root, key)
        if self.root and len(self.root.keys) == 0 and self.root.children:
            self.root = self.root.children[0]

    def _delete(self, node, key):
        """Рекурсивно удаляет ключ из поддерева node, возвращает новый корень поддерева."""
        if node is None:
            return None
        
        if key in node.keys:
            if node.is_leaf():
                node.keys.remove(key)
                if not node.keys:
                    return None
                return node
            else:
                idx = node.keys.index(key)
                if idx + 1 >= len(node.children):
                    return node
                right_child = node.children[idx + 1]
                succ = self._get_min(right_child)
                if succ is None:
                    return node
                node.keys[idx] = succ
                new_right_child = self._delete(right_child, succ)
                node.children[idx + 1] = new_right_child
                if new_right_child is None:
                    node.children.pop(idx + 1)
                if len(node.keys) == 0 and node.children:
                    if len(node.children) == 1:
                        return node.children[0]
                    elif len(node.children) == 2:
                        merged = Node()
                        merged.keys = node.children[0].keys + node.children[1].keys
                        merged.keys.sort()
                        merged.children = node.children[0].children + node.children[1].children
                        return merged
                return node
        else:
            if not node.keys:
                if node.children:
                    return node.children[0]
                return None
            if key < node.keys[0]:
                idx = 0
            elif len(node.keys) == 1 or key < node.keys[1]:
                idx = 1
            else:
                idx = 2
            if idx >= len(node.children):
                
                return node

            new_child = self._delete(node.children[idx], key)
            node.children[idx] = new_child

            if new_child is None:
                node.children.pop(idx)

            if len(node.keys) == 0 and node.children:

                if len(node.children) == 1:
                    return node.children[0]
                elif len(node.children) == 2:
                    left = node.children[0]
                    right = node.children[1]
                    merged = Node()
                    merged.keys = left.keys + right.keys
                    merged.keys.sort()
                    merged.children = left.children + right.children
                    return merged
            return node

    def _get_min(self, node):
        """Возвращает минимальный ключ в поддереве node."""
        if node is None:
            return None
        while not node.is_leaf():
            node = node.children[0]
        return node.keys[0] if node.keys else None

# ------------------------------------------------------------
# Декоратор для замера времени
# ------------------------------------------------------------
def time_measure(func):
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        return result, elapsed
    return wrapper

TwoThreeTree.insert = time_measure(TwoThreeTree.insert)
TwoThreeTree.delete = time_measure(TwoThreeTree.delete)

# ------------------------------------------------------------
# Генерация данных
# ------------------------------------------------------------
def generate_data(n=10000, low=-10000, high=10000):
    desktop_path = get_desktop_path()
    data_dir = os.path.join(desktop_path, 'meanings')
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    data = [random.randint(low, high) for _ in range(n)]
    with open(os.path.join(data_dir, 'input_data.txt'), 'w', encoding='utf-8') as f:
        for val in data:
            f.write(f"{val}\n")
    return data

# ------------------------------------------------------------
# Основная программа
# ------------------------------------------------------------
def main():
    print("Генерация 10 000 случайных чисел...")
    data = generate_data()
    print(f"Сгенерировано {len(data)} чисел, сохранены в {os.path.join(get_desktop_path(), 'meanings/input_data.txt')}")

    tree = TwoThreeTree()

    # 1. Вставка всех элементов с замерами
    print("\n--- Вставка 10 000 элементов ---")
    insert_times = []
    insert_steps = []
    for key in data:
        _, t = tree.insert(key)
        insert_times.append(t)
        insert_steps.append(tree.comparisons_count)

    avg_insert_time = sum(insert_times) / len(insert_times)
    avg_insert_steps = sum(insert_steps) / len(insert_steps)
    print(f"Среднее время вставки: {avg_insert_time:.8f} сек")
    print(f"Среднее число сравнений при вставке: {avg_insert_steps:.2f}")

    # 2. Поиск 100 случайных элементов
    search_sample = random.sample(data, 100)
    print("\n--- Поиск 100 случайных элементов ---")
    search_times = []
    search_steps = []
    for key in search_sample:
        start = time.perf_counter()
        tree.search(key)
        elapsed = time.perf_counter() - start
        search_times.append(elapsed)
        search_steps.append(tree.comparisons_count)

    avg_search_time = sum(search_times) / len(search_times)
    avg_search_steps = sum(search_steps) / len(search_steps)
    print(f"Среднее время поиска: {avg_search_time:.8f} сек")
    print(f"Среднее число сравнений при поиске: {avg_search_steps:.2f}")

    # 3. Удаление 1000 случайных элементов
    delete_sample = random.sample(data, 1000)
    print("\n--- Удаление 1000 случайных элементов ---")
    delete_times = []
    delete_steps = []
    for key in delete_sample:
        try:
            _, t = tree.delete(key)
            delete_times.append(t)
            delete_steps.append(tree.comparisons_count)
        except Exception as e:
            print(f"Ошибка при удалении {key}: {e}")

    if delete_times:
        avg_delete_time = sum(delete_times) / len(delete_times)
        avg_delete_steps = sum(delete_steps) / len(delete_steps)
        print(f"Среднее время удаления: {avg_delete_time:.8f} сек")
        print(f"Среднее число сравнений при удалении: {avg_delete_steps:.2f}")
    else:
        print("Не удалось выполнить ни одного удаления.")
        avg_delete_time = 0
        avg_delete_steps = 0

    # Сохранение результатов на рабочем столе
    desktop_path = get_desktop_path()
    results_file = os.path.join(desktop_path, "results.txt")
    with open(results_file, "w", encoding="utf-8") as f:
        f.write("РЕЗУЛЬТАТЫ ИЗМЕРЕНИЙ ДЛЯ 2-3 ДЕРЕВА\n")
        f.write("===================================\n")
        f.write(f"Вставка (10 000 элементов):\n")
        f.write(f"  Среднее время: {avg_insert_time:.10f} сек\n")
        f.write(f"  Среднее число сравнений: {avg_insert_steps:.2f}\n\n")
        f.write(f"Поиск (100 элементов):\n")
        f.write(f"  Среднее время: {avg_search_time:.10f} сек\n")
        f.write(f"  Среднее число сравнений: {avg_search_steps:.2f}\n\n")
        f.write(f"Удаление (1000 элементов):\n")
        f.write(f"  Среднее время: {avg_delete_time:.10f} сек\n")
        f.write(f"  Среднее число сравнений: {avg_delete_steps:.2f}\n")

    print(f"\nРезультаты сохранены в {results_file}")

    # Построение графиков
    try:
        plot_file = os.path.join(desktop_path, "analysis.png")
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))

        axes[0, 0].hist(insert_steps, bins=30, color='blue', alpha=0.7)
        axes[0, 0].set_title('Распределение шагов при вставке')
        axes[0, 0].set_xlabel('Количество сравнений')
        axes[0, 0].set_ylabel('Частота')

        axes[0, 1].hist(search_steps, bins=20, color='green', alpha=0.7)
        axes[0, 1].set_title('Распределение шагов при поиске')
        axes[0, 1].set_xlabel('Количество сравнений')
        axes[0, 1].set_ylabel('Частота')

        axes[1, 0].hist(delete_steps, bins=30, color='red', alpha=0.7)
        axes[1, 0].set_title('Распределение шагов при удалении')
        axes[1, 0].set_xlabel('Количество сравнений')
        axes[1, 0].set_ylabel('Частота')

        axes[1, 1].bar(['Insert', 'Search', 'Delete'],
                       [avg_insert_steps, avg_search_steps, avg_delete_steps],
                       color=['blue', 'green', 'red'])
        axes[1, 1].axhline(y=13.3, color='black', linestyle='--', label='log₂(10 000) ≈ 13.3')
        axes[1, 1].set_title('Среднее число сравнений vs теоретическая оценка')
        axes[1, 1].set_ylabel('Среднее количество сравнений')
        axes[1, 1].legend()

        plt.tight_layout()
        plt.savefig(plot_file, dpi=150, bbox_inches='tight')
        plt.close(fig)
        print(f"Графики сохранены в {plot_file}")
    except Exception as e:
        print(f"Не удалось построить графики: {e}")

    print("\nЭксперимент завершён успешно!")

if __name__ == "__main__":
    main()




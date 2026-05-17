import time
from random import randint, sample
from os import mkdir, listdir
import matplotlib.pyplot as plt

class TwoThreeNode:
    def __init__(self):
        self.keys = []           # Ключи (1 или 2 элемента)
        self.children = []       # Дочерние узлы (0, 2 или 3 элемента)
        self.parent = None       # Родительский узел

    def is_leaf(self):
        return len(self.children) == 0

    def is_two_node(self):
        return len(self.keys) == 1

    def is_three_node(self):
        return len(self.keys) == 2


class TwoThreeTree:
    def __init__(self):
        self.root = None
        self.comparisons = 0      # счётчик сравнений для измерения шагов

    def reset_counter(self):
        self.comparisons = 0

    # ------------------------- Поиск (с подсчётом сравнений) -------------------------
    def search(self, key):
        self.reset_counter()
        return self._search_recursive(self.root, key)

    def _search_recursive(self, node, key):
        if node is None:
            return False
        self.comparisons += 1   # проверка key in node.keys или хотя бы первое сравнение
        if key in node.keys:
            return True

        if key < node.keys[0]:
            child_idx = 0
            self.comparisons += 1
        elif node.is_two_node() or key < node.keys[1]:
            child_idx = 1
            self.comparisons += 2
        else:
            child_idx = 2
            self.comparisons += 2

        if child_idx < len(node.children):
            return self._search_recursive(node.children[child_idx], key)
        return False
-
    def insert(self, key):
        self.reset_counter()
        if self.root is None:
            self.root = TwoThreeNode()
            self.root.keys.append(key)
            return
        new_root = self._insert_recursive(self.root, key)
        if new_root:
            self.root = new_root

    def _insert_recursive(self, node, key):
        self.comparisons += 1
        if node.is_leaf():
            node.keys.append(key)
            node.keys.sort()
            if len(node.keys) == 3:
                return self._split_node(node)
            return None

        self.comparisons += 1
        if key < node.keys[0]:
            child_idx = 0
        elif node.is_two_node() or key < node.keys[1]:
            child_idx = 1
            self.comparisons += 1
        else:
            child_idx = 2
            self.comparisons += 1

        child = node.children[child_idx]
        new_child = self._insert_recursive(child, key)

        if new_child:
            node.children.pop(child_idx)
            if new_child.keys[0] < node.keys[0]:
                node.children.insert(child_idx, new_child)
                node.children.insert(child_idx + 1, new_child.children[1])
            else:
                node.children.insert(child_idx, new_child.children[0])
                node.children.insert(child_idx + 1, new_child)
            node.keys = sorted(node.keys + [new_child.keys[0]])
            if len(node.keys) == 3:
                return self._split_node(node)
        return None

    def _split_node(self, node):
        left_node = TwoThreeNode()
        right_node = TwoThreeNode()
        left_node.keys.append(node.keys[0])
        right_node.keys.append(node.keys[2])
        if not node.is_leaf():
            left_node.children = node.children[:2]
            right_node.children = node.children[2:]
            for child in left_node.children:
                child.parent = left_node
            for child in right_node.children:
                child.parent = right_node
        parent_node = TwoThreeNode()
        parent_node.keys.append(node.keys[1])
        parent_node.children = [left_node, right_node]
        left_node.parent = parent_node
        right_node.parent = parent_node
        return parent_node

    def delete(self, key):
        self.reset_counter()
        if self.root is None:
            return
        self._delete_recursive(self.root, key)
        if self.root and self.root.is_leaf() and len(self.root.keys) == 0:
            self.root = None

    def _delete_recursive(self, node, key):
        self.comparisons += 1
        if key in node.keys:
            if not node.is_leaf():
                successor = self._find_successor(node, key)
                idx = node.keys.index(key)
                node.keys[idx] = successor
                self._delete_recursive(node.children[idx + 1], successor)
            else:
                node.keys.remove(key)
                if len(node.keys) == 0 and node != self.root:
                    self._restore_balance(node)
        else:
            self.comparisons += 1
            if key < node.keys[0]:
                child_idx = 0
            elif node.is_two_node() or key < node.keys[1]:
                child_idx = 1
                self.comparisons += 1
            else:
                child_idx = 2
                self.comparisons += 1
            if child_idx < len(node.children):
                self._delete_recursive(node.children[child_idx], key)

    def _find_successor(self, node, key):
        idx = node.keys.index(key)
        child = node.children[idx + 1]
        while not child.is_leaf():
            child = child.children[0]
        return child.keys[0]

    def _restore_balance(self, node):
        parent = node.parent
        if parent is None:
            return
        node_idx = parent.children.index(node)
        if node_idx > 0:
            left_sibling = parent.children[node_idx - 1]
            if left_sibling.is_three_node():
                self._borrow_from_left(node, left_sibling, parent, node_idx)
                return
        if node_idx < len(parent.children) - 1:
            right_sibling = parent.children[node_idx + 1]
            if right_sibling.is_three_node():
                self._borrow_from_right(node, right_sibling, parent, node_idx)
                return
        if node_idx > 0:
            self._merge_with_left(node, parent, node_idx)
        else:
            self._merge_with_right(node, parent, node_idx)

    def _borrow_from_left(self, node, left_sibling, parent, node_idx):
        node.keys.append(parent.keys[node_idx - 1])
        node.keys.sort()
        borrowed_key = left_sibling.keys.pop()
        parent.keys[node_idx - 1] = borrowed_key
        if not left_sibling.is_leaf():
            borrowed_child = left_sibling.children.pop()
            node.children.insert(0, borrowed_child)
            borrowed_child.parent = node

    def _borrow_from_right(self, node, right_sibling, parent, node_idx):
        node.keys.append(parent.keys[node_idx])
        node.keys.sort()
        borrowed_key = right_sibling.keys.pop(0)
        parent.keys[node_idx] = borrowed_key
        if not right_sibling.is_leaf():
            borrowed_child = right_sibling.children.pop(0)
            node.children.append(borrowed_child)
            borrowed_child.parent = node

    def _merge_with_left(self, node, parent, node_idx):
        left_sibling = parent.children[node_idx - 1]
        left_sibling.keys.append(parent.keys[node_idx - 1])
        left_sibling.keys.extend(node.keys)
        left_sibling.keys.sort()
        if not node.is_leaf():
            left_sibling.children.extend(node.children)
            for child in node.children:
                child.parent = left_sibling
        parent.keys.pop(node_idx - 1)
        parent.children.pop(node_idx)
        if len(parent.keys) == 0 and parent != self.root:
            self._restore_balance(parent)

    def _merge_with_right(self, node, parent, node_idx):
        right_sibling = parent.children[node_idx + 1]
        node.keys.append(parent.keys[node_idx])
        node.keys.extend(right_sibling.keys)
        node.keys.sort()
        if not right_sibling.is_leaf():
            node.children.extend(right_sibling.children)
            for child in right_sibling.children:
                child.parent = node
        parent.keys.pop(node_idx)
        parent.children.pop(node_idx + 1)
        if len(parent.keys) == 0 and parent != self.root:
            self._restore_balance(parent)


def time_measure(func):
    def wrapper(*args, **kwargs):
        started = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - started
        return result, elapsed
    return wrapper
TwoThreeTree.insert = time_measure(TwoThreeTree.insert)
TwoThreeTree.delete = time_measure(TwoThreeTree.delete)


# ---------------------- Генерация данных ----------------------
def generate_data(n=10000, low=-10000, high=10000):
    # Создаём папку, если её нет
    if 'meanings' not in listdir():
        mkdir('meanings')
    data = [randint(low, high) for _ in range(n)]
    with open('meanings/input_data.txt', 'w') as f:
        for val in data:
            f.write(f"{val}\n")
    return data


def main():
    # 1. Генерация массива из 10 000 целых чисел
    print("Генерация 10 000 случайных чисел...")
    data = generate_data()
    print(f"Сгенерировано {len(data)} чисел, сохранены в meanings/input_data.txt")

    # 2. Поэлементная вставка всех чисел с замерами времени и шагов
    print("\n--- Вставка 10 000 элементов ---")
    tree = TwoThreeTree()
    insert_times = []
    insert_steps = []

    for key in data:
        # insert возвращает (None, время) благодаря декоратору
        _, t = tree.insert(key)
        insert_times.append(t)
        insert_steps.append(tree.comparisons)   # после вставки счётчик уже накоплен

    avg_insert_time = sum(insert_times) / len(insert_times)
    avg_insert_steps = sum(insert_steps) / len(insert_steps)
    print(f"Среднее время вставки: {avg_insert_time:.8f} сек")
    print(f"Среднее количество сравнений при вставке: {avg_insert_steps:.2f}")

    # 3. Поиск 100 случайных элементов (из сгенерированного массива)
    search_sample = sample(data, 100)
    print("\n--- Поиск 100 случайных элементов ---")
    search_times = []
    search_steps = []
    for key in search_sample:
        start = time.perf_counter()
        tree.search(key)      # поиск сам обнуляет и заполняет comparisons
        elapsed = time.perf_counter() - start
        search_times.append(elapsed)
        search_steps.append(tree.comparisons)

    avg_search_time = sum(search_times) / len(search_times)
    avg_search_steps = sum(search_steps) / len(search_steps)
    print(f"Среднее время поиска: {avg_search_time:.8f} сек")
    print(f"Среднее количество сравнений при поиске: {avg_search_steps:.2f}")

    # 4. Удаление 1000 случайных элементов
    delete_sample = sample(data, 1000)
    print("\n--- Удаление 1000 случайных элементов ---")
    delete_times = []
    delete_steps = []
    for key in delete_sample:
        _, t = tree.delete(key)
        delete_times.append(t)
        delete_steps.append(tree.comparisons)

    avg_delete_time = sum(delete_times) / len(delete_times)
    avg_delete_steps = sum(delete_steps) / len(delete_steps)
    print(f"Среднее время удаления: {avg_delete_time:.8f} сек")
    print(f"Среднее количество сравнений при удалении: {avg_delete_steps:.2f}")

    # 5. Сохранение результатов в файл
    with open("results.txt", "w") as f:
        f.write("РЕЗУЛЬТАТЫ ИЗМЕРЕНИЙ ДЛЯ 2-3 ДЕРЕВА\n")
        f.write("====================================\n")
        f.write(f"Вставка (10 000 элементов):\n")
        f.write(f"  Среднее время: {avg_insert_time:.10f} сек\n")
        f.write(f"  Среднее число сравнений: {avg_insert_steps:.2f}\n\n")
        f.write(f"Поиск (100 элементов):\n")
        f.write(f"  Среднее время: {avg_search_time:.10f} сек\n")
        f.write(f"  Среднее число сравнений: {avg_search_steps:.2f}\n\n")
        f.write(f"Удаление (1000 элементов):\n")
        f.write(f"  Среднее время: {avg_delete_time:.10f} сек\n")
        f.write(f"  Среднее число сравнений: {avg_delete_steps:.2f}\n")
    print("\nРезультаты сохранены в results.txt")

    # 6. Построение графиков (для сравнения теории с практикой)
    try:
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        axes[0, 0].hist(insert_steps, bins=30, color='blue', alpha=0.7)
        axes[0, 0].set_title('Распределение шагов при вставке')
        axes[0, 0].set_xlabel('Количество сравнений')
        axes[0, 0].set_ylabel('Частота')

        axes[0, 1].hist(search_steps, bins=20, color='green', alpha=0.7)
        axes[0, 1].set_title('Распределение шагов при поиске')
        axes[0, 1].set_xlabel('Количество сравнений')

        axes[1, 0].hist(delete_steps, bins=30, color='red', alpha=0.7)
        axes[1, 0].set_title('Распределение шагов при удалении')
        axes[1, 0].set_xlabel('Количество сравнений')

        axes[1, 1].bar(['Insert', 'Search', 'Delete'],
                       [avg_insert_steps, avg_search_steps, avg_delete_steps],
                       color=['blue', 'green', 'red'])
        axes[1, 1].axhline(y=13.3, color='black', linestyle='--', label='log2(10000) ≈ 13.3')
        axes[1, 1].set_title('Среднее число сравнений vs теоретическая оценка')
        axes[1, 1].set_ylabel('Среднее количество сравнений')
        axes[1, 1].legend()
        plt.tight_layout()
        plt.savefig('analysis.png')
        print("Графики сохранены в analysis.png")
    except Exception as e:
        print(f"Не удалось построить графики (возможно, нет matplotlib): {e}")

    print("\nЭксперимент завершён.")


if __name__ == "__main__":
    main()




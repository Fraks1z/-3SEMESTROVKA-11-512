class TwoThreeNode:
    def __init__(self):
        self.keys = []           #Ключи (1 или 2 элемента)
        self.children = []             #Дочерние узлы (0, 2 или 3 элемента)
        self.parent = None           #Родительский узел

    def is_leaf(self):
        return len(self.children) == 0

    def is_two_node(self):
        return len(self.keys) == 1

    def is_three_node(self):
        return len(self.keys) == 2


class TwoThreeTree:
    def __init__(self):
        self.root = None

    def search(self, key):
        return self._search_recursive(self.root, key)       #Поиск ключа

    def _search_recursive(self, node, key):
        if node is None:
            return False

        if key in node.keys:
            return True

        if key < node.keys[0]:
            child_idx = 0
        elif node.is_two_node() or key < node.keys[1]:
            child_idx = 1
        else:
            child_idx = 2

        if child_idx < len(node.children):
            return self._search_recursive(node.children[child_idx], key)
        return False

    def insert(self, key):            #Добавление ключа
        if self.root is None:
            self.root = TwoThreeNode()
            self.root.keys.append(key)
            return
        new_root = self._insert_recursive(self.root, key)  #Если произошло разделение, вставляем ключ и определяем новый корень
        if new_root:
            self.root = new_root

    def _insert_recursive(self, node, key):   # Если узел лист, добавляем ключ
        if node.is_leaf():
            node.keys.append(key)
            node.keys.sort()
            if len(node.keys) == 3:    # Если получилось 3 ключа нужно разделить узел
                return self._split_node(node)
            return None

        if key < node.keys[0]:
            child_idx = 0
        elif node.is_two_node() or key < node.keys[1]:
            child_idx = 1
        else:
            child_idx = 2

        child = node.children[child_idx]
        new_child = self._insert_recursive(child, key)

        # Если дочерний узел был разделён, обновляем текущий узел
        if new_child:
            node.children.pop(child_idx)

            if new_child.keys[0] < node.keys[0]:
                node.children.insert(child_idx, new_child)
                node.children.insert(child_idx + 1, new_child.children[1])
            else:
                node.children.insert(child_idx, new_child.children[0])
                node.children.insert(child_idx + 1, new_child)

            node.keys = sorted(node.keys + [new_child.keys[0]])

            # Если текущий узел переполнен, разделяем его
            if len(node.keys) == 3:
                return self._split_node(node)

        return None

    def _split_node(self, node):      #Разделение узла с 3 ключами на два узла и создание нового родительского узла
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

    def delete(self, key):      #Удаление ключа из дерева
        if self.root is None:
            return

        self._delete_recursive(self.root, key)
        if (self.root and self.root.is_leaf() and        # Если корень стал пустым листом, удаляем его
                len(self.root.keys) == 0):
            self.root = None

    def _delete_recursive(self, node, key):
        if key in node.keys:
            if not node.is_leaf():            # Если узел не лист, заменяем ключ на преемника
                successor = self._find_successor(node, key)
                idx = node.keys.index(key)
                node.keys[idx] = successor
                self._delete_recursive(node.children[idx + 1], successor)
            else:
                node.keys.remove(key)
                if len(node.keys) == 0 and node != self.root:
                    self._restore_balance(node)
        else:
            if key < node.keys[0]:
                child_idx = 0
            elif node.is_two_node() or key < node.keys[1]:
                child_idx = 1
            else:
                child_idx = 2
            if child_idx < len(node.children):
                self._delete_recursive(node.children[child_idx], key)

    def _find_successor(self, node, key):    #Нахождение преемника ключа (наименьший ключ в правом поддереве)
        idx = node.keys.index(key)
        child = node.children[idx + 1]
        while not child.is_leaf():
            child = child.children[0]
        return child.keys[0]

    def _restore_balance(self, node):      #Восстановление баланса
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


"""
ТЕСТ(Для себя) 

def test_two_three_tree():
    tree = TwoThreeTree()

    # Тестирование вставки
    print("Тестирование вставки:")
    keys_to_insert = [10, 20, 5, 15, 25, 3, 7]
    for key in keys_to_insert:
        tree.insert(key)
        print(f"Вставлен ключ {key}")

    # Тестирование поиска
    print("\nТестирование поиска:")
    for key in [5, 15, 8, 25]:
        result = tree.search(key)
        print(f"Ключ {key}: {'найден' if result else 'не найден'}")

    # Тестирование удаления
    print("\nТестирование удаления:")
    keys_to_delete = [5, 10, 15]
    for key in keys_to_delete:
        print(f"Удаляем ключ {key}")
        tree.delete(key)

    # Проверка оставшихся ключей
    print("\nПроверка оставшихся ключей:")
    remaining_keys = [3, 7, 20, 25]
    for key in remaining_keys:
        result = tree.search(key)
        print(f"Ключ {key}: {'остался' if result else 'удален'}")

# Запуск тестов
if __name__ == "__main__":
    test_two_three_tree()
"""





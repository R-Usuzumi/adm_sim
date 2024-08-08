import numpy as np
import sys


def create_complete_binary_tree_adj_matrix(n):
    # nはノード数
    adj_matrix = np.zeros((n, n), dtype=int)

    for i in range(n):
        left_child = 2 * i + 1
        right_child = 2 * i + 2

        if left_child < n:
            adj_matrix[i][left_child] = 1
            adj_matrix[left_child][i] = 1  # 無向グラフなので双方向に1をセット

        if right_child < n:
            adj_matrix[i][right_child] = 1
            adj_matrix[right_child][i] = 1  # 無向グラフなので双方向に1をセット

    return adj_matrix


# ノード数1023の完全二分木の隣接行列を作成
n = int(sys.argv[1])
adj_matrix = create_complete_binary_tree_adj_matrix(n)

for i in range(len(adj_matrix)):
    for j in range(len(adj_matrix[i])):
        print(adj_matrix[i][j], end=" ")
    print()

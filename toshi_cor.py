import networkx as nx
import pygraphviz as pgv
from networkx.drawing.nx_agraph import graphviz_layout
import matplotlib.pyplot as plt
import random
from collections import deque
import numpy as np
import copy
import sys
import math
import os
from scipy.sparse.csgraph import dijkstra
from scipy.stats import pearsonr
"""
ランダムウォークがなぜ公平性を実現できるかを確かめる
"""


class NetworkSimulation:
    def __init__(self, adj_matrix, num_resources):

        self.G = nx.from_numpy_array(adj_matrix)
        self.n = self.G.number_of_nodes()
        self.G_A = adj_matrix
        self.G_D = self.create_shortest_path_matrix()

        # ユーザがいるノードとユーザがアクセスする資源
        self.num_users = (self.n + 1) // 4
        self.users = {}

        # 初期化資源
        self.num_resources = num_resources
        self.resources = {}

        self.mu = {}

        self.degrees = dict(self.G.degree())
        self.cc = dict(nx.closeness_centrality(self.G))

        # 資源の次数積と中心性積
        self.res_d_multi = []
        self.res_cc_multi = []
        self.sigmas = []
        self.cvs = []

    def init_user(self):
        """
        グラフのノードにユーザを重複なしで配置する     
        """

        # ランダムに配置
        random.seed(1)
        while len(self.users) < self.num_users:
            r = random.randint(0, self.n - 1)
            if r not in self.users:
                self.users[r] = r
                self.mu[r] = 0

        # cc_sorted = sorted(self.cc.items(), key=lambda x: x[1])
        # print(cc_sorted[:10])
        # for i in range(self.num_users):
        #     node = cc_sorted[i][0]
        #     self.users[node] = node
        #     self.mu[node] = 0
        # print(self.users)
        print(list(self.users.items())[:10])

    def init_resources(self):
        """
        グラフのノードに資源を重複なしでランダムに配置する
        """
        for k in range(self.num_users):
            r = random.uniform(0.8, 1.2)

        while len(self.resources) < self.num_resources:
            r = random.randint(0, self.n - 1)
            if r not in self.resources:
                self.resources[r] = r
        print(list(self.resources.items())[:10])

    def init_network(self):
        self.init_user()
        self.init_resources()

    def create_shortest_path_matrix(self):
        """
         i-j成分がノードiからノードjまでの最短経路を格納している行列を作成
        """

        shortest_path_matrix = np.full((self.n, self.n), np.inf)

        for node in range(self.n):
            dists_to_nodes = nx.single_source_dijkstra_path_length(self.G,
                                                                   source=node)
            for target_node, dist in dists_to_nodes.items():
                shortest_path_matrix[node][target_node] = dist

        return shortest_path_matrix

    def random_walk(self, resource_x):
        neighbors = list(self.G.neighbors(resource_x))
        k = len(neighbors)

        sumTi = 0
        r = random.random()
        for x_pr in neighbors:
            if x_pr in self.resources:
                continue

            Ti = 1 / k

            if r < sumTi + Ti:
                return x_pr

            sumTi += Ti
        return resource_x

    def get_result(self, result_file):
        for line in open(result_file, "r"):
            result = line.split()

            resources = result[3:]
            d_multi = 1
            cc_multi = 1

            for resource in resources:
                d_multi *= self.degrees[int(resource)]
                cc_multi *= self.cc[int(resource)]

            for user in self.users.values():
                min_dist = float("inf")
                for nu in range(self.num_resources):
                    resource = int(result[nu + 3])
                    dist = self.G_D[user][resource]
                    if dist < min_dist:
                        min_dist = dist
                self.mu[user] = min_dist

            dists = list(self.mu.values())
            sigma = np.std(dists)
            mean = np.mean(dists)
            cv = sigma / mean

            self.res_d_multi.append(d_multi)
            self.res_cc_multi.append(cc_multi)
            self.sigmas.append(sigma)
            self.cvs.append(cv)

            self.mu = {user: 0 for user in self.users.values()}

    def print_data(self, t):
        with open("tree_toshi.res", 'a') as f:
            f.write(
                f"t {t} entity {' '.join(map(str, self.resources.values()))}\n"
            )

    def plot_distribution(self, data, description, filename):
        plt.figure(figsize=(10, 6))
        plt.hist(data, bins=30, edgecolor='k', alpha=0.7)
        plt.title(description)
        plt.xlabel(description)
        plt.ylabel('Frequency')
        plt.grid(True)
        plt.savefig(filename)
        plt.show()

    def draw_tree(self, filename):
        """
        グラフの描画
        """
        pos = graphviz_layout(self.G, prog='twopi')
        plt.figure(figsize=(20, 15))
        node_size = 1500
        nx.draw(self.G,
                pos,
                with_labels=True,
                node_size=node_size,
                node_color="white",
                font_size=20,
                font_weight="bold",
                edgecolors="black")
        common_nodes = set(self.users) & set(self.resources)
        nx.draw_networkx_nodes(self.G,
                               pos,
                               nodelist=list(set(self.users) - common_nodes),
                               node_color="red",
                               node_size=node_size)
        nx.draw_networkx_nodes(
            self.G,
            pos,
            nodelist=list(set(self.resources) - common_nodes),
            node_color="blue",
            node_size=node_size)
        nx.draw_networkx_nodes(self.G,
                               pos,
                               nodelist=list(common_nodes),
                               node_color="purple",
                               node_size=node_size)

        plt.savefig(filename)
        plt.show()

    def scatter_plot(self, x, y, title, xlabel, ylabel, file_basename=None):
        """
        ノードの次数とユーザからそのノードへの距離のばらつきの散布図を生成する
        """
        cor, _ = pearsonr(x, y)
        plt.scatter(x, y)
        plt.xlabel(xlabel, fontsize=14)
        plt.ylabel(ylabel, fontsize=14)

        plt.title(title, fontsize=18)

        x_mean = np.mean(x)
        y_mean = np.mean(y)
        plt.axvline(x=x_mean,
                    color='r',
                    linestyle='--',
                    label=f'Average x = {x_mean:.2f}')
        plt.axhline(y=y_mean,
                    color='b',
                    linestyle='--',
                    label=f'Average y = {y_mean:.2f}')

        # 相関係数をプロットに追加

        plt.text(0.95,
                 0.05,
                 f'r = {cor:.2f}',
                 horizontalalignment='right',
                 verticalalignment='bottom',
                 transform=plt.gca().transAxes,
                 fontsize=14,
                 bbox=dict(facecolor='white', alpha=0.5))

        if file_basename:
            filename = title + "_" + file_basename + "_" + str(
                self.num_resources) + ".png"
            plt.savefig(f"pic/{filename}")
        #plt.show()

    def run_simulation(self, T, seed):
        random.seed(seed)
        for t in range(T):

            # if t >= (T / 2):
            #     self.print_data(t)
            self.print_data(t)

            # key = random.randint(0, self.num_resources - 1)
            resource_x = random.choice(list(self.resources.keys()))
            resource_xpr = self.random_walk(resource_x)
            self.resources.pop(resource_x)
            self.resources[resource_xpr] = resource_xpr

        self.get_result("tree_toshi.res")

        # 散布図の取得
        file_basename = os.path.splitext(os.path.basename(tplfile))[0]

        if is_save:
            print('save')
            self.scatter_plot(self.res_d_multi, self.cvs, "D_vs_CV", "D", "CV",
                              file_basename)
            self.scatter_plot(self.res_d_multi, self.sigmas, "D_vs_sigma", "D",
                              "sigma", file_basename)
            # self.scatter_plot(self.res_cc_multi, self.cvs, "CC_vs_CV", "CC",
            #                   "CV", file_basename)
            # self.scatter_plot(self.res_cc_multi, self.sigmas, "CC_vs_sigma",
            #                   "CC", "sigma", file_basename)

        else:
            self.scatter_plot(self.res_d_multi, self.cvs, "D_vs_CV", "D", "CV")
            self.scatter_plot(self.res_d_multi, self.sigmas, "D_vs_sigma", "D",
                              "sigma")
            # self.scatter_plot(self.res_cc_multi, self.cvs, "CC_vs_CV", "CC",
            #                   "CV")
            # self.scatter_plot(self.res_cc_multi, self.sigmas, "CC_vs_sigma",
            #                   "CC", "sigma")
        # self.plot_distribution(self.M, 'M', f'lam{self.lam_T_lam}mavg.png')


if __name__ == "__main__":
    tplfile = sys.argv[1]
    num_resources = int(sys.argv[2])
    T = int(sys.argv[3])
    seed = sys.argv[4]
    is_save = int(sys.argv[5]) == 1

    adj_matrix = np.loadtxt(tplfile)

    simulation = NetworkSimulation(adj_matrix, num_resources)
    simulation.init_network()
    simulation.run_simulation(T, seed)

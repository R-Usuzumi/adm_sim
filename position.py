#!/usr/bin/env python3
# coding: UTF-8
import matplotlib.pyplot as plt
from numpy.random import *
import networkx as nx
import numpy as np
import random
import math
import sys

try:
    import pygraphviz
    from networkx.drawing.nx_agraph import graphviz_layout
except ImportError:
    try:
        import pydot
        from networkx.drawing.nx_pydot import graphviz_layout
    except ImportError:
        raise ImportError("This example needs Graphviz and either "
                          "PyGraphviz or pydot")

from collections import defaultdict



class Graph(object):
    """ class of Graph g
    """
    def __init__(self, n):
        self._n = n # number of nodes
        self._nodes = [Node(i) for i in range(n)] # nodes in Graph G
        self._A = np.zeros((n, n))


    def init_nodes(self, gfile):
        for line in open(gfile, 'r'):
            i, j ,w = map(int, line.split())
            self._A[i,j] = w
        
            tok = line.split()
            self._nodes[int(tok[0])]._k += 1
            self._nodes[int(tok[0])]._d += float(tok[2])
            self._nodes[int(tok[0])]._link.append(Link(self._nodes[int(tok[0])], self._nodes[int(tok[1])], float(tok[2])))    

class Node(object):
    """ class of node i
    """
    def __init__(self, i):
        self._i = i # node id
        self._k = 0 # degree of node i 
        self._d = 0 # weighted degree of node i 
        self._link = [] # links  
        self._n = 0 # number of resources on node i

class Link(object):
    """ class of link i, j
    """
    def __init__(self, i, j, w):
        self._i = i # node i
        self._j = j # node j
        self._w = w # link weight

class User(object):
    """ class of user i
    """
    def __init__(self, i):
        self._i = i # user id
        self._cnode = None # current node
        self._rate = 0 # access rate a_i



class Centrality(object):
    
    def __init__(self, n, k, type):
        self._n = n
        self._edge = None
        self._type = type
        self._central = {}
        self._users = [User(i) for i in range(k)]  # ユーザのいるノードのリスト
        self._k = k
        self._k_now = 0
        self._graph = None

    def initGraph(self, gfile):
        """ set Graph's info
        Args:
            gfile : link list file
        Returns:
        """
        self._graph = Graph(self._n)
        self._graph.init_nodes(gfile)

    def set_edge(self):
        g = nx.Graph(self._graph._A)
        if self._type == "BC":
            self._edge = nx.betweenness_centrality(g)
        elif self._type == "CC": 
            self._edge = nx.closeness_centrality(g)
        else:
            assert self._edge is None, "no exist"
            
    def select_node(self, node_list):
        select_list = {}
        while self._k_now + len(select_list) < self._k:
            r = random.randint(0,len(node_list)-1)
            select_list[r] = node_list[r]
            
        select_list = list(select_list.values())

        
        for k in range(len(select_list)):
            self._users[self._k_now]._cnode = self._graph._nodes[select_list[k]]
            self._k_now += 1
    
    def add_user(self, node_list):
        """
        ユーザ追加の際に発生する分岐

        if 現在のユーザ ＋ 追加したいユーザの数 ＞ 指定したユーザ数 
           乱数を発生させランダムにn選択

        else (指定したユーザ数を超えない場合)
           そのまま追加

        """
                
        if self._k_now + len(node_list) > self._k:
            self.select_node(node_list)
            #print(self._UserList)
            
        else:
            for k in range(len(node_list)):
                self._users[self._k_now]._cnode = self._graph._nodes[node_list[k]]
                self._k_now += 1

                
    def init_user(self):
        for i in range(self._n):
            self._central[i] = self._edge[i]
        self._central = sorted(self._central.items(), key=lambda x:x[1])

        min = self._central[0][1]
        node_list = []

        for i in range(self._n):
            if self._k_now >= self._k:
                assert self._k_now == self._k, "error k_now over k"
                break
            
            # 同じ数値がくるまで配列に追加
            if self._central[i][1] == min:
                node_list.append(self._central[i][0])
            # 異なる数値が現れたときにユーザへ追加
            else:
                #print(node_list)
                self.add_user(node_list)
                
                # リストの初期化 + 配列の要素の追加
                node_list = []
                node_list.append(self._central[i][0])
                min = self._central[i][1]


    def print_user(self):
        for user in self._users:
            print("{0} ".format(user._cnode._i), end="")
        print("")            



def main():
    """

    N : ノード数
    nu : キャッシュ数
    lam : 制御パラメータ
    alpha : 安全係数(0.1)
    name : 中心性指標の種類
    File : 隣接行列のデータのファイル名

    """
    # パラメータ設定-------------------
    
    N = int(sys.argv[1])   # ノード数
    row = int(sys.argv[2]) # ユーザ数を決定するパラメータ row=2 -> k = N/2
    k = int((N+1)/row)     # ユーザ数
    gfile = sys.argv[3]    # トポロジファイル
    type = sys.argv[4]     # ユーザ配置の種類

    t = int(sys.argv[5])   # シード値  
    random.seed(t)   
    
    
    if type == "BC":
        # Betweenness Centrality(BC)
        BC = Centrality(N,k,type)
        BC.initGraph(gfile)
        BC.set_edge()
        BC.init_user()
        BC.print_user()

    elif type == "CC":
        
        # Closeness Centrality (CC)
        CC = Centrality(N,k,type)
        CC.initGraph(gfile)
        CC.set_edge()
        CC.init_user()
        CC.print_user()

    elif type == "random":
        user = {}
        while True:
            r = random.randint(0,N-1)
            user[r] = 1
            if len(user) >= k:
                break
            
        for i in user:
            print("{0} ".format(i),end="")
        print("")
        
    else :
        print("no exist")
    
        
        
if __name__ == "__main__":
    main()

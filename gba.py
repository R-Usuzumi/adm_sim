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


class Node(object):
    """各ノードの次数のリスト
    """
    def __init__(self, id):
        self._id = id
        self._d = 0
        

class GBA_model(object):
    def __init__(self, N, m, alpha):
        self._N = N
        self._m = m
        self._d = np.zeros(self._N)
        self._sum_d = 0

        self._alpha = alpha

        self._NodeList = []
        self._n = m

        self._A = np.zeros((self._N, self._N))
        
        
    def complete_graph(self):
        """ 初期ノードの配置
 
        Args:
        Returns:
        """
        
        ## 完全グラフの作成
        for i in range(self._m):
            for j in range(i+1,self._m):
                self._A[i,j] = 1
                self._A[j,i] = 1
                
                self._sum_d += 2
                
            ## ノードの情報追加
            self._NodeList.append(Node(i))         # ノードの追加
            self._NodeList[i]._d = self._m - 1     # 次数データ

        ## m+1番目のノードの追加
        self._NodeList.append(Node(self._m))         
        
        for i in range(self._m):
            ## m+1番目の情報追加
            self._A[i, self._m] = 1
            self._A[self._m, i] = 1

            self._sum_d += 2
            
            self._NodeList[i]._d += 1
            self._NodeList[self._m]._d += 1


        self._n += 1   ## ノード数確認
        self._sum_d +=  (self._m + 1) * self._alpha      # 総次数
               
   
    def add_node(self, n):
        """ ノードの追加　と　リンクの更新
 
        Args: 
            n : 追加するノード番号 
        Returns:
        """
        self._NodeList.append(Node(n))

        addlist = self.select_node()
        
        for i in addlist:
            self._A[i,n] = 1
            self._A[n,i] = 1

            self._sum_d += 2
            
            self._NodeList[i]._d += 1
            self._NodeList[n]._d += 1

        self._n += 1   ## ノード数確認

        assert self._NodeList[n]._d == self._m ,"error"

        self._sum_d += (self._alpha - 1)
        
    def select_node(self) :  
        """ 接続するノードの選択
 
        Args: 
        Returns:
           addList : 接続するノードのリスト
        """
        node = [0] * self._N
        

        addList = []

        

        while True :
            sumP = 0
            r = random.random()
            
            for i in range(self._n):
                p = (self._NodeList[i]._d + (self._alpha - 1)) / self._sum_d  ## ノードの次数 / 総次数
                #print("p {0}".format(p))
                if r <= sumP + p :
                    node[i] = 1
                    break
                sumP += p
                
            s = 0
            for i in range(self._N):
                s += node[i]
                
            if s == self._m :
                for i in range(self._N):
                    if node[i] == 1:
                        addList.append(i)
                break
            
        return addList
        
                        
    def generate_network(self):
        """ ネットワークの生成

        Args: 
        Returns:
        """
        for i in range(self._m+1, self._N):
            self.add_node(i)

            #print("add node {0}".format(i))

        #print(self._n, self._N)
        assert self._n == self._N , "node is not success"
        for i in range(self._N):
            self._d[i] = self._NodeList[i]._d


            
    def print_network(self) :
        """ ネットワークの隣接リストの表示(print)

        Args: 
        Returns:
        """
         
        for i in range(self._N):
            for j in range(self._N):
                if self._A[i,j] > 0:
                    print(i,j,"1")
            
            
        

        
def main():

    N = int(sys.argv[1]) # ノード数
    m = int(sys.argv[2]) # BA ネットワークにおける追加ノードが張るリンク数
    alpha = int(sys.argv[3]) # alpha = 1 で BA
    t = int(sys.argv[4]) # シード値
    random.seed(t)
            
    assert alpha >= 1 , "alpha is  lower than  1"
    G = GBA_model(N, m, alpha)
    G.complete_graph()
    G.generate_network()
    G.print_network()

    
    
        
if __name__=="__main__":
    main()

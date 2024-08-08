#!/usr/bin/env python3
# coding: UTF-8
from __future__ import print_function
cimport numpy as np

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import math
import sys
from scipy.sparse.csgraph import dijkstra

cdef class CV_M(object):

    cdef public int _N, _nu, _k, _lam
    cdef public int _t, _s, _T, _endTime
    cdef public double _dg_d, _dg_avg
    cdef public double _M_avg, _cv, _M_error
    cdef public list _UserList, _rate, _dg, _stay , _mu
    cdef public list _M
    cdef public double[:,:] _ag, _dm


    def __init__(self, N, row, delta, s):
        self._N = N
        self._nu = int((self._N+1)/delta)
        #self._lam = lam
        self._M_avg = 0
        self._k = int((self._N+1)/row)
        self._rate = [0] * self._k
        self._ag = np.zeros((N, N))
        self._dm = np.zeros((N, N))
	
        self._dg = [0] * self._N
        self._UserList = []  
        self._mu = [0] * self._k
        self._endTime = 0
	
        self._cv = 0
        self._M_error = 0
        self._dg_d = 0
        self._dg_avg = 0
        self._stay = [0] * self._N
        self._T = 0
        self._s = s
        self._M = []

    def init_AG(self, gfile, ufile):
        i=0
        self._UserList = []
        # トポロジ情報の取得
        for line in open(gfile, 'r'):
            i, j ,w = map(int, line.split())
            self._ag[i,j] = w

        # ユーザ位置情報の取得
        for line in open(ufile, 'r'):
            tok = line.split()
            assert self._k == len(tok), "error: user={0}, tok={1}".format(self._k, len(tok))
    
            for user in tok:
                self._UserList.append(int(user))

        
        self._dm = dijkstra(self._ag) # delay Matrix

        

    def delay(self,i, d, nu):
        if d > self._dm[i, nu]:
            return self._dm[i, nu]
        else:
            return d
        
    cdef input_file(self, gfile, ufile, rfile):        
        cdef int i, j, nu
        cdef double m, d, dispersion
        cdef list M,  tok
        
        M = []
        dispersion = 0	             
                        
        self.init_AG(gfile, ufile)
                            
        for line in open(rfile, "r"):
            tok = line.split()
                    
            self._M_avg += float(tok[self._nu+4])      
              
            M.append(float(tok[self._nu+4]))
                    
            self._T += 1

                    
            for i in range(self._k):
                d = 10000.0
                for nu in range(self._nu):
                    # ユーザ k と各キャッシュの最短のものを検索
                    d = self.delay(self._UserList[i], d, int(float(tok[nu+3])))
                    self._stay[int(float(tok[nu+3]))] += 1
                                
                assert d < 1000, "error"
                self._mu[i] += d

                    
        # M の平均
        self._M_avg /= self._T
            
        # M の分散
        for m in M :
            dispersion += (m-self._M_avg)**2
        dispersion /= (self._T-1)


        """
        # 信頼区間の計算
        self._M_error[j] = 1.96 * math.sqrt(dispersion[j]/self._T[j])
        """

        self._endTime = self._T
            
           
    cdef calc_CV(self):
        cdef int i, j
        cdef double mu_avg, mu_avg_sq, mu_sq, fi
	
                              
        mu_avg = 0
        mu_avg_sq = 0
        mu_sq = 0

        for i in range(self._k):
            self._mu[i] /= float(self._endTime)

            mu_avg += self._mu[i] / self._k       # mu の平均
            mu_sq += (self._mu[i]**2) / self._k   # mu の二乗の平均
                
        mu_avg_sq = mu_avg**2        # mu の平均の二乗

        
        fi = 0
        fi = mu_avg_sq / mu_sq 
        self._cv = (1/fi) - 1

    def data_init(self, gfile, ufile, rfile):
        self.input_file(gfile, ufile, rfile)
        self.calc_CV()
	
    def	print_data(self):
        print("cv ",end="")
        print("{0} ".format(self._cv))
        
    
        print("M_avg ",end="")
        print("{0} ".format(self._M_avg))
        

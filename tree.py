#!/usr/bin/env python3
# coding: UTF-8
from numpy.random import *
import numpy as np
import random
import sys

N = int(sys.argv[1])

ag = np.zeros((N, N))
i = 0
n = 0
while True:
    for j in range(2) :
        append = i * 2 + (j+1)
            
        ag[i][append] = 1
        ag[append][i] = 1

        n += 1
    if n == N-1:
        #print(ag)
        break
    i += 1

for i in range(N):
    for j in range(N):
        if ag[i, j] > 0:
            print("{0} {1} {2}".format(i, j, int(ag[i, j])))
    


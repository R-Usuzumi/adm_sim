#!/usr/bin/env python3
# coding: UTF-8
from __future__ import print_function
cimport numpy as np
import random
import numpy as np
from scipy.sparse.csgraph import dijkstra
import sys
import math

cdef class Graph(object):
    """ class of Graph g
    """
    cdef public list _nodes, tok
    cdef public int _n, i, j
    cdef public double w
    cdef public double[:,:] _A

    def __init__(self, int n):
        self._n = n # number of nodes
        self._nodes = [Node(i) for i in range(n)] # nodes in Graph G
        self._A = np.zeros((n, n), dtype=np.float64)


    def init_nodes(self, gfile):
        for line in open(gfile, 'r'):
            i, j ,w = map(int, line.split())
            self._A[i,j] = w
        
            tok = line.split()
            self._nodes[int(tok[0])]._k += 1
            self._nodes[int(tok[0])]._d += float(tok[2])
            #self._nodes[int(tok[0])]._link.append(Link(self._nodes[int(tok[0])], self._nodes[int(tok[1])], float(tok[2])))
            self._nodes[int(tok[0])]._link[int(tok[1])] = float(tok[2])    

cdef class Entity(object):
    """ class of entitiy l
    """
    cdef public int _i
    cdef public Node _cnode
    def __init__(self, int i):
        self._i = i # entity id
        self._cnode = None # current node

    def move(self, Node node):
        self._cnode._n -= 1
        self._cnode = node
        self._cnode._n += 1

        
cdef class Node(object):
    """ class of node i
    """
    cdef public int _i, _k
    cdef public double _d
    cdef public dict _link
    cdef public int _n
    
    def __init__(self, int i):
        self._i = i # node id
        self._k = 0 # degree of node i 
        self._d = 0 # weighted degree of node i 
        self._link = {} # links  
        self._n = 0 # number of resources on node i

cdef class Link(object):
    """ class of link i, j
    """
    cdef public Node _i
    cdef public Node _j
    cdef public float _w
    def __init__(self, Node i, Node j, float w):
        self._i = i # node i
        self._j = j # node j
        self._w = w # link weight

cdef class User(object):
    """ class of user i
    """
    cdef public int _i
    cdef public Node _cnode
    cdef public double _rate
    cdef public dict _access
    def __init__(self, int i):
        self._i = i # user id
        self._cnode = None # current node
        self._rate = 0 # access rate a_i
        self._access = {} # user access to entity
        
cdef class Network(object):
    cdef public int _n, _nu, _k
    cdef public list  _entities, _users
    cdef public double _lam, _kappa
    cdef public dict _d_ij, _p
    cdef public Graph _graph
    
    def __init__(self, int n, int nu, int k, double lam, double kappa):
        self._n = n # number of nodes
        self._nu = nu # number of entities
        self._k = k # number of users

        self._entities = [Entity(i) for i in range(nu)] # list of entities
        self._users = [User(i) for i in range(k)] # list of users
        self._graph = None # network g
        
        self._kappa = kappa 
        self._lam = lam 
        self._d_ij = {} # distance(hopps) between node i and node j
    
    
    def initGraph(self, gfile):
        """ set Graph's info
        Args:
            gfile : link list file
        Returns:
        """
        self._graph = Graph(self._n)
        self._graph.init_nodes(gfile)
    
    def initUser(self, ufile, a, b):
        """ set user's info
        Args:
            ufile : user position file
        Returns:
        """
        for line in open(ufile, 'r'):
            tok = line.split()
            assert self._k == len(tok), "error: user={0}, tok={1}".format(self._k, len(tok))
            
            for k in range(self._k):
                r = random.uniform(a, b) # user rate is satisfied a<=rate<= b
                self._users[k]._cnode = self._graph._nodes[int(tok[k])]
                self._users[k]._rate = r
            #random.seed()
                
    def initEntity(self):
        """ set entity's info
        Args:
        Returns:
        """
        for entity in self._entities:
            r = random.randint(0, self._n-1)
            entity._cnode = self._graph._nodes[r]
            #entity._cnode = self._graph._nodes[0]
            entity._cnode._n += 1
                
    def set_dij(self):
        """ set distance between node i and node j
        Args:
        Returns:
        """
        dm = dijkstra(self._graph._A)
        for i in range(self._n):
            self._d_ij[i,i] = 0
            for j in range(i+1,self._n):
                self._d_ij[i,j] = dm[i,j]
                self._d_ij[j,i] = dm[j,i]
            
    cdef void setRates(self):
        """ set access rate p (dictionary)
            user i to entity l
        Args:
        Returns:
        """
        cdef int l, count
        cdef double mini
        cdef User user
        cdef list p_array

        for user in self._users:
            user._access = {}
            mini = 100000000.0
            p_array = []
            count = 0
            for entity in self._entities:
                                
                if self._d_ij[user._cnode._i, entity._cnode._i] == mini :
                    p_array.append(entity._i)
                    count += 1
                if self._d_ij[user._cnode._i, entity._cnode._i] < mini:
                    mini = self._d_ij[user._cnode._i, entity._cnode._i]
                    p_array=[entity._i]
                    count = 1

            assert count > 0, "count error"

            for l in p_array:
                user._access[l] = float(user._rate/count)


        
            
    def calcTi_random(self, Entity v):
        """ calc transition probability of whether entity v move to node u
            method : random walk
        Args:
            v : entity  
            u : destination node 
        Returns:
            Ti : calculation result of transition probability
        """
        Ti = 1 / v._cnode._k
        return Ti
            
    
    cdef double calcTi_MCMC(self, Entity v, int u):
        """ calc transition probability of whether entity v move to node u
            method : MCMC

        Args:
            v : entity 
            u : destination node
        Returns:
            Ti : calculation result of transition probability
        """
        cdef double delta_mi, Ti

        delta_mi = self.calc_delta_mi(v, u)
        
        
        if delta_mi <= 0:
            Ti = np.exp(-self._kappa * self._lam * delta_mi) / v._cnode._k
        else:
            Ti = np.exp(-(1 - self._kappa) * self._lam * delta_mi) / v._cnode._k

        return Ti

    cdef double calc_delta_mi(self, Entity v, int u):
        """ calc delta m_i
            method : d_next - d_now
        Args:
            v : entity 
            u : destination node
        Returns:
            delta_mi : delta mi when entity v move node u
        """
        cdef double delta_mi, D_now, D_next, p
        cdef User user

        delta_mi = 0.0
        for user in self._users:
            #p = self._p[user._i, v._i]
            if v._i in user._access:
                p = user._access[v._i]
                D_now = self._d_ij[user._cnode._i, v._cnode._i] * p
                D_next = self._d_ij[user._cnode._i, u] * p

                delta_mi += D_next - D_now
        
        return delta_mi

    def set_ti(self, Entity v, int u):
        """ select pattern of ti and calc ti
        Args:    
            v : entity  
            u : destination node 
        Returns:
            ti : transition probability
        """
        
        # if entity exsist same node 2 or more 
        if v._cnode._n >= 2 :
            ti = self.calcTi_random(v)

        # if only one entity
        else :
            # if already entity exsists in destination node
            
            if self._graph._nodes[u]._n >= 1:
                ti = 0 # don't move
            else :
                ti=self.calcTi_MCMC(v, u)
            
        return ti
            
    def move_entity(self, Entity v):
        """  move entity v
        Args:
             v : entity
        Returns:
        """
        sumTi = 0
        r = random.random()
        
        assert v._cnode._n >= 1, "entity does not exsist : n = {0}".format(v._cnode._n)
        assert len(v._cnode._link) == v._cnode._k

        for j in v._cnode._link:
            #j = i._j # j is i's adjacent node
            
            #assert type(j) is Node, "j is not Node. j is {0}.".format(type(j))
            
            ti = self.set_ti(v, j)

            if r < sumTi + ti :
                # adjust user rate
                v.move(self._graph._nodes[j])
                self.setRates()
                break
            sumTi += ti
                
            
    
    cdef double calcM(self):
        """  calc and return value of M
        Args:
        Returns:
             M (float): calculation result of M
        """
        cdef double M
        cdef Entity entity 
        cdef User user
        M = 0.0

        for user in self._users:
            for entity in self._entities:
                if entity._i in user._access:
                    # r_ij * d_ij
                    M += user._access[entity._i] * self._d_ij[entity._cnode._i, user._cnode._i]
                
        
        assert M > 0, "error {0}".format(M)
        
        return M

    def sim_init(self, gfile, ufile, a, b, t) :
        random.seed(t)
        self.initGraph(gfile)
        self.initUser(ufile, a, b)
        self.initEntity()
        self.set_dij()
        self.setRates()

    def print_result(self, int t):
        """ print result each time
            ex) t 1 entity 5 7 13 M 55.5
        """
        print("t {0} entity ".format(t), end="")
        for entity in self._entities:
            print("{0} ".format(entity._cnode._i), end="")

        M = self.calcM()
        print("M {0}".format(M))

    def simulation(self, int endTime, int t_lam, double lam) :

        for t in range(endTime):
            v = random.randint(0, self._nu-1)
            self.move_entity(self._entities[v])

            if t == t_lam:
                self._lam = lam
            
            if t >= (endTime/2) :
                self.print_result(t)

        
        

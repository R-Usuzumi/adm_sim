#!/usr/bin/env python3

from network import Network
import sys

def main():
    # set parameter -------------------
    
    n = int(sys.argv[1])
    lam = float(sys.argv[2])
    row = int(sys.argv[3]) # ユーザ数のパラメータ
    delta = int(sys.argv[4]) # エンティティ数のパラメータ
    nu = int((n+1)/delta)
    k = int((n+1)/row)
    gfile = sys.argv[5]
    ufile = sys.argv[6]
    t = sys.argv[7]
    
    kappa = 0.1

    lam_0 = 0.1
    a = 0.8
    b= 1.2
    t_lam = 10000
    endTime = 100000

    # simulation -----------------------
    
    net = Network(n, nu, k, lam_0, kappa)
    #net = Network(n, nu, k, lam, kappa)
    net.sim_init(gfile, ufile, a, b, t)
    net.simulation(endTime, t_lam, lam)
    
    
if __name__ == "__main__":
    main()

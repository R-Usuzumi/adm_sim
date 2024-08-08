#!/usr/bin/env python3
# coding: UTF-8

from result import CV_M
import sys


def main():


    N = int(sys.argv[1])
    gfile = sys.argv[2]
    ufile = sys.argv[3]
    rfile = sys.argv[4]
    row = int(sys.argv[5])
    delta = int(sys.argv[6])
    #lam = int(sys.argv[7])
    #t = int(sys.argv[7])

    s = 10
    
    cv_list = CV_M(N, row, delta, s)
    cv_list.data_init(gfile,ufile,rfile)
    cv_list.print_data()

        
    
if __name__ == "__main__":
    main()

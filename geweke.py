#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
/*================================================================
*   Copyright (C) 2020. All rights reserved.
*   Author：Leon Wang
*   Date：Sat Jul  4 20:43:37 2020
*   Email：leonwang@bu.edu
*   Description： 
================================================================*/
"""


from gibbs import Model, w_mu_nominator# analysis:ignore
from data_simu import generate_data

import numpy as np
import matplotlib.pyplot as plt


from mcmc_plot import trace_plot, get_trace_list




def forward_sample(d, q_star, n_sample):
    """
        Function to simulate ppca data using X= WZ + \sigma^2 I_n
        param: d, dimension of data
        param: q_star, true dimension of principle components
        param: n_sample, numebr of observations
        param: a_star_list, jx1 vector, 1/variance parameter to generate W_j ~ N(0, 1/a_j I_d)
    """
    # sampling for z
    mu_z = np.zeros([q_star])
    sigma2_z = np.diag(np.ones([q_star]))
    Z_star = np.random.multivariate_normal(mu_z, sigma2_z, n_sample).T


    # sampling for sigma2
    sigma2_star = np.random.gamma(3,0.1)
    
    # sampling for alpha
    a_star_list = np.random.gamma(1,2, d-1)
    
  #  print(sigma2_star)
    # sampling for w
    mu_w = np.zeros([d])
    W = np.zeros([d, q_star])
    for j in range(q_star):
        sigma2_w = np.diag(a_star_list[j] * np.ones(d))
        W_star_j = np .random.multivariate_normal(mu_w, sigma2_w)
        W[:, j] = W_star_j

    X = np.dot(W, Z_star) + np.random.normal(0, sigma2_star, [d, n_sample])

    return X



def geweke(iterations, d, q_star, prior_param, init_dict, n_sample, xi = None):
    forward_results = []
    for i in range(iterations):
        X_i = forward_sample(d, q_star, n_sample)
        forward_results.append(np.mean(np.std(X_i,axis=1)))
    
 
    gibbs_results = []                      
    X_i_origin = forward_sample(d, q_star, n_sample)
    inference = Model(X_i_origin, init_dict, iterations, q, prior_param, xi = xi)  
#    trace_plot([inference.gibbs_result()], var_list= ['sigma2_list', 'alpha_list'])      
    inference.gibbs_result()
    
    count =0
    X_i = X_i_origin.copy()
    while len(gibbs_results) != iterations:
        count += 1
        inference.gibbs_step(X_i)
        X_i = inference.sample_x()
        if count %10 ==0:
            gibbs_results.append(np.mean(np.std(X_i,axis=1)))
        
    return forward_results, gibbs_results
  


if __name__ == '__main__':

    d = 5
    q_star = 4
    q = d-1
    

        
    prior_param = dict({'beta_sigma2':2,
          'a_sigma2':10,
          'a_aj': 1 / np.linspace(1,10,q),
          'beta_aj':1 / np.linspace(1,10,q)    
    })
    
    init_dict = dict({'Z0':np.random.normal(0,1, [q, 1]),
        "sigma20":np.random.gamma(3,0.1),
        "w0":np.random.normal(0, 1, [d,q]),
        "alpha0": np.random.gamma(1,2, d-1)})   

    iterations = 1000
    n_sample = 50
    forward_results, gibbs_results = geweke(iterations, d, q_star, prior_param, init_dict, n_sample)
    
    
    
    indx = 0
    #plt.scatter(np.sort(np.array(forward_results)[:,indx]), np.sort(np.array(gibbs_results)[:,indx]))
    plt.scatter(np.sort(np.array(forward_results[500:])), np.sort(np.array(gibbs_results[500:])))
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.show()
    
    
print(np.mean(np.array(forward_results))/np.mean(gibbs_results))
    
    
import seaborn as sns    
sns.distplot(np.array(forward_results[500:]))
sns.distplot(np.array(gibbs_results[500:]))
plt.show()

a=gibbs_results
b= np.mean(gibbs_results)
plt.acorr(a-b, normed=True, usevlines=False, maxlags=10, label=u'thinned')
plt.show()
import numpy as np
from matplotlib import pyplot as plt
import scipy

N = 1000

if False:
    D = [0.0]
    dmu = 0.5
    mu = np.arange(-5, 5 + dmu, dmu)
    P = np.exp( -(mu**2)/2 )/np.sqrt(2*np.pi)
    sample = np.random.normal(0, 1, N)

if True:
    D = [0.5, 1.5]
    dmu = 0.05
    #mu = np.arange(-3, 4 + dmu, dmu)
    mu = np.arange(-1, 1 + dmu, dmu)
    p1 = np.exp( -((mu-D[0])**2)/2 )/np.sqrt(2*np.pi)
    p2 = np.exp( -((mu-D[1])**2)/2 )/np.sqrt(2*np.pi)
    
    P = p1*p2
    P = P/np.sum(P*dmu)
    sample = np.random.normal((D[0] + D[1])/2, 1/np.sqrt(2), N)

if True:
    nD = 30
    D = np.random.chisquare(3, size=nD)
    dmu = 1
    mu = np.arange(0, 6 + dmu, dmu)
    P = np.full(mu.shape, np.nan)
    for i in range(mu.size):
        P[i] = np.prod(scipy.stats.chi2(i).pdf(D))
    P[0] = 0
    P = P/np.sum(P)


def mcmc1d(P, N, i_mu):


    # Algorithm:
    #
    #   1. First opinion fair coin is heads
    #      1a. If P_right > P_curr, step right
    #      1b. If P_right <= P_curr, get second opinion:
    #          Flip biased coin with p_heads = P_right/P_curr.
    #          If heads, follow first opinion.
    #          If tails, don't step.
    #
    #   2. First opinion coin is tails
    #      1a. If P_left > P_curr, step left
    #      1b. If P_left <= P_curr, get second opinion
    #          If P_right <= P_curr, get second opinion:
    #          Flip biased coin with p_heads = P_left/P_curr.
    #          If heads, follow first opinion.
    #          If tails, don't step.

    step_size = 1

    # History of steps
    i_mu_hist = np.zeros(N, dtype=np.int64)
    for i in range(N):
    
        # "First opinion" fair coin toss
        ht = np.random.binomial(1, 0.5)
    
        P_right = P[i_mu+1]
        P_curr = P[i_mu]
        P_left  = P[i_mu-1]
    
        if ht == 1:
            flip1 = "H"
            if P_right > P_curr:
                # If first opinion coin toss says step right and P is higher to right, step right
                flip2 = "N/A" # Not Applicable
                step_dir = 1
            else:
                # If first opinion coin toss says step right and P is lower to right, flip biased
                # coin with p_heads = P_right/P_curr as second opinion.
                ht = np.random.binomial(1, P_right/P_curr)
                if ht == 1:
                    flip2 = "H"
                    # Second opinion "H" means follow first opinion instructions
                    step_dir = 1
                else:
                    flip2 = "T"
                    # Don't take a step
                    step_dir = 0
        else:
            flip1 = "T"
            if P_left > P_curr:
                # If first opinion coin toss says step left and P is higher to left, step left
                flip2 = "N/A"
                step_dir = -1
            else:
                # If first opinion coin toss says step left and P is lower to left, flip biased coin
                # with p_heads = P_left/P_curr for second opinion.
                ht = np.random.binomial(1, P_left/P_curr)
                if ht == 1:
                    flip2 = "H" 
                    # Second opinion "H" means follow first opinion instructions
                    step_dir = -1
                else:
                    flip2 = "T"
                    # Don't take a step
                    step_dir = 0
    
        # Take step
        if step_dir != 0:
            i_mu = i_mu + step_size*step_dir
    
        # Handle steps out-of-bounds by not taking a step
        if i_mu < 1:
            i_mu = 0
        if i_mu > mu.shape[0] - 2:
            i_mu = mu.shape[0] - 2
    
        i_mu_hist[i] = i_mu
        
        if i < 100 or np.mod(i, 100) == 0:
            print('i = {0:3d}; step = {1:2d} P_left = {2:.5f}; P_curr = {3:.5f}; '\
                  .format(i, step_dir, P_left, P_curr), end="")
            print('P_right = {0:.5f}; Flip 1: {1:s}; Flip 2: {2:s}' \
                  .format(P_right, flip1, flip2))

    return i_mu_hist

i_mu_hist = mcmc1d(P, N, 2)

# Remove first 10% of history of steps
a = np.int(np.round(0.1*N))
i_mu_hist_r = i_mu_hist[a:]

if N <= 10000:
    plt.figure()
    plt.axvline(a, c='k', ls='--', label='burn-in step')
    plt.plot(mu[i_mu_hist])
    plt.grid()
    plt.xlabel('Step index, i_mu')
    plt.ylabel('$\mu$ associated with i_mu')

plt.figure()
plt.grid()
bins = 50
bins = mu - dmu/2 # Center bins on possible x positions
plt.hist(mu[i_mu_hist_r], bins=bins, density=True, histtype='step', 
         label='Metropolis sampling; {0:d} steps'.format(N))
plt.plot(mu, P, 'k.',label='Exact')
plt.ylabel('$p(\\nu|\\mathcal{D})$')
plt.xlabel('$\\nu$')
plt.ylim([0,1.2])
plt.legend(loc='upper left')
plt.title('$\mathcal{{D}}$=np.random.chisquare(3, size={0:d})'.format(nD))
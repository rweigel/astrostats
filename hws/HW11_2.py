import numpy as np
import emcee

from matplotlib import pyplot as plt
import scipy

nD = 30
# Draw nD samples from a chi-square distribution with three degrees of freedom.
# Objective is to use MCMC to find the posterior for the number of degrees
# of freedom.
D = np.random.chisquare(3, size=nD)
variable_str = '$\\nu$'


def log_LxP_chi2(theta, D):
    """Return Log( Likelihood * Posterior) given data D."""

    #print("theta = {0:.1f}".format(theta[0]))
    if theta >= 1:
        LxP = np.prod(scipy.stats.chi2(np.round(theta[0])).pdf(D))
    else:
        LxP = 0.0
    #print("LxP = {0:.1f}".format(LxP))

    if LxP == 0:
        return -np.inf
    else:
        return np.log(LxP)

log_LxP = log_LxP_chi2

# Compute analytic value for posterior
dnu = 1
nu = np.arange(1, 6 + dnu, dnu)
P = np.full(nu.shape, np.nan)
for i in range(nu.size):
    P[i] = np.prod(scipy.stats.chi2(nu[i]).pdf(D))
P[0] = 0
P = P/np.sum(P)



nstep = 1e3     # Number of steps each walker takes
nwalk = 10      # Number of initial values for theta
ndims = 1       # Number of unknown parameters in theta vector

# Create a set of 10 inital values for theta.
thetas_initial =  np.random.uniform(0.1, 5, (nwalk, ndims))

# Initialize the sampler object
sampler = emcee.EnsembleSampler(nwalk, ndims, log_LxP, args=(D, ))

# Run the MCMC algorithm for each initial theta for nsteps
sampler.run_mcmc(thetas_initial, nstep, progress=True);

# Get the values of theta at each step
samples = sampler.get_chain()

# print(samples.shape) # (nstep, nawlk, ndims)

plt.figure()
plt.plot(samples[:,0,0])
plt.title('First Walker')
plt.xlabel('Step')
plt.ylabel('$\\theta$')
plt.grid()


if False:
    plt.figure()
    #plt.hist(samples[:,0,0],bins=20)
    plt.hist(np.round(samples[:,0,0]),bins=20)
    plt.title('Histogram of $\\theta$ values for first walker')
    plt.ylabel('# in bin')
    plt.xlabel('$\\theta$')
    plt.grid()

plt.figure()
plt.hist(np.round(samples[:,0,0]),density=True, bins=np.arange(1,7)-0.5, label='emcee')
plt.plot(nu, P, 'k.', label='Exact')
plt.title('pdf of ' + variable_str + ' values for first walker')
plt.ylabel('p(' + variable_str + '|$\\mathcal{D})$')
plt.xlabel(variable_str)
plt.xticks(nu)
plt.title('$\mathcal{{D}}$=np.random.chisquare(3, size={0:d})'.format(nD))
plt.legend()
plt.grid()

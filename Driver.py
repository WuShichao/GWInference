## Marcus E. Lower (2017)

import numpy as np
import os, sys, time
import mod_GWInf as gwi
from scipy.interpolate import interp1d
import argparse

import pickle
#------------------------------------------------#
## Get job number:
parser = argparse.ArgumentParser(description='Setting name of output file.')
parser.add_argument('-f','--file',type=str,required=True,dest='filename',help='filename output')
job = parser.parse_args()

## Setting up sampling parameters:
ntemps = 16
nwalkers = 16
ndim = 8
nsteps = 20

## Waveform parameters:
fmax = 512.
fmin = 20.
Fs = 2*fmax
deltaF = 1./8.

## Load in data from file:
#data_file = np.load('injections/injection_'str(job.filename)'/injectionFFT_'+str(job.filename)+'.npy')
data_file = np.load('injections/injectionFFT.npy')
data = data_file[:,1]
data = data[:int(fmax/deltaF)+1]
freq = data_file[:,0].real[:int(fmax/deltaF)+1]

PSD_file = np.loadtxt("../../../../MonashGWTools/NoiseCurves/aLIGO_ZERO_DET_high_P_psd.txt")
PSD = PSD_file[:,1][:int(fmax/deltaF)+1]
PSD_interp_func = interp1d(PSD_file[:,0], PSD_file[:,1], bounds_error=False, fill_value=np.inf)
PSD = PSD_interp_func(freq)
#------------------------------------------------#

p0_e = gwi.get_p0(ntemps, ndim, nsteps, nwalkers, ecc=True)

p0_o = gwi.get_p0(ntemps, ndim, nsteps, nwalkers, ecc=False)

## Running sampler + get log evidence & log Bayes factor:
t1 = time.time()

sampler_e, pos, lnprob, rstate = gwi.run_sampler(p0_e, ntemps, nwalkers, ndim, nsteps, data, PSD, fmin, fmax, deltaF)
print 'finished sampling with e > 0top'
sampler_0, pos, lnprob, rstate = gwi.run_sampler(p0_o, ntemps, nwalkers, ndim, nsteps, data, PSD, fmin, fmax, deltaF)
print 'finished sampling with e = 0'

t2=time.time()
print 'time taken = ',t2-t1

## save samples

file = 'samples/samples_e_'+str(job.filename)
with open(file, 'wb') as handle:
    pickle.dump(sampler_e, handle, protocol=pickle.HIGHEST_PROTOCOL)

file = 'samples/samples_0_'+str(job.filename)
with open(file, 'wb') as handle:
    pickle.dump(sampler_0, handle, protocol=pickle.HIGHEST_PROTOCOL)
    
lnZe_pt, dlnZe_pt = gwi.get_Evidence(sampler_e, pos, lnprob, rstate)
lnZ0_pt, dlnZ0_pt = gwi.get_Evidence(sampler_0, pos, lnprob, rstate)

lnBF = lnZe_pt - lnZ0_pt
BF = np.exp(lnBF)

print "lnBF = {} ".format(BF)

np.savetxt('samples/BayesFactor/logEvidence_and_logBF_'+str(job.filename)+'.txt',np.c_[lnZe_pt, dlnZe_pt, dlnZ0_pt, dlnZ0_pt, BF])
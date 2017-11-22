## Script to create eccentric injection waveforms:
import numpy as np
import sys, os, argparse
import lalsimulation as lalsim
import lal

#sys.path.append('../../../../..')
import waveforms as wv
import tools as tools

def make_waveform(m1, m2, eccen, dist, job):
    '''
    Generates an eccentric timesries
    '''
    cmde = ["/bin/lalsim-inspiral -a EccentricFD -F -O -1 -u 0 -f 10 -r 20 -e "+str(eccen)+" -R 1024. -m1 "+str(m1)+" -m2 "+str(m2)+" -i 0 -d "+str(dist)+" > Injection_"+job+"/signal.dat"]
    cmde = ''.join(cmde)
    os.system(cmde)
    
    
def detector_strain(h_p, h_c, RA, DEC, psi, epoch, deltaF):
    
    tgps = lal.LIGOTimeGPS(epoch)
    gmst = lal.GreenwichMeanSiderealTime(tgps)
    
    # Antenna response:
    fplus, fcross = wv.AntennaResponse(RA, DEC, psi, epoch, ifo='H1')
    diff = lal.LALDetectorIndexLHODIFF
    
    timedelay = lal.TimeDelayFromEarthCenter(lal.CachedDetectors[diff].location, RA, DEC, tgps)
    timeshift = epoch + timedelay
    
    #Calculate the observed strain at the detector, properly shifting the waveform from geocenter to detector frame.
    h = np.zeros_like(h_p, dtype=complex)
    pit = np.pi*timeshift
    if timeshift != 0.0:
        shift = complex(1.0, 0)
        dshift = complex(-2.*np.sin(pit*deltaF)*np.sin(pit*deltaF), -2.*np.sin(pit*deltaF)*np.cos(pit*deltaF))
        for i in xrange(0,h_p.size):
            h[i] = shift*(fplus*h_p[i] + fcross*h_c[i])
            shift += shift*dshift
    else: h = (fplus*h_p) + (fcross*h_c)
        
    return h

parser = argparse.ArgumentParser(description='Setting name of output file.')
parser.add_argument('-f','--file',type=str,required=True,dest='filename',help='filename output')
inj = parser.parse_args()

os.system("mkdir Injection_"+str(inj.filename))

m1 = 31.2
m2 = 19.4
dist = 880.

min_e,max_e = np.log10(1.e-3),np.log10(0.5)
eccen = round(10**(np.random.uniform(low=min_e,high=max_e,size=1)),10)

make_waveform(m1, m2, eccen, dist, str(inj.filename))

RA = 90.#20.9375
DEC = 90.#45.
psi = 0.
epoch = 1000000008

data = np.loadtxt('Injection_'+str(inj.filename)+'/signal.dat')
deltaF = data[1,0] - data[0,0]

data_p = data[:,1] + 1j*data[:,2]
data_c = data[:,3] + 1j*data[:,4]
data_t = detector_strain(data_p, data_c, RA, DEC, psi, epoch, deltaF)

output = 'Injection_'+str(inj.filename)+'/injectionFFT_'+str(inj.filename)+'.npy'
np.save(output,np.c_[data[:,0],data_t])

np.savetxt('Injection_'+str(inj.filename)+'/true_parameters',np.c_[m1,m2,eccen,dist,RA,DEC])

print("Injection made")

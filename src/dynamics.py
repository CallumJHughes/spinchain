import matplotlib.pyplot as plt
import numpy as np
import re
import sys
from pylab import *
import cmath
import subprocess

#GET TARGET QUBIT LABEL FROM custom_string VARIABLE WRITTEN TO genetic.out FILE
gen = subprocess.check_output("sed -n '23p' genetic.out", shell=True)

target = ""

for char in range(len(gen)):
	if gen[char] == 124: # Checks for '|' symbol using ASCII code
		while gen[char] != 62:
			target = target + chr(gen[char+1]) # Character after '|' is target qubit label. Also converts ASCII code to char using chr() function
			char += 1
			if gen[char+1] == 62:
				break
	else:
		continue

#CHANGE FORMAT FOR THE COMPLEX NUMBERS FORTRAN->PYTHON
input=open('dynamics.data','r')
output=open('dynamics_formatted.data','a')
for line in input:
    line=re.sub(r'\(([^,\)]+),([^,\)]+)\)', r' \1+\2j ', line.replace(' ',''))
    line=re.sub(r'\+-',r'-',line)
    output.write(line+'\n')
output.close()

#READ THE DATA FROM FILE
fidelity = np.loadtxt('dynamics_formatted.data',dtype=complex,comments='#')

#SET SIZE FIGURE
plt.figure(figsize=(10,7))

#ARGUMENTS PASSED
totaltime=float(sys.argv[1])
injection=int(sys.argv[2])
N=int(sys.argv[3])

#CREATE PLOT
ax1=plt.subplot()

#DEFINE RANGES
ax1.set_xlim([0,totaltime])
ax1.set_ylim([0,1])

x = np.absolute(fidelity[:,0])

# Load the info file and get the initial/final vectors
init = fidelity[:, 1]*0.0
final = fidelity[:, 1]*0.0
numI = 0
numF = 0
initialIndexes = []
initialCoeffs = []
finalIndexes = []
finalCoeffs = []
inInit = True
with open("spinchain.out", "r") as f:
    for line in f:
        if "FINAL VECTOR" in line:
            inInit = False
            split = line.split()
            # final += fidelity[:, int(split[4])]
            finalIndexes.append(int(split[4]))
            numF += 1
        elif "INITIAL INJECTED" in line:
            split = line.split()
            # init += fidelity[:, int(split[5])]
            initialIndexes.append(int(split[5]))
            numI += 1
        elif "WITH COEFFICIENT" in line:
            split = line.split()
            realVal = float(split[4][:-1])
            imagVal = float(split[5][:-1])
            if inInit:
                initialCoeffs.append(complex(realVal, imagVal))
            else:
                finalCoeffs.append(complex(realVal, imagVal))
        elif "FOR MODE 2" in line:
            break

# Construct the vectors
for i in range(numI):
    init = init + np.conj(initialCoeffs[i]) * fidelity[:, initialIndexes[i]]
for i in range(numF):
    final = final + np.conj(finalCoeffs[i]) * fidelity[:, finalIndexes[i]]

#PLOT FIDELITY AGAINST INITIAL STATE AND TARGET STATE (CHANGE WHENEVER)
y1 = (np.absolute(init))**2
y2 = (np.absolute(final))**2
# for i in range(len(x)):
    # print(x[i], y1[i], y2[i])
plt.plot(x,y1,color='gray',lw=2,label=r'$|\langle\Psi(t)\vert \psi_{o}\rangle|^2$')
psistring = "psi_{" + target + "}"
plt.plot(x,y2,color='black',ls=':',lw=2,label=fr'$|\langle\Psi(t)\vert \{psistring}\rangle|^2$')

#SET SIZE OF AXIS TICKS
ax1.tick_params(axis='y', labelsize=20)
ax1.tick_params(axis='x', labelsize=20)

#SET LABEL NAMES
plt.xlabel('$\mathrm{t \cdot J_{max}}$',fontsize=25,color='black')
plt.ylabel("fidelity",fontsize=25,color='black')
plt.tight_layout()

#LEGEND
l=legend(loc=1,frameon=False,borderaxespad=0.0,fontsize=20)

#SAVE AS PNG PICTURE
savefig('dynamics.pdf',transparent=False)

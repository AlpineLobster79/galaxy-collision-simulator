G = 1.0

#softening factor to prevent singularities & stabilize integration
EPSILON = 0.03

#smaller timestep = more stable orbits, but slower
DT = 0.05

#barnes-hut opening angle (higher=faster but less accurate)
#controls speed & accuracy of barnes-hut approximation (commonly 0.5)
THETA = 0.7

#deeper tree = more accurate forces (better close interactions), but slower
#prevent infinite subdivision in pathological cases (may cause issues w/ very close particles)
MAX_DEPTH = 10  

#min node size to prevent infinite subdivision
MIN_SIZE = 0.01

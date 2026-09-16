G = 1.0

#softening factor to prevent singularities & stabilize integration
EPSILON = 0.03

#smaller timestep = more stable orbits, but slower
DT = 0.05

#barnes-hut opening angle (lower=faster but less accurate)
THETA = 0.7

#deeper tree = more accurate forces (better close interactions), but slower
MAX_DEPTH = 12

MIN_SIZE = 0.01  #min node size to prevent infinite subdivision

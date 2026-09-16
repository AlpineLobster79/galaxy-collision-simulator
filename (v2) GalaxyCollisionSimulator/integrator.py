from gravity import calc_acceleration

#symplectic leapfrog integrator
def leapfrog_step(positions, velocities, masses, dt, tree=None):
    
    acc = calc_acceleration(positions, masses, tree)
    
    velocities_half = velocities + 0.5 * acc * dt
    
    positions_new = positions + velocities_half * dt
    acc_new = calc_acceleration(positions_new, masses)
    velocities_new = velocities_half + 0.5 * acc_new * dt
    
    return positions_new, velocities_new
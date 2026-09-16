from gravity import build_tree, calc_acceleration

""" symplectic leapfrog integrator """
def leapfrog_step(positions, velocities, masses, dt):
    
    #current acceleration
    tree = build_tree(positions, masses)
    
    acc = calc_acceleration(positions, masses, tree)
    
    #half velocity step
    velocities_half = velocities + 0.5 * acc * dt
    
    #full position step
    positions_new = positions + velocities_half * dt
    
    #rebuild new tree ONCE
    new_tree = build_tree(positions_new, masses)
    
    acc_new = calc_acceleration(positions_new, masses, new_tree)
    
    #final velocity step
    velocities_new = velocities_half + 0.5 * acc_new * dt
    
    return positions_new, velocities_new
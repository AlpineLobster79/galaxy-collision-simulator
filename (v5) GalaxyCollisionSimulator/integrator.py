from gravity import build_tree, compute_acceleration

def leapfrog_step(
    positions,
    velocities,
    masses,
    dt
):
    """ BUILD TREE """
    tree = build_tree(positions, masses)
    
    """ CURRENT ACCELERATION """
    acc = compute_acceleration(positions, masses, *tree)
    
    """ HALF VELOCITY STEP """
    velocities_half = velocities + 0.5 * acc * dt
    
    """ POSITION STEP """
    positions_new = positions + velocities_half * dt

    """ NEW TREE (ONCE) """
    new_tree = build_tree(positions_new, masses)
    
    """ NEW ACCELERATION """
    acc_new = compute_acceleration(positions_new, masses, *new_tree)
    
    """ FINAL VELOCITY STEP """
    velocities_new = velocities_half + 0.5 * acc_new * dt
    
    return positions_new, velocities_new
    
    
    
"""
from gravity import build_tree, calc_acceleration

###symplectic leapfrog integrator
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
"""
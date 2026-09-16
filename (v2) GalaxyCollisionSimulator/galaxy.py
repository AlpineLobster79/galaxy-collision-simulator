from matplotlib import scale
import numpy as np
from constants import EPSILON, G

def create_galaxy(n_particles, radius, center, velocity, total_mass=1.0):
    #spiral angles
    theta = np.random.uniform(0, 2*np.pi, n_particles)
    
    #exponential disk distribution (compact)
    r = np.random.exponential(scale=radius/12, size=n_particles)
    r = np.clip(r, 0.2, radius) #limit radius to specified maximum
    
    #spiral arm perturbation
    theta += 2.0 * (r / radius)
    
    x = r * np.cos(theta)
    y = r * np.sin(theta)
    
    positions = np.column_stack((x, y))
    
    #stable orbital velocity
    M_enc = total_mass * (1 - np.exp(-r / scale))   #mass enclosed w/in radius r
    speed = np.sqrt((G * M_enc) / (r + EPSILON))
    
    vx = -speed * np.sin(theta)
    vy = speed * np.cos(theta)
    
    velocities = np.column_stack((vx, vy))
    
    #small velocity dispersion
    velocities += np.random.normal(scale=0.02, size=velocities.shape)
    
    #move galaxy into place
    positions += center
    velocities += velocity
    
    #star masses
    masses = np.full(n_particles, total_mass / n_particles)
    
    #black hole
    bh_mass = total_mass * 0.01
    
    #stellar bulge
    n_bulge = int(0.15 * n_particles)
    r_bulge = np.random.exponential(scale=radius/40, size=n_bulge)
    
    positions = np.vstack([positions, center])
    velocities = np.vstack([velocities, velocity])
    masses = np.concatenate([masses, [bh_mass]])
    
    #float32 performance boost    
    return (
        positions.astype(np.float32),
        velocities.astype(np.float32),
        masses.astype(np.float32)
    )
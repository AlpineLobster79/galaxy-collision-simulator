# from matplotlib import scale
import numpy as np
from constants import EPSILON, G

def create_galaxy(n_particles, radius, center, velocity, total_mass=1.0):
    
    """ DISK STARS  """
    disk_fraction = 0.85
    bulge_fraction = 0.15
    
    n_disk = int(n_particles * disk_fraction)
    n_bulge = int(n_particles * bulge_fraction)
    
    ### exponential disk ###
    theta_disk = np.random.uniform(0, 2*np.pi, n_disk)
    
    r_disk = np.random.exponential(scale=radius/5, size=n_disk)
    
    r_disk = np.clip(r_disk, 0.05, radius) #limit r to specified max
    
    #spiral perturbation
    theta_disk += 2.0 * (r_disk / radius)
    
    x_disk = r_disk * np.cos(theta_disk)
    y_disk = r_disk * np.sin(theta_disk)
    
    ### dense stellar bulge ###
    theta_bulge = np.random.uniform(0, 2*np.pi, n_bulge)
    
    r_bulge = np.random.exponential(scale=radius/30, size=n_bulge)
    
    r_bulge = np.clip(r_bulge, 0.001, radius/5)
    
    x_bulge = r_bulge * np.cos(theta_bulge)
    y_bulge = r_bulge * np.sin(theta_bulge)
    
    ### combine stars (disk + bulge) ###
    x = np.concatenate([x_disk, x_bulge])
    y = np.concatenate([y_disk, y_bulge])

    positions = np.column_stack((x, y))
    
    r = np.sqrt(x**2 + y**2)
    
    theta = np.arctan2(y, x)
    
    """ ORBITAL VELOCITIES """
    speed = np.sqrt(
        (G * total_mass * (1 - np.exp(-r / radius))) / (r + EPSILON)
    )
    
    speed *= 0.45
    
    vx = -speed * np.sin(theta)
    vy = speed * np.cos(theta)
    
    velocities = np.column_stack((vx, vy))
    
    #velocity dispersion
    velocities += np.random.normal(scale=0.02, size=velocities.shape)
    
    """ MOVE GALAXY INTO PLACE """
    positions += center
    velocities += velocity
    
    """ STAR MASSES """
    stellar_mass = total_mass * 0.98
    
    masses = np.full(len(positions), stellar_mass / len(positions))
    
    """ SUPERMASSIVE BLACK HOLE """
    bh_mass = total_mass * 0.02
    
    positions = np.vstack([positions, center])
    velocities = np.vstack([velocities, velocity])
    masses = np.concatenate([masses, [bh_mass]])
    
    return (
        np.ascontiguousarray(positions, dtype=np.float32),
        np.ascontiguousarray(velocities, dtype=np.float32),
        np.ascontiguousarray(masses, dtype=np.float32)
    )




    """
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
    """
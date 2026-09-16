import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

from galaxy import create_galaxy
from integrator import leapfrog_step
from constants import DT

#particle count
N = 3000

""" GALAXY 1 """
p1, v1, m1 = create_galaxy(
    n_particles=N,
    radius=6,
    center=np.array((-8, 0), dtype=np.float32),
    velocity=np.array((0.14, 0.03), dtype=np.float32),
    total_mass=1.0
)

""" GALAXY 2 """
p2, v2, m2 = create_galaxy(
    n_particles=N,
    radius=6,
    center=np.array((8, 0), dtype=np.float32),
    velocity=np.array((-0.14, -0.03), dtype=np.float32),
    total_mass=1.0
)

""" COMBINE GALAXIES """
positions = np.vstack((p1, p2))
velocities = np.vstack((v1, v2))
masses = np.concatenate((m1, m2))

""" MATPLOTLIB WINDOW """
fig, ax = plt.subplots(figsize=(10, 10))

def init():
    fig.patch.set_facecolor("black")
    ax.set_facecolor("black")

    ax.axis("off")

    ax.set_xlim(-30, 30)
    ax.set_ylim(-30, 30)
    
    return scat,

### PARTICLE DRAWING ###
scat = ax.scatter(
    positions[:, 0],
    positions[:, 1],
    s=0.3,
    c="white",
    alpha=0.6,
    edgecolors="none"
)


def update(frame):
    
    global positions, velocities
    
    if frame % 100 == 0:
        print(frame) #progress indicator
    
    positions, velocities = leapfrog_step(
        positions,
        velocities,
        masses,
        DT
    )
    
    #removes need to redraw scatter plot each frame, much faster
    scat.set_offsets(positions)
    
    return scat,
   
animation = FuncAnimation(
    fig,
    update,
    interval=1,     #smoother animation
    init_func=init,
    blit=True,      #can't get redraw trail effect when set to True, but much faster when True
    cache_frame_data=False  #reduce memory usage
)

plt.show()
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

from galaxy import create_galaxy
from integrator import leapfrog_step
from gravity import build_tree
from constants import DT

N = 1000
cached_tree = None
tree_frame = 0

# Galaxy 1
p1, v1, m1 = create_galaxy(
    n_particles=N, 
    radius=5, 
    center=np.array((-4, 0)), 
    velocity=np.array((1.2, 0.0)), 
    total_mass=1.0
)

# Galaxy 2
p2, v2, m2 = create_galaxy(
    n_particles=N,
    radius=5,
    center=np.array((4, 0)),
    velocity=np.array((-1.2, 0.0)),
    total_mass=1.0
)

positions = np.vstack((p1, p2))
velocities = np.vstack((v1, v2))
masses = np.concatenate((m1, m2))

fig, ax = plt.subplots(figsize=(10, 10))

scat = ax.scatter(
    positions[:, 0],
    positions[:, 1],
    s=0.3,
    c="white",
    alpha=0.6,
    edgecolors="none"
)

def init():
    fig.patch.set_facecolor("black")
    ax.set_facecolor("black")
    ax.axis("off")
    ax.set_xlim(-20, 20)
    ax.set_ylim(-20, 20)
    
    return scat,
    

def update(frame):
    if frame % 100 == 0:
        print(frame) #progress indicator
    
    global positions, velocities, cached_tree, tree_frame
    
    tree_frame += 1
    
    ##rebuild every 5 frames
    #if tree_frame % 5 == 0 or cached_tree is None:
        #cached_tree = build_tree(positions, masses)
    
    positions, velocities = leapfrog_step(
        positions,
        velocities,
        masses,
        DT,
        cached_tree
    )
    
    #removes need to redraw scatter plot each frame, much faster
    scat.set_offsets(positions)
    ##remove old scatter and redraw w/ trail effect
    #scat.remove()
    
    #scat = ax.scatter(
    #    positions[:, 0],
    #    positions[:, 1],
    #    s=0.3,
    #    c="white",
    #    alpha=0.05,
    #    edgecolors="none"
    #)
    
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
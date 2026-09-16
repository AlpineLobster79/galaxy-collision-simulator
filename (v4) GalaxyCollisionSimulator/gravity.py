import numpy as np
from numba import njit

from constants import (
    G,
    EPSILON,
    THETA,
    MAX_DEPTH
)
#from main import N

""" MAXIMUM TEE NODES """
MAX_NODES = 200000  #safe upper bound
#MAX_NODES = N * 32  #static allocation faster but no risk of overflow

""" BUILD TREE """
def build_tree(positions, masses):
    n = len(positions)
    
    # === allocate node arrays === #
    node_mass = np.zeros(MAX_NODES, dtype=np.float32)
    node_com_x = np.zeros(MAX_NODES, dtype=np.float32)
    node_com_y = np.zeros(MAX_NODES, dtype=np.float32)
    
    node_center_x = np.zeros(MAX_NODES, dtype=np.float32)
    node_center_y = np.zeros(MAX_NODES, dtype=np.float32)
    
    node_size = np.zeros(MAX_NODES, dtype=np.float32)
    
    #child indices
    children = np.full((MAX_NODES, 4), -1, dtype=np.int32)
    
    #particle index stored in node
    particle = np.full(MAX_NODES, -1, dtype=np.int32)
    
    # === root node === #
    min_x = np.min(positions[:, 0])
    max_x = np.max(positions[:, 0])
    min_y = np.min(positions[:, 1])
    max_y = np.max(positions[:, 1])
    
    size = max(max_x - min_x, max_y - min_y) + 1.0
    
    node_center_x[0] = (min_x + max_x) / 2
    node_center_y[0] = (min_y + max_y) / 2
    node_size[0] = size
    
    node_count = 1
    
    # === insert particles === #
    for i in range(n):
        px = positions[i, 0]
        py = positions[i, 1]
        pm = masses[i]
        
        current = 0
        depth = 0
        
        while True:
            old_mass = node_mass[current]
            new_mass = old_mass + pm
            
            #update center of mass
            if new_mass > 0:
                node_com_x[current] = (
                    node_com_x[current] * old_mass +
                    px * pm
                ) / new_mass
                
                node_com_y[current] = (
                    node_com_y[current] * old_mass +
                    py * pm
                ) / new_mass
                
            node_mass[current] = new_mass
            
            #empty leaf
            if (
                particle[current] == -1 and 
                children[current, 0] == -1
            ):
                particle[current] = i
                break
            
            #stop subdivision
            if depth >= MAX_DEPTH:
                break
            
            #subdivide if nec
            if children[current, 0] == -1:
                cx = node_center_x[current]
                cy = node_center_y[current]
                half_size = node_size[current] / 2
                quarter_size = node_size[current] / 4
                
                for q in range(4):
                    child = node_count
                    node_count += 1
                    
                    children[current, q] = child
                    
                    dx = -1 if q in (0, 2) else 1
                    dy = -1 if q in (0, 1) else 1
                    
                    node_center_x[child] = cx + dx * quarter_size
                    node_center_y[child] = cy + dy * quarter_size
                    node_size[child] = half_size
                    
                #reinsert existing particle
                old_particle = particle[current]
                particle[current] = -1
                
                opx = positions[old_particle, 0]
                opy = positions[old_particle, 1]
                
                quadrant = 0
                
                if opx > cx:
                    quadrant += 1
                if opy > cy:
                    quadrant += 2
                
                current_old = children[current, quadrant]
                
                particle[current_old] = old_particle
                
                node_mass[current_old] = masses[old_particle]
                node_com_x[current_old] = opx
                node_com_y[current_old] = opy
                
            #descend into correct child
            cx = node_center_x[current]
            cy = node_center_y[current]
            
            quadrant = 0
            
            if px > cx:
                quadrant += 1
            if py > cy:
                quadrant += 2
                
            current = children[current, quadrant]
            depth += 1
            
    return (
        node_mass,
        node_com_x,
        node_com_y,
        node_center_x,
        node_center_y,
        node_size,
        children,
        particle,
        node_count
    )

""" COMPUTE ACCELERATIONS """
@njit(cache=True, fastmath=True)
def compute_acceleration(
    positions,
    masses,
    node_mass,
    node_com_x,
    node_com_y,
    node_center_x,
    node_center_y,
    node_size,
    children,
    particle,
    node_count
):
    n = len(positions)
    
    accelerations = np.zeros_like(positions)
    
    for i in range(n):
        px = positions[i, 0]
        py = positions[i, 1]
        
        ax = 0.0
        ay = 0.0
        
        stack = np.empty(256, dtype=np.int32)
        stack_ptr = 0
        
        stack[stack_ptr] = 0  #start with root
        stack_ptr += 1
        
        while stack_ptr > 0:
            stack_ptr -= 1
            node = stack[stack_ptr]
            
            if node_mass[node] == 0:
                continue
            
            #self-node
            if (
                particle[node] == i and 
                children[node, 0] == -1
            ):
                continue
            
            dx = node_com_x[node] - px
            dy = node_com_y[node] - py
            
            dist2 = dx**2 + dy**2 + EPSILON**2
            dist = np.sqrt(dist2)
            
            #barnes-hut criteria
            if (
                children[node, 0] == -1 or 
                node_size[node] / dist < THETA
            ):
                inv_dist3 = 1.0 / (dist2 * dist)
                
                force = G * node_mass[node] * inv_dist3
                
                ax += dx * force
                ay += dy * force
            else:
                for q in range(4):
                    child = children[node, q]
                    if child != -1:
                        stack[stack_ptr] = child
                        stack_ptr += 1
                        
        accelerations[i, 0] = ax
        accelerations[i, 1] = ay
    return accelerations


"""
from logging import root

import numpy as np

from constants import (
    G,
    EPSILON,
    THETA,
    MAX_DEPTH,
    MIN_SIZE
)


#node_mass = np.zeros(MAX_NODES)
#node_com_x = np.zeros(MAX_NODES)
#node_com_y = np.zeros(MAX_NODES)
#children = np.full((MAX_NODES, 4), -1)


class QuadNode:
    
    __slots__ = (
        "x", "y", "size",
        "mass", "com_x", "com_y",
        "particle",
        "children",
        "depth"
    )
    
    def __init__(self, x, y, size, depth=0):
        self.x = x
        self.y = y
        self.size = size
        self.depth = depth
        
        self.mass = 0.0
        self.com_x = 0.0
        self.com_y = 0.0
        
        self.particle = -1
        
        self.children = None
    
    def contains(self, px, py):
        h = self.size / 2
        
        return (
            (self.x - h <= px < self.x + h) and 
            (self.y - h <= py < self.y + h)
        )
    
    def subdivide(self):
        h = self.size / 2
        q = self.size / 4
        
        d = self.depth + 1
        
        self.children = [
            QuadNode(self.x - q, self.y - q, h, d),  # SW
            QuadNode(self.x + q, self.y - q, h, d),  # SE
            QuadNode(self.x - q, self.y + q, h, d),  # NW
            QuadNode(self.x + q, self.y + q, h, d)   # NE
        ]
        
    def insert(self, index, positions, masses):
        px, py = positions[index]
        
        if not self.contains(px, py):
            return False
        
        old_mass = self.mass
        self.mass += masses[index]
        
        if self.mass > 0:
            self.com_x = (self.com_x * old_mass + px * masses[index]) / self.mass
            self.com_y = (self.com_y * old_mass + py * masses[index]) / self.mass
        
        #empty leaf
        if self.particle == -1 and self.children is None:
            self.particle = index
            return True
        
        #stop subdivision
        if (self.depth >= MAX_DEPTH) or (self.size <= MIN_SIZE):
            return True
        
        #subdivide if nec
        if self.children is None:
            self.subdivide()
            
            old_particle = self.particle
            self.particle = -1
            
            for child in self.children:
                if child.insert(old_particle, positions, masses):
                    break
                
        #insert new particle
        for child in self.children:
            if child.insert(index, positions, masses):
                return True
        
        return False

# BUILD TREE
def build_tree(positions, masses):
    
    min_x = np.min(positions[:, 0])
    max_x = np.max(positions[:, 0])
    
    min_y = np.min(positions[:, 1])
    max_y = np.max(positions[:, 1])
    
    size = max(max_x - min_x, max_y - min_y) + 1.0
    
    root = QuadNode(
        (min_x + max_x) / 2, 
        (min_y + max_y) / 2, 
        size
    )
    
    for i in range(len(positions)):
        root.insert(i, positions, masses)
    
    return root

# BARNES-HUT FORCE CALCULATION
def compute_acceleration(index, positions, root):
    
    px, py = positions[index]
        
    ax = 0.0
    ay = 0.0
    
    stack = [root]
    
    while stack:
        node = stack.pop()
        
        if node.mass == 0:
            continue
        
        #ignore self-node
        if (
            node.particle == index and 
            node.children is None
        ):
            continue
        
        dx = node.com_x - px
        dy = node.com_y - py
        
        dist2 = dx**2 + dy**2 + EPSILON**2
        dist = np.sqrt(dist2)
        
        #barnes-hut criteria
        if (
            node.children is None or
            node.size / dist < THETA
        ):
            inv_dist3 = 1.0 / (dist2 * dist)
            
            force = G * node.mass * inv_dist3
            
            ax += dx * force
            ay += dy * force
        else:
            stack.extend(node.children)
            
    return ax, ay

# ALL PARTICLE ACCELERATIONS
def calc_acceleration(positions, masses, root=None):
    if root is None:
        root = build_tree(positions, masses)
        
    accelerations = np.zeros_like(positions)
    
    for i in range(len(positions)):
        
        ax, ay = compute_acceleration(i, positions, root)
        
        accelerations[i, 0] = ax
        accelerations[i, 1] = ay
    
    return accelerations
    
"""
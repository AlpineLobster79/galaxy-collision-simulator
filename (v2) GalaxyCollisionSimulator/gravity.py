import numpy as np
from numba import njit
from constants import G, EPSILON

THETA = 0.5     #controls speed & accuracy of barnes-hut approximation
#THETA = 1.0     #higher=faster, but less accurate (0.5 is a common choice)
#MAX_DEPTH = 10   #prevent infinite subdivision in pathological cases
MAX_DEPTH = 7   #lower for better performance (may cause issues w/ very close particles)
MIN_SIZE = 0.01  #min node size to prevent infinite subdivision

"""
node_mass = np.zeros(MAX_NODES)
node_com_x = np.zeros(MAX_NODES)
node_com_y = np.zeros(MAX_NODES)
children = np.full((MAX_NODES, 4), -1)
"""

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

def compute_acceleration(index, positions, masses, root):
    
    stack = [root]
    
    ax = 0.0
    ay = 0.0
    
    px, py = positions[index]
    
    while stack:
        node = stack.pop()
        
        if node.mass == 0:
            continue
        
        #skip self-only node
        if (
            node.particle == index and 
            node.children is None
        ):
            continue
        
        dx = node.com_x - px
        dy = node.com_y - py
        
        dist2 = dx*dx + dy*dy + EPSILON*EPSILON
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

def calc_acceleration(positions, masses, root=None):
    if root is None:
        root = build_tree(positions, masses)
    accelerations = np.zeros_like(positions)
    
    for i in range(len(positions)):
        
        ax, ay = compute_acceleration(i, positions, masses, root)
        
        accelerations[i, 0] = ax
        accelerations[i, 1] = ay
    
    return accelerations
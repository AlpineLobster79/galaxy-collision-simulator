import sys
import numpy as np

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QApplication, QWidget

from galaxy import create_galaxy
from integrator import leapfrog_step
from constants import DT

""" PARTICLE COUNT """
N = 3000

""" GALAXIES """
p1, v1, m1 = create_galaxy(
    n_particles=N,
    radius=6,
    center=np.array((-8, 0), dtype=np.float32),
    velocity=np.array((0.14, 0.03), dtype=np.float32),
    total_mass=1.0
)

p2, v2, m2 = create_galaxy(
    n_particles=N,
    radius=6,
    center=np.array((8, 0), dtype=np.float32),
    velocity=np.array((-0.14, -0.03), dtype=np.float32),
    total_mass=1.0
)

positions = np.vstack((p1, p2))
velocities = np.vstack((v1, v2))
masses = np.concatenate((m1, m2))

""" WINDOW """
class GalaxyWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Galaxy Merger Simulator")
        self.resize(800, 800)
        self.setStyleSheet("background-color: black;")
        
        #sim timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_simulation)
        self.timer.start(10)    #update every 10 ms
        
""" UPDATE SIMULATION """
def update_simulation(self):
    global positions, velocities
    
    positions, velocities = leapfrog_step(
        positions,
        velocities,
        masses,
        DT
    )
    
    self.update()  #trigger repaint
    
""" DRAW PARTICLES """
def paintEvent(self, event):
    painter = QPainter(self)
    painter.setRenderHint(QPainter.Antialiasing, False)
    
    pen = QPen()
    pen.setColor(QColor(255, 255, 255, 150))  #slightly transparent white    
    painter.setPen(pen)
    
    width = self.width()
    height = self.height()
    
    scale = 12
    
    for p in positions:
        x = width * 0.5 + p[0] * scale
        y = height * 0.5 + p[1] * scale
        painter.drawPoint(int(x), int(y))
        
    painter.end()
    
""" APPLICATION """
app = QApplication(sys.argv)
window = GalaxyWindow()
window.show()
sys.exit(app.exec())
    
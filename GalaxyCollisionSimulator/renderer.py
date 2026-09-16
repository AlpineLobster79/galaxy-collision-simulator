import time
# import numpy as np

from OpenGL.GL import *

from PySide6.QtCore import QTimer
from PySide6.QtOpenGLWidgets import QOpenGLWidget


class GalaxyRenderer(QOpenGLWidget):
    def __init__(self, sim):
        
        super().__init__()
        
        self.sim = sim
        
        #fps tracking  
        self.last_time = time.time()
        self.fps = 0.0
        
        #progress tracking
        self.frame_count = 0

        #update timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_simulation)
        self.timer.start(0)    #update as fast as possible
        
    """ OPENGL INIT """
    def initializeGL(self):
        glClearColor(0.0, 0.0, 0.0, 0.05)    #black background
        glEnable(GL_BLEND)            #alpha blending, smooth points
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glEnable(GL_POINT_SMOOTH)       #smoother points
        glPointSize(2.0)        #default point size
        
    """ RESIZE WINDOW """
    def resizeGL(self, w, h):
        glViewport(0, 0, w, h)
        
    """ SIM UPDATE """
    def update_simulation(self):
        #fps calculation
        now = time.time()
        delta = now - self.last_time
        self.last_time = now
    
        if delta > 0:
            self.fps = 1.0 / delta
        
        #increment frame count for progress tracking
        self.frame_count += 1
        #update every 100 frames
        if self.frame_count % 100 == 0:
            print(
                f"Frame: {self.frame_count} | "
                f"FPS: {self.fps:.1f} | "
                f"Particles: {len(self.sim.positions)}"
            )
            
        self.sim.step()  #physics step
        self.update()    #trigger repaint, redraw window
    
    """ MOUSE ZOOM """
    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        if delta > 0:
            self.sim.camera.zoom *= 0.9
        else:
            self.sim.camera.zoom *= 1.1
    
    """ DRAW """
    def paintGL(self):
        ### trail effect ###
        #don't fully clear the screen, just draw a transparent black quad to fade prev frame slowly
        glColor4f(0.0, 0.0, 0.0, 0.5)    #fade effect, creating trails
        glBegin(GL_QUADS)
        
        glVertex2f(-1, -1)
        glVertex2f(1, -1)
        glVertex2f(1, 1)
        glVertex2f(-1, 1)
        
        glEnd()
        
        ### particle data ###
        positions = self.sim.positions
        camera = self.sim.camera
        
        ### bloom pass ###
        glPointSize(4.0)    #larger points for bloom
        glBegin(GL_POINTS)
        
        for p in positions:
            #transform to camera space
            x = (p[0] - camera.x) / camera.zoom
            y = (p[1] - camera.y) / camera.zoom
            
            glColor4f(1.0, 1.0, 1.0, 0.01)   #bright, transparent points for bloom
            
            glVertex2f(x, y)
        
        glEnd()
        
        ### main particle pass ###
        glPointSize(2.0)    #smaller points for main particles
        glBegin(GL_POINTS)
        
        for p in positions:
            #transform to camera space
            x = (p[0] - camera.x) / camera.zoom
            y = (p[1] - camera.y) / camera.zoom
            
            glColor4f(1.0, 1.0, 1.0, 0.35)   #less transparent points for main particles
            
            glVertex2f(x, y)
        
        glEnd()
    
    
from ctypes import alignment
import sys
import numpy as np

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QSlider
)
from PySide6.QtCore import Qt, QTimer

from renderer import GalaxyRenderer
from camera import Camera

from galaxy import create_galaxy
from integrator import leapfrog_step
from constants import DT

class GalaxySimulation:
    def __init__(self):
        self.camera = Camera()
        self.paused = False
        self.dt = DT
        N = 2000
        
        p1, v1, m1 = create_galaxy(
            n_particles=N,
            radius=6,
            center=np.array((-6, 0), dtype=np.float32),
            velocity=np.array((0.14, 0.03), dtype=np.float32),
            total_mass=1.0
        )

        p2, v2, m2 = create_galaxy(
            n_particles=N,
            radius=6,
            center=np.array((6, 0), dtype=np.float32),
            velocity=np.array((-0.14, -0.03), dtype=np.float32),
            total_mass=1.0
        )
        
        self.positions = np.vstack((p1, p2))
        self.velocities = np.vstack((v1, v2))
        self.masses = np.concatenate((m1, m2))
    
    """ SIM STEP """
    def step(self):
        if self.paused:
            return
        
        self.positions, self.velocities = leapfrog_step(
            self.positions,
            self.velocities,
            self.masses,
            self.dt
        )
        
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Galaxy Merger Simulator")
        self.resize(800, 800)
        self.sim = GalaxySimulation()
        self.renderer = GalaxyRenderer(self.sim)
        self.setFocusPolicy(Qt.StrongFocus)   #ensures keyboard input will work
        
        """ UI """
        container = QWidget()
        layout = QVBoxLayout()
        
        container.setLayout(layout)
        layout.addWidget(self.renderer)
        
        layout.setStretch(0, 20)   #make renderer take most space
        
        ### buttons ###
        #pause btn
        self.pause_btn = QPushButton("Pause")
        self.pause_btn.setStyleSheet(
            """
            QPushButton {
                background-color: white;
                color: black;
                font-weight: bold;
                padding: 8px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #2d6cdf;
                color: white;
            }
            """
        )
        self.pause_btn.clicked.connect(self.toggle_pause)
        #reset btn
        self.reset_btn = QPushButton("Reset")
        self.reset_btn.setStyleSheet(
            """
            QPushButton {
                background-color: white;
                color: black;
                font-weight: bold;
                padding: 8px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: red;
                color: white;
            }
            """
        )
        self.reset_btn.clicked.connect(self.reset_simulation)   #reinitialize entire window
        
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.pause_btn)
        button_layout.addWidget(self.reset_btn)
        layout.addLayout(button_layout)
        layout.setStretch(1, 1)    #buttons take less space
        
        #pointing hand cursor for buttons
        self.pause_btn.setCursor(Qt.PointingHandCursor)
        self.reset_btn.setCursor(Qt.PointingHandCursor)
        
        
        #timestep slider
        self.dt_slider = QSlider(Qt.Horizontal)
        
        self.dt_slider.setMinimum(1)
        self.dt_slider.setMaximum(100)
        
        self.dt_slider.setValue(5)
        
        self.dt_slider.valueChanged.connect(self.change_dt)
        
        layout.addWidget(QLabel("Timestep (ms)"))
        layout.setStretch(2, 1)
        layout.addWidget(self.dt_slider)
        layout.setStretch(3, 1)
        
        #pointing hand cursor for slider
        self.dt_slider.setCursor(Qt.PointingHandCursor)
        
        #fps & sim runtime timer label
        progress_layout = QHBoxLayout()
        self.fps_label = QLabel("FPS: 0.0")
        progress_layout.addWidget(self.fps_label)
        self.fps_label.setAlignment(Qt.AlignLeft)
        #self.timer = QTimer()
        #progress_layout.addWidget(self.timer)
        """
        NEW, FIG OUT
        """
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer_label)
        self.timer.start(1000)    #update timer label every 1 second
        self.runtime_label = QLabel("Simulation Runtime: 00:00:00")
        progress_layout.addWidget(self.runtime_label)
        self.runtime_label.setAlignment(Qt.AlignRight)
        layout.addLayout(progress_layout)
        
        self.ui_timer = QTimer()
        self.ui_timer.timeout.connect(self.update_ui)
        self.ui_timer.start(250)    #update UI every 0.25 seconds
        
        self.setCentralWidget(container)

    """
    NEW, FIG OUT
    """
    def update_timer_label(self):
        elapsed = self.renderer.start_time if hasattr(self, 'renderer') and self.renderer else 0
        hours, remainder = divmod(int(elapsed), 3600)
        minutes, seconds = divmod(remainder, 60)
        self.runtime_label.setText(f"Simulation Runtime: {hours:02d}:{minutes:02d}:{seconds:02d}")
        
    """ PAUSE """
    def toggle_pause(self):
        self.sim.paused = not self.sim.paused
        
        #paused state
        if self.sim.paused:
            self.pause_btn.setText("Resume")
            
            self.pause_btn.setStyleSheet(
                """
                QPushButton {
                    background-color: #2d6cdf;
                    color: white;
                    font-weight: bold;
                    padding: 8px;
                    border-radius: 6px;
                }
                QPushButton:hover {
                    background-color: black;
                    color: white;
                }
                """
            )
        #running state
        else:
            self.pause_btn.setText("Pause")
            
            self.pause_btn.setStyleSheet(
                """
                QPushButton {
                    background-color: white;
                    color: black;
                    font-weight: bold;
                    padding: 8px;
                    border-radius: 6px;
                }
                """
            )
    
    """ RESET """
    def reset_simulation(self):
        #recreate simulation
        self.sim = GalaxySimulation()
        #reconnect renderer to new sim
        self.renderer.sim = self.sim
        
    """ LIVE PARAM EDITING """
    def change_dt(self, value):
        self.sim.dt = value * 0.001  #scale slider to reasonable range
        
    """ CAMERA CONTROLS """
    def keyPressEvent(self, event):
        cam = self.sim.camera
        
        if event.key() == Qt.Key_W:     #move up
            cam.y += cam.move_speed
        
        elif event.key() == Qt.Key_S:   #move down
            cam.y -= cam.move_speed
        elif event.key() == Qt.Key_A:   #move left
            cam.x -= cam.move_speed
        elif event.key() == Qt.Key_D:   #move right
            cam.x += cam.move_speed
            
    """ FPS DISPLAY """
    def update_ui(self):
        self.fps_label.setText(f"FPS: {self.renderer.fps:.1f}")
    
    """ RUNTIME DISPLAY """
    #def update_ui(self):
        #self.runtimer_label.setText(f"Simulation Runtime: {self.renderer.startTimer:.1f}")
        
    
""" APPLICATION """
app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec())
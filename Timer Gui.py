#  Timer v1


import sys
import time
from enum import Enum, auto

from PyQt5.QtCore import QObject, QTimer, pyqtSignal
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QSpinBox
)



class TimerState(Enum):
    STOPPED = auto()
    RUNNING = auto()
    PAUSED = auto()
    FINISHED = auto()



class TimerModel:
    def __init__(self):
        self.duration = 0
        self.end_time = 0
        self.remaining = 0



class TimerViewModel(QObject):

    time_changed = pyqtSignal(str)
    state_changed = pyqtSignal(object)
    button_text_changed = pyqtSignal(str)

    def __init__(self):
        super().__init__()

        self.model = TimerModel()
        self.state = TimerState.STOPPED

        self.timer = QTimer()
        self.timer.timeout.connect(self.tick)



    def start(self, duration):
        if self.state == TimerState.RUNNING:
            return

        self.model.duration = duration
        self.model.end_time = time.monotonic() + duration

        self.state = TimerState.RUNNING
        self.state_changed.emit(self.state)
        self.button_text_changed.emit("Pause")

        self.timer.start(200)

    def pause(self):
        if self.state != TimerState.RUNNING:
            return

        self.model.remaining = self.model.end_time - time.monotonic()
        self.timer.stop()

        self.state = TimerState.PAUSED
        self.state_changed.emit(self.state)
        self.button_text_changed.emit("Resume")

    def resume(self):
        if self.state != TimerState.PAUSED:
            return

        self.model.end_time = time.monotonic() + self.model.remaining

        self.state = TimerState.RUNNING
        self.state_changed.emit(self.state)
        self.button_text_changed.emit("Pause")

        self.timer.start(200)

    def stop(self):
        self.timer.stop()
        self.state = TimerState.STOPPED
        self.state_changed.emit(self.state)
        self.button_text_changed.emit("Start")



    def tick(self):
        remaining = self.model.end_time - time.monotonic()

        if remaining <= 0:
            self.timer.stop()
            self.state = TimerState.FINISHED
            self.state_changed.emit(self.state)
            self.time_changed.emit("00:00:00")
            self.button_text_changed.emit("Start")
            return

        h = int(remaining // 3600)
        m = int((remaining % 3600) // 60)
        s = int(remaining % 60)

        self.time_changed.emit(f"{h:02d}:{m:02d}:{s:02d}")




class View(QMainWindow):
    def __init__(self, vm):
        super().__init__()
        self.vm = vm

        self.setWindowTitle("Timer")

        # --- UI ---
        self.label = QLabel("00:00:00")
        
        

        self.hours = QSpinBox()
        self.hours.setRange(0, 99)
        self.hours.setSuffix(" h")

        self.minutes = QSpinBox()
        self.minutes.setRange(0, 59)
        self.minutes.setSuffix(" m")

        self.seconds = QSpinBox()
        self.seconds.setRange(0, 59)
        self.seconds.setSuffix(" s")

        self.button = QPushButton("Start")


        layout = QVBoxLayout()

        input_row = QHBoxLayout()
        input_row.addWidget(self.hours)
        input_row.addWidget(self.minutes)
        input_row.addWidget(self.seconds)

        layout.addLayout(input_row)
        layout.addWidget(self.label)
        layout.addWidget(self.button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)


        self.button.clicked.connect(self.handle_button)


        self.vm.time_changed.connect(self.label.setText)
        self.vm.button_text_changed.connect(self.button.setText)

    def get_duration(self):
        return (
            self.hours.value() * 3600 +
            self.minutes.value() * 60 +
            self.seconds.value()
        )

    def handle_button(self):
        text = self.button.text()

        if text == "Start":
            self.vm.start(self.get_duration())
        elif text == "Pause":
            self.vm.pause()
        elif text == "Resume":
            self.vm.resume()




def main():
    app = QApplication(sys.argv)

    vm = TimerViewModel()
    view = View(vm)

    view.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()


    

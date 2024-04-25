import os
import re
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class LogMonitor:
    def __init__(self, log_file, socketio):
        self.observer = None
        self.log_file = log_file
        self.socketio = socketio
        self.talkers = []
        self.active_talker = None
        self.last_position = 0  # Track the last read position in the log file
        self.read_log()  # Read the log file initially

    def start_monitoring(self):
        event_handler = LogFileEventHandler(self)
        observer = Observer()
        observer.schedule(event_handler, path=os.path.dirname(self.log_file), recursive=False)
        observer.start()
        self.observer = observer
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop_monitoring()

    def stop_monitoring(self):
        self.observer.stop()
        self.observer.join()

    def read_log(self):
        try:
            with open(self.log_file, 'r') as file:
                file.seek(self.last_position)
                for line in file:
                    self.parse_line(line)
                self.last_position = file.tell()  # Update the last read position
        except FileNotFoundError:
            print(f"Log file '{self.log_file}' not found.")

    def parse_line(self, line):
        if re.match(r'.*Talker start on TG #\d+: (.+)', line):
            match = re.search(r'Talker start on TG #\d+: (.+)', line)
            self.active_talker = match.group(1)
            self.talkers.insert(0, self.active_talker)
            if len(self.talkers) > 10:
                self.talkers.pop()
            # Emit an update whenever a new talker starts
            self.socketio.emit('update_last_talker', {'last_talker': self.active_talker}, namespace='/')
        elif re.match(r'.*Talker stop on TG #\d+: (.+)', line):
            match = re.search(r'Talker stop on TG #\d+: (.+)', line)
            if self.active_talker == match.group(1):
                self.active_talker = None
                # Emit an update when a talker stops
                self.socketio.emit('update_last_talker', {'last_talker': "No one currently talking"}, namespace='/')


class LogFileEventHandler(FileSystemEventHandler):
    def __init__(self, log_monitor):
        super().__init__()
        self.log_monitor = log_monitor

    def on_modified(self, event):
        monitor_path = os.path.abspath(self.log_monitor.log_file)
        if event.src_path == monitor_path:
            self.log_monitor.read_log()

import os
import re
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class LogMonitor:
    def __init__(self, log_file, socketio):
        self.active_session = None
        self.talk_start_time = None
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
        start_pattern = r'(\d+\.\d+\.\d+ \d+:\d+:\d+): ReflectorLogic: Talker start on TG #(\d+): (\S+)'
        stop_pattern = r'(\d+\.\d+\.\d+ \d+:\d+:\d+): ReflectorLogic: Talker stop on TG #(\d+): (\S+)'
        if re.match(start_pattern, line):
            match = re.search(start_pattern, line)
            date_time, tg_number, talker_name = match.groups()
            self.active_session = {'start_time': time.time(), 'date_time': date_time, 'tg_number': tg_number,
                                   'call_sign': talker_name}
            if len(self.talkers) >= 10:
                self.talkers.pop(0)
            self.talkers.insert(0, self.active_session)
            self.socketio.emit('update_last_talker', self.active_session, namespace='/')
        elif re.match(stop_pattern, line):
            match = re.search(stop_pattern, line)
            date_time, tg_number, talker_name = match.groups()
            if (self.active_session and self.active_session['call_sign'] == talker_name and
                    self.active_session['tg_number'] == tg_number):
                talk_duration = time.time() - self.active_session['start_time']
                self.active_session.update({'stop_time': time.time(), 'duration': talk_duration})
                self.socketio.emit('update_last_talker',
                                   {'last_talker': None, 'duration': talk_duration},
                                   namespace='/')
                self.active_session = None

    def get_last_talkers(self):
        return self.talkers


class LogFileEventHandler(FileSystemEventHandler):
    def __init__(self, log_monitor):
        super().__init__()
        self.log_monitor = log_monitor

    def on_modified(self, event):
        monitor_path = os.path.abspath(self.log_monitor.log_file)
        if event.src_path == monitor_path:
            self.log_monitor.read_log()

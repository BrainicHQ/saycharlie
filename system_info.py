#  Copyright (c) 2024 by Silviu Stroe (brainic.io)
#  #
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#  #
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  GNU General Public License for more details.
#  #
#  You should have received a copy of the GNU General Public License
#  along with this program. If not, see <http://www.gnu.org/licenses/>.
#  #
#  Created on 6/20/24, 3:23 PM
#  #
#  Author: Silviu Stroe

import psutil


def get_cpu_temperature():
    try:
        return f"{psutil.sensors_temperatures()['coretemp'][0].current:.1f}°C"
    except Exception as e:
        return f"Not available: {e}"


def get_fans_speed():
    fans_speed = {}
    try:
        for hw, fans in psutil.sensors_fans().items():
            if fans:  # Check if there are any fans detected
                fans_speed[hw] = f"{fans[0].current} RPM"
    except Exception as e:
        fans_speed['Error'] = f"Fans speed not available: {e}"
    return fans_speed


def get_system_info():
    system_info = {
        'CPU Temperature': get_cpu_temperature(),
        'CPU Usage': f"{psutil.cpu_percent(interval=1)}%",
        'CPU Times': {
            'user': f"{psutil.cpu_times().user} s",
            'system': f"{psutil.cpu_times().system} s",
            'idle': f"{psutil.cpu_times().idle} s",
            'frequency': f"{psutil.cpu_freq().current:.2f} MHz"
        },
        'Fans Speed': get_fans_speed(),
        'Memory Usage': f"{psutil.virtual_memory().percent}%",
        'Memory Details': {
            "total": f"{psutil.virtual_memory().total / (1024 ** 3):.2f} GB",
            "used": f"{psutil.virtual_memory().used / (1024 ** 3):.2f} GB",
            "free": f"{psutil.virtual_memory().free / (1024 ** 3):.2f} GB",
            "swap_total": f"{psutil.swap_memory().total / (1024 ** 3):.2f} GB",
            "swap_used": f"{psutil.swap_memory().used / (1024 ** 3):.2f} GB",
            "swap_free": f"{psutil.swap_memory().free / (1024 ** 3):.2f} GB"
        },
        'Disk Usage': {
            "total": f"{psutil.disk_usage('/').total / (1024 ** 3):.2f} GB",
            "used": f"{psutil.disk_usage('/').used / (1024 ** 3):.2f} GB",
            "free": f"{psutil.disk_usage('/').free / (1024 ** 3):.2f} GB",
            "percent": f"{psutil.disk_usage('/').percent}%",
            "read_bytes": f"{psutil.disk_io_counters().read_bytes / (1024 ** 2):.2f} MB",
            "write_bytes": f"{psutil.disk_io_counters().write_bytes / (1024 ** 2):.2f} MB"
        },
        'Network I/O': {
            "bytes_sent": f"{psutil.net_io_counters().bytes_sent / (1024 ** 2):.2f} MB",
            "bytes_recv": f"{psutil.net_io_counters().bytes_recv / (1024 ** 2):.2f} MB"
        },
        'System Load': {
            "1_min": psutil.getloadavg()[0],
            "5_min": psutil.getloadavg()[1],
            "15_min": psutil.getloadavg()[2]
        }
    }
    return system_info

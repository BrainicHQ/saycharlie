# saycharlie - Free SVXLink Dashboard for Ham Radio Operators

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)  
[![GitHub issues](https://img.shields.io/github/issues/BrainicHQ/saycharlie)](https://https://github.com/BrainicHQ/saycharlie/issues)
![GitHub stars](https://img.shields.io/github/stars/BrainicHQ/saycharlie)
![GitHub contributors](https://img.shields.io/github/contributors/BrainicHQ/saycharlie)
![GitHub last commit](https://img.shields.io/github/last-commit/BrainicHQ/saycharlie)
![GitHub code size](https://img.shields.io/github/languages/code-size/BrainicHQ/saycharlie)


<p align="center">
  <img src="/saycharlie-dashboard.jpg" width="400">
</p>

## Overview

saycharlie is a comprehensive dashboard designed to manage and interact with SVXLink, a general-purpose voice service
system for ham radio operators. Built with Python and JavaScript, saycharlie leverages Flask for robust backend
functionality and utilizes SocketIO for seamless real-time communication. This integration facilitates dynamic
interactions and ensures efficient management of the SVXLink services.

## Features

- **Real-time Updates**: Instantly displays the last talker in the communication system, ensuring users are always
  up-to-date.
- **DTMF Code Transmission**: Allows users to send DTMF codes through a well-defined API, enabling remote control over
  radio links.
- **SVXLink Control**: Provides API endpoints to stop and restart the SVXLink service, offering administrative control
  without needing direct server access.
- **Callsign Lookup**: Fetch ham radio operator names using their callsigns, integrating with external databases for
  enhanced communication.
- **Interactive Dashboard**: A user-friendly dashboard that not only visualizes but also allows interaction with the
  SVXLink system in real time.
- **Talk Group Management**: Facilitates the management of talk groups, enabling users to create, edit, and delete
  groups as needed.
- **PTT Control**: Enable or disable Push-to-Talk (PTT) via a simple button interface, facilitating easy management of
  transmission.
- **UI Customization**: Offers dynamic customization of the user interface, including adding buttons, configuring
  columns, and changing the application background.
- **Comprehensive Settings Management**: Manage settings and categories to adapt the dashboard to specific needs and
  preferences.
- **VU Meter**: Displays the volume unit meter for the both input and output audio signals, providing a visual
  representation of the audio signal strength.
- **Update System**: Allows users to update the application with a simple button click, ensuring the latest features and
  improvements are always available.

## Getting Started

### Prerequisites

- SVXLink installed and configured on a linux system
- Python 3.6 or higher

### Installation

#### Clone the repository

```bash
git clone https://github.com/BrainicHQ/saycharlie.git
```

#### Change directory

```bash
cd saycharlie
```

#### Make the install script executable

```bash
sudo chmod +x install.sh
```

#### Run the install script

```bash
sudo ./install.sh
```

### Enabling the SVXLink raw audio stream for VU Meter support

To enable the VU Meter to display audio signal strength, you must enable the raw audio stream in the SVXLink
configuration. Locate the SVXLink configuration file and add the following line under the Rx (microphone) block and Tx
(speaker) block:

```conf
[Rx...]
...
RAW_AUDIO_UDP_DEST=127.0.0.1:10000
...

[Tx...]
...
RAW_AUDIO_UDP_DEST=127.0.0.1:10001
```

After adding the line, restart your SVXLink service. The VU Meter should now display the audio signal strength.

### Updating

To update saycharlie, run the following command:

```bash
cd saycharlie && git pull && sudo systemctl restart saycharlie
```

## Usage

After installation, access the dashboard via http://saycharlie:8337 or http://localhost:8337 to begin managing and
interacting with your SVXLink service.

## Logging

The application logs are stored in the `/tmp/saycharlie.log` directory. To view the logs, use the following command:

```bash
tail -f /tmp/saycharlie.log
```

## Contributing

The project is open-source, created and maintained by [**Silviu Stroe YO6SAY**](https://brainic.io/?utm=saycharliegit).
We welcome contributions from the community, whether they are feature requests, bug fixes, or improvements to
documentation.

## License

This project is licensed under the GNU General Public License v3.0 - see the LICENSE file for details.

## Support

For support, feature requests, or any other inquiries, please open an issue in the GitHub issue tracker for this
repository.

## Acknowledgements

We would like to express our gratitude to the following contributors for their support and contributions to the project:

- [Michael Gross (DK1AJ)](https://www.qrz.com/db/DK1AJ) for his valuable testing and feedback.
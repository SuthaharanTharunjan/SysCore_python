# SysCore
#### Video Demo: https://youtu.be/l3YHsJunmEA
#### Description

SysCore is a lightweight terminal-based system monitoring application written in Python. Its goal is to provide useful system information through a TUI (Terminal User Interface), acting as a lightweight alternative to a graphical task manager. It also includes a process log feature that allows the user to view a snapshot of the processes running on the system at that time.

## Features

### CPU Monitoring

The CPU section provides:

- Overall CPU usage
- Current CPU frequency
- Number of physical and logical CPU cores
- Individual CPU core usage
- Individual CPU core temperatures when available
- Overall CPU temperature when available

### Memory Monitoring

The RAM section displays information about both physical memory and swap memory:

- Usage percentage
- Used memory
- Free memory
- Total memory

### Disk Monitoring

For each available storage device, SysCore displays:

- Storage usage percentage
- Used space
- Free space
- Total space
- Filesystem
- Read speed
- Write speed
- Total read count since boot
- Total write count since boot

### Network Monitoring

The network section displays information for active network interfaces, including:

- Upload speed
- Download speed
- Total data sent since boot
- Total data received since boot

### Battery Monitoring

When a battery is available, SysCore displays:

- Battery percentage
- Charging status
- Estimated remaining time when running on battery

### Fan Monitoring

On systems where fan sensors are available, SysCore displays:

- Fan manufacturer
- Fan type
- Fan speed in RPM

### Process Monitor

The process screen provides information about currently running processes, including:

- Process number
- Process name
- PID
- Parent PID
- Process status
- Username
- CPU usage
- RAM usage

The process screen can be navigated using the keyboard and allows the user to scroll through the available processes.

### Process Log

SysCore also provides a command-line option for creating a process log. Using:

python project.py --p_log

the program displays the processes detected at that moment. This provides a simple snapshot of the processes currently running on the system by printing it in terminal.

## Operating System Support

SysCore primarily targets Windows and Linux.

Most system information is available on both operating systems through "psutil". However, some low-level hardware information, particularly CPU temperature and fan speed, depends on the sensors exposed by the operating system and hardware.

Linux generally provides easier access to these sensors through its hardware monitoring interfaces. Supporting the same information reliably on Windows would require additional libraries and hardware-specific methods. I decided to keep SysCore relatively simple rather than adding multiple libraries specifically for Windows sensor monitoring.

## Technologies Used

### Python

Python is used for the entire application and provides the structure for collecting, processing, and displaying system information.

### psutil

"psutil" is used to retrieve system and process information such as:

- CPU usage and frequency
- CPU core information
- Memory usage
- Disk information
- Network statistics
- Battery information
- Fan and temperature sensors
- Running processes

I chose "psutil" because it is well-established, relatively simple to use, and supports multiple operating systems.

### Rich

Rich is responsible for the terminal interface. It is used for:

- Tables
- Progress bars
- Live display updates
- Text formatting
- Columns
- Grouping different sections of the interface

I originally considered using Textual, but after spending several hours learning it, I found that it introduced more complexity than I needed for this project. Rich provided the specific terminal features I needed while allowing me to build the interface with a smaller and simpler structure.

### pynput

"pynput" is used to capture keyboard input. It allows SysCore to respond to keys such as:

- ↑ — Scroll up
- ↓ — Scroll down
- ← — Return to the main screen
- → — Open the process screen
- Esc — Exit the application

## Project Development

One of the biggest challenges was figuring out where to start. I initially began learning Textual, but I eventually decided that Rich was more appropriate for the scope of this project.

My first major feature was the CPU usage display and its progress bars. After learning how Rich worked, I implemented live updating and gradually built the CPU section. During development, I realized that I was initially using Rich Live incorrectly, so I had to learn how live displays should be structured and updated.

Once I had a working structure, I organized the program into separate functions for each section of the system monitor. This made it easier to add new features without rewriting the entire program.

The process monitor was the most challenging part. Initially, retrieving information about every process and continuously rebuilding the table made the interface slow. I improved this by only retrieving the data needed for the visible section, using slicing, and later using a generator function to make process data retrieval more efficient.

I then implemented keyboard navigation, process scrolling, and the process log feature.

## Performance

SysCore is designed to update its terminal interface frequently while collecting system information at a lower rate. This helps balance responsiveness with resource usage.

The refresh rate can be reduced to decrease memory usage. At higher refresh rates the application uses more memory, while lowering the refresh rate can significantly reduce its resource consumption.

The process screen is currently less responsive than the main monitoring screen, especially when dealing with a large number of processes. This is a known limitation of the current implementation.

## Testing

The project includes tests written with pytest.

System information such as CPU usage, RAM usage, and the number of running processes cannot be reliably predicted during a test because these values constantly change. Therefore, the tests focus on predictable properties of the functions, such as:

- Whether the correct Rich table type is returned
- Table structure
- Number of columns
- Expected data types
- Basic table dimensions

This allows the parts of the program that can be tested deterministically to be verified without depending on the current state of the computer.

## Motivation

I have always been interested in computers, hardware, and interacting with systems at a lower level. I also have an interest in self-hosting and would like to build a home server in the future.

Because of this, I wanted to create something that I could potentially use on a future server to quickly check system resources from the terminal. SysCore started as an idea for a simple system monitor and gradually developed into a more complete TUI with multiple monitoring sections, keyboard navigation, process monitoring, and process logging.
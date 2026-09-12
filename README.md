# 🖥️ SysCore

#### 🎥 Video Demo: https://youtu.be/l3YHsJunmEA

#### 📖 Description

**SysCore** is a lightweight terminal-based system monitoring application written in Python. Its goal is to provide useful system information through an intuitive TUI (Terminal User Interface), acting as a lightweight alternative to a graphical task manager. It also includes a process log feature that allows the user to view a snapshot of the processes running on the system at that time.

---

## ⚙️ Installation & Setup

### 📋 Prerequisites
- Python 3.8 or higher installed
- `pip` (Python package manager)

---

### 🪟 Windows Setup

1. **Open the Terminal:**
Press `Win + R`, type `cmd` or `powershell`, and press **Enter**.

2. **Navigate to the Project Directory:**
```bash
cd path/to/SysCore

```
   
3. **Install Required Packages:**
```cmd
pip install -r requirements.txt

```


4. **Launch the Program:**
```cmd
python main.py

```



---

### 🐧 Linux Setup

1. **Open the Terminal:**
Press `Ctrl + Alt + T`.
2. **Navigate to the Project Directory:**
```bash
cd path/to/SysCore

```


3. **Install Required Packages:**
```bash
pip install -r requirements.txt

```


*(If your distribution restricts system-wide pip packages, add the `--break-system-packages` flag or `--user`)*:
```bash
pip install -r requirements.txt --break-system-packages

```


4. **Launch the Program:**
```bash
python3 main.py

```

---

## 🎮 How to Use

### 🖥️ Standard TUI Mode

Run the main live monitoring interface:

```bash
python main.py

```

*(Use `python3 main.py` on Linux)*

### ⌨️ Navigation Controls

* ⬆️ **↑** — Scroll up in process list
* ⬇️ **↓** — Scroll down in process list
* ➡️ **→** — Open the detailed process screen
* ⬅️ **←** — Return to the main overview screen
* 🛑 **Esc** — Exit the application

### 📜 Process Snapshot (CLI Mode)

Generate a one-time terminal snapshot of active processes without launching the continuous UI:

```bash
python main.py --p_log

```

---

## ✨ Features

### 🧠 CPU Monitoring

The CPU section provides:

* 📊 Overall CPU usage

* ⚡ Current CPU frequency

* 🧩 Number of physical and logical CPU cores

* 📈 Individual CPU core usage

* 🌡️ Individual CPU core temperatures *(when available)*

* 🔥 Overall CPU temperature *(when available)*


### 💾 Memory Monitoring

The RAM section displays information about both physical memory and swap memory:

* 📊 Usage percentage

* 📉 Used memory

* 📈 Free memory

* 📦 Total memory


### 💽 Disk Monitoring

For each available storage device, SysCore displays:

* 📊 Storage usage percentage

* 📁 Used space

* 📂 Free space

* 💾 Total space

* 🗂️ Filesystem

* ⏩ Read speed

* ⏪ Write speed

* 📖 Total read count since boot

* ✍️ Total write count since boot


### 🌐 Network Monitoring

The network section displays information for active network interfaces, including:

* ⬆️ Upload speed

* ⬇️ Download speed

* 📤 Total data sent since boot

* 📥 Total data received since boot


### 🔋 Battery Monitoring

When a battery is available, SysCore displays:

* 🔋 Battery percentage

* ⚡ Charging status

* ⏳ Estimated remaining time when running on battery


### 🌀 Fan Monitoring

On systems where fan sensors are available, SysCore displays:

* 🏷️ Fan manufacturer

* ⚙️ Fan type

* 🔄 Fan speed in RPM


### 📋 Process Monitor

The process screen provides information about currently running processes, including:

* 🔢 Process number

* 🏷️ Process name

* 🆔 PID

* 👨‍👦 Parent PID

* 🚦 Process status

* 👤 Username

* 🧠 CPU usage

* 💾 RAM usage

---

## 🪟🐧 Operating System Support

SysCore primarily targets **Windows** and **Linux**.

Most system information is available on both operating systems through `psutil`. However, some low-level hardware information—particularly CPU temperature and fan speed—depends on the sensors exposed by the operating system and hardware.

* 🐧 **Linux** generally provides easier access to these sensors through its hardware monitoring interfaces.

* 🪟 Supporting the same information reliably on **Windows** would require additional libraries and hardware-specific methods. SysCore stays lightweight by using built-in sensor hooks where available rather than relying on heavy kernel-driver wrappers.


---

## 🛠️ Technologies Used

### 🐍 Python

Python provides the primary structure for collecting, processing, and displaying system metrics.

### ⚙️ psutil

`psutil` retrieves system and process hardware telemetry:

* 🧠 CPU utilization, frequency, and core topology

* 💾 Memory and swap statistics

* 💽 Storage partitions and disk I/O rates

* 🌐 Network interface metrics

* 🔋 Battery status

* 🌡️ Hardware temperature and fan sensors

* 📋 Active process metadata


### 🎨 Rich

Rich is responsible for rendering the components for terminal interface:

* 📊 Tables

* 🔤 Text formatting & styles


### 🖼️ Textual
TUI framework powering the entire application interface:

* 🎨 Modern widget layouts and responsive CSS-like styling

* ⌨️ Built-in event loop and native terminal keybinding handling

* 🔄 Reactive UI updates and asynchronous message workers

---
## ⚡ Performance
SysCore balances responsive navigation with low resource consumption:

* Controlled Polling Intervals: Telemetry gathering runs on measured background timers to maintain a negligible CPU footprint.

* Predictable Memory Usage: Data structures are kept compact and recycled between ticks, preventing memory leaks during long-running sessions.

* Efficient UI Rendering: Textual's diff-based terminal engine renders only updated screen elements, eliminating full-screen flickering and unnecessary repaint cycles.

---

## 🗄️ Project History & Legacy Archive

The repository was updated to use a modern interface powered by **Textual**. 

If you are looking for the original, earlier release:
- 📁 **Archive Location:** [`old_version_unupdated/`](./old_version_unupdated/)
- ⚙️ **Legacy Stack:** Built using the older baseline implementation.
- 📖 **Documentation:** Refer to the standalone `README.md` inside that directory for setup and usage instructions specific to the archived version.
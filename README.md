# ⚡ EV Charging Optimizer

This project simulates an electric vehicle (EV) charging network using graph algorithms. It helps optimize EV routing, locate the nearest charging stations, and print summaries of the network using real-world-inspired data.

---

## Project Structure

```
├── main.cpp           # Main program currently working with CLI
├── graph.h            # Graph, Node, Edge, ChargingStation class declarations
├── graph.cpp          # Graph method definitions

# Feature Modules (used in main.cpp)
├── nearest.h          # Nearest charging station declarations
├── nearest.cpp        # Nearest charging station logic
├── path2.h            # Route Planning with Charging Stops declarations
├── path2.cpp          # Route Planning with Charging Stops logic
├── placement.h        # Charging Station Placement declarations
├── placement.cpp      # Charging Station Placement logic
├── traffic.h        # Traffic declarations
├── traffic.cpp      # Traffic Placement logic

# Data & Dependencies
├── ev_network.json    # Sample input data (nodes, edges, stations)
├── json.hpp           # nlohmann/json library
```

---

## Module Interaction

All feature modules (`nearest`, `path2`, `placement`) are designed as separate components and **rely on the `Graph` class** defined in `graph.h` and implemented in `graph.cpp`.

They are imported and used in `main.cpp` like so:

```cpp
#include "graph.h"
#include "nearest.h"
#include "path2.h"
#include "placement.h"
```

Each module uses `Graph& g` as input and can query the full network via:

- `getNodes()`
- `getGraph()`
- `getNodeMap()`
- *(Optional: `getEdges()` if implemented)*

---

## ⚙️ Compilation & Execution

✅ **This project currently compiles and runs successfully using the following command:**

```bash
g++ main.cpp graph.cpp nearest.cpp path2.cpp placement.cpp traffic.cpp -o ev_project
```

### ▶ Run the program:

```bash
./ev_project        # On Linux/macOS
.\ev_project.exe    # On Windows PowerShell or CMD
```


# GUI Integration for EV Charging Optimizer

This folder provides a graphical user interface (GUI) to interact with the EV Charging Optimizer tool. The GUI is designed to simplify parameter input, execute optimization routines, and visualize results in an intuitive interface.

---

## 📁 **Folder Structure**

```
gui_integration_for_current_use/
├── main_gui.py                     # UI components and layout ( it calls functions from backend logic )
├── ev_backend.py          # Backend logic - all algorthims
├── network_diagram_widget.py     # Graph diagram Logic
├── ev_network.json               # Dataset
```


## ✅ **Requirements**

Ensure you have Python 3.8+ installed. Then install the required Python packages:

```bash
pip install PyQt6 numpy pandas
```

## 🚀 How to Run
```
1.Open a terminal or command prompt.

2.Navigate to the gui_integration_for_current_use directory.

3.Launch the GUI:
```

```bash
python main_gui.py
```

## Notes

```
Make sure the backend optimization logic is functional and correctly linked in main_gui.py
```

## Support


```
If you encounter any bugs or have suggestions, feel free to open an issue in the main repository.
```










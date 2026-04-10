import sys
import os
import json
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QComboBox, QLineEdit, QTextEdit, QTabWidget,
    QMessageBox, QScrollArea, QFrame, QInputDialog
)
from PyQt6.QtCore import Qt, QUrl, QTimer, pyqtSlot, pyqtSignal

from ev_backend import Graph, TrafficManager, find_nearest_charging_station, suggest_path_with_charging, suggest_charging_stations, Node

from network_diagram_widget import NetworkDiagramWidget

class EVOptimizerApp(QMainWindow):
    """Main application window for the EV Network Optimizer."""

    def __init__(self):
        super().__init__()
        self.graph = Graph() # Initialize your backend graph
        self.traffic_manager = TrafficManager() # Initialize traffic manager

        self.setWindowTitle("EV Network Optimizer (Graph View)") # Updated title
        self.setGeometry(100, 100, 1200, 800) # Initial window size

        # Load graph data immediately
        try:
            self.graph.load_data("ev_network.json")
        except (FileNotFoundError, ValueError, Exception) as e:
            QMessageBox.critical(self, "Data Loading Error", f"Failed to load network data: {e}\n"
                                                              f"Please ensure 'ev_network.json' is valid and in the same directory.")
            sys.exit(1) # Exit if essential data can't be loaded

        self.init_ui()
        self.connect_signals()
        
        # Initial display of nodes when the app starts
        self.network_diagram_widget.update_nodes() # Trigger initial draw

    def init_ui(self):
        """Initializes the main UI components."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)

        # --- Left Sidebar for Navigation (Tabs) ---
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget, 1) # Take 1/3 of the width

        # --- Right Area for Graph Visualization ---
        self.network_diagram_widget = NetworkDiagramWidget(self.graph)
        main_layout.addWidget(self.network_diagram_widget, 2) # Take 2/3 of the width

        # --- Create Tabs ---
        self.create_route_planner_tab()
        self.create_nearest_charger_tab()
        self.create_placement_tab()
        self.create_traffic_tab()
        self.create_summary_tab()

    def connect_signals(self):
        """Connects UI signals to backend logic or helper methods."""
        # Connect buttons from the placeholder tabs
        self.calculate_route_btn.clicked.connect(self.on_calculate_route_clicked)
        self.find_nearest_btn.clicked.connect(self.on_find_nearest_clicked)
        self.suggest_placement_btn.clicked.connect(self.on_suggest_placement_clicked)
        self.reset_traffic_btn.clicked.connect(self.on_reset_traffic_clicked)
        self.update_traffic_btn.clicked.connect(self.on_update_traffic_clicked)
        
        # Connect node_clicked signal from the NetworkDiagramWidget
        self.network_diagram_widget.node_clicked.connect(self.on_diagram_node_clicked)

    @pyqtSlot(int)
    def on_diagram_node_clicked(self, node_id):
        """Slot to handle clicks on nodes within the network diagram."""
        node = self.graph.node_map.get(node_id)
        if node:
            print(f"Diagram: Node '{node.name}' (ID: {node_id}) clicked.")
            # e.g., displaying node info in a sidebar, populating fields etc.
            self.output_text_area.setText(f"Selected Node: {node.name} (ID: {node.id})\n"
                                           f"Lat: {node.lat:.4f}, Lon: {node.lon:.4f}\n"
                                           f"Is Charging Station: {'Yes' if node.is_charging else 'No'}")
        else:
            print(f"Diagram: Node with ID {node_id} clicked, but not found in graph.")

    # --- UI Creation Methods ---
    def create_route_planner_tab(self):
        self.route_planner_tab = QWidget()
        self.tab_widget.addTab(self.route_planner_tab, "Route Planner")
        layout = QVBoxLayout(self.route_planner_tab)
        
        # Input fields for route planning
        layout.addWidget(QLabel("Start Node ID:"))
        self.start_node_input = QLineEdit()
        self.start_node_input.setPlaceholderText("e.g., 1")
        layout.addWidget(self.start_node_input)

        layout.addWidget(QLabel("End Node ID:"))
        self.end_node_input = QLineEdit()
        self.end_node_input.setPlaceholderText("e.g., 5")
        layout.addWidget(self.end_node_input)

        layout.addWidget(QLabel("Battery Level (%):"))
        self.battery_level_input = QLineEdit()
        self.battery_level_input.setPlaceholderText("e.g., 80")
        layout.addWidget(self.battery_level_input)
        
        layout.addWidget(QLabel("Max Range (km):"))
        self.max_range_input = QLineEdit()
        self.max_range_input.setPlaceholderText("e.g., 150")
        layout.addWidget(self.max_range_input)

        self.calculate_route_btn = QPushButton("Calculate Route")
        layout.addWidget(self.calculate_route_btn)
        
        self.route_output_text = QTextEdit()
        self.route_output_text.setReadOnly(True)
        layout.addWidget(self.route_output_text)

        layout.addStretch(1) # Push content to top

    def create_nearest_charger_tab(self):
        self.nearest_charger_tab = QWidget()
        self.tab_widget.addTab(self.nearest_charger_tab, "Nearest Charger")
        layout = QVBoxLayout(self.nearest_charger_tab)

        layout.addWidget(QLabel("Current Node ID:"))
        self.current_node_nearest_input = QLineEdit()
        self.current_node_nearest_input.setPlaceholderText("e.g., 1")
        layout.addWidget(self.current_node_nearest_input)

        self.find_nearest_btn = QPushButton("Find Nearest Charger")
        layout.addWidget(self.find_nearest_btn)
        
        self.nearest_output_text = QTextEdit()
        self.nearest_output_text.setReadOnly(True)
        layout.addWidget(self.nearest_output_text)

        layout.addStretch(1)

    def create_placement_tab(self):
        self.placement_tab = QWidget()
        self.tab_widget.addTab(self.placement_tab, "Station Placement")
        layout = QVBoxLayout(self.placement_tab)

        layout.addWidget(QLabel("Number of new stations to suggest:"))
        self.num_suggestions_input = QLineEdit()
        self.num_suggestions_input.setPlaceholderText("e.g., 2")
        layout.addWidget(self.num_suggestions_input)

        self.suggest_placement_btn = QPushButton("Suggest New Placements")
        layout.addWidget(self.suggest_placement_btn)
        
        self.placement_output_text = QTextEdit()
        self.placement_output_text.setReadOnly(True)
        layout.addWidget(self.placement_output_text)

        layout.addStretch(1)

    def create_traffic_tab(self):
        self.traffic_tab = QWidget()
        self.tab_widget.addTab(self.traffic_tab, "Traffic Management")
        layout = QVBoxLayout(self.traffic_tab)

        layout.addWidget(QLabel("Simulate Traffic (Node IDs, comma-separated):"))
        self.traffic_simulate_input = QLineEdit()
        self.traffic_simulate_input.setPlaceholderText("e.g., 1,2,1,3,5")
        layout.addWidget(self.traffic_simulate_input)

        layout.addWidget(QLabel("Traffic Threshold:"))
        self.traffic_threshold_input = QLineEdit()
        self.traffic_threshold_input.setPlaceholderText("e.g., 2")
        layout.addWidget(self.traffic_threshold_input)

        self.update_traffic_btn = QPushButton("Update Traffic")
        self.reset_traffic_btn = QPushButton("Reset All Traffic Data")
        layout.addWidget(self.update_traffic_btn)
        layout.addWidget(self.reset_traffic_btn)
        
        self.traffic_output_text = QTextEdit()
        self.traffic_output_text.setReadOnly(True)
        layout.addWidget(self.traffic_output_text)

        layout.addStretch(1)

    def create_summary_tab(self):
        self.summary_tab = QWidget()
        self.tab_widget.addTab(self.summary_tab, "Summary")
        layout = QVBoxLayout(self.summary_tab)

        self.output_text_area = QTextEdit()
        self.output_text_area.setReadOnly(True)
        layout.addWidget(self.output_text_area)

        # Generate the content as a string
        summary_content = "<h2>EV Network Summary</h2>"
        summary_content += f"<b>Nodes:</b> {len(self.graph.get_nodes())}<br>"
        summary_content += f"<b>Edges:</b> {len(self.graph.edges)}<br>"
        summary_content += f"<b>Charging Stations:</b> {len(self.graph.get_charging_stations())}<br>"

        summary_content += "<h3>All Nodes:</h3>"
        for node in self.graph.get_nodes():
            summary_content += f"ID: {node.id}, Name: {node.name}, Charging: {node.is_charging}<br>"

        # Set the generated content to the QTextEdit
        self.output_text_area.setHtml(summary_content) # Use setHtml to render HTML tags

        layout.addStretch(1)


        

    # --- UI Event Handlers ---
    def on_calculate_route_clicked(self):
        self.network_diagram_widget.clear_diagram_layers() # Clear previous highlights
        start_id_str = self.start_node_input.text()
        end_id_str = self.end_node_input.text()
        battery_level_str = self.battery_level_input.text()
        max_range_str = self.max_range_input.text()

        try:
            start_node_id = int(start_id_str)
            end_node_id = int(end_id_str)
            battery_level = float(battery_level_str)
            max_range_km = float(max_range_str)

            if start_node_id not in self.graph.node_map or end_node_id not in self.graph.node_map:
                QMessageBox.warning(self, "Invalid Input", "Start or End Node ID not found in the network.")
                return

            path_info = suggest_path_with_charging(self.graph, start_node_id, end_node_id, battery_level, max_range_km)
            
            if path_info and path_info[0]: # Check if path list is not empty
                path_nodes = path_info[0]
                total_distance = path_info[1]
                charging_stops = path_info[2]

                path_names = " -> ".join([self.graph.node_map[nid].name for nid in path_nodes])
                charging_stop_names = ", ".join([self.graph.node_map[cs_id].name for cs_id in charging_stops])

                self.route_output_text.setText(
                    f"Calculated Path:\n{path_names}\n\n"
                    f"Total Distance: {total_distance:.2f} km\n"
                    f"Charging Stops: {charging_stop_names if charging_stop_names else 'None'}"
                )
                self.network_diagram_widget.set_current_path(path_nodes)
            else:
                self.route_output_text.setText("No path found between the specified nodes or within range.")
                QMessageBox.information(self, "No Path", "No path found or not reachable with available charging.")

        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Please enter valid numbers for node IDs, battery level, and max range.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An unexpected error occurred: {e}")


    def on_find_nearest_clicked(self):
        self.network_diagram_widget.clear_diagram_layers() # Clear previous highlights
        current_node_id_str = self.current_node_nearest_input.text()

        try:
            current_node_id = int(current_node_id_str)

            if current_node_id not in self.graph.node_map:
                QMessageBox.warning(self, "Invalid Input", "Current Node ID not found in the network.")
                return

            # Call the updated find_nearest_charging_station (without range constraint)
            nearest_charger_id, distance, path_ids = find_nearest_charging_station(self.graph, current_node_id)

            if nearest_charger_id is not None:
                charger_node = self.graph.node_map[nearest_charger_id]
                path_names = " -> ".join([self.graph.node_map[nid].name for nid in path_ids])

                self.nearest_output_text.setText(
                    f"Nearest Charging Station: {charger_node.name} (ID: {charger_node.id})\n"
                    f"Distance: {distance:.2f} km\n"
                    f"Path: {path_names}"
                )
                self.network_diagram_widget.set_current_nearest_path(path_ids)
            else:
                self.nearest_output_text.setText("No charging station found in the network.")
                QMessageBox.information(self, "No Charger", "No charging station found in the network.")

        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Please enter a valid integer ID for the current node.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An unexpected error occurred: {e}")

    def on_suggest_placement_clicked(self):
        self.network_diagram_widget.clear_diagram_layers() # Clear previous highlights
        num_suggestions_str = self.num_suggestions_input.text()

        try:
            num_suggestions = int(num_suggestions_str)
            if num_suggestions <= 0:
                QMessageBox.warning(self, "Invalid Input", "Please enter a positive number for suggestions.")
                return

            # Adjusted call for suggest_charging_stations (removed traffic_manager arg)
            suggested_nodes = suggest_charging_stations(self.graph, num_suggestions)

            if suggested_nodes:
                suggestion_text = "Suggested locations for new charging stations:\n"
                suggested_ids = []
                for node in suggested_nodes:
                    suggestion_text += f"- {node.name} (ID: {node.id})\n"
                    suggested_ids.append(node.id)
                self.placement_output_text.setText(suggestion_text)
                self.network_diagram_widget.set_suggested_stations(suggested_ids)
            else:
                self.placement_output_text.setText("Could not suggest new charging stations based on current criteria.")

        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Please enter a valid integer for the number of suggestions.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An unexpected error occurred: {e}")

    def on_update_traffic_clicked(self):
        path_str = self.traffic_simulate_input.text()
        threshold_str = self.traffic_threshold_input.text()

        try:
            path_ids_str = [x.strip() for x in path_str.split(',') if x.strip()]
            path_ids = [int(x) for x in path_ids_str]
            threshold = int(threshold_str)

            if not path_ids:
                QMessageBox.warning(self, "Invalid Input", "Please enter node IDs to simulate traffic.")
                return
            if threshold <= 0:
                QMessageBox.warning(self, "Invalid Input", "Traffic threshold must be a positive integer.")
                return

            # Record traffic
            self.traffic_manager.record_user_path(path_ids)
            # Update high traffic nodes based on threshold
            self.traffic_manager.update_traffic(self.graph, threshold)
            
            self.update_traffic_display()
            self.network_diagram_widget.set_high_traffic_nodes(list(self.traffic_manager.get_high_traffic_nodes()))

        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Please enter comma-separated integers for node IDs and a valid integer for threshold.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An unexpected error occurred: {e}")

    def update_traffic_display(self):
        """Refreshes the high-traffic nodes display."""
        high_traffic_ids = self.traffic_manager.get_high_traffic_nodes()
        if high_traffic_ids:
            traffic_names = sorted([self.graph.node_map[node_id].name for node_id in high_traffic_ids])
            self.traffic_output_text.setText("Current High-Traffic Nodes:\n" + "\n".join(traffic_names))
        else:
            self.traffic_output_text.setText("No nodes are currently marked as high-traffic.")

    def on_reset_traffic_clicked(self):
        reply = QMessageBox.question(self, "Reset Traffic Data", 
                                     "Are you sure you want to reset all traffic data?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.traffic_manager.reset()
            self.update_traffic_display()
            self.network_diagram_widget.set_high_traffic_nodes([]) # Clear traffic highlight on diagram
            QMessageBox.information(self, "Traffic Reset", "All traffic data has been reset.")


# --- Main Application Entry Point ---
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = EVOptimizerApp()
    window.show()
    sys.exit(app.exec())
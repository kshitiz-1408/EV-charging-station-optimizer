import math
from PyQt6.QtWidgets import QWidget, QMessageBox
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QFont, QTextOption
from PyQt6.QtCore import Qt, QRectF, QPointF, pyqtSignal

# Import Node class for type hinting
from ev_backend import Node

class NetworkDiagramWidget(QWidget):
    # Signal emitted when a node is clicked, carrying its ID
    node_clicked = pyqtSignal(int)

    def __init__(self, graph_backend):
        super().__init__()
        self.graph = graph_backend
        self.nodes_to_draw = self.graph.get_nodes()
        self.edges_to_draw = self.graph.edges 

        self.high_traffic_node_ids = set()
        self.current_path_ids = []
        self.current_nearest_path_ids = []
        self.suggested_stations_ids = [] # Store IDs of suggested nodes

        self.node_positions = {} # {node_id: QPointF(x, y)}
        self.node_radius = 35 # Further increased node radius for more text space
        self.spacing_x = 100
        self.spacing_y = 100
        self.padding = 80 # Further increased padding

        self.selected_node_id = -1 # For highlighting clicked node

        self.setMinimumSize(600, 400) # Set a minimum size for the widget
        self.setMouseTracking(True) # Enable mouse tracking for hover effects

        # Set a clear background color for the widget itself
        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), QColor(240, 240, 240)) # Light grey background
        self.setPalette(p)

        # Generate initial node positions
        self._generate_node_positions()

    def _generate_node_positions(self):
        """
        Generates positions for nodes based on their geographical coordinates
        or a simple grid/spiral layout if coords are not suitable for direct mapping.
        """
        if not self.nodes_to_draw:
            return

        min_lat = min(node.lat for node in self.nodes_to_draw)
        max_lat = max(node.lat for node in self.nodes_to_draw)
        min_lon = min(node.lon for node in self.nodes_to_draw)
        max_lon = max(node.lon for node in self.nodes_to_draw)

        effective_width = max(1.0, float(self.width()) - 2 * self.padding)
        effective_height = max(1.0, float(self.height()) - 2 * self.padding)

        range_lat = max_lat - min_lat
        range_lon = max_lon - min_lon

        # Threshold to determine if geographical coordinates are too clustered
        # If the total geographical spread is very small, use a grid/circular layout
        # This helps when all nodes are essentially at the same lat/lon or very close.
        MIN_GEO_SPREAD_THRESHOLD = 0.005 # degrees (approx 500m)

        if range_lat < MIN_GEO_SPREAD_THRESHOLD and range_lon < MIN_GEO_SPREAD_THRESHOLD:
            # Fallback to a grid/circular layout for extremely clustered nodes
            num_nodes = len(self.nodes_to_draw)
            if num_nodes == 1:
                self.node_positions[self.nodes_to_draw[0].id] = QPointF(self.width() / 2, self.height() / 2)
            else:
                # Use a spiral/circular layout to spread nodes out
                # Calculate a base radius large enough to avoid overlap
                base_spread_radius = self.node_radius * 3.0 # A larger base spread
                
                # Dynamic adjustment for many nodes in a cluster
                current_spiral_radius = base_spread_radius
                angle_increment = (2 * math.pi) / num_nodes # Initial angle step
                
                for i, node in enumerate(self.nodes_to_draw):
                    angle = i * angle_increment
                    # Increase radius for subsequent nodes in the spiral
                    # Ensure minimum distance between nodes in the spiral
                    x = self.width() / 2 + current_spiral_radius * math.cos(angle)
                    y = self.height() / 2 + current_spiral_radius * math.sin(angle)
                    self.node_positions[node.id] = QPointF(x, y)
                    
                    # Increment radius for next node to create spiral effect
                    current_spiral_radius += (2 * self.node_radius) / num_nodes # Increment by avg node diameter over spiral turns


        else:
            # Use geographical scaling
            scale_x = effective_width / range_lon if range_lon > 0 else 1.0
            scale_y = effective_height / range_lat if range_lat > 0 else 1.0

            # Use min scale, but scale more aggressively to fill space
            scale = min(scale_x, scale_y) * 0.9 # Adjusted factor

            for node in self.nodes_to_draw:
                x = ((node.lon - min_lon) * scale) + self.padding + (effective_width - range_lon * scale) / 2
                y = ((max_lat - node.lat) * scale) + self.padding + (effective_height - range_lat * scale) / 2 # Invert lat for Y-axis

                self.node_positions[node.id] = QPointF(x, y)


    def resizeEvent(self, event):
        """Recalculate node positions on resize."""
        self._generate_node_positions()
        self.update() # Redraw
        super().resizeEvent(event)

    def paintEvent(self, event):
        """Draws the network diagram."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing) # Ensure text is antialiased
        
        # Set default font for text, can be overridden for specific elements
        painter.setFont(QFont("Arial", 10))

        # Draw edges first
        self._draw_edges(painter)

        # Draw nodes on top of edges
        self._draw_nodes(painter)

        painter.end()

    def _draw_edges(self, painter):
        """Draws all edges in the graph."""
        for edge in self.edges_to_draw:
            from_pos = self.node_positions.get(edge.from_node)
            to_pos = self.node_positions.get(edge.to_node)

            if from_pos and to_pos:
                pen = QPen(QColor(100, 100, 100), 2) # Darker grey edge for better contrast
                
                # Check if this edge is part of the current path
                # Ensure the nodes are consecutive in the path to draw the edge
                if edge.from_node in self.current_path_ids and edge.to_node in self.current_path_ids:
                    from_index = self.current_path_ids.index(edge.from_node)
                    to_index = self.current_path_ids.index(edge.to_node)
                    if abs(from_index - to_index) == 1: # Check if they are direct neighbors in the sequence
                        pen = QPen(QColor(0, 0, 200), 4) # Darker Blue for current path
                
                # Check if this edge is part of the nearest path
                if edge.from_node in self.current_nearest_path_ids and edge.to_node in self.current_nearest_path_ids:
                    from_index = self.current_nearest_path_ids.index(edge.from_node)
                    to_index = self.current_nearest_path_ids.index(edge.to_node)
                    if abs(from_index - to_index) == 1: # Check if they are direct neighbors in the sequence
                        pen = QPen(QColor(128, 0, 128), 5, Qt.PenStyle.DashLine) # Purple dashed for nearest path

                painter.setPen(pen)
                painter.drawLine(from_pos, to_pos)

    def _draw_nodes(self, painter):
        """Draws all nodes in the graph."""
        for node in self.nodes_to_draw:
            pos = self.node_positions.get(node.id)
            if not pos:
                continue

            # Determine node fill color
            node_color = QColor(100, 150, 200) # Lighter SteelBlue default
            if node.is_charging:
                node_color = QColor(90, 200, 140) # Lighter MediumSeaGreen for charging stations
            
            if node.id in self.high_traffic_node_ids:
                node_color = QColor(255, 100, 50) # Brighter OrangeRed for high traffic

            if node.id in self.suggested_stations_ids:
                node_color = QColor(255, 190, 70) # Brighter Orange for suggested stations
            
            # Draw selection highlight *behind* the node, or as a border
            if node.id == self.selected_node_id:
                painter.setBrush(QBrush(QColor(255, 255, 100))) # Bright Yellow for selection
                painter.setPen(QPen(Qt.GlobalColor.black, 2))
                painter.drawEllipse(pos, self.node_radius + 5, self.node_radius + 5) # Draw a larger selection circle

            # Draw node circle
            painter.setBrush(QBrush(node_color))
            painter.setPen(QPen(Qt.GlobalColor.black, 1)) # Black border for nodes
            painter.drawEllipse(pos, self.node_radius, self.node_radius)

            # --- Draw node ID and name (ensure text is visible and well-placed) ---
            # Text for Node ID
            painter.setPen(Qt.GlobalColor.white) # White text for ID, good on darker node colors
            font_id = QFont("Arial", 12, QFont.Weight.Bold) # Larger, bold ID font
            painter.setFont(font_id)
            
            # ID text rectangle: centered horizontally, in the upper half of the node
            # Adjusted vertical position to be more precise
            id_text_rect = QRectF(pos.x() - self.node_radius, pos.y() - self.node_radius * 0.7,
                                  self.node_radius * 2, self.node_radius)
            painter.drawText(id_text_rect, Qt.AlignmentFlag.AlignCenter | Qt.TextFlag.TextSingleLine, str(node.id))

            # Text for Node Name
            painter.setPen(Qt.GlobalColor.darkBlue) # Darker text for name, good on lighter background nodes
            font_name = QFont("Arial", 7) # Smaller font for name
            painter.setFont(font_name)
            
            # Name text rectangle: centered horizontally, in the lower half of the node
            # Adjusted vertical position to be more precise
            name_text_rect = QRectF(pos.x() - self.node_radius, pos.y() + self.node_radius * 0.1,
                                    self.node_radius * 2, self.node_radius)
            
            # Use QTextOption for word wrapping if name is too long
            text_option = QTextOption(Qt.AlignmentFlag.AlignCenter)
            text_option.setWrapMode(QTextOption.WrapMode.WordWrap)
            
            # Draw name text. QPainter.drawText with QTextOption needs QRectF and string
            painter.drawText(name_text_rect, node.name, text_option)


    def mousePressEvent(self, event):
        """Handles mouse presses to select nodes."""
        if event.button() == Qt.MouseButton.LeftButton:
            clicked_pos = event.pos()
            for node_id, pos in self.node_positions.items():
                # Using QPointF.distanceTo() for more accurate circle hit detection
                distance = QPointF(clicked_pos).distanceTo(pos)
                if distance <= self.node_radius: # Check if click is within the node circle
                    self.selected_node_id = node_id
                    self.node_clicked.emit(node_id) # Emit signal
                    self.update() # Redraw to show selection
                    return
            self.selected_node_id = -1 # No node clicked
            self.update()

    def update_nodes(self):
        """Triggers a redraw of all nodes. Also regenerates positions on initial load."""
        self._generate_node_positions() # Ensure positions are calculated for initial draw
        self.update()

    def set_high_traffic_nodes(self, node_ids: list[int]):
        """Sets the list of high-traffic node IDs for highlighting."""
        self.high_traffic_node_ids = set(node_ids)
        self.update()

    def set_current_path(self, path_ids: list[int]):
        """Sets the current path to be highlighted."""
        self.current_path_ids = path_ids
        self.update()

    def set_current_nearest_path(self, path_ids: list[int]):
        """Sets the current nearest path to be highlighted."""
        self.current_nearest_path_ids = path_ids
        self.update()

    def set_suggested_stations(self, node_ids: list[int]):
        """Sets the list of suggested charging station node IDs for highlighting."""
        self.suggested_stations_ids = node_ids
        self.update()

    def clear_diagram_layers(self):
        """Clears all dynamic highlights (paths, suggested stations, traffic)."""
        self.current_path_ids = []
        self.current_nearest_path_ids = []
        self.suggested_stations_ids = []
        self.high_traffic_node_ids = set() # Also clear traffic highlights
        self.update()
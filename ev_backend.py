import json
import heapq
import math
from collections import defaultdict

# --- Data Structures ---

class Node:
    def __init__(self, id: int, name: str, lat: float, lon: float, is_charging: bool):
        self.id = id
        self.name = name
        self.lat = lat
        self.lon = lon
        self.is_charging = is_charging

    def __repr__(self):
        return f"Node(ID: {self.id}, Name: '{self.name}', Lat: {self.lat}, Lon: {self.lon}, Charging: {self.is_charging})"

class Edge:
    def __init__(self, from_node: int, to_node: int, distance: float):
        self.from_node = from_node
        self.to_node = to_node
        self.distance = distance

    def __repr__(self):
        return f"Edge(From: {self.from_node}, To: {self.to_node}, Dist: {self.distance}km)"

class ChargStation:
    def __init__(self, id: str, location_id: int, capacity: int, charging_rate_kw: float, avg_wait_time_min: float):
        self.id = id
        self.location_id = location_id
        self.capacity = capacity
        self.charging_rate_kw = charging_rate_kw
        self.avg_wait_time_min = avg_wait_time_min

    def __repr__(self):
        return f"ChargStation(ID: {self.id}, Loc: {self.location_id}, Cap: {self.capacity})"


# --- Graph Management and Algorithms ---

class Graph:
    def __init__(self):
        self.nodes: list[Node] = []
        self.edges: list[Edge] = []
        self.charging_stations: list[ChargStation] = []
        self.adj = defaultdict(list)  # Adjacency list: {node_id: [(neighbor_id, distance), ...]}
        self.node_map: dict[int, Node] = {}  # Node lookup: {node_id: Node_object}
        self.charging_station_map: dict[int, ChargStation] = {} # {location_id: ChargStation_object}

    def load_data(self, filename: str):
        """Loads graph data from a JSON file."""
        try:
            with open(filename, 'r') as f:
                data = json.load(f)

            for node_data in data.get("nodes", []):
                node = Node(
                    node_data["id"],
                    node_data["name"],
                    node_data["latitude"],  # Use 'latitude'
                    node_data["longitude"], # Use 'longitude'
                    node_data["is_charging_station"] # Use 'is_charging_station'
                )
                self.nodes.append(node)
                self.node_map[node.id] = node

            for edge_data in data.get("edges", []):
                edge = Edge(
                    edge_data["from"],
                    edge_data["to"],
                    edge_data["distance_km"]
                )
                self.edges.append(edge)
                # Add edges for both directions (assuming undirected graph)
                self.adj[edge.from_node].append((edge.to_node, edge.distance))
                self.adj[edge.to_node].append((edge.from_node, edge.distance))

            for station_data in data.get("charging_stations", []):
                charg_station = ChargStation( 
                    station_data["id"],
                    station_data["location"],
                    station_data["capacity"],
                    station_data["charging_rate_kw"],
                    station_data["avg_wait_time_min"]
                )
                self.charging_stations.append(charg_station)
                self.charging_station_map[charg_station.location_id] = charg_station

            print(f"Loaded {len(self.nodes)} nodes, {len(self.edges)} edges, {len(self.charging_stations)} charging stations.")

        except FileNotFoundError:
            raise FileNotFoundError(f"Error: File '{filename}' not found. Please ensure it's in the same directory.")
        except json.JSONDecodeError:
            raise ValueError(f"Error: Could not decode JSON from '{filename}'. Check JSON format.")
        except Exception as e:
            raise Exception(f"An unexpected error occurred during data loading: {e}")

    def get_nodes(self) -> list[Node]:
        return self.nodes

    def get_node_map(self) -> dict[int, Node]:
        return self.node_map

    def get_adj_list(self) -> defaultdict[int, list[tuple[int, float]]]:
        return self.adj

    def get_charging_stations(self) -> list[ChargStation]:
        return self.charging_stations

    def find_path_bfs(self, start_id: int, end_id: int) -> list[int]:
        """
        Finds a path between two nodes using Breadth-First Search (BFS).
        Returns a list of node IDs forming the path, or an empty list if no path.
        """
        if start_id not in self.node_map or end_id not in self.node_map:
            return []

        q = []
        q.append(start_id)
        parent = {start_id: None}

        while q:
            current_id = q.pop(0)

            if current_id == end_id:
                path = []
                temp = end_id
                while temp is not None:
                    path.append(temp)
                    temp = parent[temp]
                return path[::-1] # Reverse to get path from start to end

            for neighbor_id, _ in self.adj[current_id]:
                if neighbor_id not in parent:
                    parent[neighbor_id] = current_id
                    q.append(neighbor_id)
        return [] # No path found

    def calculate_path_distance(self, path: list[int]) -> float:
        """Calculates the total distance of a given path."""
        if len(path) < 2:
            return 0.0
        
        total_distance = 0.0
        for i in range(len(path) - 1):
            u = path[i]
            v = path[i+1]
            found_edge = False
            for neighbor_id, distance in self.adj[u]:
                if neighbor_id == v:
                    total_distance += distance
                    found_edge = True
                    break
            if not found_edge:
                return float('inf') 
        return total_distance


# --- Nearest Charging Station Logic ---

def find_nearest_charging_station(graph: Graph, start_id: int) -> tuple[int | None, float, list[int]]:
    """
    Finds the nearest charging station from a start_id using Dijkstra's algorithm.
    Returns the ID of the nearest charging station, the distance, and the path to it.
    """
    if start_id not in graph.node_map:
        return None, float('inf'), []

    distances = {node_id: float('inf') for node_id in graph.node_map}
    distances[start_id] = 0
    priority_queue = [(0, start_id)]  # (distance, node_id)
    parents = {start_id: None}

    nearest_station_id = None
    min_distance = float('inf')

    while priority_queue:
        current_distance, current_id = heapq.heappop(priority_queue)

        if current_distance > distances[current_id]:
            continue

        if graph.node_map[current_id].is_charging:
            # We found a charging station, and since it's Dijkstra, it's the nearest one
            nearest_station_id = current_id
            min_distance = current_distance
            break # Exit loop once the nearest is found

        for neighbor_id, weight in graph.adj[current_id]:
            distance = current_distance + weight
            if distance < distances[neighbor_id]:
                distances[neighbor_id] = distance
                parents[neighbor_id] = current_id
                heapq.heappush(priority_queue, (distance, neighbor_id))

    if nearest_station_id is not None:
        path = []
        temp = nearest_station_id
        while temp is not None:
            path.append(temp)
            temp = parents[temp]
        return nearest_station_id, min_distance, path[::-1] # Path from start to station
    else:
        return None, float('inf'), []


# --- Path with Charging Stops Logic ---

def suggest_path_with_charging(graph: Graph, start_id: int, end_id: int,
                               battery_level: float, max_range_km: float) -> tuple[list[int], float, list[int]]:
    """
    Suggests a path, potentially with charging stops, between two nodes.
    Returns the full path, total distance, and IDs of charging stops.
    """
    if start_id not in graph.node_map or end_id not in graph.node_map:
        return [], 0.0, []

    remaining_range = (battery_level / 100.0) * max_range_km
    full_path: list[int] = []
    charging_stops: list[int] = []
    current_node = start_id
    total_distance = 0.0

    while current_node != end_id:
        # Dijkstra to find path from current_node to end_id directly or to a charging station
        pq = [(0.0, current_node)] # (distance, node_id)
        dist = {node_id: float('inf') for node_id in graph.node_map}
        dist[current_node] = 0.0
        parent = {current_node: None}

        target_reached = False
        next_destination_id = -1
        distance_to_next_dest = float('inf') # Distance to the chosen next point (end or station)

        while pq:
            d, u = heapq.heappop(pq)

            if d > dist[u]:
                continue # Already found a shorter path

            # If destination is reachable directly within current range
            if u == end_id and d <= remaining_range:
                next_destination_id = end_id
                distance_to_next_dest = d
                target_reached = True
                break # Found direct path, prioritize this

            # If current node is a charging station (and not the start node if it's already charged)
            if graph.node_map[u].is_charging and u != current_node:
                # Consider this charging station if it's reachable within current range
                # and if it's a better intermediate step (e.g., closer than current 'next_destination_id')
                if d <= remaining_range and d < distance_to_next_dest:
                    next_destination_id = u
                    distance_to_next_dest = d
                    # Don't break yet, keep searching for a direct path to end_id if possible
                    
            # If we've passed our current remaining range, and haven't found a viable next_destination_id yet,
            # then any further nodes are out of reach from this charge.
            if d > remaining_range and next_destination_id == -1:
                continue

            for v, weight in graph.adj[u]:
                new_dist = d + weight
                if new_dist < dist[v]:
                    dist[v] = new_dist
                    parent[v] = u
                    heapq.heappush(pq, (new_dist, v))

        # If end_id was reachable within remaining range
        if target_reached:
            path_segment = []
            temp = end_id
            while temp is not None:
                path_segment.append(temp)
                temp = parent[temp]
            path_segment.reverse()
            
            # Add the segment to full path
            # If full_path is empty, add the whole segment. Otherwise, skip first element (current_node)
            full_path.extend(path_segment if not full_path else path_segment[1:])
            total_distance += graph.calculate_path_distance(path_segment)
            current_node = end_id # Reached final destination
            break # Exit main loop

        # If end_id was NOT reachable directly, try to find a charging station within range
        elif next_destination_id != -1 and graph.node_map[next_destination_id].is_charging:
            path_segment = []
            temp = next_destination_id
            while temp is not None:
                path_segment.append(temp)
                temp = parent[temp]
            path_segment.reverse()

            full_path.extend(path_segment if not full_path else path_segment[1:])
            total_distance += graph.calculate_path_distance(path_segment)
            current_node = next_destination_id
            charging_stops.append(current_node)
            remaining_range = max_range_km # Fully charged

        else:
            # Cannot reach end_id or any charging station
            return [], 0.0, [] # No path found

    return full_path, total_distance, charging_stops


# --- New Charging Station Placement Logic ---

def suggest_charging_stations(graph: Graph, max_stations: int) -> list[Node]:
    """
    Suggests optimal locations for new charging stations based on areas underserved by existing ones.
    Uses a greedy approach, prioritizing nodes furthest from existing stations.
    """
    if not graph.nodes:
        return []

    suggested_nodes: list[Node] = []
    
    # Calculate initial distances from every node to its nearest existing charging station
    # This uses a multi-source BFS/Dijkstra
    dist_to_nearest_station = {node.id: float('inf') for node in graph.nodes}
    queue = []

    for station_loc_id in graph.charging_station_map.keys():
        if station_loc_id in graph.node_map: # Ensure the location_id corresponds to a valid node
            dist_to_nearest_station[station_loc_id] = 0
            queue.append(station_loc_id)

    # BFS to find shortest distance from any node to any existing charging station
    q = list(queue) # Use a list as a deque for BFS
    head = 0
    while head < len(q):
        u = q[head]
        head += 1
        
        for v, weight in graph.adj[u]:
            if dist_to_nearest_station[u] + weight < dist_to_nearest_station[v]:
                dist_to_nearest_station[v] = dist_to_nearest_station[u] + weight
                q.append(v)

    # Sort nodes by their distance to the nearest existing charging station (descending)
    # The idea is to place new stations where existing ones are most sparse.
    nodes_sorted_by_remoteness = sorted(graph.nodes, key=lambda node: dist_to_nearest_station[node.id], reverse=True)

    for node in nodes_sorted_by_remoteness:
        if node.is_charging: # Don't suggest placing a station where one already exists
            continue
        
        suggested_nodes.append(node)
        if len(suggested_nodes) >= max_stations:
            break
            
    return suggested_nodes


# --- Traffic Management Logic ---

class TrafficManager:
    """Manages traffic data (node frequency and high-traffic nodes)."""
    def __init__(self):
        self.node_frequency: dict[int, int] = defaultdict(int)  # Count of users passing through each node
        self.high_traffic_nodes: set[int] = set()               # Nodes considered congested

    def record_user_path(self, path: list[int]):
        """Records a path taken by a user, incrementing node frequencies."""
        for node_id in path:
            self.node_frequency[node_id] += 1

    def update_traffic(self, graph: Graph, threshold: int):
        """
        Marks nodes as high-traffic if their frequency meets/exceeds the threshold.
        Assumes graph is loaded to get node names for print messages.
        """
        for node_id, count in self.node_frequency.items():
            if count >= threshold:
                if node_id not in self.high_traffic_nodes:
                    node_name = graph.node_map.get(node_id, f"Unknown Node {node_id}").name
                    print(f"[Traffic] Node '{node_name}' (ID: {node_id}) reached threshold ({count} >= {threshold}), marked as congested.")
                    self.high_traffic_nodes.add(node_id)
            else: # If traffic drops below threshold, remove from high traffic (optional, but good for dynamic systems)
                if node_id in self.high_traffic_nodes:
                    self.high_traffic_nodes.remove(node_id)


    def get_high_traffic_nodes(self) -> set[int]:
        """Returns the current set of high-traffic node IDs."""
        return self.high_traffic_nodes

    def reset(self):
        """Resets all traffic data."""
        self.node_frequency.clear()
        self.high_traffic_nodes.clear()
        print("[Traffic] All traffic data has been reset.")


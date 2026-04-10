#include "graph.h"

void Graph::loaddata(string filename) {
    ifstream file(filename);
    json data;
    file >> data;

    for (auto& node : data["nodes"]) {
        Node n(node["id"], node["name"], node["latitude"], node["longitude"], node["is_charging_station"]);
        nodes.push_back(n);
        node_map.insert({n.id, n});
    }

    for (auto& edge : data["edges"]) {
        Edge e(edge["from"], edge["to"], edge["distance_km"]);
        edges.push_back(e);
        graph[edge["from"]].emplace_back(edge["to"], edge["distance_km"]);
        graph[edge["to"]].emplace_back(edge["from"], edge["distance_km"]);
    }

    for (auto& station : data["charging_stations"]) {
        charg_station c(station["location"], station["capacity"], station["charging_rate_kw"]);
        stations.push_back(c);
    }
}

void Graph::printsummary() {
    cout << "EV Network Summary\n";
    cout << "Nodes : " << nodes.size() << endl;
    cout << "Edges : " << edges.size() << endl;
    cout << "Charging Stations : " << stations.size() << endl;
}

void Graph::printAllNodes() {
    cout << "\nAll Nodes:\n";
    for (auto& n : nodes) {
        cout << "ID: " << n.id
             << " | Name: " << n.name
             << " | Location: (" << n.lat << ", " << n.lon << ")"
             << " | Charging Station: " << (n.is_charging ? "Yes" : "No")
             << endl;
    }
}

void Graph::printAllEdges() {
    cout << "\nAll Edges:\n";
    for (auto& e : edges) {
        cout << "From: " << e.from
             << " to " << e.to
             << " | Distance: " << e.distance << " km"
             << endl;
    }
}

void Graph::printAllChargingStations() {
    cout << "\nAll Charging Stations:\n";
    for (auto& s : stations) {
        cout << "Location ID: " << s.location_id
             << " | Capacity: " << s.capacity
             << " | Rate: " << s.charging_rate_kw << " kW"
             << endl;
    }
}

vector<int> Graph::findpath(int start, int end) {
    queue<int> q;
    unordered_map<int, int> parent;
    vector<int> path;

    q.push(start);
    parent[start] = -1;

    while (!q.empty()) {
        int i = q.front();
        q.pop();

        if (i == end) {
            while (i != -1) {
                path.push_back(i);
                i = parent[i];
            }
            reverse(path.begin(), path.end());
            return path;
        }

        for (auto& j : graph[i]) {
            if (!parent.count(j.first)) {
                parent[j.first] = i;
                q.push(j.first);
            }
        }
    }
    return {};
}

void Graph::printpath(vector<int> path) {
    if (path.empty()) {
        cout << "No path exists between these nodes!\n";
        return;
    }

    cout << "\nPath: ";
    for (size_t i = 0; i < path.size(); i++) {
        auto it = node_map.find(path[i]);
        if (it != node_map.end()) cout << it->second.name;
        else cout << "[Unknown Node " << path[i] << "]";
        if (i != path.size() - 1) cout << " -> ";
    }
    cout << "\n\n";
}

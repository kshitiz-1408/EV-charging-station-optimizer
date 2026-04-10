#include "nearest.h"

int findNearestChargingStation(Graph& g, int start_id) {
    unordered_map<int, double> dist;
    priority_queue<pair<double, int>, vector<pair<double, int>>, greater<>> pq;

    for (const auto& node : g.getNodes()) {
        dist[node.id] = DBL_MAX;
    }

    dist[start_id] = 0;
    pq.push({0.0, start_id});

    while (!pq.empty()) {
        auto [cur_dist, cur_id] = pq.top(); pq.pop();

        if (g.getNodeMap().at(cur_id).is_charging) {
            return cur_id;
        }

        for (const auto& [neighbor_id, weight] : g.getGraph().at(cur_id)) {
            double new_dist = cur_dist + weight;
            if (new_dist < dist[neighbor_id]) {
                dist[neighbor_id] = new_dist;
                pq.push({new_dist, neighbor_id});
            }
        }
    }

    return -1;
}

void printNearestChargingStation(Graph& g, int from_id) {
    int result = findNearestChargingStation(g, from_id);
    if (result == -1) {
        cout << "No reachable charging station from node ID: " << from_id << "\n";
    } else {
        cout << "Nearest Charging Station is at Node ID: " << result
             << " (" << g.getNodeMap().at(result).name << ")\n";
    }
}

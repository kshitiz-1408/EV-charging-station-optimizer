#include "path2.h"
#include <queue>
#include <unordered_set>
#include <limits>
#include <iostream>
#include <algorithm>

using namespace std;

std::vector<int> suggestPathWithCharging(Graph& g, int start_id, int end_id, double battery_level, double max_range_km) {
    unordered_map<int, vector<pair<int, double>>> adj = g.getGraph();
    unordered_map<int, Node>& nodes = g.getNodeMap();

    double remaining_range = (battery_level / 100.0) * max_range_km;
    vector<int> full_path;
    int current = start_id;

    while (current != end_id) {
        // Dijkstra to find if destination is reachable directly
        priority_queue<pair<double, int>, vector<pair<double, int>>, greater<>> pq;
        unordered_map<int, double> dist;
        unordered_map<int, int> parent;

        pq.push({0.0, current});
        dist[current] = 0.0;
        parent[current] = -1;
        bool reached = false;

        while (!pq.empty()) {
            auto [d, u] = pq.top(); pq.pop();
            if (d > remaining_range) continue;
            if (u == end_id) {
                reached = true;
                break;
            }

            for (auto& [v, w] : adj[u]) {
                if (!dist.count(v) || d + w < dist[v]) {
                    dist[v] = d + w;
                    parent[v] = u;
                    pq.push({dist[v], v});
                }
            }
        }

        if (reached) {
            vector<int> sub_path;
            int temp = end_id;
            while (temp != -1) {
                sub_path.push_back(temp);
                temp = parent[temp];
            }
            reverse(sub_path.begin(), sub_path.end());
            full_path.insert(full_path.end(), sub_path.begin() + (full_path.empty() ? 0 : 1), sub_path.end());
            break;
        }

        // Dijkstra to find nearest reachable charging station
        int next_station = -1;
        double min_dist = numeric_limits<double>::max();
        unordered_map<int, double> sd;
        unordered_map<int, int> station_parent;
        priority_queue<pair<double, int>, vector<pair<double, int>>, greater<>> sq;

        sq.push({0.0, current});
        sd[current] = 0.0;
        station_parent[current] = -1;

        while (!sq.empty()) {
            auto [d, u] = sq.top(); sq.pop();
            if (d > remaining_range) continue;

            if (nodes.at(u).is_charging && d < min_dist) {
                min_dist = d;
                next_station = u;
            }

            for (auto& [v, w] : adj[u]) {
                if (!sd.count(v) || d + w < sd[v]) {
                    sd[v] = d + w;
                    station_parent[v] = u;
                    sq.push({sd[v], v});
                }
            }
        }

        if (next_station == -1) {
            cout << "Cannot reach any charging station from node " << current << ". Trip not possible.\n";
            return {};
        }

        vector<int> sub_path;
        int temp = next_station;
        while (temp != -1) {
            sub_path.push_back(temp);
            temp = station_parent[temp];
        }
        reverse(sub_path.begin(), sub_path.end());
        full_path.insert(full_path.end(), sub_path.begin() + (full_path.empty() ? 0 : 1), sub_path.end());

        current = next_station;
        remaining_range = max_range_km;
    }

    return full_path;
}
void printSuggestedPath(Graph& g, int start_id, int end_id, double battery_level, double max_range_km) {
    vector<int> path = suggestPathWithCharging(g, start_id, end_id, battery_level, max_range_km);
    if (path.empty()) {
        cout << "No valid path with charging stations found.\n";
        return;
    }

    cout << "\nBattery-aware path from source to destination:\n";
    for (size_t i = 0; i < path.size(); ++i) {
        cout << g.getNodeMap().at(path[i]).name;
        if (i != path.size() - 1) cout << " -> ";
    }
    cout << "\n";
}

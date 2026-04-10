#include "placement.h"
#include <queue>
#include <unordered_set>
#include <tuple>
#include <algorithm>
using namespace std;

std::vector<Node> suggestChargingStations(Graph& g, int maxStations) {
    auto& graph = g.getGraph();
    auto& nodes = g.getNodes();
    auto& nodeMap = g.getNodeMap();

    unordered_map<int, bool> inMst;
    unordered_map<int, bool> isStation;
    for (const auto& n : nodes) {
        isStation[n.id] = n.is_charging;
    }

    using EdgeInfo = tuple<double, int, int>; // {weight, from, to}
    priority_queue<EdgeInfo, vector<EdgeInfo>, greater<>> pq;

    int root = nodes[0].id;
    inMst[root] = true;

    for (const auto& [nbr, dist] : graph[root]) {
        pq.push({dist, root, nbr});
    }

    unordered_set<int> mstNodes = {root};
    while (!pq.empty() && mstNodes.size() < nodes.size()) {
        auto [w, u, v] = pq.top(); pq.pop();
        if (inMst[v]) continue;
        inMst[v] = true;
        mstNodes.insert(v);

        for (const auto& [nbr, dist] : graph[v]) {
            if (!inMst[nbr]) {
                pq.push({dist, v, nbr});
            }
        }
    }

    vector<pair<double, Node>> candidates;
    for (int id : mstNodes) {
        if (isStation[id]) continue;

        queue<pair<int, double>> q;
        unordered_set<int> visited;
        q.push({id, 0});
        visited.insert(id);

        bool found = false;
        while (!q.empty()) {
            auto [cur, d] = q.front(); q.pop();
            if (isStation[cur]) {
                candidates.emplace_back(d, nodeMap.at(id));
                found = true;
                break;
            }
            for (const auto& [nbr, dist] : graph.at(cur)) {
                if (visited.insert(nbr).second) {
                    q.push({nbr, d + dist});
                }
            }
        }

        if (!found) {
            candidates.emplace_back(1e9, nodeMap.at(id));
        }
    }

    sort(candidates.begin(), candidates.end(), [](const pair<double, Node>& a, const pair<double, Node>& b) {
    return a.first > b.first; // Sort descending by distance
});


    vector<Node> res;
    for (int i = 0; i < min((int)candidates.size(), maxStations); ++i) {
        res.push_back(candidates[i].second);
    }

    return res;
}

void printSuggestedChargingStations(Graph& g, int maxStations) {
    auto stations = suggestChargingStations(g, maxStations);
    cout << "\nSuggested Charging Station Locations (Top " << maxStations << "):\n";
    if (stations.empty()) {
        cout << "No suggestions needed. All nodes are covered.\n";
        return;
    }
    for (const auto& n : stations) {
        cout << "ID: " << n.id << " | Name: " << n.name
             << " | Location: (" << n.lat << ", " << n.lon << ")\n";
    }
}

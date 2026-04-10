#include "traffic.h"
#include <iostream>
#include "graph.h"

void TrafficManager::recordUserPath(const std::vector<int>& path) {
    for (int node : path) {
        nodeFrequency[node]++;
    }
}

void TrafficManager::updateTraffic(int threshold) {
    for (const auto& [node, count] : nodeFrequency) {
        if (count >= threshold) {
            if (highTrafficNodes.count(node) == 0) {
                Graph g;
                g.loaddata("ev_network.json");
                // std::cout << "[Traffic] Node " <<  g.getNodeMap().at(node).name  << " reached threshold, marked as congested.\n";
                std::cout << "[Traffic] " <<  g.getNodeMap().at(node).name  << " reached Maximum Capacity.\n";
                highTrafficNodes.insert(node);
            }
        }
    }
}

const std::set<int>& TrafficManager::getHighTrafficNodes() const {
    return highTrafficNodes;
}

void TrafficManager::reset() {
    nodeFrequency.clear();
    highTrafficNodes.clear();
}

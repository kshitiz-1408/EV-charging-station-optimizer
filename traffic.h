#pragma once
#include <unordered_map>
#include <set>
#include <vector>

class TrafficManager {
public:
    // Record a path taken by a user
    void recordUserPath(const std::vector<int>& path);

    // Mark nodes as high-traffic if frequency >= threshold
    void updateTraffic(int threshold);

    // Return the current set of high-traffic nodes
    const std::set<int>& getHighTrafficNodes() const;

    // Reset all traffic data (optional, for testing)
    void reset();

private:
    std::unordered_map<int, int> nodeFrequency;  // Count of users passing through each node
    std::set<int> highTrafficNodes;              // Nodes considered congested
};

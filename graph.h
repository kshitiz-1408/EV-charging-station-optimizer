// graph.h
#ifndef GRAPH_H
#define GRAPH_H

#include <iostream>
#include <vector>
#include <unordered_map>
#include <queue>
#include <string>
#include <fstream>
#include <float.h>
#include <algorithm>
#include "json.hpp"

using namespace std;
using json = nlohmann::json;

class Node {
public:
    int id;
    string name;
    double lat, lon;
    bool is_charging;
    Node(int i, string n, double la, double lo, bool c) : id(i), name(n), lat(la), lon(lo), is_charging(c) {}
};

class Edge {
public:
    int from, to;
    double distance;

    Edge(int f, int t, double d) : from(f), to(t), distance(d) {}
};

class charg_station {
public:
    int location_id;
    int capacity;
    double charging_rate_kw;

    charg_station(int loc, int c, double cr) : location_id(loc), capacity(c), charging_rate_kw(cr) {}
};

class Graph {
    vector<Node> nodes;
    vector<Edge> edges;
    vector<charg_station> stations;
    unordered_map<int, vector<pair<int, double>>> graph;
    unordered_map<int, Node> node_map;

public:
    void loaddata(string filename);
    void printsummary();
    void printAllNodes();
    void printAllEdges();
    void printAllChargingStations();
    vector<int> findpath(int start, int end);
    void printpath(vector<int> path);

    vector<Node>& getNodes() { return nodes; }
    unordered_map<int, Node>& getNodeMap() { return node_map; }
    unordered_map<int, vector<pair<int, double>>>& getGraph() { return graph; }
};

#endif

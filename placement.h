#ifndef PLACEMENT_H
#define PLACEMENT_H

#include "graph.h"
#include <vector>

std::vector<Node> suggestChargingStations(Graph& g, int maxStations);
void printSuggestedChargingStations(Graph& g, int maxStations);

#endif

#ifndef PATH2_H
#define PATH2_H

#include "graph.h"
#include <vector>

std::vector<int> suggestPathWithCharging(Graph& g, int start_id, int end_id, double battery_level, double max_range_km);
void printSuggestedPath(Graph& g, int start_id, int end_id, double battery_level, double max_range_km);

#endif

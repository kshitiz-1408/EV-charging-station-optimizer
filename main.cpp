#include "graph.h"
#include "nearest.h"
#include "placement.h"
#include "path2.h"

int main() {
    Graph g;
    g.loaddata("ev_network.json");
    g.printsummary();

    g.printAllNodes();
    g.printAllEdges();
    g.printAllChargingStations();

    int c = 0;
    do {
        cout << "Enter choice:\n(1-Find path)\n(2-Find nearest charging station)\n(3-New charging station placement)\n(4-Suggest path with charging stops)\n(0-Exit)\n";
        cin >> c;
        switch (c) {
            case 1: {
                int s, e;
                cout << "Enter starting station id: ";
                cin >> s;
                cout << "Enter ending station id: ";
                cin >> e;
                g.printpath(g.findpath(s, e));
                break;
            }
            case 2: {
                int start;
                cout << "Enter starting node ID: ";
                cin >> start;
                printNearestChargingStation(g, start);
                break;
            }
            case 3: {
                int k;
                cout << "Enter number of new charging stations to suggest: ";
                cin >> k;
                printSuggestedChargingStations(g, k);
                break;
            }
            case 4: {
                int start, end;
                double battery, range;
                cout << "Enter start node ID: ";
                cin >> start;
                cout << "Enter end node ID: ";
                cin >> end;
                cout << "Enter current battery percentage (0-100): ";
                cin >> battery;
                cout << "Enter maximum EV range (in km): ";
                cin >> range;
                printSuggestedPath(g, start, end, battery, range);
                break;
            }
            case 0:
                break;
            default:
                cout << "Incorrect Choice" << endl;
        }
    } while (c != 0);

    return 0;
}

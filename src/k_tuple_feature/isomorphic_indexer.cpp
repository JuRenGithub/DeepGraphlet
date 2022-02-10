#include "isomorphic_indexer.h"

IsomorphicIndexer::IsomorphicIndexer() {
    deg_seq_2_iso_index[123] = 0;
    deg_seq_2_iso_index[303] = 1;

    deg_seq_2_iso_index[224] = 2;
    deg_seq_2_iso_index[1034] = 3;
    deg_seq_2_iso_index[404] = 4;
    deg_seq_2_iso_index[1214] = 5;
    deg_seq_2_iso_index[2204] = 6;
    deg_seq_2_iso_index[4004] = 7;


    deg_seq_2_iso_index[325] = 8;
    deg_seq_2_iso_index[1135] = 9;
    deg_seq_2_iso_index[10045] = 10;
    deg_seq_2_iso_index[2125] = 11;

    deg_seq_2_iso_index[10225] = 13;
    deg_seq_2_iso_index[505] = 14;

    deg_seq_2_iso_index[11215] = 16;
    deg_seq_2_iso_index[10405] = 17;
    deg_seq_2_iso_index[3115] = 18;
    deg_seq_2_iso_index[20305] = 21;
    deg_seq_2_iso_index[13015] = 22;
    deg_seq_2_iso_index[12205] = 23;
    deg_seq_2_iso_index[4105] = 24;
    deg_seq_2_iso_index[22105] = 25;
    deg_seq_2_iso_index[14005] = 26;
    deg_seq_2_iso_index[32005] = 27;
    deg_seq_2_iso_index[50005] = 28;
}

IsomorphicIndexer::~IsomorphicIndexer() {
    std::unordered_map<unsigned short, unsigned char>().swap(deg_seq_2_iso_index);
}

char IsomorphicIndexer::get_isomorphic_index(SmallGraph* graph) {
    unsigned short deg_seq = graph->get_deg_seq();
    if (deg_seq_2_iso_index.count(deg_seq)) {
        return deg_seq_2_iso_index[deg_seq];
    } else if (deg_seq == 1315) {
        for (unsigned char i = 0; i < graph->edges.size(); ++i) {
            if (graph->edges[i].size() == 1) {
                if (graph->edges[graph->edges[i][0]].size() == 2) {
                    return 12;
                } else if (graph->edges[graph->edges[i][0]].size() == 3) {
                    return 15;
                }
            }
        }
    } else if (deg_seq == 2305) {
        char u = -1;
        for (int i = 0; i < graph->edges.size(); ++i) {
            if (graph->edges[i].size() == 3) {
                if (u == -1) {
                    u = i;
                } else {
                    for (int j = 0; j < graph->edges[u].size(); ++j) {
                        if (graph->edges[u][j] == i) {
                            return 20;
                        } else {
                            return 19;
                        }
                    }
                }
            }
        }
    }
    return -1;
}
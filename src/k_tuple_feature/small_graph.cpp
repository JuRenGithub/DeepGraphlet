#include "small_graph.h"
#include <iostream>

SmallGraph::SmallGraph(unsigned char nodes) {
    N = nodes;
    for (unsigned char i = 0 ; i < N; i++) {
        edges.emplace_back(std::vector<unsigned char>());
    }
}

SmallGraph::~SmallGraph() {
    for (unsigned char i = 0 ; i < N ; i++)
        std::vector<unsigned char>().swap(edges[i]);
    std::vector<std::vector<unsigned char>>().swap(edges);
}

void SmallGraph::add_edge(unsigned char u, unsigned char v) {
    edges[u].emplace_back(v);
    edges[v].emplace_back(u);
}

void SmallGraph::print() {
    std::cout << "-----------------------" << std::endl;
    std::cout << N << std::endl;
    for (unsigned char i = 0; i < edges.size(); ++i) {
        for (unsigned char j = 0; j < edges[i].size(); ++j) {
            std::cout << edges[i][j] << " ";
        }
        std::cout << std::endl;
    }
}

unsigned short SmallGraph::get_deg_seq() {
    std::vector<unsigned short> count(N, 0);
    for (unsigned char i = 0; i < N; ++i) {
        count[edges[i].size()] += 1;
    }
    unsigned short hash_val = 0;
    for (unsigned char i = N - 1; i > 0; --i) {
        hash_val = count[i] + hash_val * 10;
    }
    hash_val = hash_val * 10 + N;
    return hash_val;
}
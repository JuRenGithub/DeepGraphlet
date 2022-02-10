#ifndef __SMALL_GRAPH_H__
#define __SMALL_GRAPH_H__
#include <vector>

class SmallGraph{
    public:
        std::vector<std::vector<unsigned char>> edges;
        unsigned char N;
        SmallGraph(unsigned char nodes);
        ~SmallGraph();
        void add_edge(unsigned char u, unsigned char v);// 2-->3
        void print();
        unsigned short get_deg_seq();//------>unsigned short
};
#endif
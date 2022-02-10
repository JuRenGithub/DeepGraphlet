#ifndef _GRAPH_H_
#define _GRAPH_H_

#include <vector>
#include <string>
#include <unordered_map>
#include <unordered_set>

class Graph{
    public:
        std::string file_path;
        std::vector<std::unordered_set<int>> judge_edge;
        unsigned int N;
        unsigned int M;
        Graph(std::string now_path);
        ~Graph();
        void getKtuples(unsigned char K, unsigned char num_sample, unsigned char thread);
        void pure(std::string now_path);
};
#endif
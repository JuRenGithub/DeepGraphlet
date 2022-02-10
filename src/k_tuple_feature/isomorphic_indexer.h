#ifndef __ISOMORPHIC_INDEXER_H__
#define __ISOMORPHIC_INDEXER_H__
#include <unordered_map>
#include "small_graph.h"
class IsomorphicIndexer {
    private:
        std::unordered_map<unsigned short, unsigned char> deg_seq_2_iso_index;
    public:
        IsomorphicIndexer();
        ~IsomorphicIndexer();
        char get_isomorphic_index(SmallGraph* graph);
};
#endif
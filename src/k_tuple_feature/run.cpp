#include "graph.h"
#include <cstdio>
#include <string>
using namespace std;

int main(int args, char * argv[])
{
    printf("%s\n", argv[0]);
    Graph* G = new Graph(string(argv[1]));
    // G->pure(string(argv[1]) + "2");
    printf("%s|%s|%s\n", argv[2], argv[4], argv[3]);
    // G->checkIsoImpl();
    G->getKtuples(atoi(argv[2]), atoi(argv[3]), atoi(argv[4]));
    // delete G;
}

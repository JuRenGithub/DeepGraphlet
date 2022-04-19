#include "graph.h"
#include "utils.h"
#include "MT19937.h"
#include "small_graph.h"
#include "alias.h"
#include "isomorphic_indexer.h"
#include <vector>
#include <omp.h>
#include <chrono>
#include <set>
#include <numeric>
#include <algorithm>
#include <iostream>
#include <sstream>
#include <vector>
#include <queue>
#include <sys/mman.h>
#include <unistd.h>
#include <fcntl.h>
#include <ctime>
#include <vector>
#include <fstream>

Graph::Graph(std::string now_path) {
    file_path = now_path;
    char *data = NULL;
    int fd = open(now_path.c_str(), O_RDONLY); 
    long long size = lseek(fd, 0, SEEK_END);    //ljr: return the location (How many Byte from head)
    printf("size: %lld\n", size);
    data = (char *) mmap(NULL, size, PROT_READ, MAP_PRIVATE, fd, 0);    //ljr: map the file (or object) into memory
    close(fd);
    long long count = 0;
    bool flag = 0;
    long long idx = 0;  //ljr: no use
    long long cnt = 0;
    while (count < size - 1) {
        std::vector<std::string> row = csv_read_row(&count, ' ', data);
        cnt += 1;
        if (cnt % 10000000 == 0) {
            printf("%lld\n", cnt);
        }
        if(flag) {
            int u = atoi(row[0].c_str());
            int v = atoi(row[1].c_str());
            judge_edge[u].insert(v);
            judge_edge[v].insert(u);
        } else {
            N = atoi(row[0].c_str());   //ljr: node num
            M = atoi(row[1].c_str());   //ljr: edge num
            judge_edge.resize(N);
        }
        idx++;
        flag = 1;
    }
    munmap(data, size); //ljr: release mmap()
}

void Graph::pure(std::string now_path) {
    int non_zero_N = 0;
    std::unordered_map<int, int> old2new;
    std::cout << N << " " << M << std::endl;
    for (int i = 0; i < N; ++i) {
        if (!judge_edge[i].empty()) {
            old2new[i] = non_zero_N++;
        }
    }
    std::ofstream outfile;
    outfile.open(now_path);
    std::cout << non_zero_N << " " << M << std::endl;
    outfile << non_zero_N << " " << M << std::endl;
    for (int i = 0; i < N; ++i) {
        for (auto it: judge_edge[i]) {
            if (i < it) {
                // std::cout << old2new[i] << " " << old2new[it] << endl;
                outfile << old2new[i] << " " << old2new[it] << std::endl;
            }
        }

    }
    outfile.close();
}

Graph::~Graph() {
    std::vector<std::unordered_set<int>>().swap(judge_edge);
}

unsigned char GetRandomNumWithWeight(unsigned char iter, std::vector<double> * weight, MT19937* rander) {
	unsigned char size = iter;
    double accumulateVal = 0;
    for (char i = 0; i < size; i++)
        accumulateVal += (*weight)[i];

    double tempSum = 0;
    double ranIndex = accumulateVal * (double)rander->get() / double(UINT32_MAX);
	for (unsigned char j = 0; j < size; j++) {
		if (ranIndex <= tempSum + (*weight)[j])
			return j;
        tempSum += (*weight)[j];
    }
}

bool is_isomorphism(IsomorphicIndexer* isomorphic_indexer, SmallGraph *graph1, SmallGraph *graph2) {
    return isomorphic_indexer->get_isomorphic_index(graph1) == isomorphic_indexer->get_isomorphic_index(graph2);
}

void Graph::getKtuples(unsigned char K, unsigned char num_sample, unsigned char thread) {
    srand(0);
    std::cout << K << " " << num_sample << " " << thread << std::endl;
    time_t ktuple_start_time = time(NULL);
    IsomorphicIndexer* isomorphic_indexer = new IsomorphicIndexer();
    std::vector<int> degree(N); //ljr: N: the number of nodes

    //ljr: initialize degree, adj, alias(for random sampling), feature
    #pragma omp parallel for num_threads(thread) schedule(dynamic, 1)
    for (int i = 0; i < N ; i++)
        degree[i] = judge_edge[i].size();   //ljr: degree is number of neighbors

    std::vector<std::vector<int>> adj(N);
    std::vector<Alias *> alias(N);  //ljr: N alias
    unsigned char length = (K == 3 ? 2 : (K == 4 ? 8 : 29));    // different k different number of tuple types
    std::vector<std::vector<unsigned char>> feature(N, std::vector<unsigned char>(length, 0));

    //ljr: fill adj, prob, alias
    #pragma omp parallel for num_threads(thread) schedule(dynamic, 1)
    for (int i = 0; i < N; i++) {
        int len = judge_edge[i].size();
        adj[i] = *(new std::vector<int>(len));  //ljr: adjacent list
        std::vector<double> prob(len);
        int count = 0;
        for (int v : judge_edge[i]) {
            adj[i][count] = v;
            prob[count] = degree[v];    //ljr: probability is degree
            count++;
        }
        alias[i] = new Alias(&prob);    //ljr: for every node, each neighbor has different prob
    }

    std::cout << "phrase1 time: " << time(NULL) - ktuple_start_time << std::endl;
    std::cout << "thread n: " << thread << std::endl;
    std::vector<MT19937*> randers;
    for (int i = 0; i < thread; ++ i) {
        MT19937* rander = new MT19937();
        rander->seed(i);
        randers.push_back(rander);
    }

    // std::vector<std::vector<int>> node_lists;
    // std::vector<std::vector<double>> degree_probs;
    // for (unsigned char i = 0; i < thread; ++i) {
    //     node_lists.emplace_back(std::vector<int>(K, 0));
    //     degree_probs.emplace_back(std::vector<double>(K, 0));
    //     // std::cout << int(i) << " " << int(thread) << std::endl;
    // }
    #pragma omp parallel for num_threads(thread) schedule(dynamic, 1)
    for (int i = 0; i < N; i++)
    {
        unsigned char thread_id = omp_get_thread_num();
        // std::cout << "thread_id: " << thread_id << std::endl;
        char idx;
        int target, present, next;
        unsigned char j, k, u, v;
        for (j = 0; j < num_sample; j++) {
            for (k = 3; k <= K; ++k) {
                // std::vector<int> node_list = {i};
                std::vector<int> node_lists(k, 0);
                std::vector<double> degree_probs(k, 0);
                // node_lists[thread_id][0] = i;
                node_lists[0] = i;
                // degree_probs[thread_id][0] = degree[i];
                degree_probs[0] = degree[i];
                for (unsigned char iter = 1; iter < k; iter++) {
                    // target = node_lists[thread_id][GetRandomNumWithWeight(iter, &degree_probs[thread_id], randers[thread_id])];
                    target = node_lists[GetRandomNumWithWeight(iter, &degree_probs, randers[thread_id])];
                    present = alias[target]->draw(randers[thread_id]);
                    // std::cout << target << " " << present << std::endl;
                    if (present == -1)
                        next = target;
                    else
                        next = adj[target][present];
                    // node_lists[thread_id][iter] = next;
                    // degree_probs[thread_id][iter] = degree[next];
                    node_lists[iter] = next;
                    degree_probs[iter] = degree[next];
                }
                SmallGraph * now_g = new SmallGraph(k);
                for(u = 0 ; u < k; u++)
                    for(v = u + 1; v < k; v++) {
                        // if (judge_edge[node_lists[thread_id][u]].count(node_lists[thread_id][v]))
                        if (judge_edge[node_lists[u]].count(node_lists[v]))
                            now_g->add_edge(u, v);
                    }
                idx = isomorphic_indexer->get_isomorphic_index(now_g);
                if (idx == -1) {
                    // for (auto node: node_lists[thread_id]) {
                    for (auto node: node_lists) {
                        std::cout << node << std::endl;
                    }
                    now_g->print();
                    std::cout << "?" << std::endl;
                } else {
                    feature[i][idx] += 1;
                }
                delete now_g;

                std::vector<int>().swap(node_lists);
                std::vector<double>().swap(degree_probs);
            }
        }
    }
    // std::vector<std::vector<int>>().swap(node_lists);
    // std::vector<std::vector<double>>().swap(degree_probs);
    time_t ktuple_end_time = time(NULL);
    std::cout << "calculation time: " << ktuple_end_time - ktuple_start_time << std::endl;

    std::stringstream ss;
    ss <<file_path<<"_"<< "features" << K;
    std::string now_path = ss.str();
    printf("%s\n", now_path.c_str());

    freopen(now_path.c_str(),"w",stdout);
    for (int i= 0; i < N; i++) {   
        printf("%d", feature[i][0]);
        for(int j=1;j < length;j++)
            printf(" %d", feature[i][j]);
        printf("\n");
    }
    fclose(stdout);

    for(int i = 0; i < N; i++) {
        delete alias[i];
        std::vector<int>().swap(adj[i]);
    }
    std::vector<Alias *>().swap(alias);
    std::vector<int>().swap(degree);
    std::vector<std::vector<int>>().swap(adj);
    delete isomorphic_indexer;
}

#include "alias.h"
#include <queue>

Alias::Alias(std::vector<double> * weight) {
    len = weight->size();
    Q.resize(len);
    J.resize(len);
    
    std::queue<int> smaller;
    std::queue<int> larger;

    for(int i = 0 ;i < len; i++) {
        Q[i] = (*weight)[i] * len;
        if (Q[i] < 1)
            smaller.push(i);
        else
            larger.push(i);
    }
    while (!smaller.empty() && !larger.empty()) {
        int small = smaller.front();
        smaller.pop();
        int large = larger.front();
        larger.pop();
        J[small] = large;
        Q[large] = Q[large] - (1 - Q[small]);

        if(Q[large] < 1.0)
            smaller.push(large);
        else
            larger.push(large);
    }
}

Alias::~Alias() {
    std::vector<double>().swap(Q);
    std::vector<int>().swap(J);
}


int Alias::draw(MT19937* rander) {
    if (len == 0)
        return -1;
    int now = rander->get()%len;
    double value = (double)rander->get() / double(UINT32_MAX);
    // std::cout << "alias draw: " << value << std::endl;
    if (value < Q[now])
        return now;
    else
        return J[now];
}
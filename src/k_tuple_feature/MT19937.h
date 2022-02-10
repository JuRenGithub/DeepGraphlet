#ifndef __MT19937_H__
#define __MT19937_H__

#include <random>
class MT19937 {
public:
    std::mt19937 rng;
    // This is equivalent to srand().
    void seed(unsigned int new_seed);

    // This is equivalent to rand().
    unsigned int get();
};
#endif
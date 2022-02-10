#ifndef __ALIAS_H__
#define __ALIAS_H__
#include <vector>
#include "MT19937.h"
class Alias{
    public:
         int len;
        std::vector<double> Q;
        std::vector<int> J;
        Alias(std::vector<double> * weight);
         int draw(MT19937* rander);
        ~Alias();
};
#endif
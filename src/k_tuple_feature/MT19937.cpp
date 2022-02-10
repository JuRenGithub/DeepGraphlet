#include "MT19937.h"
#include <iostream>
void MT19937::seed(unsigned int new_seed = std::mt19937_64::default_seed) {
    rng.seed(new_seed);
}

unsigned int MT19937::get() {
    return rng();
}

#include "utils.h"
#include <fstream>
#include <sstream>
std::vector<std::string> csv_read_row(long long* count, char delimiter, char* data) {
    std::stringstream ss;
    std::vector<std::string> row;
    while (true) {
        char c = data[*count];
        if (c == delimiter) {
            row.push_back(ss.str());
            ss.str("");
        } else if(c=='\r' || c=='\n') {
            if (c == '\n')
                (*count) = (*count) + 1;
            row.push_back(ss.str());
            return row;
        }
        else {
            ss << c;
        }
        (*count) = (*count) + 1;
    }
}
CXXFLAGS = -mcmodel=large
all: run clean
run:run.o graph.o utils.o MT19937.o small_graph.o isomorphic_indexer.o alias.o
	g++ run.o graph.o utils.o MT19937.o small_graph.o alias.o isomorphic_indexer.o -o run $(CXXFLAGS) -fopenmp -O3
run.o: run.cpp graph.h 
	g++ -c -Wall -std=c++11 $(CXXFLAGS) run.cpp -o run.o -fopenmp -O3
graph.o: graph.cpp graph.h utils.h MT19937.h isomorphic_indexer.h small_graph.h alias.h
	g++ -c -Wall -std=c++11 $(CXXFLAGS)  graph.cpp -o graph.o -fopenmp -O3
utils.o: utils.cpp utils.h
	g++ -c -Wall -std=c++11 $(CXXFLAGS)  utils.cpp -o utils.o -fopenmp -O3
MT19937.o: MT19937.cpp MT19937.h
	g++ -c -Wall -std=c++11 $(CXXFLAGS)  MT19937.cpp -o MT19937.o -fopenmp -O3
small_graph.o: small_graph.cpp small_graph.h
	g++ -c -Wall -std=c++11 $(CXXFLAGS)  small_graph.cpp -o small_graph.o -fopenmp -O3
isomorphic_indexer.o: isomorphic_indexer.cpp isomorphic_indexer.h small_graph.h
	g++ -c -Wall -std=c++11 $(CXXFLAGS)  isomorphic_indexer.cpp -o isomorphic_indexer.o -O3
alias.o: alias.cpp alias.h
	g++ -c -Wall -std=c++11 $(CXXFLAGS)  alias.cpp -o alias.o -fopenmp -O3
clean:
	rm -rf *.o
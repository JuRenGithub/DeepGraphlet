from utils import readEdgeList, split_between_last_char
import numpy as np
import time
from ResultWritter import ResultWritter
import os

class KTupleFeatureGenerator:
    def __init__(self, path, k = 5, sample_times = 100, thread_num = 40):
        self.path = path
        self.k = k
        self.sample_times = sample_times
        self.thread_num = thread_num

    def generate_k_tuple_feature(self, path):
        os.system('./run ' + path + " " + str(self.k) + " " + str(self.sample_times) + " " + str(self.thread_num))
    
    def generate_k_tuple_feature_old(self, path):
        for i in range(3, self.k + 1):
            os.system('./runold ' + path + " " + str(i) + " " + str(self.sample_times) + " " + str(self.thread_num))

    def generateDataFeature(self):
        print(self.path)
        # self.generate_k_tuple_feature(self.path)
        prefix, _ = split_between_last_char(self.path, '.')
#             prefix += suffix
        print(prefix)
        if os.path.exists(prefix):
            filenames = os.listdir(prefix)
            filenames = [(prefix + "/" + name) for name in filenames]
            fileNames = []
            for name in filenames:
                if name.split('.')[-1] == "edges":
                    print(name)
                    self.generate_k_tuple_feature_old(name)
                
if __name__ == '__main__':
    path = "../data/artist_edges.edges"
    ktuple = KTupleFeatureGenerator(path = path)
    ktuple.generate_k_tuple_feature_old(ktuple.path)
    ktuple.generateDataFeature()
    
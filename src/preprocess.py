
from utils import split_between_last_char
import GraphSampling
import GenerateLabel
from k_tuple_feature_generator import KTupleFeatureGenerator

def preprocess_data(filePath, is_training = True):
	k_tuple_feature_generator = KTupleFeatureGenerator(filePath)
	k_tuple_feature_generator.generate_k_tuple_feature_old(filePath)
	if is_training == True:
		# GenerateLabel.GenerateLabel(filePath)
# 		GraphSampling.partition(filePath, 30, 15)
		k_tuple_feature_generator.generateDataFeature()

if __name__ == '__main__':
    preprocess_data("../data/artist_edges.edges", is_training = True)
    preprocess_data("../data/cit-Patents.edges", is_training = True)
    preprocess_data("../data/com-lj.edges", is_training = True)
    preprocess_data("../data/com-orkut.edges", is_training = True)
    preprocess_data("../data/soc-Slashdot0902.edges", is_training = True)
    preprocess_data("../data/web-BerkStan.edges", is_training = True)
    preprocess_data("../data/web-Google.edges", is_training = True)
    preprocess_data("../data/wiki-topcats.edges", is_training = True)
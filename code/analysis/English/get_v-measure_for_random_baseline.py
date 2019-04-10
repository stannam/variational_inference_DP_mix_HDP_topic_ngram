# coding: utf-8

import numpy as np
import pandas as pd
import sklearn.metrics as sklm
import argparse, os.path, collections


class Random_Sampler(object):
	def __init__(self, random_type):
		if random_type=='uniform':
			self._sample = self._uniform_iid_sample
		elif random_type=='weighted':
			self._sample = self._weighted_iid_sample
		elif random_type=='shuffle':
			self._sample = self._shuffle
		else:
			raise ValueError('Invalid random_type: {random_type}'.format(random_type=random_type))

	def sample(self, grand_truth_labels, num_samples):
		v_measures = []
		self.grand_truth_labels = grand_truth_labels
		counts = collections.Counter(self.grand_truth_labels)
		self.label_inventory = counts.keys()
		self.weights = np.array(counts.values()).astype(np.float64)
		self.weights /= self.weights.sum()
		self.data_size = len(self.grand_truth_labels)
		for iter_ix in range(num_samples):
			labels_pred = self._sample()
			v_measures.append(sklm.v_measure_score(self.grand_truth_labels, labels_pred))
		return v_measures

	def _uniform_iid_sample(self):
		return np.random.choice(self.label_inventory, size=self.data_size)

	def _weighted_iid_sample(self):
		return np.random.choice(self.label_inventory, size=self.data_size, p=self.weights)

	def _shuffle(self):
		return np.random.permutation(self.grand_truth_labels)




if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('data_path', type=str, help='Path to the grand truth data.')
	parser.add_argument('num_samples', type=int, help='# of samples.')
	parser.add_argument('random_type', type=str, help='Type of randomness. "uniform" for iid uniform sampling, "weighted" for iid sampling weighted by class frequency, and "shuffle" for shuffling the grand truth labels.')
	parser.add_argument('-w', '--whole_data', action='store_true', help='Use the whole data rather than Anglo-Saxon and Latin alone.')
	# parser.add_argument('--seed', type=int, default=111, help='Random seed.')
	args = parser.parse_args()

	np.random.seed(111)

	df_data = pd.read_csv(args.data_path, sep='\t', encoding='utf-8')
	df_data = df_data[~df_data.origin.isnull()]
	origin2ix=dict([('AngloSaxon', 0), ('OldNorse', 0), (u'Dutch', 0), (u'Latin', 1), (u'French', 1), (u'LatinatesOfGermanic', -1)])
	df_data['actual_sublex']=df_data.origin.map(origin2ix)
	if not args.whole_data:
		df_data = df_data[df_data.origin.isin(['AngloSaxon','Latin'])]
	df_data = df_data[df_data.actual_sublex!=-1]

	df_result = pd.DataFrame()
	sampler = Random_Sampler(args.random_type)
	df_result['v_measure'] = sampler.sample(df_data.actual_sublex.tolist(), args.num_samples)
	if args.whole_data:
		filepath = 'English_v-measure_{random_type}-random_baseline_{num_samples}-samples_WITH-WHOLE-DATA.csv'.format(num_samples=args.num_samples, random_type=args.random_type)
	else:
		filepath = 'English_v-measure_{random_type}-random_baseline_{num_samples}-samples.csv'.format(num_samples=args.num_samples, random_type=args.random_type)
	df_result.to_csv(filepath, index=False)
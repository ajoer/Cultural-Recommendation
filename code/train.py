#!/usr/bin/python3
"""
	Train ML method for page prediction

	1) import JSON, split into train and test
	2) train on train, test on test
	3) output performance + wrong prediction examples.
"""
import utils
import numpy as np
import matplotlib.pyplot as plt
from sklearn import svm, metrics, model_selection

languages = sorted(["ar"]) #"fr", "da", "sv", "nb", "nl", "de", "is"]) #sorted(open("resources/wikipedia_LVs.txt").readlines())

for language in languages:
	f1s = []
	accuracies = []
	precisions = []
	recalls = []
	data = utils.read_from_json("data/data_%s.json" % language)

	X = [data[dp]["representation"] for dp in data]
	y = [data[dp]["y"] for dp in data]

	true_pos = 0
	false_pos = 0
	true_neg = 0
	false_neg = 0

	cross_val = 10
	for i in range(cross_val):
		X_train, X_test, y_train, y_test = model_selection.train_test_split(X, y, test_size=0.20)

		weight = 2
		clf = svm.SVC(kernel='linear', class_weight={1: weight})
		clf.fit(X_train, y_train)

		y_pred = clf.predict(X_test)

		recalls.append(metrics.recall_score(y_test, y_pred))
		precisions.append(metrics.precision_score(y_test, y_pred))
		f1s.append(metrics.f1_score(y_test, y_pred))
		accuracies.append(metrics.accuracy_score(y_test, y_pred))

		for yt, yp in zip(y_test, y_pred):
			if yt == 0 and yp == 0:  true_neg += 1
			if yt == 0 and yp == 1:  false_pos += 1
			if yt == 1 and yp == 0:  false_neg += 1
			if yt == 1 and yp == 1:  true_pos += 1


	print(language, "\twith weight %d" % weight)
	print("average f1:\t\t", sum(f1s)/len(f1s))
	print("average precision:\t", sum(precisions)/len(precisions))
	print("average recall:\t\t", sum(recalls)/len(recalls))
	print("average accuracy:\t", sum(accuracies)/len(accuracies))
	
	print("true positives\t", 	true_pos/cross_val, 	"\t(", 	true_pos/cross_val/len(y_test),")")
	print("true negatives\t", 	true_neg/cross_val, 	"\t(", 	true_neg/cross_val/len(y_test),")")
	print("false positives\t", 	false_pos/cross_val, 	"\t(", 	false_pos/cross_val/len(y_test),")")
	print("false negatives\t", 	false_neg/cross_val, 	"\t(", 	false_neg/cross_val/len(y_test),")")
	print("total size of test:\t", len(y_test))
	print()
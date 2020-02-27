"""
Classify data.
"""
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import KFold
from sklearn.metrics import accuracy_score
import pandas as pd
import numpy as np
import pickle

def readData():
	""" Method to read annotated data and return data and data_labels
	Returns:
		data and data_labels

	"""
	tweets = pd.read_csv("Annotated_Tweets.csv",header=None,names=['user', 'text','link','polarity'])
	data_labels = np.array(tweets['polarity'])
	data = np.array(tweets['text'])
	return data, data_labels

def main():
	data, data_labels = readData()
	vectorizer = CountVectorizer( analyzer = 'word', lowercase =False)
	features = vectorizer.fit_transform(data)
	features_nd = features.toarray()

	cross_validation = KFold(n_splits = 3)
	accuracies = []

	clf = LogisticRegression(solver='liblinear', multi_class ='auto')

	for X_train_index, X_test_index in cross_validation.split(features):
		clf.fit(features[X_train_index], data_labels[X_train_index])
		predictions = clf.predict(features[X_test_index])
		accuracies.append(accuracy_score(data_labels[X_test_index], predictions))

	accuracies = np.array(accuracies)
	for i in range(len(accuracies)):
		print("Accuracy for fold", i+1, ": %.4f" %(accuracies[i]))
	k_fold_mean_acc = np.mean(accuracies)
	print("Mean Accuracy: %.4f" %(k_fold_mean_acc))
	

	#Train_Test_split	
	X_train, X_test, y_train, y_test = train_test_split(features_nd, data_labels, train_size =0.8, test_size= 0.2, random_state = 1234)
	clf = clf.fit(X=X_train, y= y_train)
	y_pred = clf.predict(X_test)
	train_test_split_accuracy = accuracy_score(y_test,y_pred)
	print("Train_test_split Accuracy: %.4f" %(train_test_split_accuracy))
	
	clf_list = []
	clf_list.append(k_fold_mean_acc)
	clf_list.append(train_test_split_accuracy)

	pos, neg, neu = 0, 0 , 0
	for i in range(len(data_labels)):
		if(data_labels[i]) == 0:
			neutral = data[i]
			neu +=1
		if(data_labels[i]) == 1:
			positive = data[i]
			pos +=1
		if data_labels[i] == -1:
			negative = data[i]
			neg +=1
	
	clf_list.append(pos)
	clf_list.append(positive)
	clf_list.append(neg)
	clf_list.append(negative)
	clf_list.append(neu)
	clf_list.append(neutral)

	print('Saving Data to pickle')
	pickle.dump(clf_list, open('classification.pkl', 'wb'))    
	print("\nData stored in classification.pkl") 
	pass

if __name__ == "__main__":
    main()
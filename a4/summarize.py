"""
Summarize data.
"""
import pickle


def readData():
	tweets = pickle.load(open('tweets.pkl', 'rb'))
	clusters = pickle.load(open('clusters.pkl', 'rb'))
	clf_data = pickle.load(open('classification.pkl', 'rb'))
	return tweets, clusters, clf_data


def main():
	tweets, clusters, clf_data = readData()
	users = sum(len(n) for n in clusters)

	print('Number of users collected: ', users)
	print('Number of messages collected: %d ' %len(tweets))
	print('Number of communities discovered: %d ' %len(clusters))
	print('Average number of users per community: %.2f' %((sum(len(n) for n in clusters))/ len(clusters)))
	print('Number of Positve Instances: ', clf_data[2])
	print('Number of Negative Instances: ', clf_data[4])
	print('Number of Neutral Instances: ', clf_data[6])

	print('Example of Positive Instance: \n', clf_data[3])
	print('Example of Negative Instance: \n', clf_data[5])
	print('Example of Neutral Instance: \n', clf_data[7])
	f = open('summary.txt', 'w',encoding = 'utf-8')
	f.write('Number of users collected: %d \n' %users)
	f.write('\nNumber of messages collected: %d \n' %len(tweets))
	f.write('\nNumber of communities discovered: %d \n' %len(clusters))
	f.write('\nAverage number of users per community: %.2f\n' %((sum(len(n) for n in clusters))/ len(clusters)))
	
	f.write("\nMean Accuracy for 3 fold cross validation: %.4f\n" %clf_data[0])
	f.write("\nTrain_test_split Accuracy: %.4f\n" %clf_data[1])

	f.write('\nNumber of Positve Instances: %s \n' % clf_data[2])
	f.write('\nNumber of Negative Instances: %s\n' %clf_data[4])
	f.write('\nNumber of Neutral Instances: %s\n' %clf_data[6])
	f.write('\nExample of Positive Instance: \n %s\n' %str(clf_data[3]))
	f.write('\nExample of Negative Instance: \n %s\n' %str(clf_data[5]))
	f.write('\nExample of Neutral Instance: \n %s\n' %str(clf_data[7]))
	
	print("\nData summerized to file 'summary.txt'.\n")
	pass


if __name__ == "__main__":
    main()
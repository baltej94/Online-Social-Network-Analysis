"""
Collect train data for annotating.
"""
import re
import pickle
from TwitterAPI import TwitterAPI

consumer_key = 'gnZ5EQddnslESKIqdFbHMHGg7'
consumer_secret = '8qw5yHpFNSxTjNZX7zhAYGGX3d56kQB3WCcwNrmvLnFNzkUKVB'
access_token = '1087946435474219013-wlYg2uJIRKkw9iddhb41wwf5pFZ6ed'
access_token_secret = 'Oj8xBPUpEnSYsb40TMslZda7aRPTknxXxyjZgp115amD2'


def get_twitter():
    """ Construct an instance of TwitterAPI using the tokens you entered above.
    Returns:
      An instance of TwitterAPI.
    """
    return TwitterAPI(consumer_key, consumer_secret, access_token, access_token_secret)


def robust_request(twitter, resource, params, max_tries=5):
    """ If a Twitter request fails, sleep for 15 minutes.
    Do this at most max_tries times before quitting.
    Args:
      twitter .... A TwitterAPI object.
      resource ... A resource string to request; e.g., "friends/ids"
      params ..... A parameter dict for the request, e.g., to specify
                   parameters like screen_name or count.
      max_tries .. The maximum number of tries to attempt.
    Returns:
      A TwitterResponse object, or None if failed.
    """
    for i in range(max_tries):
        request = twitter.request(resource, params)
        if request.status_code == 200:
            return request
        else:
            print('Got error %s \nsleeping for 15 minutes.' % request.text)
            sys.stderr.flush()
            time.sleep(61 * 15)

def get_training_tweets(twitter):
    tweets = []
    f = open('tweets_for_annotation.csv', 'w',encoding='utf-8')
    
    for tweet in robust_request(twitter, 'search/tweets', {'q': 'Muller Report', 'count' : 100, 'lang' : 'en', 'tweet_mode' : 'extended' }):
        tweets.append(tweet)

    for i in range(10):
      minId = getMinID(tweets)
      for tweet in robust_request(twitter, 'search/tweets', {'q': 'Muller Report', 'count' : 100, 'lang' : 'en', 'tweet_mode' : 'extended' }):
        tweets.append(tweet)    

    for i in tweets:
        string = i['full_text']                
        string = re.sub(',', '', string)
        string = re.sub('\n', '', string)
        user = i['user']['screen_name']
        link = "https://twitter.com/i/web/status/" + i['id_str']
        row = user + "," + string + "," + link + "\n"
        f.write(row)
    print("Tweets written on file tweets_for_annotation.csv")    

def getMinID(tweets):
  """
  Method to find the minimum id of the collected tweets and return it.

  Args: Tweets
  Returns: Min id of all the tweets
  """
  minID = tweets[0]['id']
  for i in range(len(tweets)):
    minID = min(minID, tweets[i]['id'])
  return minID - 1

def main():
  twitter = get_twitter()
  print('\nEstablished Twitter connection.')
  print('\nFetching Tweets.')
  get_training_tweets(twitter)
  pass

if __name__ == "__main__":
    main()
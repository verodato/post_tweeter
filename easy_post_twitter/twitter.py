from dotenv import load_dotenv
from datetime import date, datetime
from time import sleep
from loguru import logger as log
import os
from pathlib import Path
import tweepy
from tweepy.auth import OAuth1, OAuthHandler


class Twitter:
    @classmethod
    def __get_env(cls):
        """ Getter for the environment variables """
        path = Path(__file__).parent.parent.parent.parent.parent.parent / '.env'
        if path.is_file():
            load_dotenv(dotenv_path=path)
        else:
            log.warning('Error loading .env file. File not found.')
            log.warning('Please create a .env file with the keys and tokens needed to connect to the Twitter API.')

    def __init__(self, surface=False, with_images=False):
        self.__get_env()
        self.__start = datetime.today().strftime('%Y-%m-%dT') + '03:00:00Z'
        self.__surface = surface
        self.__with_images = with_images

    @classmethod
    def __get_client(cls):
        """ Getter for the client object """
        try:
            client = tweepy.Client(bearer_token=os.getenv('BEARER_TOKEN'),
                                   access_token=os.getenv('ACCESS_TOKEN'),
                                   access_token_secret=os.getenv('ACCESS_TOKEN_SECRET'),
                                   consumer_key=os.getenv('API_KEY'),
                                   consumer_secret=os.getenv('API_KEY_SECRET'),
                                   wait_on_rate_limit=False)
            log.info(f'Client created successfully. ID: {client.get_me().data.id}')
            return client
        except Exception as e:
            log.error(f'Error creating client. Error: {e}')
            return None

    def get_client(self):
        """ Getter for the client object """
        return self.__get_client()

    def __get_api(self):
        """ Getter for the api object """
        try:
            client = self.__get_client()
            auth = OAuthHandler(client.consumer_key,
                                client.consumer_secret)
            auth.set_access_token(client.access_token, client.access_token_secret)
            api = tweepy.API(auth=auth)
            #log.info(f'API created successfully. ID:')
            return api
        except Exception as e:
            log.error(f'Error creating API. Error: {e}')
            return None

    def __search_tweets_user(self, client, query, max_results):

        tweets = client.get_users_tweets(client.get_me().data.id, max_results=max_results, start_time=self.__start)
        results = []
        if not tweets.data is None and len(tweets.data) > 0:
            if self.__with_images:
                for tweet in tweets.data:
                    if (tweet.text.split('\n')[0] == query.split('-')[0].strip()) \
                            or (tweet.text.split('https')[0].strip() == query.split('-')[0].strip()):
                        results.append({
                            'id': tweet.id,
                            'text': tweet.text
                        })
            else:
                for tweet in tweets.data:
                    if tweet.text.split('\n')[0] == query.split('-')[0].strip():
                        results.append({
                            'id': tweet.id,
                            'text': tweet.text
                        })
        return results

    def __search_tweets_surface(self, client, query, max_results):
        """
            Searching for Tweets is an important feature used to surface Twitter conversations about a specific topic or event.
            While this functionality is present in Twitter, these endpoints provide greater flexibility and power when filtering
            for and ingesting Tweets so you can find relevant data for your research more easily; build out near-real-time
            ‘listening’ applications; or generally explore, analyze, and/or act upon Tweets related to a topic of interest.
        """
        tweets = client.search_recent_tweets(query=query, max_results=max_results, start_time=self.__start)
        results = []
        if not tweets.data is None and len(tweets.data) > 0:
            for tweet in tweets.data:
                results.append({
                    'id': tweet.id,
                    'text': tweet.text
                })
        return results

    @classmethod
    def __get_tweet(cls, client, id):
        tweet = client.get_tweet(id, expansions=['author_id'], user_fields=['username'])
        return tweet

    def __search_tweet_list(self, query, max_results):
        """ Search for a tweet list """
        client = self.__get_client()
        # Searching for tweets
        if self.__surface:
            tweets = self.__search_tweets_surface(client, query, max_results)
        else:
            tweets = self.__search_tweets_user(client, query, max_results)

        # Creating list of tweets
        objs = []
        if len(tweets) > 0:
            for tweet in tweets:
                twt = self.__get_tweet(client, tweet['id'])
                objs.append({
                    'text': tweet['text'],
                    'username': twt.includes['users'][0].username,
                    'id': tweet['id'],
                    'url': 'https://twitter.com/{}/status/{}'.format(twt.includes['users'][0].username, tweet['id'])
                })
        return objs, client

    def tweet_to_publish_with_image(self, text, imgs, query=None, sequential=False):
        """ Publish a tweet with an image """
        if self.__with_images is False:
            raise Exception('Images are not enabled. E.g. Twitter(with_images=True)')

        log.info('Starting post')
        try:
            if sequential is False:
                if isinstance(imgs, list) | isinstance(imgs, dict):
                    raise Exception('Sequential is False. Only one image is allowed.')
                api = self.__get_api()
                media = api.media_upload(imgs)
                api.update_status(status=text, media_ids=[media.media_id])
                log.info('Tweet published successfully')
                return

            api.update_status(status=text)
            log.info('Header posted')
            log.info('Waiting broadcasting')
            sleep(10)
            tweets, client = self.__search_tweet_list(query, 10)
            if tweets:
                # if we already have tweeted about it today we create a sequential post
                # For this to happen we get the id of the tweet we want to follow
                for key, value in imgs.items():
                    log.info(f'Tweeting image: {value}')
                    media = api.media_upload(value)
                    api.update_status(status=key, media_ids=[media.media_id], in_reply_to_status_id=tweets[0]['id'])
                    log.info('Waiting broadcasting.')
                    sleep(25)
                    tweets, client = self.__search_tweet_list(f'{key} -is:retweet', 10)
        except BaseException as err:
            log.error(f'There was an error trying to post the images. Error: {err}')

    def tweet_to_publish(self, text, query=None, sequential=False):
        """ Publish a tweet
        :parameters: text: text of the tweet
        :parameters: query: query to search for the tweet (used only if sequential is True)
        :parameters: sequential: if True, the tweet will be published sequentially
        """

        if sequential:
            tweets, client = self.__search_tweet_list(query, 10)
            if tweets:
                # if it already exists we create a sequential post
                # For this to happen we get the id of the tweet we want to follow
                try:
                    response = client.create_tweet(text=text, in_reply_to_tweet_id=tweets[0]['id'])
                    log.info(f'Tweet created successfully. ID: {response.data["id"]}')
                except Exception as e:
                    log.error(f'Error creating tweet. Error: {e}')

            else:
                # if there are no posts on the day we create a new post
                try:
                    response = client.create_tweet(text=text)
                    log.info(f'Tweet created successfully. ID: {response.data["id"]}')
                except Exception as e:
                    log.error(f'Error creating tweet. Error: {e}')

        else:
            try:
                client = self.__get_client()
                response = client.create_tweet(text=text)
                log.info(f'Tweet created successfully. ID: {response.data["id"]}')
            except Exception as e:
                log.error(f'Error creating tweet. Error: {e}')

    def tweetItNow(self, text):
        '''Tweet the "text" and do not ask questions'''
        client = self.__get_client()
        try:
            response = client.create_tweet(text=text)
            log.info(f'Tweet created successfully. ID: {response.data["id"]}')
        except Exception as e:
            log.error(f'Error creating tweet. Error: {e}')

    def tweetNthread(self, text, isThread, id):
        ''' This method do not use twitter's api search to determine if
        a tweet is the day's opening one or a response to an early one. A state 
        local file keeps the state that informs the last day when the 
        state was last updated and the ID of the last tweet.
        '''
        client = self.__get_client()
        if isThread:
            try:
                print('Thread. Last tweet id:',id)
                response = client.create_tweet(text=text, in_reply_to_tweet_id=id)
                return response
            except Exception as e:
                log.error(f'Error creating thread. Error: {e}')
        else:
            try:
                response = client.create_tweet(text=text)
                log.info(f'Tweet created successfully. ID: {response.data["id"]}')
                return response
            except Exception as e:
                log.error(f'Error creating tweet. Error: {e}')


    def tweetIt(self, text, img, isThread, id):
        ''' This method do not use twitter's api search to determine if
        a tweet is the day's opening one or a response to an early one. 
        Tweets with or without images.
        '''
        # with image
        if img != '':
          client = self.__get_client()
          if isThread:
              api = self.__get_api()
              media = api.media_upload(img)
              response = client.create_tweet(text=text, media_ids=[media.media_id], in_reply_to_tweet_id=id)
              return response
          else:
              api = self.__get_api()
              media = api.media_upload(img)
              response = client.create_tweet(text=text, media_ids=[media.media_id])
              return response

        # no image
        else:          
          client = self.__get_client()
          if isThread:
              try:
                  print('Thread. Last tweet id:',id)
                  response = client.create_tweet(text=text, in_reply_to_tweet_id=id)
                  return response
              except Exception as e:
                  log.error(f'Error creating thread. Error: {e}')
          else:
              try:
                  response = client.create_tweet(text=text)
                  log.info(f'Tweet created successfully. ID: {response.data["id"]}')
                  return response
              except Exception as e:
                  log.error(f'Error creating tweet. Error: {e}')



if __name__ == '__main__':
    img = '/home/drakon/Documents/DEV/projetos/easy_post_twitter/imgs/market1.png'
    tw = Twitter(with_images=True)
    status = 'B3 interbank deposit futures: today and a month ago #FuturodoCDI #mercadofinanceiro'
    tw.tweet_to_publish_with_image(text=status, imgs=img, sequential=False)

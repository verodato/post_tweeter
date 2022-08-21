from easy_post_twitter.twitter import Twitter

if __name__ == '__main__':
    ptax = '''
        BRL USD exchange rate
        PTAX: cotação de compra
        10:00h 4,7390
        11:00h 4,7390  
        12:00h 4,7390  
        '''
    query_ptax = 'BRL USD exchange rate  -is:retweet'

    tw = Twitter(surface=False)
    tw.tweet_to_publish(text=ptax, sequential=True, query=query_ptax)

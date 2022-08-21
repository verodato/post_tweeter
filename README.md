
# Easy Post Twitter

This is a basic project for twitter posts.

Project built using tweepy.


## Usage

 ```Python

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
 
 ```


## Environment variables

Create an .env file in the project root, as shown in the example.

```bash
BEARER_TOKEN=AAAAAAAAAAAAAAAAAAAAABPlaAEAAAAAUbvcbHGUxMgXicxczmxE12uF055gs%3D0Nxt70Hx19URABGJoYAuR5Gv1FJ2BtNKI65bER74YSoH0gFQDj
ACCESS_TOKEN=754983417029206016-w4U4IgkhYrwwmYREJNhxcsNlp2EC3Urfq
ACCESS_TOKEN_SECRET=3elowiIsAUKPxHLJzgwrkP3jxVuVDioB4wWkvcf5hSkHLf4
API_KEY=HdtdQsnCZTJgxqtspNW2GSGdN0
API_KEY_SECRET=L8mPKrRfto5SfLseN5v7eQi9tpGchxxasAAPigX1on0s9SVAxjT
```


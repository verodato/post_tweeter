from easy_post_twitter.twitter import Twitter

if __name__ == '__main__':
    ptax = '''
        BRL USD exchange rate
        PTAX: cotação de compra
        10:00h 4,7390
        
        '''
    query_ptax = 'BRL USD exchange rate  -is:retweet'

    imgs = {
        'Titulo imagem 1': '/home/drakon/Documents/DEV/projetos/easy_post_twitter/imgs/market1.png',
        'Titulo imagem 2': '/home/drakon/Documents/DEV/projetos/easy_post_twitter/imgs/market2.png',
        'Titulo imagem 3': '/home/drakon/Documents/DEV/projetos/easy_post_twitter/imgs/market3.png'}

    single_image = '/home/drakon/Documents/DEV/projetos/easy_post_twitter/imgs/market1.png'
    tw = Twitter(with_images=True)
    status = 'B3 interbank deposit futures: today and a month ago #FuturodoCDI #mercadofinanceiro'
    tw.tweet_to_publish_with_image(text=status, imgs=imgs, sequential=False)

    # tw1 = Twitter(surface=False, with_images=True)
    # tw1.tweet_to_publish_with_image(ptax, query_ptax, imgs)
    #
    # tw2 = Twitter(surface=False)
    # tw2.tweet_to_publish(text=ptax, sequential=True, query=query_ptax)

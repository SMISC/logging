import datetime

def twittertime(dt):
    return (datetime.datetime.strptime(dt, "%a %b %d %H:%M:%S +0000 %Y") - datetime.datetime(1970,1,1)).total_seconds()

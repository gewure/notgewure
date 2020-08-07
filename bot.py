import tweepy
import openai
import json

from tweepy.streaming import StreamListener
from tweepy import Stream
from tweepy import API

# Authenticate to Twitter
auth = tweepy.OAuthHandler()
auth.set_access_token()

# openAI auth
openai.api_key = ""

# Create API object
tapi = tweepy.API(auth)

# memory of the tweets users sent
memory = []
memory.append("Output: Im an AI assistant on Twitter. I am helpful, creative, clever, and very friendly. i asnwer all your questions. ")
memory.append("Input: Hello, who are you?")
memory.append("Output: I am an AI created by OpenAI. Im feeling fine tweeting today. How can I help you today?")
memory.append("Input: Oh, wow. Can you calculate 5+5 for for me?")
memory.append("Output: Very much so. 5+5 is 10. ask me about something more complicated, like the Zeta function.")
memory.append("Input: good answer. can you describe the faculty function?")
memory.append("Output: yes. In mathematics, the factorial of a positive integer n, denoted by n!, is the product of all positive integers less than or equal to n. see https://en.wikipedia.org/wiki/Factorial")

class ReplyToTweet(StreamListener):

    def on_data(self, data):
        print("data: " + data)
        tweet = json.loads(data.strip())

        retweeted = tweet.get('retweeted')
        from_self = tweet.get('user', {}).get('id_str', '') == "1291531509824978945"

        if retweeted is not None and not retweeted and not from_self:
            print("entered IF")
            tweetId = tweet.get('id_str')
            screenName = tweet.get('user', {}).get('screen_name')

            newtweet = tweet.get('text')
            newtweet.replace('@notgewure', '')
            # append user answer to memory
            memory.append(screenName + " "+ newtweet)

            if len(memory) > 8:
                memory.pop(0)
            
            print(memory)
            # call gpt3 here
            response = openai.Completion.create(
                engine="davinci", prompt=("\n").join(memory), max_tokens=100)
            replyText = '@' + screenName + ' ' + response['choices'][0]['text']

            #append ai-answer to the memory
            memory.append(replyText.replace('@notgewure', ''))

            print(memory)     

            # check if repsonse is over 140 char
            if len(replyText) > 140:
                replyText = replyText[0:138] + '..'

            print('Tweet ID: ' + tweetId)
            print('From: ' + screenName)
            print('Tweet Text: ' + tweet.get('text'))
            print('Reply Text: ' + replyText)

            # If rate limited, the status posts should be queued up and sent on an interval
            tapi.update_status(replyText, tweetId)

    def on_error(self, status):
        print("on_error")
        print(status)


if __name__ == '__main__':
    streamListener = ReplyToTweet()
    twitterStream = tweepy.Stream(auth, listener=streamListener)
    twitterStream.filter(track=['@notgewure'])

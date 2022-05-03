from flask import Flask, render_template, request
import matplotlib.pyplot as plt
import os
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import snscrape.modules.twitter as sntwitter
import re
import matplotlib
import datetime

app = Flask(__name__)

if __name__ == "__main__":
    app.run()

@app.route("/")
def home():
    return render_template('index.html')

matplotlib.use('agg')

nltk.download('vader_lexicon') #required for Sentiment Analysis

# class with main logic
class SentimentAnalysis:
 
    def __init__(self):
        self.tweets = []
        self.tweetContent = []
 
    # This function first connects to the Tweepy API using API keys
    def DownloadData(self, keyword, tweets, fromDate, toDate):

        # passing the keyword, no. of tweets to their respective variables
        kw = keyword
        tweets = int(tweets)

        # fetching the tweets from twitter for the past week
        fromDay = datetime.datetime.strptime(fromDate, '%Y-%m-%d')
        fromDay = fromDay.strftime('%Y-%m-%d')
        toDay = datetime.datetime.strptime(toDate, '%Y-%m-%d')
        toDay = toDay.strftime('%Y-%m-%d')

        for i, tweet in enumerate(sntwitter.TwitterSearchScraper(kw + ' lang:en since:' +  fromDay + ' until:' + toDay + ' -filter:links -filter:replies').get_items()):
            if i >= int(tweets):
                break
            self.tweets.append(tweet)

        # remove comment below to view tweets and their dates in terminal    

        # for tweet in self.tweets:
            # print(str(tweet.id) + "\t" + str(tweet.date) + "\t" + str(tweet.content) + "", end="\n")


        # iterating through tweets fetched, cleaning text and storing in tweetContent
        for tweet in self.tweets:
            self.tweetContent.append(self.cleanTxt(tweet.content))

        # initial reaction indicator variables
        compound = 0
        positive = 0
        negative = 0
        neutral = 0

        # Calculating sentiment score for each tweet
        for tweet in self.tweetContent:
            analyzer = SentimentIntensityAnalyzer().polarity_scores(tweet)
            neg = analyzer['neg']
            pos = analyzer['pos']
            comp = analyzer['compound']

            if (neg > pos):
                negative += 1 #increasing negative tweet count by 1
            elif (neg < pos):
                positive += 1 #increasing positive tweet count by 1
            elif (neg == pos):
                neutral += 1 #increasing neutral tweet count by 1

            # calculate sum to get average score later
            compound += comp


        # finding average of how people are reacting
        positive = self.percentage(positive, len(self.tweetContent))
        negative = self.percentage(negative, len(self.tweetContent))
        neutral = self.percentage(neutral, len(self.tweetContent))
 

        # finding average reaction
        compound = compound / len(self.tweetContent)
 
        if (compound <= -0.05):
            htmlcompound = "Negative :("
        elif (compound >= 0.05):
            htmlcompound = "Positive :)"
        else:
            htmlcompound = "Neutral :|"
 
        # call plotPieChart to generate pie chart visual
        self.plotPieChart(positive, negative, neutral, kw)

        return compound, htmlcompound, positive, negative, neutral, keyword, len(self.tweetContent), fromDate, toDate
 

    def cleanTxt(self, text):
        text = re.sub('@[A-Za-z0-9]+', '', text) #Removing @mentions
        text = re.sub('#', '', text) # Removing '#' hash tag
        text = re.sub('RT[\s]+', '', text) # Removing RT
        text = re.sub('https?:\/\/\S+', '', text) # Removing hyperlink
        return text
 

    # function to calculate percentage
    def percentage(self, part, whole):
        return float(format(100 * float(part) / float(whole), '0.2f'))
 

    # function which sets and plots the pie chart. The chart is saved in an img file every time the project is run.
    def plotPieChart(self, positive, negative, neutral, query):
        labels = ['Positive [' + str(positive) + '%]', 'Neutral [' + str(neutral) + '%]', 'Negative [' + str(negative) + '%]']
        sizes = [positive, neutral, negative]
        colors = ['yellowgreen', 'blue','red']
        patches, texts = plt.pie(sizes, colors=colors, startangle=90)
        plt.style.use('default')
        plt.legend(patches, labels, loc="best")
        plt.title("Sentiment Analysis Result for keyword = "+ query + "")
        plt.axis('equal')
        plt.tight_layout()

        # set path to save pie chart plot
        strFile = r"C:\Users\Clinton\Documents\GitHub\MajorProject\static\img\plots\plot1.png"
        if os.path.isfile(strFile):
            os.remove(strFile)  # Opt.: os.system("rm "+strFile)

        # save the pie chart plot
        plt.savefig(strFile)
        plt.show()
 
 

@app.route('/sentiment_logic', methods=['POST', 'GET'])
def sentiment_logic():

    # Get keyword to search and no. of tweets from html form enter by the user
    keyword = request.form.get('keyword')
    tweets = request.form.get('tweets')
    fromDate = request.form.get('fromDate')
    toDate = request.form.get('toDate')

    sa = SentimentAnalysis()

    # set variables which can be used in the jinja supported html page
    compound, htmlcompound, positive, negative, neutral, keyword1, tweets1, fromDay, toDay = sa.DownloadData(keyword, tweets, fromDate, toDate)

    return render_template('sentiment_analyzer.html', compound=compound, htmlcompound=htmlcompound, positive=positive, 
                            negative=negative, neutral=neutral, keyword=keyword1, tweets=tweets1, fromDate=fromDay, toDate=toDay)


@app.route('/visualize')
def visualize():
    return render_template('PieChart.html')
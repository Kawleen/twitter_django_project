from django.shortcuts import render
from django.http import HttpResponse
from analysis.forms import HomeForm
from django.views.generic import TemplateView
from analysis.models import Post

import re
import tweepy
from tweepy import OAuthHandler
from textblob import TextBlob
import pandas as pd
import collections
from itertools import groupby
from dateutil import relativedelta
from datetime import datetime
from urllib.request import urlopen
from bs4 import BeautifulSoup
import random

import matplotlib.pyplot as plt
import seaborn

class HomeView(TemplateView):
	template_name = 'analysis/tweet.html'

	def twitter_auth(self):
		consumer_key = 'qbsjhEePuzwRyMn6vnkxny4z2'
		consumer_secret = 'xZa5u0P0wlMcPl7XCAG7vpSgpxyPS65ss10GUDJCjRYiNocWPC'
		access_token = '152227079-Z20CdGCnNQgRA1KkeEuj8AUBFFqWTLcXTEnWR95D'
		access_token_secret = 'jEUBz4SlPiJPCZe2jPXU2xz0RqnG979KOkxWLyzs2R0dI'
		try:
        
			auth = OAuthHandler(consumer_key, consumer_secret)
			auth.set_access_token(access_token, access_token_secret)
			api = tweepy.API(auth,wait_on_rate_limit = True)
			return api
		except:
			print("Error: Authentication Failed")

	def search_trends(self,topic,api):
		result=[]

		for tweet in tweepy.Cursor(api.search,q=topic,lang='en').items(1000):
			result.append(tweet)

			text= []
			all_tweet = []
			hash_list_per_tweet = []
			username= []
			author_name = []
			retweet_count = []
			like = []
			user_description = []
			author_description=[]

			for tweets in result:
				txt = tweets.text
				if txt not in text:
					text.append(txt)
					all_tweet.append(tweets)
			        
					user = tweets.user.screen_name
					username.append(user)
			        
					re_count = tweets.retweet_count
					retweet_count.append(re_count)
			        
					likes = tweets.favorite_count
					like.append(likes)
			        
					user_desc = tweets.user.description
					user_description.append(user_desc)
			        
			        
					if tweets.retweeted == True:
						author_desc = tweets.author.description
						author_description.append(author_desc)
			            
						author = tweets.author.screenname
						author_name.append(author)
			        
					else:
						author_desc = ''
						author_description.append(author_desc)
			            
						author = ''
						author_name.append(author)
			        
					hashtg = tweets.entities['hashtags']
					if len(hashtg) > 0:
						hq = []
						for i in hashtg:
							h = i['text']
							hq.append(h)
						hsh_list = ','.join(hq)
						hash_list_per_tweet.append(hsh_list)
					else:
						hsh_list = ''
						hash_list_per_tweet.append(hsh_list)
	            
		dff = dict()
		dff['Username'] = username
		dff['Author_name'] = author_name
		dff['User_Description'] = user_description
		dff['Author_description'] = author_description
		dff['Tweet'] = text
		dff['Retweet_count'] = retweet_count
		dff['Likes'] = like
		dff['Hashtags'] = hash_list_per_tweet



		return dff



	def search_user(self,user,api):
		alltweets = []

		new_tweets = api.user_timeline(user,count=200)  
		alltweets.extend(new_tweets)
		oldest = alltweets[-1].id - 1

		while len(new_tweets) > 0:
			new_tweets = api.user_timeline(user,count=200,max_id=oldest)
			alltweets.extend(new_tweets)
			oldest = alltweets[-1].id - 1


		
		today = datetime.now().replace(microsecond=0)
		year_back = today - relativedelta.relativedelta(months=12)

		for tweets in alltweets:
			if tweets.created_at < year_back:
				alltweets.remove(tweets)


		my_tweets_id = []
		hash_list_per_tweet = []
		tweet_text_user = []

		for tweets in alltweets:
			id_str  = tweets.id_str
			my_tweets_id.append(id_str)

			tweet_text = tweets.text
			tweet_text_user.append(tweet_text)

    
			hashtg = tweets.entities['hashtags']
			if len(hashtg) > 0:
				hq = []
				for i in hashtg:
					h = i['text']
					hq.append(h.lower())
				hsh_list = ','.join(hq)
				hash_list_per_tweet.append(hsh_list)
			else:
				hsh_list = ''
				hash_list_per_tweet.append(hsh_list)



		my_dict = dict()
		my_dict['Tweet_ID'] = my_tweets_id
		my_dict['Hashtag'] = hash_list_per_tweet
		my_dict['Tweet'] = tweet_text_user

		return my_dict

	# def clean_tweet(self,tweet):
	# 	return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())
	
	# def get_tweet_sentiment(self,tweet):
	# 	analysis = TextBlob(HomeView.clean_tweet(self,tweet))
	# 	# set sentiment
	# 	if analysis.sentiment.polarity > 0:
	# 		return 'positive'
	# 	elif analysis.sentiment.polarity == 0:
	# 		return 'neutral'
	# 	else:
	# 		return 'negative'

	# def tweet_text_clean(self,tweet_text):
	# 	text = tweet_text
	# 	if text.startswith('RT'):
	# 		text = re.sub('RT','',text)
	# 	text = re.sub('@[A-Za-z0-9]+:','',text)
	# 	return text

	def to_dataframe(self,topic,user,api):


		# Search Trends Data Frame
		trends = HomeView.search_trends(self,topic,api)
		column_names = ['Username','User_Description','Author_name','Author_description','Tweet','Retweet_count','Likes','Hashtags']
		df_trends = pd.DataFrame(columns=column_names)
		new_df = pd.DataFrame(trends)
		df_trends = df_trends.append(new_df,ignore_index=True)
		df_trends = df_trends[['Username','User_Description','Tweet','Hashtags','Retweet_count','Likes','Author_name','Author_description']]

		hasht_trends = df_trends.loc[:,['Hashtags','Retweet_count']]

		h_list_trends = hasht_trends.Hashtags.tolist()
		c_list_trends = hasht_trends.Retweet_count.tolist()

		all_hashtags_trends = []

		for h,c in zip(h_list_trends,c_list_trends):
			if h != '':
				h_split = h.split(',')
				for a in h_split:
					if c == 0:
						all_hashtags_trends.append(a.lower())
					else:
						for n in range(c):
							all_hashtags_trends.append(a.lower())

		
		h_unique_trends = list(set(all_hashtags_trends))
		h_count_trends = [len(list(group)) for key,group in groupby(all_hashtags_trends)]
		hashtag_dict_trends = {hashtag:count for hashtag,count in zip(h_unique_trends,h_count_trends)}
		hashtag_dict_trends = sorted(hashtag_dict_trends.items(), key=lambda x:x[1],reverse=True)

		# End Trends DataFrame

		# Search User DataFrame

		user_dict = HomeView.search_user(self,user,api)
		columns_list_user = ['Tweet_ID','Hashtag','Tweet']
		df_user = pd.DataFrame(columns = columns_list_user)
		new_df_user = pd.DataFrame(user_dict)
		df_user = df_user.append(new_df_user,ignore_index=True)

		user_hash_list = df_user.Hashtag.tolist()


		all_user_hashtags_with_count = []
		for has in user_hash_list:
			h_l = has.split(',')
			for h in  h_l:
				all_user_hashtags_with_count.append(h)

		Set_of_user_hashtags_trending = set(all_user_hashtags_with_count)

        # End User Data Frame

        # Final Trends Search 
		final_trends_search = []

		for i in hashtag_dict_trends:
			if i[1] > 100:
				key = i[0]
				for j in Set_of_user_hashtags_trending:
					if key == j:
						final_trends_search.append(key)

		stopwords = ['algorithms','content','applications','internet']
		for trends in final_trends_search:
			if trends in stopwords:
				final_trends_search.remove(trends)

		return final_trends_search, df_user

	# def get_plot(self,df):
	# 	seaborn.set()
		
	# 	hashtags1 = []
	# 	for hs in df["Hashtags"]:
	# 	    if hs != '':
	# 	        hashtags1 += hs.split(" ")

	# 	fig=plt.figure(figsize=(12, 10))
        
	# 	x = collections.Counter(hashtags1)
	# 	l = range(len(x.keys()))
	# 	plt.bar(l, x.values(), align='center')
	# 	plt.xticks(l, x.keys(),rotation='vertical')
	# 	#plt.show()
	# 	fig.savefig('/home/kawaleenm/Documents/django_files/twitter/static/analysis.png')
	# 	return set(hashtags1)

	def get(self,request):
		form = HomeForm()
		# topic = Post.objects.all()
		# user = Post.objects.all()
		args = {'form':form}#,'topic':topic,'user':user}
		return render(request,self.template_name,args)

	def post(self,request):
		form = HomeForm(request.POST)
		if form.is_valid():
			# form.save()
			topic = form.cleaned_data['topic']
			user = form.cleaned_data['user']
		

			api = HomeView.twitter_auth(self)
			
			trending_topics, df_user = HomeView.to_dataframe(self,topic,user,api)
			
			most_trending = trending_topics[0]
			tweet_id_list = []

			for n in range(len(df_user)):
				cell_value = df_user.loc[n,'Hashtag']
				if most_trending in cell_value:
					tweet_id_list.append(df_user.loc[n,'Tweet_ID'])

			most_trending_tweet_id = []

			for id_str in tweet_id_list:
				try:
					id_and_text = []
					url1 = urlopen('https://mobile.twitter.com/allerint/status/'+id_str+'.html')
					bs_twitter = BeautifulSoup(url1.read(),'lxml')
					tweet_content = bs_twitter.find("td", {"class": "tweet-content"})
					tweet_text = tweet_content.find("div", {"class": "dir-ltr"}).get_text()
					tweet_external_link = tweet_content.find("a", {"class": "twitter_external_link dir-ltr tco-link"}).get_text()
					url_tweet_external_link_open = urlopen('https://'+tweet_external_link)
					id_and_text.append(id_str)
					id_and_text.append(tweet_text)
				except:
					for i in range(len(df_user)):
						tweet_text = df_user.loc[df_user.Tweet == id_str,'Tweet']
				try:
					bs_external_link = BeautifulSoup(url_tweet_external_link_open.read(),'lxml')
					external_link_text = bs_external_link.title.text
					external_link_description = bs_external_link.head.find('meta',{'property':'og:description'})['content']
					if bs_external_link.head.find('meta',{'name':'keywords'})['content'] in bs_external_link.head:
						external_link_keywords = bs3.head.find('meta',{'name':'keywords'})['content']
				
				except:
					external_link_description = tweet_text

				
				if most_trending in external_link_description:
					most_trending_tweet_id.append(id_and_text)

			tweet_id_final = random.choice(most_trending_tweet_id)

			final_tweet_text = tweet_id_final[1]
			final_tweet_text = re.sub('pic.twitter.*','',final_tweet_text)
			final_tweet_text = re.sub(r'\xa0',' ',final_tweet_text)
			final_tweet_text = re.sub(r'^\s{1,5}','',final_tweet_text)
			final_tweet_text = re.sub(r'\n','',final_tweet_text)
			final_tweet_text = re.sub(r'\s{1,5}$','',final_tweet_text)
			
			# post_tweet = api.update_status(final_tweet_text)



		args = {'topic': topic,'user':user,'most_trending':most_trending,'final_tweet_text':final_tweet_text,'trending_topics':trending_topics}

		return render(request,self.template_name,args)

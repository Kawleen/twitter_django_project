from django.db import models


# Create your models here.
 
class Post(models.Model):
	topic = models.CharField(max_length = 140)
	user = models.CharField(max_length = 140)#,blank=True)
	# image = models.ImageField(upload_to='Images',blank=True)
	

# class Result(models.Model):
# 	tweets = models.CharField(max_length = 140)
# 	hastags = models.CharField(max_length = 250)
# 	username = models.CharField(max_length = 100)
# 	sentiments = models.CharField(max_length = 20)	
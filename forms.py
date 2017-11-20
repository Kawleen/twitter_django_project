from django import forms
from analysis.models import Post
# from .views import trending_topic

# trending = views.HomeView

class HomeForm(forms.ModelForm):
	user = forms.CharField()
	topic = forms.CharField()
	


	class Meta:
		model = Post
		fields  = ('topic','user',)
	
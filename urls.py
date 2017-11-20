#from django.shortcuts.urls import url
from django.conf.urls import url,include
from analysis.views import HomeView
from django.conf.urls.static import static
from django.conf import settings

from . import views

urlpatterns = [
	url('^$',HomeView.as_view(),name='index')
	]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
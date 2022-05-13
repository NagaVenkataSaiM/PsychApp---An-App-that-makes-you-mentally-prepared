from django.urls import path,include
#now import the views.py file into this code
from . import views

urlpatterns=[
   path('',views.Login,name='login'),
   path('signup/',views.SignUP,name='signup'),
   path('getnewface/',views.newface,name='newface'),
   path('verifyface/',views.verifyface,name='verifyface'),
   path('dashboard/',views.dashboard,name='dashboard'),
   path('takeattendence/',views.takeattendence,name='takeattendence'),
   path('logout/',views.logout,name="logout"),
   path('download/',views.download,name="download"),
   path('allphotos/',views.allphotos,name="allphotos")
  ]
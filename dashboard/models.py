from django.db import models

# Create your models here.
class user(models.Model):
	email=models.CharField(max_length=30,null=False,blank=False,unique=True)
	password=models.CharField(max_length=20,null=False,blank=False)


class userface(models.Model):
	email=models.CharField(max_length=30,null=False,blank=False,unique=True)
	url=models.CharField(max_length=100,null=False,blank=False)

class studentface(models.Model):
	studentid=models.CharField(max_length=30,null=False,blank=False,unique=True)
	url=models.CharField(max_length=100,null=False,blank=False)

class attendence(models.Model):
	studentid=models.CharField(max_length=30,null=False,blank=False)
	date=models.CharField(max_length=30,null=False,blank=False)
	time=models.CharField(max_length=30,null=False,blank=False)
	status=models.CharField(max_length=30,null=False,blank=False)

class usermood(models.Model):
	email=models.CharField(max_length=30,null=False,blank=False)
	date=models.CharField(max_length=30,null=False,blank=False)
	time=models.CharField(max_length=30,null=False,blank=False)
	mood=models.CharField(max_length=30,null=False,blank=False)

class userphotos(models.Model):
	email=models.CharField(max_length=30,null=False,blank=False)
	url=models.CharField(max_length=100,null=False,blank=False)
	metadata=models.TextField(null=False)

	
from django.shortcuts import render,redirect
from django.http import HttpResponse
from .models import user,userface,studentface,attendence,usermood,userphotos
import requests
import csv
import datetime
from PIL import Image
import matplotlib.pyplot as plt
import psycopg2
import io
from io import BytesIO
from azure.storage.blob import  BlobServiceClient,ContentSettings
import json
import base64,urllib
from django.core.files.base import ContentFile
import numpy as np
import urllib.parse as urlparse
import os
from collections import Counter

# Create your views here.
def logout(request):
	if 'email' in request.session and 'faceconfirm' in request.session:
		del request.session['email']
	del request.session['faceconfirm']
	return redirect('login')
def Login(request):
	if 'email' in request.session and 'faceconfirm' in request.session:
		if request.session['faceconfirm']:
			return redirect('dashboard')
	if request.method=='POST':
		if request.POST.get('email') and request.POST.get('password'):
			try:
				User=user.objects.get(email=request.POST.get('email'))
			except:
				User=None
				User=user.objects.filter(email=request.POST.get('email'))
			if User:
				if User.password==request.POST.get('password'):
					request.session['email']=User.email
					request.session['faceconfirm']=False
					return redirect('verifyface')
	return render(request,'login.html')

def SignUP(request):
	if request.method=='POST':
		if request.POST.get('email') and request.POST.get('password') and request.POST.get('confirmpassword'):
			User=user()
			User.email=request.POST.get('email')
			if request.POST.get('password')==request.POST.get('confirmpassword'):
				User.password=request.POST.get('password')
				User.save()
				request.session['email']=User.email
				request.session['faceconfirm']=False
				return redirect('newface')
			else:
				HttpResponse("Confirmpassword is not same as your password.")
		else:
			HttpResponse("Please fill all the details.")
	return render(request,'signup.html')

def newface(request):
	if request.method=="POST":
		img_data=request.POST.get('photodata')
		print(img_data)
		format, imgstr = img_data.split(';base64,')
		ext = format.split('/')[-1]
		data = ContentFile(base64.b64decode(imgstr))
		email=request.session['email']
		email_list=email.split('@')
		file_name=email_list[0]
		connect_str=""
		blob_service_client = BlobServiceClient.from_connection_string(connect_str)
		container_name="myazurecontainer"
		blob_client = blob_service_client.get_blob_client(container=container_name, blob=file_name+'.png')
		blob_client.upload_blob(data)
		print(blob_client.url)
		Userface=userface()
		Userface.email=request.session['email']
		Userface.url=blob_client.url
		Userface.save()
		request.session['faceconfirm']=True
		return redirect('dashboard')
	return render(request,"newface.html")

def verifyface(request):
	if request.method=="POST":
		img_data=request.POST.get('photodata')
		format, imgstr = img_data.split(';base64,')
		ext = format.split('/')[-1]
		data = ContentFile(base64.b64decode(imgstr))
		sub_key=''
		Userface=userface.objects.get(email=request.session['email'])
		file1=Userface.url
		print(file1)
		response=requests.get(file1)
		img_data1=BytesIO(response.content)
		uri_base="https://facerecogbynvs.cognitiveservices.azure.com/"
		headers = {
		'Content-Type': 'application/octet-stream',
		'Ocp-Apim-Subscription-Key': sub_key,
		}
		headers2={
			'Content-Type': 'application/json',
			'Ocp-Apim-Subscription-Key': sub_key,
		}
		params = {
			'returnFaceId': 'true',
		}
		img_list=[]
		face_api1='/face/v1.0/detect'
		face_api2='/face/v1.0/verify'
		img_list.append(data)
		img_list.append(img_data1)
		faceid_list=[]
		try:
			for img in img_list:
				response=requests.post(uri_base+face_api1,
					data=img,
					headers=headers,
					params=params
					)
				parsed=response.json()
				print(parsed)
				json_str=parsed[0]
				faceid_list.append(json_str['faceId'])
		except Exception as e:
			print(e)
		print(faceid_list)
		data={"faceId1":faceid_list[0],"faceId2":faceid_list[1]}
		data_json=json.dumps(data)
		response=requests.post(uri_base + face_api2,data=data_json,headers=headers2)
		parsed=response.json()
		if parsed['isIdentical']:
			request.session['faceconfirm']=True
			return redirect('dashboard')
		else:
			del request.session['email']
			return HttpResponse('<h1>Face id doesnt match please try again.</h1>')
	return render(request,"newface.html")

def takeattendence(request):
	if 'email' in request.session and 'faceconfirm' in request.session:
		if request.session['faceconfirm']:
			if request.method=="POST":
				studentid=request.POST.get('studentid')
				if request.POST.get("action")=="upload":
					img_data=request.POST.get('photodata')
					format, imgstr = img_data.split(';base64,')
					ext = format.split('/')[-1]
					data = ContentFile(base64.b64decode(imgstr))
					file_name=studentid
					connect_str=""
					blob_service_client = BlobServiceClient.from_connection_string(connect_str)
					container_name="myazurecontainer"
					blob_client = blob_service_client.get_blob_client(container=container_name, blob=file_name+'.png')
					blob_client.upload_blob(data)
					print(blob_client.url)
					Studentface=studentface()
					Studentface.studentid=studentid
					Studentface.url=blob_client.url
					Studentface.save()
					return redirect('dashboard')
				if request.POST.get("action")=="take":
					img_data=request.POST.get('photodata')
					format, imgstr = img_data.split(';base64,')
					ext = format.split('/')[-1]
					data = ContentFile(base64.b64decode(imgstr))
					sub_key=''
					try:
						Studentface=studentface.objects.get(studentid=studentid)
					except:
						return HttpResponse("Student id not found!")
					file1=Studentface.url
					print(file1)
					response=requests.get(file1)
					img_data1=BytesIO(response.content)
					uri_base="https://facerecogbynvs.cognitiveservices.azure.com/"
					headers = {
					'Content-Type': 'application/octet-stream',
					'Ocp-Apim-Subscription-Key': sub_key,
					}
					headers2={
						'Content-Type': 'application/json',
						'Ocp-Apim-Subscription-Key': sub_key,
					}
					params = {
						'returnFaceId': 'true',
					}
					img_list=[]
					face_api1='/face/v1.0/detect'
					face_api2='/face/v1.0/verify'
					img_list.append(data)
					img_list.append(img_data1)
					faceid_list=[]
					try:
						for img in img_list:
							response=requests.post(uri_base+face_api1,
								data=img,
								headers=headers,
								params=params
								)
							parsed=response.json()
							print(parsed)
							json_str=parsed[0]
							faceid_list.append(json_str['faceId'])
					except Exception as e:
						print(e)
					print(faceid_list)
					data={"faceId1":faceid_list[0],"faceId2":faceid_list[1]}
					data_json=json.dumps(data)
					response=requests.post(uri_base + face_api2,data=data_json,headers=headers2)
					parsed=response.json()
					if parsed['isIdentical']:
						Attendence=attendence()
						Attendence.studentid=studentid
						x = datetime.datetime.now()
						str1 = x.strftime('%m/%d/%y-%H:%M:%S')
						y=str1.split("-")
						Attendence.date=y[0]
						Attendence.time=y[1]
						Attendence.status="present"
						Attendence.save()
						return redirect("takeattendence")
					else:
						return HttpResponse("Student Face not identical!")
			return render(request,"takeattendence.html")
		else:
			return redirect('verifyface')
	else:
		return redirect('login')

def download_csv(request, queryset):
	opts = queryset.model._meta
	model = queryset.model
	response = HttpResponse(content_type='text/csv')
	# force download.
	response['Content-Disposition'] = 'attachment;filename=export.csv'
	# the csv writer
	writer = csv.writer(response)
	field_names = [field.name for field in opts.fields]
	# Write a first row with header information
	writer.writerow(field_names)
	# Write data rows
	for obj in queryset:
	    writer.writerow([getattr(obj, field) for field in field_names])
	return response

def download(request):
	if 'email' in request.session and 'faceconfirm' in request.session:
		if request.session['faceconfirm']:
			data = download_csv(request, attendence.objects.all())
			return HttpResponse (data, content_type='text/csv')
		else:
			return redirect('verifyface')
	else:
		return redirect('login')

def dashboard(request):
	if 'email' in request.session and 'faceconfirm' in request.session:
		if request.session['faceconfirm']:
			if request.method=="POST":
				file_name=request.POST.get('imagename');
				file_name_list=file_name.split('.')
				img_data=request.POST.get('imagedata');
				format, imgstr = img_data.split(';base64,')
				ext = format.split('/')[-1]
				data = base64.b64decode(imgstr)
				uri_base="https://facerecogbynvs.cognitiveservices.azure.com/"
				sub_key=''
				headers = {
				'Content-Type': 'application/octet-stream',
				'Ocp-Apim-Subscription-Key': sub_key,
				}
				params = {
				'returnFaceId': 'true',
				'returnFaceAttributes': 'age,gender,emotion',
				}
				img_list=[]
				face_api1='/face/v1.0/detect'
				img_list.append(data)
				faceid_list=[]
				facelist_data={}
				try:
					for img in img_list:
						response=requests.post(uri_base+face_api1,
							data=img,
							headers=headers,
							params=params
							)
						parsed=response.json()
						print(parsed)
						json_str=parsed[0]
						faceid_list.append(json_str['faceId'])
						facelist_data[json_str['faceId']]=json_str['faceAttributes']
				except Exception as e:
					print(e)
				if len(faceid_list)>1:
					userface_url=userface(email=request.session['email'])
					uri_base="https://facerecogbynvs.cognitiveservices.azure.com/"
					response=requests.get(userface_url)
					img_data1=BytesIO(response.content)
					headers = {
					'Content-Type': 'application/octet-stream',
					'Ocp-Apim-Subscription-Key': sub_key,
					}
					params = {
					'returnFaceId': 'true',
					}
					img_list2=[]
					face_api1='/face/v1.0/detect'
					img_list2.append(img_data1)
					faceid_list2=[]
					try:
						for img in img_list:
							response=requests.post(uri_base+face_api1,
								data=img,
								headers=headers,
								params=params
								)
							parsed=response.json()
							print(parsed)
							json_str=parsed[0]
							faceid_list2.append(json_str['faceId'])
					except Exception as e:
						print(e)
					face_api2='/face/v1.0/findsimilars'
					headers2={
					'Content-Type': 'application/json',
					'Ocp-Apim-Subscription-Key': sub_key,
					}
					datax={"faceId":faceid_list2[0],"faceListId":faceid_list}
					try:
						response=requests.post(uri_base + face_api12,
						data=datax, 
						headers=headers2)
						parsed=response.json()
						print(parsed)
						json_str=parsed[0]
						final_faceid=json_str['persistedFaceId']
					except Exception as e:
						print(e)
				else:
					final_faceid=faceid_list[0]
					print(final_faceid)
				emotions=facelist_data[final_faceid]["emotion"]
				sort_by_value = dict(sorted(emotions.items(), key=lambda item: item[1]))
				top_emotions=list(sort_by_value.keys())
				print(top_emotions)
				connect_str=""
				blob_service_client = BlobServiceClient.from_connection_string(connect_str,logging_enable=True)
				container_name="myazurecontainer"
				blob_client = blob_service_client.get_blob_client(container=container_name, blob=file_name_list[0]+'.png')
				image_content_setting = ContentSettings(content_type='image/png')
				print("uploading...")
				print(type(data))
				blob_client.upload_blob(data,content_settings=image_content_setting)
				context = {
				'gender':facelist_data[final_faceid]["gender"],
				'age': facelist_data[final_faceid]["age"],
				'top_emotion': top_emotions[0],
				'img_url': blob_client.url
				}
				Userphotos=userphotos()
				Userphotos.email=request.session['email']
				Userphotos.url=blob_client.url
				len(str(facelist_data[final_faceid]))
				Userphotos.metadata=str(facelist_data[final_faceid])
				Userphotos.save()
				Usermood=usermood()
				Usermood.email=request.session['email']
				Usermood.mood=top_emotions[0]
				Usermood.save()
				return render(request,"viewphoto.html",context)
			"""url = urlparse.urlparse(os.environ['DATABASE_URL'])
			dbname = url.path[1:]
			user = url.username
			password = url.password
			host = url.hostname
			port = url.port"""
			mydb = psycopg2.connect(host="psychoappdb.postgres.database.azure.com",
									user="postgres",
									password="Nvsai222",
									database="psychoappdb")
			"""mydb = psycopg2.connect(
			dbname=dbname,
			user=user,
			password=password,
			host=host,
			port=port
			)"""
			mycursor = mydb.cursor()
			mycursor.execute("select mood from dashboard_usermood where email='"+request.session['email']+"';")
			result = mycursor.fetchall
			upref2 = []
			for i in mycursor:
				upref2.append(i[0])
			counter_object = Counter(upref2)
			keys = counter_object.keys()
			values=counter_object.values()
			num_values = len(keys)
			print(num_values)
			bar_plt = plt
			bar_plt.pie(values,labels = keys)
			bar_plt.legend(title="your Moods:")
			fig = bar_plt.gcf()
			buf = io.BytesIO()
			fig.savefig(buf, format='png', transparent=True)
			buf.seek(0)
			string = base64.b64encode(buf.read())
			uri1 = urllib.parse.quote(string)
			bar_plt.close()
			context = {
			'data1':uri1
			}
			return render(request,"dashboard.html",context)
		else:
			return redirect('verifyface')
	else:
		return redirect('login')

def allphotos(request):
	eve={}
	if not 'email' in request.session and not 'faceconfirm' in request.session:
		return redirect('login')
	if not request.session['faceconfirm']:
		return redirect('login')
	if request.method=="POST":
		try:
			data=userphotos.objects.get(url=request.POST.get('viewphoto'))
			facelist_data=eval(data.metadata)
			print(facelist_data)
			emotions=facelist_data["emotion"]
			sort_by_value = dict(sorted(emotions.items(), key=lambda item: item[1]))
			top_emotions=list(sort_by_value.keys())
			context = {
			'gender':facelist_data["gender"],
			'age': facelist_data["age"],
			'top_emotion': top_emotions[0],
			'img_url': data.url
			}
		except Exception as e:
			print(e)
			print("Got exception")
			context={}
		return render(request,"viewphoto.html",context)
	try:
		data=userphotos.objects.all()
	except:
		print("nodata")
		data={}
	eve={
	"event_d" : data
	}
	return render(request,"allphotos.html",eve)


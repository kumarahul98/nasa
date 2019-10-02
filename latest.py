import io
import os
import sys,json
from urllib import request
import googlemaps
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
# Imports the Google Cloud client library
from google.cloud import vision
from google.cloud.vision import types
class vis:
	lat,lng=0,0
	def __init__(self,img) :
		# Instantiates a client
		client = vision.ImageAnnotatorClient()
		# Loads the image into memory
		with io.open(img, 'rb') as image_file:
			content = image_file.read()

		image = types.Image(content=content)

		# Performs label detection on the image file
		response = client.label_detection(image=image)
		labels = response.label_annotations
		print("label\t\t:\tConfidense")
		for label in labels :
			if(label.description=="wildfire" or  label.description=='forest' or label.description=='heat' or label.description=='tree'):
				print(label.description,end="\t\t:\t")
				print(label.score*100,"%")
		
		
		
	def get_exif_data(self,image):
		"""Returns a dictionary from the exif data of an PIL Image item. Also converts the GPS Tags"""
		exif_data = {}
		info = image._getexif()
		if info:
			for tag, value in info.items():
				decoded = TAGS.get(tag, tag)
				if decoded == "GPSInfo":
					gps_data = {}
					for gps_tag in value:
						sub_decoded = GPSTAGS.get(gps_tag, gps_tag)
						gps_data[sub_decoded] = value[gps_tag]

			exif_data[decoded] = gps_data
		else:
			exif_data[decoded] = value

		return exif_data
		
		
	def _convert_to_degress(self,value):
		"""Helper function to convert the GPS coordinates stored in the EXIF to degress in float format"""
		deg_num, deg_denom = value[0]
		d = float(deg_num) / float(deg_denom)

		min_num, min_denom = value[1]
		m = float(min_num) / float(min_denom)
		
		sec_num, sec_denom = value[2]
		s = float(sec_num) / float(sec_denom)
    
		return d + (m / 60.0) + (s / 3600.0)
		
	def get_lat_lon(self,exif_data):
		lat = None
		lon = None

		if "GPSInfo" in exif_data:		
			gps_info = exif_data["GPSInfo"]
			gps_latitude = gps_info.get("GPSLatitude")
			gps_latitude_ref = gps_info.get('GPSLatitudeRef')
			gps_longitude = gps_info.get('GPSLongitude')
			gps_longitude_ref = gps_info.get('GPSLongitudeRef')

		if gps_latitude and gps_latitude_ref and gps_longitude and gps_longitude_ref:
			lat = self._convert_to_degress(gps_latitude)
			if gps_latitude_ref != "N":                     
				lat *= -1

			lon = self._convert_to_degress(gps_longitude)
			if gps_longitude_ref != "E":
				lon *= -1

			self.lat,self.lng = lat, lon
		if not (self.lat) : exit(0)
		print("latitude and longitude : ",self.lat,self.lng)
		gmaps = googlemaps.Client(key="YOUR API_KEY")

		address_list = gmaps.reverse_geocode((self.lat,self. lng))
		with open('/root/nasa/geo.json', 'w') as outfile:
			json.dump(address_list, outfile)
		a=address_list[0]["formatted_address"]
		print("Address : ",a[6:])
		
		
f = open('1.jpg', 'wb')
f.write(request.urlopen("https://s3.ap-south-1.amazonaws.com/kumarahul/w.jpg").read())
f.close()
o=vis("1.jpg")
image = Image.open("1.jpg")

exif_data=o.get_exif_data(image)
o.get_lat_lon(exif_data)

 


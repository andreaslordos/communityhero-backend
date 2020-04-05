from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.template import loader
from rest_framework.decorators import api_view
from rest_framework.response import Response
from backend.models import *
from backend.serializers import *
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
import numpy as np
import random
import names
import json
import decimal
import nltk

from math import radians, cos, sin, asin, sqrt 
def distance(lat1, lon1, lat2, lon2): 
	  
	# The math module contains a function named 
	# radians which converts from degrees to radians. 
	lon1 = radians(lon1) 
	lon2 = radians(lon2) 
	lat1 = radians(lat1) 
	lat2 = radians(lat2) 
	   
	# Haversine formula  
	dlon = lon2 - lon1  
	dlat = lat2 - lat1 
	a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
  
	c = 2 * asin(sqrt(a))  
	 
	# Radius of earth in kilometers. Use 3956 for miles 
	r = 6371
	   
	# calculate the result 
	return(c * r) 

@api_view(['GET'])
def category_collection(request):
	if request.method == 'GET':
		posts = Category.objects.all()
		serializer = CategorySerializer(posts, many=True)
		return Response(serializer.data)


@api_view(['GET'])
def category_element(request, pk):
	try:
		post = Category.objects.get(CategoryID=pk)
	except Category.DoesNotExist:
		return HttpResponse(status=404)

	if request.method == 'GET':
		serializer = CategorySerializer(post)
		return Response(serializer.data)


@api_view(['GET'])
def producttype_collection(request):
	if request.method == 'GET':
		posts = ProductType.objects.all()
		serializer = ProductTypeSerializer(posts, many=True)
		return Response(serializer.data)

@api_view(['GET'])
def producttype_name(request, name):
	if request.method == 'GET':
		posts = ProductType.objects.filter(Q(ProductTypeName__icontains=name) | Q(CategoryID__CategoryName__icontains=name))
		serializer = ProductTypeSerializer(posts, many=True)
		return Response(serializer.data)

@api_view(['GET'])
def producttype_element(request, pk):
	try:
		post = ProductType.objects.get(ProductTypeID=pk)
	except ProductType.DoesNotExist:
		return HttpResponse(status=404)

	if request.method == 'GET':
		serializer = ProductTypeSerializer(post)
		return Response(serializer.data)

@api_view(['GET'])
def product_name(request, name):
	if request.method == 'GET':
		posts = Product.objects.filter(Q(ProductName__icontains=name) | Q(ProductTypeID__ProductTypeName__icontains=name))
		serializer = ProductSerializer(posts, many=True)
		return Response(serializer.data)

@api_view(['GET'])
def product_barcode(request):
	barcode = request.query_params['barcode']
	try:
		post = Product.objects.get(ProductBarcode=barcode)
	except Product.DoesNotExist:
		return HttpResponse(status=404)

	if request.method == 'GET':
		serializer = ProductSerializer(post)
		return Response(serializer.data)

@api_view(['GET'])
def product_element(request, pk):
	try:
		post = Product.objects.get(ProductID=pk)
	except ProductType.DoesNotExist:
		return HttpResponse(status=404)

	if request.method == 'GET':
		serializer = ProductSerializer(post)
		return Response(serializer.data)

@api_view(['GET'])
def user_radius(request):
	if request.method == 'GET':
		lat = float(request.query_params['lat'])
		lng = float(request.query_params['lng'])
		rad = float(request.query_params['rad'])
		# TODO: Implement direct distance from DB
		users = PastOrder.objects.filter(OrderDelivered=False)
		result_users = []
		for user in users:
			if distance(lat, lng, user.UserID.Userlatitude, user.UserID.Userlongitude)<rad:
				result_users.append(user)

		serializer = OrderSerializer(result_users, many=True)
		return Response(serializer.data)

@api_view(['GET'])
def order_by_id(request):
	if request.method == 'GET':
		oid = int(request.query_params['orderId'])
		orders = OrderItems.objects.filter(OrderID=oid)
		serializer = OrderItemSerializer(orders, many=True)
		return Response(serializer.data)

@api_view(['GET'])
def create_data(request):
	if request.method == 'GET':
		probability = 0.8
		mean_price = 4
		stdev = 1
		shops = Shop.objects.filter(ShopTypeID=1)
		products = Product.objects.all()
		for shop in shops:
			for product in products:
				if product.ProductTypeID.ProductTypeID in [8,9,10,37]:
					print(shop, product)
					if random.random() < probability:
						print('saving')
						price = Price(ShopID=shop, ProductID=product, Price=np.random.normal(mean_price, stdev))
						price.save()

		num_users = 100

		for j in range(num_users):
			phonenumber = '99' + ''.join(random.choice("0123456789") for _ in range(6))
			username = names.get_first_name()
			print(phonenumber, username)
			user = User(Userlatitude=np.random.normal(35.15938300, 0.1), Userlongitude=np.random.normal(33.39632500, 0.1), Userphonenumber=phonenumber, UserName=username)
			user.save()

		users = User.objects.all()
		for user in users:
			if len(PastOrder.objects.filter(UserID=user.UserID, OrderDelivered=False))>0:
				continue
			shop = random.choice(Shop.objects.all())
			available_items = Price.objects.all().filter(ShopID=shop.ShopID)
			num_of_items = random.randint(1, len(available_items)-1)

			items = random.sample(list(available_items), num_of_items)
			
			order = PastOrder(UserID=user, OrderDelivered=False)
			order.save()
			for item in items:
				order_item = OrderItems(OrderID=order, PriceID=item, Quantity=random.randint(1, 5))
				order_item.save()
			
		
		return Response("Done")


@api_view(['POST'])
def deliver_order(request, order):
	if request.method == 'POST':
		print(request.data)
		obj = PastOrder.objects.get(OrderID=order)
		obj.OrderDelivered = True
		obj.save()
		return Response("Done")

@api_view(['POST'])
def sms_order(request):
	if request.method == 'POST':
		names = ProductType.objects.all()
		b = request.data
		print(b["from"])
		resp = {}
		print(b["content"])
		try:
			user = User.objects.get(Userphonenumber=b['from'])
		except User.DoesNotExist:
			resp["status"]="user_error"
			return JsonResponse(resp)
		items = []
		totalCost = 0
		for product in b["content"].split('\n'):
			product = product.lower()
			mindist = 100000000000
			for p in Product.objects.all():
				if decimal.Decimal(nltk.jaccard_distance(set(nltk.ngrams(product, n=3)), set(nltk.ngrams(p.ProductTypeID.ProductTypeName.lower(), n=3)).union(set(nltk.ngrams(p.ProductName.lower(), n=3))).union(set(nltk.ngrams(p.ProductBrandID.BrandName.lower(), n=3)))))/(p.ProductWeight) < mindist:
					mindist = decimal.Decimal(nltk.jaccard_distance(set(nltk.ngrams(product, n=3)), set(nltk.ngrams(p.ProductTypeID.ProductTypeName.lower(), n=3)).union(set(nltk.ngrams(p.ProductName.lower(), n=3))).union(set(nltk.ngrams(p.ProductBrandID.BrandName.lower(), n=3)))))/p.ProductWeight
					mindistproduct = p

			print(mindistproduct.ProductName, mindist)
			print(Price.objects.filter(ProductID=mindistproduct).order_by('Price')[0])
			# TODO: Return cheapest/closest combination
			if mindist<0.95:
				items.append(mindistproduct.ProductBrandID.BrandName + ' ' + mindistproduct.ProductName)
				price = Price.objects.filter(ProductID=mindistproduct).order_by('Price')[0]
				totalCost+=price.Price
				item = ShoppingItem(UserID=user, PriceID=price, Quantity=1)
				item.save()
			else:
				items.append('not found')
			
		resp = {}
		resp["items"] = items
		resp["cost"] = totalCost
		resp["status"]="ok"
		print(resp)
		return JsonResponse(resp)

@api_view(['POST'])
def sms_register(request):
	if request.method == 'POST':
		b = json.loads(request.body.decode('utf-8'))
		u = User(Userphonenumber=b["from"], Userlatitude=float(b['lat']), Userlongitude=float(b['lng']))
		u.save()
		return Response("Done")

@api_view(['GET'])
def download_products(request, shop):
	# Create the HttpResponse object with the appropriate CSV header.
	response = HttpResponse(content_type='text/csv')
	response['Content-Disposition'] = 'attachment; filename="somefilename.csv"'
	b = Price.objects.filter(ShopID=shop)
	
	t = loader.get_template('csv.txt')
	c = {'data': b}
	response.write(t.render(c))
	return response

@api_view(['GET'])
def get_user_by_phone(request, phone):
	try:
		post = User.objects.get(Userphonenumber=phone)
	except User.DoesNotExist:
		return HttpResponse(status=404)
	return HttpResponse(post.UserName)

from django.shortcuts import render
from sodapy import Socrata
import pandas as pd

def home(request):
	client = Socrata('www.datos.gov.co', 'k25EB69oNekTcnbXvrgklJRQn')
	capturas = client.get('qa6k-wzms', limit=1000)
	data_frame = pd.DataFrame(capturas)
	json = data_frame.to_json(orient='records')

	return render(request, 'home/index.html', {'data_frame': data_frame, 'json': json})

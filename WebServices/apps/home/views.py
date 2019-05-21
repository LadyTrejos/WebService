from django.shortcuts import render
from sodapy import Socrata
import pandas as pd
from bokeh.plotting import figure
from bokeh.embed import components

def home(request):
	# Obtaining the dataset
	client = Socrata('www.datos.gov.co', 'k25EB69oNekTcnbXvrgklJRQn')
	capturas = client.get('qa6k-wzms', limit=1000)
	
	# Creating the data frame and the json for the boostrap table
	data_frame = pd.DataFrame(capturas)
	json = data_frame.to_json(orient='records')

	# Example of bokeh figure
	x = [1, 2, 3, 4, 5]
	y = [1, 2, 3, 4, 5]

	plot = figure(title='Line Graph', x_axis_label='X', y_axis_label='Y', plot_width=400, plot_height=400)
	plot.line(x, y, line_width=2)

	script, div = components(plot)

	return render(request, 'home/index.html', 
		{
		'data_frame': data_frame, 
		'json': json, 
		'bokehScript': script,
		'bokehDiv': div
		})

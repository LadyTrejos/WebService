from django.shortcuts import render
from sodapy import Socrata
import pandas as pd
from bokeh.models import ColumnDataSource
from bokeh.layouts import row, column
from bokeh.models import Select
from bokeh.palettes import BuGn
from bokeh.transform import factor_cmap
from bokeh.plotting import figure
from bokeh.embed import components

def update_plot():
	pass

def update(attr, old, new):
	layout.children[1] = update_plot()

def home(request):
	# Obtaining the dataset
	client = Socrata('www.datos.gov.co', 'k25EB69oNekTcnbXvrgklJRQn')
	capturas = client.get('qa6k-wzms', limit=1000)
	
	# Creating the data frame and the json for the boostrap table
	capturas = pd.DataFrame(capturas)
	
	# Changing the column names
	capturas.columns = ['Barrio', 'Codigo_DANE',  'Cantidad', 'Clase_de_Empleado', 'Clase_de_Sitio', 'Dia', 
	'Delito', 'Departamento', 'Edad', 'Escolaridad', 'Estado_Civil', 'Fecha', 'Hora', 'Municipio', 
	'Profesion', 'Genero', 'Zona']
	
	# Reordering the columns
	ordered_columns = ['Fecha', 'Dia', 'Hora', 'Departamento', 'Municipio', 'Barrio', 'Zona', 'Clase_de_Sitio', 
	'Delito', 'Genero', 'Edad', 'Estado_Civil', 'Clase_de_Empleado', 'Profesion', 'Escolaridad', 'Codigo_DANE', 
	'Cantidad']
	capturas = capturas[ordered_columns]

	# Adjusting the columns Fecha and Hora (Cleanning)
	capturas.Fecha = capturas.Fecha.str[0:10]
	capturas.Hora = capturas.Hora.str[11:]
	capturas.Hora = capturas.Hora.str[0:5]

	# Eliminating the columns with many NAN values
	capturas.drop(['Profesion', 'Escolaridad'], axis=1, inplace=True)
	
	# Extracting the records
	json = capturas.to_json(orient='records')

	# Creating the select widget for change the displayed plot
	select = Select(title='Escoge una gráfica', value='barras', 
		options=['barras', 'histograma'])
	select.on_change('value', update)

	# Creating group generos for the categorical plot
	generos = pd.DataFrame(capturas.groupby('Genero')['Cantidad'].count())

	# Creating the source data for Bokeh
	source = ColumnDataSource(generos)
	lista_generos = source.data['Genero'].tolist()

	plot = figure(x_range=lista_generos, title='Cantidad de Delitos por Genero', x_axis_label='Generos', 
		y_axis_label='Cantidad', plot_height=400)
	color_map = factor_cmap(field_name='Genero', palette=BuGn[4], factors=lista_generos)
	plot.vbar(x='Genero', top='Cantidad', source=source, width=0.4, color=color_map)


	# Creating the layout to be displayed
	controles = column([select], width=200)
	layout = row(controles, plot)

	script, div = components(layout)

	return render(request, 'home/index.html', 
		{
		'data_frame': capturas, 
		'json': json, 
		'bokehScript': script,
		'bokehDiv': div
		})

from django.shortcuts import render
from sodapy import Socrata
import numpy as np
import pandas as pd
from bokeh.models import ColumnDataSource, CustomJS,Select
from bokeh.layouts import row, column
from bokeh.palettes import BuGn
from bokeh.transform import factor_cmap
from bokeh.plotting import figure
from bokeh.embed import components


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

	# Adjusting the data types
	capturas.Edad = capturas.Edad.astype('int')
	
	# Extracting the records
	json = capturas.to_json(orient='records')

	# Creating group generos for the categorical plot
	generos = pd.DataFrame(capturas.groupby('Genero')['Cantidad'].count())

	# Creating the source data for Bokeh
	source = ColumnDataSource(generos)
	lista_generos = source.data['Genero'].tolist()

	# Creating the genres plot (Categorical)
	catGeneros = figure(x_range=lista_generos, title='Cantidad de Delitos por Genero', x_axis_label='Generos', 
		y_axis_label='Cantidad', plot_height=400)
	color_map = factor_cmap(field_name='Genero', palette=BuGn[4], factors=lista_generos)
	catGeneros.vbar(x='Genero', top='Cantidad', source=source, width=0.4, color=color_map)

	# Creating the histogram plot for Edad
	hist, edges = np.histogram(capturas.Edad.dropna(), bins=10)

	histEdad = figure(title='Distribución de edades', x_axis_label='Edades', y_axis_label='Cantidad', 
		plot_height=400, background_fill_color='#fafafa')
	histEdad.quad(top=hist, bottom=0, left=edges[:-1], right=edges[1:], color='navy', line_color='white', alpha=0.6)

	# Creating the select widget for change the displayed plot
	select = Select(title='Escoge una gráfica', value='barras', 
		options=['barras', 'histograma'])

	# Creating the layout to be displayed
	controles = column([select], width=200)
	layout = row(controles, catGeneros)

	# Creating the CustomJS function to update the plot
	update = CustomJS(args=dict(layout=layout, catGeneros=catGeneros, histEdad=histEdad), code="""
			if (cb_obj.value == 'barras') {
				layout.children = [layout.children[0], catGeneros];
			}
			if (cb_obj.value == 'histograma') {
				layout.children = [layout.children[0], histEdad]
			}
		""")

	# Adding the callback method
	select.js_on_change('value', update)

	script, div = components(layout)

	return render(request, 'home/index.html', 
		{
		'data_frame': capturas, 
		'json': json, 
		'bokehScript': script,
		'bokehDiv': div
		})

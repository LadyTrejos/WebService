from django.shortcuts import render
from sodapy import Socrata
import numpy as np
import pandas as pd
from bokeh.models import ColumnDataSource, CustomJS,Select, FactorRange
from bokeh.layouts import row, column
from bokeh.palettes import BuGn
from bokeh.transform import factor_cmap
from bokeh.plotting import figure
from bokeh.embed import components

def categorical_plot(df, colname, title, xlabel, num_cats, x_orientation):
	# Creating group for the categorical plot
	cat_ranges = df[colname].unique()  # For the x_range and the color map
	categories = pd.DataFrame(df.groupby([colname])['Cantidad'].count())

	# Creating the source data for Bokeh
	source = ColumnDataSource(categories)

	# Creating the genres plot (Categorical)
	catPlot = figure(x_range=cat_ranges, title=title, x_axis_label=xlabel, 
		y_axis_label='Cantidad', plot_height=400, plot_width=600, background_fill_color='#fafafa')
	color_map = factor_cmap(field_name=colname, palette=BuGn[num_cats], factors=cat_ranges)
	catPlot.vbar(x=colname, top='Cantidad', source=source, width=0.4, color=color_map)
	catPlot.y_range.start = 0
	catPlot.xaxis.major_label_orientation = x_orientation

	return catPlot


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

	# Creating the categorical plots

	catGeneros = categorical_plot(capturas, 'Genero', 'Cantidad de Delitos por Genero', 'Generos', 3, 0)
	catZona = categorical_plot(capturas, 'Zona', 'Cantidad de Delitos por Zona', 'Zona', 3, 0)
	catDepartamento = categorical_plot(capturas, 'Departamento', 'Cantidad de Delitos por Departamento', 
		'Departamento', 7, 1)
	catEstadoCivil = categorical_plot(capturas, 'Estado_Civil', 'Cantidad de Delitos por Estado Civil', 
		'Estado Civil', 4, 0)
	catEmpleado = categorical_plot(capturas, 'Clase_de_Empleado', 'Cantidad de Delitos por Clase de Empleado', 
		'Clase de Empleado', 6, 1)
	catClaseSitio = categorical_plot(capturas, 'Clase_de_Sitio', 'Cantidad de Delitos por Clase de Sitio', 
		'Clase de Sitio', 8, 1)
	catDelito = categorical_plot(capturas, 'Delito', 'Cantidad de Delitos por Delito', 'Delito', 7, 1)

	# Creating the histogram plot for Edad
	hist, edges = np.histogram(capturas.Edad.dropna(), bins=10)

	histEdad = figure(title='Distribución de edades', x_axis_label='Edades', y_axis_label='Cantidad', 
		plot_height=400, plot_width=600, background_fill_color='#fafafa')
	histEdad.quad(top=hist, bottom=0, left=edges[:-1], right=edges[1:], color='navy', line_color='white', alpha=0.6)
	histEdad.y_range.start = 0

	# Creating the select widget for change the displayed plot
	options = ['genero', 'empleado', 'estado civil', 'zona', 'departamento', 'delito', 'sitio', 'edad']
	select = Select(title='Escoge una variable', value='barras', options=options, margin=30, 
		css_classes=['select'])

	# Creating the layout to be displayed
	controles = column([select], width=200)
	layout = row(controles, catGeneros)

	# Creating the CustomJS function to update the plot
	update = CustomJS(args=dict(layout=layout, catGeneros=catGeneros, catEmpleado=catEmpleado, 
	catEstadoCivil=catEstadoCivil, catZona=catZona, catDepartamento=catDepartamento, 
	catDelito=catDelito, catClaseSitio=catClaseSitio, histEdad=histEdad), code="""
			if (cb_obj.value == 'genero') {
				layout.children = [layout.children[0], catGeneros];
			}
			if (cb_obj.value == 'empleado') {
				layout.children = [layout.children[0], catEmpleado];
			}
			if (cb_obj.value == 'estado civil') {
				layout.children = [layout.children[0], catEstadoCivil];
			}
			if (cb_obj.value == 'zona') {
				layout.children = [layout.children[0], catZona];
			}
			if (cb_obj.value == 'departamento') {
				layout.children = [layout.children[0], catDepartamento];
			}
			if (cb_obj.value == 'delito') {
				layout.children = [layout.children[0], catDelito];
			}
			if (cb_obj.value == 'sitio') {
				layout.children = [layout.children[0], catSitio];
			}
			if (cb_obj.value == 'edad') {
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

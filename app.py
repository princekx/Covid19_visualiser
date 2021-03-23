from flask import Flask, render_template
from bokeh.embed import components
from bokeh.resources import INLINE
import pandas as pd
import geopandas as gpd
import json
from bokeh.io import output_file, show, output_notebook, export_png
from bokeh.models import ColumnDataSource, GeoJSONDataSource, LinearColorMapper, ColorBar
from bokeh.plotting import figure
from bokeh.palettes import brewer

app = Flask(__name__)



def get_gdf():
    shapefile = 'shapefiles/ne_110m_admin_0_countries_lakes.shp'
    #Read shapefile using Geopandas
    gdf = gpd.read_file(shapefile)[['ADMIN', 'ADM0_A3', 'geometry']]
    #Rename columns.
    gdf.columns = ['country', 'country_code', 'geometry']
    gdf = gdf.drop(gdf.index[159])
    return gdf

def get_data():
    url = 'https://covid19.who.int/WHO-COVID-19-global-data.csv'
    df = pd.read_csv(url, encoding='utf-8-sig', engine='python')
    df.columns = df.columns.str.strip()
    totals = df.groupby(['Country']).sum()
    return totals

def bokeh_plot_map(column=None, title=''):
    print('Hello')
    gdf = get_gdf()
    # print(gdf)
    data = get_data()
    # print(data)
    # Merge dataframes gdf and data.
    merged = gdf.merge(data, left_on='country', right_on='Country')
    print(merged)

    # Read data to json.
    merged_json = json.loads(merged.to_json())
    # Convert to String like object.
    json_data = json.dumps(merged_json)
    #Input GeoJSON source that contains features for plotting.
    geosource = GeoJSONDataSource(geojson = json_data)#Define a sequential multi-hue color palette.
    palette = brewer['YlGnBu'][8]#Reverse color order so that dark blue is highest obesity.
    palette = palette[::-1]#Instantiate LinearColorMapper that linearly maps numbers in a range, into a sequence of colors.
    color_mapper = LinearColorMapper(palette = palette, low = 0, high = 400000)#Define custom tick labels for color bar.
    # Create color bar.
    color_bar = ColorBar(color_mapper=color_mapper, label_standoff=8, width=500, height=20,
                         border_line_color=None, location=(0, 0), orientation='horizontal')
    TOOLS = "pan,wheel_zoom,reset,hover,save"
    p = figure(title = 'Share of adults who are obese, 2016', tools=TOOLS,
               plot_height = 500 , plot_width = 950)
    #p.xgrid.grid_line_color = None
    #p.ygrid.grid_line_color = None#Add patch renderer to figure.
    p.patches('xs','ys', source = geosource, fill_color = {'field' :'Cumulative_deaths', 'transform' : color_mapper},
              line_color = 'black', line_width = 0.25, fill_alpha = 1)#Specify figure layout.
    p.add_layout(color_bar, 'below')#Display figure inline in Jupyter Notebook.
    return p

@app.route('/')

def bokeh():
    fig = bokeh_plot_map()
    print(fig)
    # grab the static resources
    js_resources = INLINE.render_js()
    css_resources = INLINE.render_css()

    # render template
    script, div = components(fig)
    html = render_template(
        'index.html',
        plot_script=script,
        plot_div=div,
        js_resources=js_resources,
        css_resources=css_resources,
    )
    return html

if __name__ == '__main__':
    app.run(debug=True)
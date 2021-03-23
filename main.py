import datetime
import json
import sys

import geopandas as gpd
import pandas as pd
from bokeh.io import show, curdoc
from bokeh.layouts import column
from bokeh.models import GeoJSONDataSource, LinearColorMapper, \
    ColorBar, DateSlider, Column, Button, Row
from bokeh.models.widgets import Panel, Tabs
from bokeh.palettes import brewer
from bokeh.plotting import figure


def get_gdf_TM_WORLD_BORDERS():
    shapefile = 'shapefiles/TM_WORLD_BORDERS-0.3.shp'
    # Read shapefile using Geopandas
    gdf = gpd.read_file(shapefile)[['NAME', 'ISO2', 'geometry']]
    # Rename columns.
    gdf.columns = ['country', 'country_code', 'geometry']
    print(gdf)
    gdf = gdf.drop(gdf.index[159])
    return gdf


def get_gdf():
    shapefile = 'shapefiles/ne_110m_admin_0_countries.shp'
    # Read shapefile using Geopandas
    gdf = gpd.read_file(shapefile)[['ADMIN', 'ISO_A2', 'geometry']]
    # Rename columns.
    gdf.columns = ['Country', 'Country_code', 'geometry']
    # print(gdf)
    gdf = gdf.drop(gdf.index[159])
    return gdf


def get_highres_gdf():
    shapefile = 'shapefiles/99bfd9e7-bb42-4728-87b5-07f8c8ac631c2020328-1-1vef4ev.lu5nk.shp'
    # Read shapefile using Geopandas
    gdf = gpd.read_file(shapefile)  # [['ADMIN', 'ISO_A2', 'geometry']]
    gdf.columns = ['OBJECTID', 'Country', 'geometry']
    # print(gdf)
    # gdf = gdf.drop(gdf.index[159])
    return gdf


def get_data_date_ranges():
    url = 'https://covid19.who.int/WHO-COVID-19-global-data.csv'
    df = pd.read_csv(url, encoding='utf-8-sig', engine='python')
    df.columns = df.columns.str.strip()
    totals = df.groupby(['Country_code']).sum()
    first = df.groupby(['Country_code']).first()
    latest = df.groupby(['Country_code']).last()
    first = first['Date_reported']
    last = latest['Date_reported']
    datetime_min = min([datetime.date(*map(int, ff.split('-'))) for ff in first])
    datetime_max = max([datetime.date(*map(int, ff.split('-'))) for ff in last])
    print(datetime_min, datetime_max)
    return datetime_min, datetime_max


def get_all_data_of_date(date):
    url = 'https://covid19.who.int/WHO-COVID-19-global-data.csv'
    df = pd.read_csv(url, encoding='utf-8-sig', engine='python')
    # print(df.columns)
    df.columns = df.columns.str.strip()
    df = df.loc[df['Date_reported'] == date.strftime('%Y-%m-%d')]
    return df


def bokeh_plot_map():
    geosource
    TOOLTIPS = [("Country", "@Country_code")]
    TOOLTIPS.extend([(tab_name, "@" + tab_name) for tab_name in all_columns])
    # print(TOOLTIPS)

    plot = figure(title='COVID-19 Statistics', tools=TOOLS,
                  tooltips=TOOLTIPS, plot_height=600, plot_width=1200)

    # Define a sequential multi-hue color palette.
    palette = brewer['YlOrRd'][8]
    # Reverse color order so that dark blue is highest obesity.
    palette = palette[::-1]
    # Instantiate LinearColorMapper that linearly maps numbers in a range, into a sequence of colors.
    color_mapper = LinearColorMapper(palette=palette, nan_color='#d9d9d9', low=0, high=3000)
    # Define custom tick labels for color bar.
    # Create color bar.
    color_bar = ColorBar(color_mapper=color_mapper, label_standoff=8, width=500, height=20,
                         border_line_color=None, location=(0, 0), orientation='horizontal')

    # p.xgrid.grid_line_color = None
    # p.ygrid.grid_line_color = None#Add patch renderer to figure.
    plot.patches('xs', 'ys', source=gdf_source, fill_color='grey',
                 line_color='black', line_width=0.5, fill_alpha=1, line_alpha=0.5)  # Specify figure layout.

    plot.patches('xs', 'ys', source=geosource, fill_color={'field': 'New_cases', 'transform': color_mapper},
                 line_color='black', line_width=0.5, fill_alpha=1, line_alpha=0.5)  # Specify figure layout.

    plot.add_layout(color_bar, 'below')  # Display figure inline in Jupyter Notebook.
    return plot


def make_json_data_for_date(date, column_name=None):
    gdf = get_gdf()
    url = 'https://covid19.who.int/WHO-COVID-19-global-data.csv'
    df = pd.read_csv(url, encoding='utf-8-sig', engine='python')
    df.columns = df.columns.str.strip()
    df.loc[df['Country'] == 'Russian Federation', ['Country']] = 'Russia'
    # print(df.columns)
    # print(gdf.columns)
    df = df.loc[df['Date_reported'] == date.strftime('%Y-%m-%d')]

    merged = gdf.merge(df, left_on='Country_code', right_on='Country_code')
    merged.fillna('No data', inplace=True)
    # merged = merged[['Date_reported', 'Country_code', 'Country',
    #                 'WHO_region', 'geometry', column_name]]

    # Read data to json.
    merged_json = json.loads(merged.to_json())
    # Convert to String like object.
    json_data = json.dumps(merged_json)

    return json_data

def update_plot(attr, old, new):
    new_date = datetime.datetime.fromtimestamp(slider.value / 1000)
    new_date = datetime.datetime(new_date.year, new_date.month, new_date.day)
    #print(datetime.fromtimestamp(new / 1000), slider.value)
    new_data = make_json_data_for_date(new_date)
    geosource.geojson = new_data
    #p.title.text = 'Share of adults who are obese, %d' %yr

def previous_date():
    print(slider.value)
    slider.value -= 8.64e+7 # that many milliseconds in a day
    new_date = datetime.datetime.fromtimestamp(slider.value / 1000)
    new_date = datetime.datetime(new_date.year, new_date.month, new_date.day)
    # print(datetime.fromtimestamp(new / 1000), slider.value)
    new_data = make_json_data_for_date(new_date)
    geosource.geojson = new_data
    print(new_date)
def next_date():
    print(slider.value)
    slider.value += 8.64e+7 # that many milliseconds in a day
    new_date = datetime.datetime.fromtimestamp(slider.value / 1000)
    new_date = datetime.datetime(new_date.year, new_date.month, new_date.day)
    # print(datetime.fromtimestamp(new / 1000), slider.value)
    new_data = make_json_data_for_date(new_date)
    geosource.geojson = new_data
    print(new_date)
# Get GDF data
gdf = get_gdf()
# gdf = get_gdf_TM_WORLD_BORDERS()

# gdf_json = json.loads(gdf.to_json())
# gdf_json_data = json.dumps(gdf_json)
# Input GeoJSON source that contains features for plotting
gdf_json = json.loads(gdf.to_json())
gdf_json_data = json.dumps(gdf_json)
gdf_source = GeoJSONDataSource(geojson=gdf_json_data)
#print(gdf_source)

datetime_min, datetime_max = get_data_date_ranges()

# Make a slider
# Make a slider object: slider
slider = DateSlider(title='Date', start=datetime_min, end=datetime_max, step=1, value=datetime_max)
slider.on_change('value', update_plot)

# Buttons
bt_prev = Button(label='<<')
bt_prev.on_click(previous_date)

# Buttons
bt_next = Button(label='>>')
bt_next.on_click(next_date)


# print(slider)
# slider.on_change('value', update_plot)
tabs = []
TOOLS = "pan,wheel_zoom,reset,hover,save"

all_columns = ['Date_reported', 'New_cases', 'Cumulative_cases', 'New_deaths', 'Cumulative_deaths']

for column_name in all_columns[1:]:
    geosource = GeoJSONDataSource(geojson=make_json_data_for_date(datetime_max,
                                                                  column_name=column_name))



    plot = bokeh_plot_map()

    tabs.append(Panel(child=column(plot), title=column_name))
    del plot
tabs_plots = Tabs(tabs=tabs)
print(tabs_plots.active)
#show(tabs_plots)
curdoc().add_root(column(tabs_plots, slider, Row(bt_prev, bt_next)))
curdoc().title = "CoVID-19"
'''
sys.exit()
tab_names = all_columns[1:]
tabs = []
for tab_name in tab_names[:1]:
    # Input GeoJSON source that contains features for plotting.

    TOOLTIPS = [("Country", "@country")]
    TOOLTIPS.extend([(tab_name, "@" + tab_name) for tab_name in all_columns])
    print(TOOLTIPS)
    plot = figure(title='COVID-19 Statistics', tools=TOOLS,
                  tooltips=TOOLTIPS, plot_height=600, plot_width=1200)



    # print(merged)
    print(df)
    # Merge dataframes gdf and data.
    merged = gdf.merge(df, left_on='country_code', right_on='Country_code')
    # Read data to json.
    merged_json = json.loads(merged.to_json())

    # Convert to String like object.
    json_data = json.dumps(merged_json)
    # plot each tab
    plot = bokeh_plot_map(json_data, gdf_json_data, tab_name, plot, min_data=min_data, max_data=max_data)

    tabs.append(Panel(child=column(plot, slider), title=tab_name))

    del plot

tabs_plots = Tabs(tabs=tabs)

# show(tabs_plots)

curdoc().add_root(tabs_plots)
curdoc().title = "CoVID-19"
'''

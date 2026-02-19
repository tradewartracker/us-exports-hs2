import datetime as dt
from os.path import dirname, join

import numpy as np

import pandas as pd

import pyarrow as pa
import pyarrow.parquet as pq

from bokeh.io import curdoc
from bokeh.layouts import column, gridplot, row
from bokeh.models import ColumnDataSource, DataRange1d, Select, HoverTool, Panel, Tabs, LinearColorMapper, Range1d, MultiChoice
from bokeh.models import NumeralTickFormatter, Title, Label, Paragraph, Div, CustomJSHover, BoxAnnotation, Button
from bokeh.models import ColorBar
from bokeh.palettes import brewer, Spectral6
from bokeh.plotting import figure
from bokeh.embed import server_document
from bokeh.transform import factor_cmap
import io
import base64

#################################################################################
# This just loads in the data...
# Alot of this was built of this "cross-fire demo"
# https://github.com/bokeh/bokeh/blob/branch-2.3/examples/app/crossfilter/main.py
#

final_month = 5
final_year = 2026

background = "#ffffff"

file = "./data"+ "/top30-HS2-exports.parquet"

df = pq.read_table(file).to_pandas()

country_options = df.index.unique(0).to_list()
product_options = df.index.unique(1).to_list()

#print(options)

product = 'ALL PRODUCTS'
country = "MEXICO"

level = "US Dollars"

#################################################################################
#These are functions used in the plot...

def growth_trade(foo):
    # what this function does is take a dataframe and create a relative 
    foo["exports_shifted"] = foo["exports"].shift(12)

    foo["growth"] = 100 * ((foo["exports"] / foo["exports_shifted"]) - 1)

    foo["growth"] = foo["growth"].fillna(0)
    
    return foo


#################################################################################
# Then this makes the simple plots:

def make_plot():
    
    height = int(1.15*533)
    width = int(1.15*750)
    
    # Debug: Print what we're trying to select
    print(f"\n=== DEBUG INFO ===")
    print(f"Selected countries: {country_select.value}")
    print(f"Selected product: {product_select.value}")
    print(f"Selected level: {level_select.value}")
    print(f"DataFrame index levels: {df.index.names}")
    print(f"DataFrame columns: {df.columns.tolist()}")
    
    # Select data for the chosen product and all selected countries
    # Need to use pd.IndexSlice for proper MultiIndex slicing
    idx = pd.IndexSlice
    foo = df.loc[idx[country_select.value, product_select.value, :], :]
    
    print(f"After slicing, foo shape: {foo.shape}")
    print(f"After slicing, foo index: {foo.index.names}")
    if len(foo) > 0:
        print(f"First few rows of foo:\n{foo.head()}")
    else:
        print("WARNING: foo is empty!")
    
    # below there is an object of selections which will be one of the values in 
    # the list of options. So the .value then grabs that particular option selected.
        
    if level_select.value == 'Year over Year % Change':

        foo = foo.groupby(level=0).apply(growth_trade)

        level_series = "growth"
        
    if level_select.value == 'US Dollars':
        
        level_series = "exports"
        
    title_name = ""
        
    for name in country_select.value:
        
        if len(country_select.value) <= 2:
            title_name = title_name + name + ", "
            
        if len(country_select.value) > 2:
            title_name = title_name + name[0:3] + ", "
        
        
    title = "US EXPORTS to " + title_name + "of " + product_select.value.title().upper()

    # This is standard bokeh stuff so far
    plot = figure(x_axis_type="datetime", plot_height = height, plot_width=width, toolbar_location = 'below',
           tools = "box_zoom, reset, pan, xwheel_zoom, save", title = title,
                  x_range = (dt.datetime(2019,final_month,1),dt.datetime(final_year,final_month,1)) )
    
    # Get fixed colors from the dataframe for each selected country
    line_colors = []
    line_widths = []
    
    for country_name in country_select.value:
        # Get the color for this country from the dataframe
        country_data = foo.loc[country_name]
        country_color = country_data.iloc[0]['color']
        line_colors.append(country_color)
        line_widths.append(5)
    
    # Plot each country as a separate line for legend support
    for i, country_name in enumerate(country_select.value):
        country_data = foo.loc[country_name]
        
        # Since we sliced by country, we still have ['E_COMMODITY_SDESC', 'time'] as index
        # We need to get the time values from the index
        time_values = country_data.index.get_level_values('time')
        
        # Create ColumnDataSource with flag URL
        source = ColumnDataSource(data=dict(
            x=time_values,
            y=country_data[level_series].values,
            country=[country_name] * len(country_data),
            flag=[country_data['flag'].iloc[0]] * len(country_data)
        ))
        
        plot.line('x', 'y', source=source,
                 line_width=line_widths[i], line_alpha=0.75, line_color=line_colors[i],
                 legend_label=country_name, name=country_name)
        
    # fixed attributes
    plot.xaxis.axis_label = None
    plot.yaxis.axis_label = ""
    plot.axis.axis_label_text_font_style = "bold"
    plot.grid.grid_line_alpha = 0.3

    # Configure tooltips with flag images
    if level_select.value == 'Year over Year % Change':
        TIMETOOLTIPS = """
                <div style="background-color:#F5F5F5; opacity: 0.95; border: 5px 5px 5px 5px;">
                <div style = "text-align:left;">
                <span style="font-size: 13px; font-weight: bold">
                <img src="@flag" alt="" style="height:20px; vertical-align:middle; margin-right:8px;"> @country
                 </span>
                 </div>
                 <div style = "text-align:left;">
                <span style="font-size: 13px; font-weight: bold"> @x{%b %Y}:  @y{0}%</span>   
                </div>
                </div>
                """
        plot.add_tools(HoverTool(tooltips = TIMETOOLTIPS,  line_policy='nearest', formatters={'@x': 'datetime'}))
        
    if level_select.value == 'US Dollars':
        TIMETOOLTIPS = """
                <div style="background-color:#F5F5F5; opacity: 0.95; border: 5px 5px 5px 5px;">
                <div style = "text-align:left;">
                <span style="font-size: 13px; font-weight: bold">
                <img src="@flag" alt="" style="height:20px; vertical-align:middle; margin-right:8px;"> @country
                 </span>
                 </div>
                 <div style = "text-align:left;">
                <span style="font-size: 13px; font-weight: bold"> @x{%b %Y}:  @y{$0.0a}</span>   
                </div>
                </div>
                """
        plot.add_tools(HoverTool(tooltips = TIMETOOLTIPS,  line_policy='nearest', formatters={'@x': 'datetime'}))
                
    if level_select.value == 'Year over Year % Change':
        if foo[level_series].max() > 1500:
            plot.y_range.end = 1500
    
    # Configure legend
    plot.legend.location = "top_left"
    plot.legend.click_policy = "hide"  # Click to hide/show lines
    plot.legend.label_text_font_size = "10pt"
    plot.legend.spacing = 2
    plot.legend.padding = 5
    
    plot.title.text_font_size = '13pt'
    plot.background_fill_color = background 
    plot.background_fill_alpha = 0.75
    plot.border_fill_color = background 
    
    tradewar_box = BoxAnnotation(left=dt.datetime(2020,2,1), right=dt.datetime(2020,4,30), fill_color='blue', fill_alpha=0.1)
    plot.add_layout(tradewar_box)

    liberation_box = BoxAnnotation(left=dt.datetime(2025,1,1), right=dt.datetime(final_year,final_month,1), fill_color='red', fill_alpha=0.1)
    plot.add_layout(liberation_box)
    
    if "CHINA" in country_select.value:
    
        tradewar_box = BoxAnnotation(left=dt.datetime(2018,7,1), right=dt.datetime(2019,10,11), fill_color='red', fill_alpha=0.1)
        
        plot.add_layout(tradewar_box)
            
    #p.yaxis.axis_label = 
    plot.yaxis.axis_label_text_font_style = 'bold'
    plot.yaxis.axis_label_text_font_size = "13px"
    
    plot.sizing_mode= "scale_both"

    if level_select.value != 'Year over Year % Change':
        
        plot.yaxis.formatter = NumeralTickFormatter(format="($0. a)")
        
        plot.yaxis.axis_label = "US Dollars"
        
    if level_select.value == 'Year over Year % Change':
        
        plot.yaxis.axis_label = level_select.value
    
    plot.max_height = height
    plot.max_width = width
    
    plot.min_height = int(0.25*height)
    plot.min_width = int(0.25*width)
    
    return plot

#################################################################################

def download_csv():
    """Generate CSV data for currently selected countries, product, and metric"""
    
    # Get the data for selected countries and product
    idx = pd.IndexSlice
    foo = df.loc[idx[country_select.value, product_select.value, :], :]
    
    if level_select.value == 'Year over Year % Change':
        foo = foo.groupby(level=0).apply(growth_trade)
        metric_column = "growth"
    else:
        metric_column = "exports"
    
    # Collect data for all selected countries
    data_list = []
    for country_name in country_select.value:
        country_data = foo.loc[country_name]
        for idx, row in country_data.iterrows():
            value = row[metric_column]
            # Skip rows where the metric value is NaN or missing
            if pd.notna(value):
                # idx is a tuple (product, time) - extract the time component
                time_val = idx[1] if isinstance(idx, tuple) else idx
                data_list.append({
                    'Country': country_name,
                    'Product': product_select.value,
                    'Date': time_val.strftime('%Y-%m-%d'),
                    'Metric': level_select.value,
                    'Value': value
                })
    
    # Create DataFrame and export to CSV
    export_df = pd.DataFrame(data_list)
    csv_string = export_df.to_csv(index=False)
    
    # Create data URI for download link
    b64 = base64.b64encode(csv_string.encode()).decode()
    data_uri = f"data:text/csv;base64,{b64}"
    
    # Update the download link div
    download_link_div.text = f'''
    <a href="{data_uri}" download="export_data.csv" 
       style="display:inline-block; padding:10px 20px; background-color:#28a745; 
              color:white; text-decoration:none; border-radius:4px; font-weight:bold;">
       Click Here to Download CSV
    </a>
    '''

#################################################################################

def update_plot(attrname, old, new):
    layout.children[0] = make_plot()
    
# This part is still not clear to me. but it tells it what to update and where to put it
# so it updates the layout and [0] is the first option (see below there is a row with the
# first entry the plot, then the controls)

level_select = Select(value=level, title='Tranformations', options=['US Dollars', 'Year over Year % Change'], width=350)
level_select.on_change('value', update_plot)

#print(sorted(options))
#################################################################################

#country_select = Select(value=country, title='Country', options=sorted(country_options), width=400)
country_select = MultiChoice(value=[country], title='Country', options=sorted(country_options), width=325)
# This is the key thing that creates teh selection object

country_select.on_change('value', update_plot)


#################################################################################

product_select = Select(value=product, title='HS2 Product', options=sorted(product_options), width=350)
# This is the key thing that creates teh selection object

product_select.on_change('value', update_plot)
# Change the value upone selection via the update plot 

#################################################################################

# Download CSV button and link
download_button = Button(label="Generate CSV Download Link", button_type="success", width=350)
download_button.on_click(download_csv)

download_link_div = Div(text="", width=350, height=50)

#################################################################################

div0 = Div(text = """Each category is a 2 digit HS Code. ALL PRODUCTS is the sum of exports across all product catagories.\n
    """, width=350, background = background, style={"justify-content": "space-between", "display": "flex"} )

div1 = Div(text = """Top 20 Countries by export volume and TOTAL which aggregates across all countries in the world. Select multiple countries.\n
    """, width=350, background = background, style={"justify-content": "space-between", "display": "flex"} )

div2 = Div(text = """<b>Download Chart:</b> Use the save icon (💾) in the chart toolbar to download as PNG.<br>
    <b>Download Data:</b> Click the button to generate a download link for CSV data.\n
    """, width=350, background = background, style={"justify-content": "space-between", "display": "flex"} )

controls = column(country_select, div1, product_select, div0, level_select, download_button, download_link_div, div2)

height = int(1.95*533)
width = int(1.95*675)

layout = row(make_plot(), controls, sizing_mode = "scale_height", max_height = height, max_width = width,
              min_height = int(0.25*height), min_width = int(0.25*width))

curdoc().add_root(layout)
curdoc().title = "us-exports-hs2-products"
#curdoc().add_root(column(p))

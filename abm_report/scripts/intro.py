#import libraries
import fiona
import pandas as pd
import numpy as np

import os

#bokeh
from bokeh.io import show, output_notebook, push_notebook, curdoc, output_file
from bokeh.plotting import figure, output_file, save
from bokeh.layouts import layout, column, row
from bokeh.models import Spacer,HoverTool,LogColorMapper, ColumnDataSource, TapTool, BoxSelectTool, LabelSet, Label, FactorRange,NumeralTickFormatter
from bokeh.tile_providers import STAMEN_TERRAIN_RETINA,CARTODBPOSITRON_RETINA
from bokeh.core.properties import value
from bokeh.transform import factor_cmap, dodge
from bokeh.models.widgets import Div, Tabs, Paragraph, Dropdown, Button, PreText, Toggle, TableColumn, DataTable

#mapping
from shapely.geometry import Polygon, Point, MultiPoint, MultiPolygon
import geopandas as gpd



def intro_tab(rings, rings_pts, metra, cta, counties, mhn):

    column_width = 1400
    bar_height = 500
    census_color = "#EFF1EF"
    survey_color = '#9EA499'
    cmap_color = '#495667'

    def make_group_vbar(df, groups, subgroups, tool_tips, chart_tools, p_width = 400, p_height = 200,
                    chart_title="Sample Grouped Bar Chart"):

        df_groupby = df.groupby(groups).sum().reset_index()
        df_groups = df_groupby[groups].values.tolist()
        numgroups = len(subgroups)

        data = {'groups': groups}

        ziplist = ()
        for s in subgroups:
            data[s] = df_groupby[s].values.tolist()
            ziplist += (data[s],)


        x = [(g, s) for g in df_groups for s in subgroups]
        sgroups = [s for g in df_groups for s in subgroups]
        pgroups = [g for g in df_groups for s in subgroups]

        if numgroups == 2:
            counts = sum(zip(ziplist[0], ziplist[1]), ())
        elif numgroups ==3:
            counts = sum(zip(ziplist[0], ziplist[1], ziplist[2]), ())
        elif numgroups ==4:
            counts = sum(zip(ziplist[0], ziplist[1], ziplist[2], ziplist[3], ziplist[4]), ())
        elif numgroups ==5:
            counts = sum(zip(ziplist[0], ziplist[1], ziplist[2], ziplist[3], ziplist[4], ziplist[5]), ())
        elif numgroups ==6:
            counts = sum(zip(ziplist[0], ziplist[1], ziplist[2], ziplist[3], ziplist[4], ziplist[5], ziplist[6]), ())
        elif numgroups ==7:
            counts = sum(zip(ziplist[0], ziplist[1], ziplist[2], ziplist[3], ziplist[4],
                             ziplist[5], ziplist[6], ziplist[7]), ())
        elif numgroups ==8:
            counts = sum(zip(ziplist[0], ziplist[1], ziplist[2], ziplist[3], ziplist[4],
                             ziplist[5], ziplist[6], ziplist[7], ziplist[8]), ())
        elif numgroups ==9:
            counts = sum(zip(ziplist[0], ziplist[1], ziplist[2], ziplist[3], ziplist[4],
                             ziplist[5], ziplist[6], ziplist[7], ziplist[8], ziplist[9]), ())
        elif numgroups ==10:
            counts = sum(zip(ziplist[0], ziplist[1], ziplist[2], ziplist[3], ziplist[4],
                             ziplist[5], ziplist[6], ziplist[7], ziplist[8], ziplist[9], ziplist[10]), ())

        source = ColumnDataSource(data=dict(x=x, counts=counts, sub=sgroups, prime=pgroups))


        p = figure(x_range=FactorRange(*x), plot_width = p_width,plot_height=p_height, title=chart_title,
           toolbar_location='right', tools=chart_tools,
           tooltips=tool_tips)

        p.vbar(x='x', top='counts', width=0.9, source=source)


        # Styling
        #p = bar_style(p)

        p.y_range.start = 0
        p.x_range.range_padding = 0.1
        p.xaxis.major_label_orientation = 1
        p.xgrid.grid_line_color = None

        return p
    def make_base_map(tile_map=CARTODBPOSITRON_RETINA,map_width=800,map_height=500, xaxis=None, yaxis=None,
                    xrange=(-9990000,-9619944), yrange=(5011119,5310000),plot_tools="pan,wheel_zoom,reset"):

        p = figure(tools=plot_tools, width=map_width,height=map_height, x_axis_location=xaxis, y_axis_location=yaxis,
                    x_range=xrange, y_range=yrange)

        p.grid.grid_line_color = None

        p.add_tile(tile_map)

        return p
    def make_poly_map(base_map, shapefile,label,fillcolor,fillalpha,linecolor,lineweight,add_label,legend_field):

        p = base_map

        shp = fiona.open(shapefile)

        # Extract features from shapefile
        district_name = [ feat["properties"][label].replace(" County","") for feat in shp]
        fill_color = [ feat["properties"]["color"] for feat in shp]
        pareas = [ feat["properties"]["legend"] for feat in shp]
        label_x = [ feat["properties"]["INSIDE_X"] for feat in shp]
        label_y = [ feat["properties"]["INSIDE_Y"] for feat in shp]
        district_area = [ feat["properties"]["Shape_Area"] for feat in shp]
        district_x = [ [x[0] for x in feat["geometry"]["coordinates"][0]] for feat in shp]
        district_y = [ [y[1] for y in feat["geometry"]["coordinates"][0]] for feat in shp]
        district_xy = [ [ xy for xy in feat["geometry"]["coordinates"][0]] for feat in shp]
        district_poly = [ Polygon(xy) for xy in district_xy] # coords to Polygon

        source = ColumnDataSource(data=dict(
            x=district_x, y=district_y,
            name=district_name,
            poly_color=fill_color,
            planning = pareas,
            label_x = label_x,
            label_y = label_y
        ))

        polygons = p.patches('x', 'y', source=source, fill_color=fillcolor,
                  fill_alpha=fillalpha, line_color=linecolor, line_width=lineweight, legend=legend_field)

        if add_label:

            labels = LabelSet(x='label_x', y='label_y', source=source,text='name', level='glyph',text_line_height=1.5,
                      x_offset = -15,y_offset = -8,render_mode='canvas',text_font_size="10pt",text_color="white")

            p.add_layout(labels)
        #TOOLTIPS = [
        #    ("Count", '@rs2'),
        #    ("Total Transit Trips From Sector", "@alightings_s{0,0}"),
        #    ("Total Transit Trips To Sector", "@boardings_s{0,0}")
        #]

        p.add_tools(HoverTool(renderers=[polygons]))


        return p
    def make_line_map(base_map, shp):

        p = base_map

        def getLineCoords(row, geom, coord_type):
            """Returns a list of coordinates ('x' or 'y') of a LineString geometry"""
            if coord_type == 'x':
                return list( row[geom].coords.xy[0] )
            elif coord_type == 'y':
                return list( row[geom].coords.xy[1] )

        gpd_shp = gpd.read_file(shp)

        gpd_shp['x'] = gpd_shp.apply(getLineCoords, geom='geometry', coord_type='x', axis=1)

        # Calculate y coordinates of the line
        gpd_shp['y'] = gpd_shp.apply(getLineCoords, geom='geometry', coord_type='y', axis=1)

        # Make a copy and drop the geometry column
        shp_df = gpd_shp.drop('geometry', axis=1).copy()

        # Point DataSource
        source = ColumnDataSource(shp_df)

        p.multi_line('x', 'y', source=source, color='black', line_width=.1)

        return p

    p = make_base_map(map_width=column_width,map_height=500, xaxis=None, yaxis=None,
                    xrange=(-9990000,-9619944), yrange=(5011119,5310000),plot_tools="pan,wheel_zoom,reset,save")

    poly_plot = make_poly_map(p, counties, 'COUNTY','poly_color',.5,None,2,False,"planning")
    line_plot = make_line_map(p, mhn)
    cmap_plot = make_poly_map(p, counties, 'COUNTY',None,.5,'white',2,True,None)


    h_1 = Div(text = """<h1># Overview</h1><hr>
                    <p>Contrary to popular belief, Lorem Ipsum is not simply random text.
                    It has roots in a piece of classical Latin literature from 45 BC,
                    making it over 2000 years old. Richard McClintock, a Latin professor
                    at Hampden-Sydney College in Virginia, looked up one of the more obscure
                    Latin words, consectetur, from a Lorem Ipsum passage, and going through
                    the cites of the word in classical literature, discovered the undoubtable
                    source. Lorem Ipsum comes from sections 1.10.32 and 1.10.33 of "de Finibus
                    Bonorum et Malorum" (The Extremes of Good and Evil) by Cicero, written in
                    45 BC. This book is a treatise on the theory of ethics, very popular during
                    the Renaissance. The first line of Lorem Ipsum, "Lorem ipsum dolor sit
                    amet..", comes from a line in section 1.10.32.</p>""",
                    width = column_width, sizing_mode='stretch_both',
                    style={"width":'100%',"text-align":'left',"margin":'0 auto'})

    h_2 = Div(text = """<h2># | Modeling Area</h2><hr>
                    <p>Contrary to popular belief, Lorem Ipsum is not simply random text.
                    It has roots in a piece of classical Latin literature from 45 BC,
                    making it over 2000 years old. Richard McClintock, a Latin professor
                    at Hampden-Sydney College in Virginia, looked up one of the more obscure
                    Latin words, consectetur, from a Lorem Ipsum passage, and going through
                    the cites of the word in classical literature, discovered the undoubtable
                    source. Lorem Ipsum comes from sections 1.10.32 and 1.10.33 of "de Finibus
                    Bonorum et Malorum" (The Extremes of Good and Evil) by Cicero, written in
                    45 BC. This book is a treatise on the theory of ethics, very popular during
                    the Renaissance. The first line of Lorem Ipsum, "Lorem ipsum dolor sit
                    amet..", comes from a line in section 1.10.32.</p>""",
                    width = column_width, sizing_mode='stretch_both',
                    style={"width":'100%',"text-align":'left',"margin":'0 auto'})

    map_title = Div(text="""<h5>Figure # - CMAP Modeling Area And Network</h5>""",width = column_width, css_classes = ["caption"])


    h_3 = Div(text = """<h2># | Population Synthesis</h2><hr>
                    <p>Contrary to popular belief, Lorem Ipsum is not simply random text.
                    It has roots in a piece of classical Latin literature from 45 BC,
                    making it over 2000 years old. Richard McClintock, a Latin professor
                    at Hampden-Sydney College in Virginia, looked up one of the more obscure
                    Latin words, consectetur, from a Lorem Ipsum passage, and going through
                    the cites of the word in classical literature, discovered the undoubtable
                    source. Lorem Ipsum comes from sections 1.10.32 and 1.10.33 of "de Finibus
                    Bonorum et Malorum" (The Extremes of Good and Evil) by Cicero, written in
                    45 BC. This book is a treatise on the theory of ethics, very popular during
                    the Renaissance. The first line of Lorem Ipsum, "Lorem ipsum dolor sit
                    amet..", comes from a line in section 1.10.32.</p>""",
                    width = column_width, sizing_mode='stretch_both',
                    style={"width":'100%',"text-align":'left',"margin":'0 auto'})


    layout = row(column(h_1,Spacer(height=25),h_2, Spacer(height=25),map_title,cmap_plot,Spacer(height=25),h_3))
    return layout

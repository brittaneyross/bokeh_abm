#import libraries
import fiona
import pandas as pd
import numpy as np

import os

#bokeh
from bokeh.plotting import figure,gmap
from bokeh.core.properties import value
from bokeh.transform import factor_cmap, dodge

#color
from bokeh.palettes import Reds6 as palette

from bokeh.layouts import layout, column, row, WidgetBox
from bokeh.models import Panel, Spacer, HoverTool, LogColorMapper, FactorRange, NumeralTickFormatter. ColumnDataSource, TapTool, BoxSelectTool, CustomJS
from bokeh.models.widgets import Div, Tabs, Paragraph, Dropdown, Button, PreText, Toggle, DataTable, DateFormatter, TableColumn
from bokeh.events import Tap

from bokeh.application.handlers import FunctionHandler
from bokeh.application import Application

from bokeh.resources import CDN

from bokeh.palettes import PuBu9

#mapping
from shapely.geometry import Polygon, Point, MultiPoint, MultiPolygon
from shapely.prepared import prep

from itertools import chain

import warnings
warnings.filterwarnings('ignore')

import math

from bokeh.io import show, output_file
from bokeh.models import GraphRenderer, StaticLayoutProvider, Oval
from bokeh.palettes import Spectral8
from bokeh.tile_providers import STAMEN_TERRAIN_RETINA,CARTODBPOSITRON_RETINA
from bokeh.models.graphs import from_networkx, NodesAndLinkedEdges, EdgesAndLinkedNodes

#import holoviews as hv
#hv.extension('bokeh')

from bokeh.models import Plot, ColumnDataSource, Range1d, from_networkx, Circle,MultiLine
from bokeh.io import show, output_file
from bokeh.palettes import Viridis, Spectral4

import geopandas as gpd

output_notebook()
#import holoviews as hv

column_width = 1000
bar_height = 200
census_color = "#EFF1EF"
survey_color = '#9EA499'
cmap_color = '#495667'

#make src data
def make_transit_src(df):
    groupby = df.index.values.tolist()
    survey = df['Observed'].values.tolist()
    model = df['Model'].values.tolist()

    data = {'Group': groupby,
           'Observed': survey,
           'Model': model}

    return ColumnDataSource(data=data)

#make groupbed bar chart
def make_transit_chart(src,groups):

    p = figure(x_range=FactorRange(*groups),
               plot_width = column_width, plot_height = bar_height,
               tools="hover",toolbar_location = None)

    p.vbar(x=dodge('Group',-0.25,range=p.x_range),top='Observed', width=0.25, source=src,
           color=survey_color, legend=value("Observed"))

    p.vbar(x=dodge('Group',0,range=p.x_range),top='Model', width=0.25, source=src,
           color=cmap_color, legend=value("Model"))

    p.select_one(HoverTool).tooltips = [
         ('Observed - Transit Trip',"@Observed{0.0}%"),
         ('Model - Transit Trip',"@Model{0.0}%")
    ]

    # Styling
    p.yaxis.formatter = NumeralTickFormatter(format='0%')

    p.legend.click_policy="hide"

    return p


def crosstabs_pct(df, index, col, value):
    return (pd.crosstab(index=df[index],columns=df[col],
            values=df[value],aggfunc=sum,margins=True,
            margins_name='Total', normalize='all')*100)

def crosstabs(df, index, col, value):
    return (pd.crosstab(index=df[index],columns=df[col],
            values=df[value],aggfunc=sum,margins=True,
            margins_name='Total'))

def order_income(df):
    df = df.reset_index()
    df.loc[:,'order'] = np.where(df['hhincome'] == '0-35K',0,9)
    df.loc[:,'order'] = np.where(df['hhincome'] == '35K-60k',1,df['order'])
    df.loc[:,'order'] = np.where(df['hhincome'] == '60K-100K',2,df['order'])
    df.loc[:,'order'] = np.where(df['hhincome'] == '100K+',3,df['order'])
    df.loc[:,'order'] = np.where(df['hhincome'] == 'Total',4,df['order'])

    df = df.sort_values(by='order')
    df.columns = ['Income Range','Bus','CTA Rail','Metra','Total','order']
    return df[['Income Range','Bus','CTA Rail','Metra','Total']]

def transit_trips_attr(model, survey, index, col):

    model_group = model.groupby([col,index]).agg({'Model':sum}).reset_index()
    survey_group = survey.groupby([col,index]).agg({'Weight2':sum}).reset_index()
    survey_group.columns = [col,index,'Observed']

    model_ct = crosstabs_pct(model_group, index, col, 'Model')
    survey_ct = crosstabs_pct(survey_group, index, col, 'Observed')

    if index == 'hhincome':
        return order_income(model_ct), order_income(survey_ct)

    if index == 'AutoxAdults':
        return model_ct.reset_index(), survey_ct.reset_index()

#commute transit trips
def commute(model_transit, survey_transit):

    model_transit_work = model_transit.loc[model_transit['trip_purpose'].isin(['Work','Work-Based'])]
    survey_transit_work = survey_transit.loc[survey_transit['trip_purpose'].isin(['Work','Work-Based'])]

    model_commute = ((float(model_transit_work[['Model']].sum()[0])/float(model_transit[['Model']].sum()[0]))) * 100
    model_noncommute = 100 - model_commute
    survey_commute = (survey_transit_work[['Weight2']].sum()[0]/survey_transit[['Weight2']].sum()[0]) * 100
    survey_noncommute = 100 - survey_commute

    commute_share = pd.DataFrame({'Observed':[survey_commute,survey_noncommute],
                                  'Model':[model_commute,model_noncommute]},index=['Commute','NonCommute'])

    commute_share.loc['Total'] = commute_share.sum()

    commute_share.loc[:,'Difference'] = commute_share['Observed'] - commute_share['Model']

    return commute_share

def transit_mode(model_transit, survey_transit):

    model = (model_transit.groupby('transit_mode').agg({'Model':sum})/model_transit[['Model']].sum())
    survey = (survey_transit.groupby('transit_mode').agg({'Weight2':sum})/survey_transit[['Weight2']].sum())
    survey.columns = ['Observed']

    model_survey = survey.merge(model, how='left',left_index=True, right_index=True)
    groups = model.index.tolist()

    transit_src = make_transit_src(model_survey)
    p = make_transit_chart(transit_src,groups)

    return p

def transit_boardings(model_boardings, cta_rail_rtams, cta_bus_rtams,
                      metra_rtams, pace_rtams):

    return

def transit_flows(model,survey):

    def replace_label(df):
        replace = {17:"Illinois",19:"Wisconsin",18:"Indiana",14:"Kendall",12:"Kane",
           11:"DuPage",8:"Cook",7:"Suburban Cook",5:"Chicago",
           13:"Will",15:"McHenry",16:"Lake",9:"Suburban Cook",3:"Chicago",4:"Chicago",1:"Central Business District"}

        df['origAreaGroup'] = df['origAreaGroup'].replace(replace)
        df['destAreaGroup'] = df['destAreaGroup'].replace(replace)
        return df

    model_ct = crosstabs_pct(replace_label(model),'origAreaGroup','destAreaGroup','Model')
    survey_ct = crosstabs_pct(replace_label(survey),'origAreaGroup','destAreaGroup','Weight2')

    return model_ct.fillna(0).reset_index(), survey_ct.fillna(0).reset_index()

def make_basemap(shapefile,label):
    shp = fiona.open(shapefile)
    # Extract features from shapefile - Ring Sector Polygons
    district_name = [ feat["properties"][label] for feat in shp]
    district_area = [ feat["properties"]["Shape_Area"] for feat in shp]
    district_x = [ [x[0] for x in feat["geometry"]["coordinates"][0]] for feat in shp]
    district_y = [ [y[1] for y in feat["geometry"]["coordinates"][0]] for feat in shp]
    district_xy = [ [ xy for xy in feat["geometry"]["coordinates"][0]] for feat in shp]
    district_poly = [ Polygon(xy) for xy in district_xy] # coords to Polygon

    source = ColumnDataSource(data=dict(
        x=district_x, y=district_y,
        name=district_name
    ))

    return source

def make_flow(model, points):

    od = model.groupby(['origin_geo','destination_geo']).agg({'Model':sum}).reset_index()
    o = model.groupby(['origin_geo']).agg({'Model':sum}).reset_index()
    d = model.groupby(['destination_geo']).agg({'Model':sum}).reset_index()



    points_b = points.merge(o[['origin_geo','Model']],how='left',left_on = 'rs2', right_on='origin_geo')
    points_b.columns = points.columns.tolist() + ['origin_geo','boardings']
    points_bd = points_b.merge(d,how='left',left_on = 'rs2', right_on='destination_geo').fillna(0)
    points_bd.columns = points_b.columns.tolist() + ['destination_geo','alightings']

    #merge points with origin boarding totals

    points.loc[:,'key'] = points.index

    #dictionary format origin as key and connections as values
    od_o = od.merge(points[['key','rs2']],how='left',left_on = 'origin_geo', right_on='rs2')
    od_o.columns = od.columns.tolist() + ['origin','rs2_origin']

    od_od = od_o.merge(points[['FID','rs2']],how='left',left_on = 'destination_geo', right_on='rs2')
    od_od.columns = od_o.columns.tolist() + ['destination','rs2_dest']

    od_od['Grouptotal'] = od_od['Model'].groupby(od_od['origin']).transform('sum')
    od_od['width'] = ((od_od['Model']/od_od['Grouptotal']) * 20).astype(int) + 2

    links = {}
    links['segments'] = {}
    links['width'] = {}
    x = points['POINT_X'].values.tolist()
    y = points['POINT_Y'].values.tolist()
    names = points['rs2'].values.tolist()
    boardings = points_bd['boardings'].values.tolist()
    alightings = points_bd['alightings'].values.tolist()

    count = 0
    for i, row in od_od.iterrows():
        if od_od.loc[i,'origin'] in links['segments'].keys():
            links['segments'][od_od.loc[i,'origin']].append(od_od.loc[i,'destination'])
            links['width'][od_od.loc[i,'origin']].append(od_od.loc[i,'width'])
        else:
            links['segments'][od_od.loc[i,'origin']] = [od_od.loc[i,'destination']]
            links['width'][od_od.loc[i,'origin']] = [od_od.loc[i,'width']]
            #board_index = count
            #boardings.append(od_od.loc[i,'Model'])
            #count +=1
    return links, x, y, names, boardings, alightings



def make_table(df,index):

    select = df.loc[index].to_html(index=False,
              classes=["table-hover","text-center","table-condensed"])

    return select


def make_map(poly_src,links,x_cr,y_cr,names,boardings,alightings,model):

    TOOLS = "pan,wheel_zoom,reset,save"

    TOOLTIPS = [
    ("Sector", "@name"),
    ]

    p = figure(tools=TOOLS, width=900,height=800, x_axis_location=None, y_axis_location=None,
                x_range=(-9990000,-9619944), y_range=(5011119,5310000))

    p.grid.grid_line_color = None

    poly = p.patches('x', 'y', source=poly_src, fill_alpha=None, line_color='Black', line_width=0.3)

    tbl = Div(text=model.loc[[len(model)-1]].reset_index().to_html(index=False,
        classes=["table-bordered", "table-hover","text-center","table-condensed"]))

    transit_trips = model_flows.transpose()
    columns = [TableColumn(field=col, title=col) for col in transit_trips.columns[0]]
    trips_tbl = DataTable(columns=columns, source=ColumnDataSource(model[['1']]),
                          height = 800, fit_columns = True, selectable = True)

    seg_src = ColumnDataSource({'x0': [], 'y0': [], 'x1': [], 'y1': [], 'width': []})


    seg = p.segment(x0='x0', y0='y0', x1='x1', y1='y1', color="#83a2d3", alpha=0.5, line_width='width',
                   source=seg_src)

    cr_src = ColumnDataSource(dict(
                x=x_cr,
                y=y_cr,
                name=names,
                boardings=boardings,
                alightings=alightings))

    cr = p.circle(x='x',y='y',color="#83a2d3", size=15, alpha=0.2, hover_color="#83a2d3", hover_alpha=1.0, source = cr_src)

    # Add a hover tool, that sets the link data for a hovered circle
    flow_code = """
    var links = %s;
    var data = {'x0': [], 'y0': [], 'x1': [], 'y1': [], 'width': []};
    var cdata = cb_obj.data;
    var indices =  cb_obj.selected.indices;
    pretext.text = indices.join();
    console.log(cdata);
    var kernel = IPython.notebook.kernel;
    IPython.notebook.kernel.execute("indices = " + indices);
    for (var i = 0; i < indices.length; i++) {
        var ind0 = indices[i]
        for (var j = 0; j < links['segments'][ind0].length; j++) {
            var ind1 = links['segments'][ind0][j];
            data['x0'].push(cdata.x[ind0]);
            data['y0'].push(cdata.y[ind0]);
            data['x1'].push(cdata.x[ind1]);
            data['y1'].push(cdata.y[ind1]);
            data['width'].push(links['width'][ind0][ind1]);
        }
    }
    segment.data = data;
    """ % (links)

    tap_code = """
    var selected= source.selected['0d'].indices
    element.text('tap, you selected:', selected)
    """


    TOOLTIPS = [
        ("Sector", '@name'),
        ("Total Transit Trips From Sector", "@alightings{0,0}"),
        ("Total Transit Trips To Sector", "@boardings{0,0}")
    ]


    index_list = PreText(text='test')
    cr_src.callback = CustomJS(args=dict(segment=seg_src, pretext=index_list), code=flow_code)

    #cr_src.on_change('selection',update)

    p.add_tools(HoverTool(tooltips=TOOLTIPS, renderers=[cr]))

    tap_callback = CustomJS(code = tap_code, args={'source': cr_src})
    p.add_tools(TapTool(renderers=[cr]))

    def selection_change(attrname, old, new):

        indices = index_list.text.split()

        table_text = make_table(model,indices)

        tbl.text = table_text

    cr_src.on_change('selected',selection_change)

    p.add_tile(CARTODBPOSITRON_RETINA)

    return column(p,index_list,tbl)



def transit_calibration(model, survey, rings, rings_pts, metra, cta):

    model_transit = model.loc[(model['transit_mode']!='Auto') & (~model['hhincome'].isin([0,'0']))]
    survey_transit = survey.loc[(survey['transit_mode']!='Auto') & (~survey['hhincome'].isin([0,'0','na']))]

    #transit trips by mode
    transit_chart = transit_mode(model_transit, survey_transit)

    #transit trips by attributes
    income = transit_trips_attr(model_transit, survey_transit, 'hhincome','transit_mode')
    model_income = income[0]
    survey_income = income[1]

    autos = transit_trips_attr(model_transit, survey_transit, 'AutoxAdults','transit_mode')
    model_autos = autos[0]
    survey_autos = autos[1]

    #transit flows
    flows = transit_flows(model_transit,survey_transit)
    model_flows = flows[0]
    survey_Flows = flows[1]

    #map
    model_flows = crosstabs_pct(model_transit,'origin_geo','destination_geo','Model')
    src = make_basemap(rings,'rs2')
    flow = make_flow(model_transit,rings_pts)
    flow_map = make_map(src,flow[0],flow[1],flow[2],flow[3],flow[4],flow[5],model_flows.reset_index())

    tp_1 = Div(text = """<h1># Transit </h1><hr>
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

    tp_2 = Div(text = """<h2>#| Transit Trips..</h2><hr>
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

    tp_3 = Div(text = """<h2>#| Transit Flows..</h2><hr>
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

    tp1_html = Div(text="<h5>Table # - Model Transit Trips By Income</h5>"+model_income.to_html(index=False,
              classes=["table-bordered", "table-hover","text-center","table-condensed","thead-dark"],
              float_format='{:20,.1f}%'.format), css_classes = ["caption"], width = 400)
    tp2_html = Div(text="<h5>Table # - Observed Transit Trips By Income</h5>"+survey_income.to_html(index=False,
              classes=["table-bordered", "table-hover","text-center","table-condensed","thead-dark"],
              float_format='{:20,.1f}%'.format), css_classes = ["caption"], width = 400)

    tp3_html = Div(text="<h5>Table # - Model Transit Trips By Autos & Adults</h5>"+model_autos.to_html(index=False,
              classes=["table-bordered", "table-hover","text-center","table-condensed","thead-dark"],
              float_format='{:20,.1f}%'.format), css_classes = ["caption"], width = 500)
    tp4_html = Div(text="<h5>Table # - Observed Transit Trips By Autos & Adults</h5>"+survey_autos.to_html(index=False,
              classes=["table-bordered", "table-hover","text-center","table-condensed","thead-dark"],
              float_format='{:20,.1f}%'.format), css_classes = ["caption"], width = 500)

    model_flow_html = Div(text="<h5>Table # - Model Transit Trip Flows</h5>"+model_flows.to_html(index=False,
                    classes=["table-bordered", "table-hover","text-center","table-condensed","thead-dark"],
                    float_format='{:20,.1f}%'.format), css_classes = ["caption"], width = column_width)

    survey_flow_html = Div(text="<h5>Table # - Survey Transit Trip Flows</h5>"+survey_Flows.to_html(index=False,
                    classes=["table-bordered", "table-hover","text-center","table-condensed","thead-dark"],
                    float_format='{:20,.1f}%'.format), css_classes = ["caption"],width = column_width)


    source = Div(text="""<small><center>*Observed Trips: <a href="http://www.cmap.illinois.gov/data/transportation/travel-survey">
                2007-08 Travel Tracker Survey</a></center></small>""",width = column_width)

    transit_content = row(column(tp_1,transit_chart,Spacer(height=25),tp_2,Spacer(height=10),
           row(Spacer(width=100), tp1_html,tp3_html, width = column_width),Spacer(height=10),
           row(Spacer(width=100), tp2_html,tp4_html,width = column_width),
           row(source, width = column_width),
           row(Spacer(height=25),tp_3, width = column_width),
           row(flow_map, width = column_width)
           row(model_flow_html, width = column_width),
           row(survey_flow_html, width = column_width)))

    return transit_content

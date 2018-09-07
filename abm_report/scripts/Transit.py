#import libraries
import fiona
import pandas as pd
import numpy as np

import os

#bokeh
from bokeh.plotting import figure,gmap, output_file, save
from bokeh.core.properties import value
from bokeh.transform import factor_cmap, dodge

#color
from bokeh.palettes import Reds6 as palette

from bokeh.layouts import layout, column, row, WidgetBox
from bokeh.models import Panel, Spacer, HoverTool, LogColorMapper, FactorRange, NumeralTickFormatter, ColumnDataSource, TapTool, BoxSelectTool, CustomJS,NumberFormatter
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
#import holoviews as hv

column_width = 1400
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


def crosstabs_pct(df, index, col, value,multiply):
    return (pd.crosstab(index=df[index],columns=df[col],
            values=df[value],aggfunc=sum,margins=True,
            margins_name='Total', normalize='all')*multiply)

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

    model_ct = crosstabs_pct(model_group, index, col, 'Model',100)
    survey_ct = crosstabs_pct(survey_group, index, col, 'Observed',100)

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

def transit_flows(model,survey,multiply):

    def replace_label(df):
        replace = {17:"Illinois",19:"Wisconsin",18:"Indiana",14:"Kendall",12:"Kane",
           11:"DuPage",8:"Cook",7:"Suburban Cook",5:"Chicago",
           13:"Will",15:"McHenry",16:"Lake",9:"Suburban Cook",3:"Chicago",4:"Chicago",1:"Central Business District"}

        df['origAreaGroup'] = df['origAreaGroup'].replace(replace)
        df['destAreaGroup'] = df['destAreaGroup'].replace(replace)
        return df

    model_ct = crosstabs_pct(model,'origin_geo','destination_geo','Model',multiply)
    survey_ct = crosstabs_pct(survey,'origin_geo','destination_geo','Weight2',multiply)

    return model_ct.fillna(0).reset_index(), survey_ct.fillna(0).reset_index()

def getLineCoords(row, geom, coord_type):
    """Returns a list of coordinates ('x' or 'y') of a LineString geometry"""
    if coord_type == 'x':
        return list( row[geom].coords.xy[0] )
    elif coord_type == 'y':
        return list( row[geom].coords.xy[1] )


def make_line(shp):

    shp['x'] = shp.apply(getLineCoords, geom='geometry', coord_type='x', axis=1)

    # Calculate y coordinates of the line
    shp['y'] = shp.apply(getLineCoords, geom='geometry', coord_type='y', axis=1)

    # Make a copy and drop the geometry column
    shp_df = shp.drop('geometry', axis=1).copy()

    # Point DataSource
    source = ColumnDataSource(shp_df)

    return source


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

def make_flow_src(model, survey, points, mf, sf):

    model_od = model.groupby(['origin_geo','destination_geo']).agg({'Model':sum}).reset_index()
    survey_od = survey.groupby(['origin_geo','destination_geo']).agg({'Weight2':sum}).reset_index()

    od_pair = survey_od.merge(model_od, how='left', on = ['origin_geo','destination_geo']).fillna(0)

    points.loc[:,'key'] = points.index

    od_o = points[['key','rs2']].merge(od_pair,how='left',left_on = 'rs2', right_on='origin_geo').fillna(0)
    od_o.columns = ['origin','rs2_origin'] + od_pair.columns.tolist()

    od_od = points[['FID','rs2']].merge(od_o,how='left',left_on = 'rs2', right_on='destination_geo').fillna(0)
    od_od.columns = ['destination','rs2_dest'] + od_o.columns.tolist()


    o = od_pair.groupby(['origin_geo']).agg({'Model':sum, 'Weight2':sum}).reset_index()
    d = od_pair.groupby(['destination_geo']).agg({'Model':sum, 'Weight2':sum}).reset_index()


    od_od['Grouptotal'] = od_od['Weight2'].groupby(od_od['origin']).transform('sum')
    od_od['width'] = ((od_od['Weight2']/od_od['Grouptotal']) * 20).astype(int) + 2


    def make_od(df, rs_pts, o, d, trips):

        points_flow = rs_pts[['rs2','POINT_X','POINT_Y']].merge(df,how='left',
                                                                right_on = 'origin_geo',left_on='rs2').fillna(0)

        points_b = points_flow.merge(o[['origin_geo', trips]],how='left', on ='origin_geo')
        points_b.columns = points_flow.columns.tolist() + ['boardings']
        points_bd = points_b.merge(d[['destination_geo', trips]],how='left',left_on = 'rs2', right_on='destination_geo').fillna(0)
        points_bd.columns = points_b.columns.tolist() + ['destination_geo','alightings']

        return points_bd

    survey_tbl = make_od(sf, points, o, d, 'Weight2')
    survey_tbl.loc[:,'XWI'] = 0.0
    survey_tbl.loc[:,'XIL'] = 0.0
    model_tbl = make_od(mf, points, o, d, 'Model')
    model_tbl.loc[:,'XIL'] = 0.0

    new_survey_columns = survey_tbl.columns[:3].tolist()
    for i in survey_tbl.columns[3:]:
        new_survey_columns.append(i+'_s')

    new_model_columns = model_tbl.columns[:3].tolist()
    for i in model_tbl.columns[3:]:
        new_model_columns.append(i+'_m')


    survey_tbl.columns = new_survey_columns
    model_tbl.columns = new_model_columns


    ms_data = survey_tbl.merge(model_tbl, how='left', on = ['rs2','POINT_X','POINT_Y'])

    ms_data = survey_tbl.merge(model_tbl, how='left', on = ['rs2','POINT_X','POINT_Y'])

    ms_data.loc[:,'origin_geo_diff'] = ms_data['origin_geo_s']

    for i in points['rs2'].values.tolist() + ['Total']:
        ms_data.loc[:,i+'_diff'] = (ms_data[i+'_m']  - ms_data[i+'_s'] ).fillna(0)


    links = {}
    links['segments'] = {}
    links['width'] = {}
    links['names'] = {}

    count = 0
    for i, row in od_od.iterrows():
        if od_od.loc[i,'origin'] in links['segments'].keys():
            links['segments'][od_od.loc[i,'origin']].append(od_od.loc[i,'destination'])
            links['width'][od_od.loc[i,'origin']].append(od_od.loc[i,'width'])

        else:
            links['segments'][od_od.loc[i,'origin']] = [od_od.loc[i,'destination']]
            links['width'][od_od.loc[i,'origin']] = [od_od.loc[i,'width']]
            links['names'][od_od.loc[i,'origin']] = od_od.loc[i,'origin_geo']

    return links, ms_data


def make_table(df,index):

    select = df.loc[index].to_html(index=False,
              classes=["table-hover","text-center","table-condensed"])

    return select



def make_map(poly_src,links,rs_data,transit_lines):

    TOOLS = "pan,wheel_zoom,reset,save"

    TOOLTIPS = [
    ("Sector", "@name"),
    ]

    p = figure(tools=TOOLS, width=column_width,height=500, x_axis_location=None, y_axis_location=None,
                x_range=(-9990000,-9619944), y_range=(5011119,5310000))

    p.grid.grid_line_color = None

    poly = p.patches('x', 'y', source=poly_src, fill_alpha=None,
                     line_color='#66676A', line_width=1)

    line_source = make_line(transit_lines)

    p.multi_line('x', 'y', source=line_source, color='color', line_width=1)

    seg_src = ColumnDataSource({'x0': [], 'y0': [], 'x1': [], 'y1': [], 'width': []})


    seg = p.segment(x0='x0', y0='y0', x1='x1', y1='y1', color="#FFD66E", alpha=0.5, line_width='width',
                   source=seg_src)

    column_names = ['Origin','1','2N','2NW','2S','2SW','2W','2WNW','2WSW',
                    '3IN','3N','3NW','3S','3SW','3W','3WNW','3WSW','4N','4NW',
                    '4SW','4W','4WNW','4WSW','XIN','XWI','XIL','Total']

    cr_src = ColumnDataSource(rs_data)
    cr = p.circle(x='POINT_X',y='POINT_Y',color="#EDBD42",
                  size=15, alpha=0.2, hover_color="#DAA316", hover_alpha=1.0, source = cr_src)


    columns = [TableColumn(field=column_names[0], title=column_names[0])]+\
    [TableColumn(field=col, title=col, formatter=NumberFormatter(format="0.0%")) for col in column_names[1:]]

    tbl_src_m = ColumnDataSource({col : [] for col in column_names})
    tbl_src_s = ColumnDataSource({col : [] for col in column_names})
    tbl_src_d = ColumnDataSource({col : [] for col in column_names})

    mtbl = DataTable(columns=columns, source=tbl_src_m, height = 100, selectable = True, width = column_width,
                         fit_columns = True)

    stbl = DataTable(columns=columns, source=tbl_src_s,   height = 100,selectable = True, width = column_width,
                         fit_columns = True)

    dtbl = DataTable(columns=columns, source=tbl_src_d,   height = 100,selectable = True, width = column_width,
                         fit_columns = True)


    # Add a hover tool, that sets the link data for a hovered circle
    code = """
    var links = %s;
    var data = {'x0': [], 'y0': [], 'x1': [], 'y1': [], 'width': []};
    var cdata = cb_obj.data;
    var indices =  cb_obj.selected.indices;

    function pushTable(source, src_indices, suffix){

        var target = {'Origin' : [], '1' : [], '2N' : [], '2NW' : [], '2S' : [], '2SW' : [],
        '2W' : [], '2WNW' : [], '2WSW': [], '3IN' : [],'3N' : [], '3NW' : [], '3S' : [],
        '3SW' : [],'3W' : [],'3WNW' : [],'3WSW' : [], '4N' : [],'4NW' : [],
        '4SW' : [],'4W' : [],'4WNW' : [],'4WSW' : [],  'XIN' : [],
        'XWI' : [], 'XIL' : [],'Total' : []};


        for (var i = 0; i < src_indices.length; i++) {
            var ind0 = src_indices[i]

            target['Origin'].push(source['origin_geo'+ suffix][ind0]);
            target['1'].push(source['1'+ suffix][ind0]);
            target['2N'].push(source['2N'+ suffix][ind0]);
            target['2NW'].push(source['2NW'+ suffix][ind0]);
            target['2S'].push(source['2S'+ suffix][ind0]);
            target['2SW'].push(source['2SW'+ suffix][ind0]);
            target['2W'].push(source['2W'+ suffix][ind0]);
            target['2WNW'].push(source['2WNW'+ suffix][ind0]);
            target['2WSW'].push(source['2WSW'+ suffix][ind0]);
            target['3IN'].push(source['3IN'+ suffix][ind0]);
            target['3N'].push(source['3N'+ suffix][ind0]);
            target['3NW'].push(source['3NW'+ suffix][ind0]);
            target['3S'].push(source['3S'+ suffix][ind0]);

            target['3SW'].push(source['3SW'+ suffix][ind0]);
            target['3W'].push(source['3W'+ suffix][ind0]);
            target['3WNW'].push(source['3WNW'+ suffix][ind0]);
            target['3WSW'].push(source['3WSW'+ suffix][ind0]);

            target['4N'].push(source['4N'+ suffix][ind0]);
            target['4NW'].push(source['4NW'+ suffix][ind0]);
            target['4SW'].push(source['4SW'+ suffix][ind0]);
            target['4W'].push(source['4W'+ suffix][ind0]);
            target['4WNW'].push(source['4WNW'+ suffix][ind0]);
            target['4WSW'].push(source['4WSW'+ suffix][ind0]);

            target['XIL'].push(source['XIL'+ suffix][ind0]);
            target['XIN'].push(source['XIN'+ suffix][ind0]);
            target['XWI'].push(source['XWI'+ suffix][ind0]);
            target['Total'].push(source['Total'+ suffix][ind0]);
        }

        return target;
    }


    for (var i = 0; i < indices.length; i++){
        var ind0 = indices[i]

        for (var j = 0; j < links['segments'][ind0].length; j++) {
            var ind1 = links['segments'][ind0][j];
            data['x0'].push(cdata.POINT_X[ind0]);
            data['y0'].push(cdata.POINT_Y[ind0]);
            data['x1'].push(cdata.POINT_X[ind1]);
            data['y1'].push(cdata.POINT_Y[ind1]);
            data['width'].push(links['width'][ind0][ind1]);
        }
    }

    segment.data = data;

    model_source.data = pushTable(cdata, indices, '_m');
    survey_source.data = pushTable(cdata, indices, '_s');
    diff_source.data = pushTable(cdata, indices, '_diff');

    model_source.trigger('change');
    survey_source.trigger('change');
    diff_source.trigger('change');

    model_tbl.trigger('change');
    survey_tbl.trigger('change');
    diff_tbl.trigger('change');

    """ % (links)

    TOOLTIPS = [
        ("Sector", '@rs2'),
        ("Total Transit Trips From Sector", "@alightings_s{0,0}"),
        ("Total Transit Trips To Sector", "@boardings_s{0,0}")
    ]


    cr_src.callback = CustomJS(args=dict(segment=seg_src, model_source = tbl_src_m, survey_source = tbl_src_s,
                                         diff_source = tbl_src_d,
                                         model_tbl = mtbl, survey_tbl = stbl, diff_tbl = dtbl), code=code)


    p.add_tools(HoverTool(tooltips=TOOLTIPS, renderers=[cr]))
    p.add_tools(TapTool(renderers=[cr]))
    #p.add_tools(BoxSelectTool(renderers=[cr]))

    p.add_tile(CARTODBPOSITRON_RETINA)

    return p, mtbl, stbl, dtbl



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
    flows = transit_flows(model_transit,survey_transit,1)
    model_flows = flows[0]
    survey_flows = flows[1]

    #map
    transit_lines = gpd.read_file(metra).append(gpd.read_file(cta))
    transit_lines.loc[:,'color'] = np.where(transit_lines['LEGEND'].isnull(),"#3F4FB5","#051057")

    src = make_basemap(rings,'rs2')
    flow = make_flow_src(model_transit, survey_transit, rings_pts, model_flows.reset_index(),survey_flows.reset_index())
    flow_map = make_map(src,flow[0],flow[1],transit_lines)



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

    model_flow_html = Div(text="<h5>Table # - Model Transit Trip Flows</h5>", css_classes = ["caption"], width = column_width)

    survey_flow_html = Div(text="<h5>Table # - Survey Transit Trip Flows</h5>", css_classes = ["caption"],width = column_width)

    diff_flow_html = Div(text="<h5>Table # - Survey & Model Transit Trip Flow Comparison</h5>", css_classes = ["caption"],width = column_width)

    # model_flow_html = Div(text="<h5>Table # - Model Transit Trip Flows</h5>"+model_flows.to_html(index=False,
    #                 classes=["table-bordered", "table-hover","text-center","table-condensed","thead-dark"],
    #                 float_format='{:20,.1f}%'.format), css_classes = ["caption"], width = column_width)
    #
    # survey_flow_html = Div(text="<h5>Table # - Survey Transit Trip Flows</h5>"+survey_Flows.to_html(index=False,
    #                 classes=["table-bordered", "table-hover","text-center","table-condensed","thead-dark"],
    #                 float_format='{:20,.1f}%'.format), css_classes = ["caption"],width = column_width)


    source = Div(text="""<small><center>*Observed Trips: <a href="http://www.cmap.illinois.gov/data/transportation/travel-survey">
                2007-08 Travel Tracker Survey</a></center></small>""",width = column_width)

    transit_content = row(column(tp_1,transit_chart,Spacer(height=25),tp_2,Spacer(height=10),
           row(Spacer(width=100), tp1_html,tp3_html, width = column_width),Spacer(height=10),
           row(Spacer(width=100), tp2_html,tp4_html,width = column_width),
           row(source, width = column_width),
           row(Spacer(height=25),tp_3, width = column_width),
           row(flow_map[0], width = column_width),
           row(model_flow_html, width = column_width),
           row(flow_map[1], width = column_width),
           row(survey_flow_html, width = column_width),
           row(flow_map[2], width = column_width),
           row(diff_flow_html, width = column_width),
           row(flow_map[3], width = column_width)))

    return transit_content

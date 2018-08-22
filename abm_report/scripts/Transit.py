import pandas as pd
import numpy as np
import os

#bokeh modules
from bokeh.plotting import figure,gmap
from bokeh.core.properties import value
from bokeh.transform import factor_cmap, dodge
from bokeh.layouts import layout, column, row
from bokeh.models import Panel, Spacer, HoverTool, ColumnDataSource, FactorRange,NumeralTickFormatter
from bokeh.models.widgets import Div, Tabs, Paragraph, Dropdown, Button, PreText, Toggle, TableColumn, DataTable

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
         ('Observed - Transit Trip',"@Observed*100{0.0}%"),
         ('Model - Transit Trip',"@Model*100{0.0}%")
    ]

    # Styling
    p.yaxis.formatter = NumeralTickFormatter(format='0.0f%')

    p.legend.click_policy="hide"

    return p


def crosstabs_pct(df, index, col, value):
    return (pd.crosstab(index=df[index],columns=df[col],
            values=df[value],aggfunc=sum,margins=True,
            margins_name='Total', normalize='all')*100)

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

def transit_calibration(model, survey):

    model_transit = model.loc[(model['transit_mode']!='Auto') & (~model['hhincome'].isin([0,'0']))]
    survey_transit = survey.loc[(survey['transit_mode']!='Auto') & (~survey['hhincome'].isin([0,'0']))]

    #transit trips by mode
    transit_chart = transit_mode(model_transit, survey_transit)

    income = transit_trips_attr(model_transit, survey_transit, 'hhincome','transit_mode')
    model_income = income[0]
    survey_income = income[1]

    autos = transit_trips_attr(model_transit, survey_transit, 'AutoxAdults','transit_mode')
    model_autos = autos[0]
    survey_autos = autos[1]

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

    transit_content = row(column(tp_1,transit_chart,Spacer(height=25),tp_2,Spacer(height=10),
           row(Spacer(width=100), tp1_html,tp3_html, width = column_width),Spacer(height=10),
           row(Spacer(width=100), tp2_html,tp4_html, width = column_width)))

    return transit_content

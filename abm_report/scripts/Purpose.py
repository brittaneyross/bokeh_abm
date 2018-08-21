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

def trip_purpose(trips,survey):

    column_width = 965
    column_width = 1000
    bar_height = 500
    census_color = "#EFF1EF"
    survey_color = '#9EA499'
    cmap_color = '#495667'

    def tripsXpurpose(trips,survey):
        mtrips = trips.groupby('trip_purpose').agg({'Model':sum}).astype(int)
        strips = survey.groupby('trip_purpose').agg({'Weight2':sum}).astype(int)
        strips.columns = ['Survey']

        trips = strips.merge(mtrips, how='left', left_index=True, right_index=True).astype(int)

        trips.loc[:,'Model Share'] = ((trips['Model']/trips['Model'].sum()) *100)
        trips.loc[:,'Survey Share'] = ((trips['Survey']/trips['Survey'].sum()) *100)
        trips.loc['Total'] = trips.sum()

        shares = trips[['Model Share','Survey Share']]
        shares.columns = ['Model','Survey']
        shares.loc[:,'Difference'] = (shares['Model'] - shares['Survey'])
        shares.loc[:,'% Difference'] = ((shares['Difference']/shares['Survey']) * 100)

        trips.loc[:,'Difference'] = (trips['Model'] - trips['Survey']).round(1).astype(int)
        trips.loc[:,'% Difference'] = ((trips['Difference']/trips['Survey']) * 100)


        trip_purpose = trips[['Survey','Model','Difference','% Difference']].reset_index()
        trip_purpose.columns = ['Purpose','Observed','Model','Difference','% Difference']

        purpose_shares = shares[['Survey','Model','Difference','% Difference']].reset_index()
        purpose_shares.columns = ['Purpose','Observed','Model','Difference','% Difference']

        return trip_purpose, purpose_shares


    def filter_trips(trips, pertype_select):

        if pertype_select == 'All' or pertype_select is None:
            t = trips['type'].drop_duplicates().values.tolist()
        else:
            t= [pertype_select]


        select_trips =  trips.loc[(trips['type'].isin(t))]
        survey_trips = survey.loc[(survey['type'].isin(t))]

        mtrips = select_trips.groupby('trip_purpose').agg({'Model':sum})
        strips = survey_trips.groupby('trip_purpose').agg({'Weight2':sum})
        strips.columns = ['Survey']

        trips_ = mtrips.merge(strips, how='left', left_index=True, right_index=True)

        return trips_

    #graphic functions
    TOOLS = "reset,hover,save"

    #make src data
    def make_src(df):

        df.sort_values(by='Survey',ascending=False, inplace=True)

        groupby = df.index.values.tolist()
        survey = df['Survey'].values.tolist()
        model = df['Model'].values.tolist()

        data = {'Group': groupby,
               'Observed': survey,
               'Model': model}

        return ColumnDataSource(data=data)

    #make groupbed bar chart
    def makeGroupBar(src):

        groups = trips.trip_mode.drop_duplicates().values.tolist()

        p = figure(x_range=FactorRange(*groups),
                   plot_width = column_width, plot_height = bar_height,
                   tools="hover",toolbar_location = None)

        p.vbar(x=dodge('Group',-0.25,range=p.x_range),top='Observed', width=0.25, source=src,
               color=survey_color, legend=value("Observed"))

        p.vbar(x=dodge('Group',0,range=p.x_range),top='Model', width=0.25, source=src,
               color=cmap_color, legend=value("Model"))

        p.select_one(HoverTool).tooltips = [
             ('Observed - Trips',"@Observed{0,}"),
             ('Model - Trips',"@Model{0,}")
        ]

        # Styling
        p = style(p)

        p.legend.click_policy="hide"

        return p

    def style(p):

        p.xgrid.visible = False
        p.ygrid.visible = False

        p.yaxis.formatter = NumeralTickFormatter(format="0,")

        return p

    def update(attr, old, new):

        type_select = type_selection.value

        perTypeTrips = filter_trips(trips, type_select)

        new_src_type = make_src(perTypeTrips)
        src_type.data.update(new_src_type.data)

        type_title.text = "<h5>Figure # - %s Trips by Mode (Select person type from dropdown)</h5>" % (type_select)

    #Dropdown#---------------------------------------------------------------------------------------------------
    type_menu = [('All','All'),
             ('Child Too Young For School','Child too young for school'),
             ('Full-Time Worker','Full-time worker'),
             ('Non-Worker','Non-worker'),
             ('Part-Time Worker','Part-time worker'),
             ('Retired','Retired'),
             ('Student Of Driving Age','Student of driving age'),
             ('Student Of Non-Driving Age','Student of non-driving age')]

    #Widgets
    type_selection = Dropdown(label="Person Type", button_type="default",
                                 menu=type_menu, width=250)

    #onchange
    type_selection.on_change('value', update)

    #create initial bar chart
    perTypeTrips = filter_trips(trips,'All')

    #if purpose_selection.value == None:
    #    purpose_selection.value = 'All'

    type_title = Div(text= "<h5>Figure # - %s Trips by Purpose (Select person type from dropdown)</h5>" % ('All'),
                   width = column_width)

    src_type = make_src(perTypeTrips)
    typeBarChart = makeGroupBar(src_type)

    #Trip Purpose
    ptrips = tripsXpurpose(trips,survey)
    trip_purpose = ptrips[0]
    share = ptrips[1]

    purp_html = Div(text="<h5>Table # - Trips by Purpose</h5>"+trip_purpose.to_html(index=False,
              classes=["table-bordered", "table-hover","text-center","table-condensed","thead-dark"],
              formatters = [str,'{:20,}'.format,'{:20,}'.format,'{:20,}'.format,'{:20,.1f}%'.format]),
              css_classes = ["caption"], width = 500)

    purpshare_html = Div(text="<h5>Table # - Trip Share by Purpose</h5>"+share.to_html(index=False,
              classes=["table-bordered", "table-hover","text-center","table-condensed","thead-dark"],
              float_format='{:20,.1f}%'.format),css_classes = ["caption"],width = 500)

    source = Div(text="""<small><center>*Observed Trips: <a href="http://www.cmap.illinois.gov/data/transportation/travel-survey">
                    2007-08 Travel Tracker Survey</a></center></small>""",width = column_width, css_classes = ["caption", "text-center"])


    h_1 = Div(text = """<h1># Calibrating Travel Purpose</h1><hr>
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


    l_1 = row(column(h_1,Spacer(height=25),
           row(purp_html,Spacer(width=50),purpshare_html,width=column_width),
           row(type_selection),
           row(source,Div(text="<hr>",width=column_width),width = column_width, css_classes = ["caption", "text-center"])))

    return l_1

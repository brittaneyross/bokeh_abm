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

def mode_choice(trips_df, survey_df, survey_hh):

    column_width = 2000
    column_width = 1000
    bar_height = 500
    census_color = "#EFF1EF"
    survey_color = '#9EA499'
    cmap_color = '#495667'

    def filter_trips(trips, mode_select, purp_select, pertype_select):

        if mode_select == 'All' or mode_select is None:
            m = trips.trip_mode.drop_duplicates().values.tolist()
        else:
            m = [mode_select]

        if purp_select == 'All' or purp_select is None:
            p = trips.trip_purpose.drop_duplicates().values.tolist()
        else:
            p= [purp_select]

        if pertype_select == 'All' or pertype_select is None:
            t = trips.type.drop_duplicates().values.tolist()
        else:
            t= [pertype_select]


        select_trips =  trips.loc[(trips['trip_purpose'].isin(p)) & (trips['type'].isin(t))]
        survey_trips = survey_df.loc[(survey_df['trip_purpose'].isin(p)) & (survey_df['type'].isin(t))]

        mtrips = select_trips.groupby('trip_mode').agg({'Model':sum})
        strips = survey_trips.groupby('trip_mode').agg({'Weight2':sum})
        strips.columns = ['Survey']

        trips = mtrips.merge(strips, how='left', left_index=True, right_index=True)


        numtrips = "{:,}".format(select_trips.Model.sum())

        return trips


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

        groups = trips_df.trip_mode.drop_duplicates().values.tolist()

        p = figure(x_range=FactorRange(*groups),
                   plot_width = column_width, plot_height = bar_height,
                   tools="hover",toolbar_location = None)

        p.vbar(x=dodge('Group',-0.25,range=p.x_range),top='Observed', width=0.25, source=src,
               color=survey_color, legend=value("Observed"))

        p.vbar(x=dodge('Group',0,range=p.x_range),top='Model', width=0.25, source=src,
               color=cmap_color, legend=value("Model"))

        p.select_one(HoverTool).tooltips = [
             ('Observed - Trip',"@Observed{0,}"),
             ('Model - Trip',"@Model{0,}")
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

        p_select, type_select = purpose_selection.value,  type_selection.value

        purposeTrips = filter_trips(trips_df,'All',p_select,'All')
        perTypeTrips = filter_trips(trips_df,'All','All', type_select)

        #numtrips.text = ftrips[0] + " | <text style='color:Gray'>100</div> Trips"

        new_src_purp = make_src(purposeTrips)
        src_purp.data.update(new_src_purp.data)

        new_src_type = make_src(perTypeTrips)
        src_type.data.update(new_src_type.data)

        purp_title.text = "<h5>Figure # - %s Trips by Mode (Select trip purpose from dropdown)</h5>" % (p_select)
        type_title.text = "<h5>Figure # - %s Trips by Mode (Select person type from dropdown)</h5>" % (type_select)

    #Dropdown#---------------------------------------------------------------------------------------------------
    purpose_menu = [('All','All'),
             ('Discretionary','Discretionary'),
             ('Eating Out','Eating Out'),
             ('Escort','Escort'),
             ('Maintenance','Maintenance'),
             ('School','School'),
             ('Shop','Shopping'),
             ('University','University'),
             ('Visiting','Visiting'),
             ('Work','Work'),
             ('Work-Based','Work-Based')]

    type_menu = [('All','All'),
             ('Child Too Young For School','Child too young for school'),
             ('Full-Time Worker','Full-time worker'),
             ('Non-Worker','Non-worker'),
             ('Part-Time Worker','Part-time worker'),
             ('Retired','Retired'),
             ('Student Of Driving Age','Student of driving age'),
             ('Student Of Non-Driving Age','Student of non-driving age')]

    #Widgets
    purpose_selection = Dropdown(label="Trip Purpose", button_type="default",
                                 menu=purpose_menu, width=250)

    type_selection = Dropdown(label="Person Type", button_type="default",
                                 menu=type_menu, width=250)

    #onchange
    purpose_selection.on_change('value', update)
    type_selection.on_change('value', update)

    #create initial bar chart
    purposeTrips = filter_trips(trips_df,'All','All','All')
    perTypeTrips = filter_trips(trips_df,'All','All','All')

    #if purpose_selection.value == None:
    #    purpose_selection.value = 'All'

    purp_title = Div(text= "<h5>Figure # - %s Trips by Mode (Select trip purpose from dropdown)</h5>" % ('All'),
                   width = column_width)

    type_title = Div(text= "<h5>Figure # - %s Trips by Mode (Select person type from dropdown)</h5>" % ('All'),
                   width = column_width)

    src_purp = make_src(purposeTrips)
    purpBarChart = makeGroupBar(src_purp)

    src_type = make_src(perTypeTrips)
    typeBarChart = makeGroupBar(src_type)

    #---------------------------------------------------------------------------------------------------------------

    h_4 = Div(text = """<h1># Trip Mode Choice</h1><hr>
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
                amet..", comes from a line in section 1.10.32.</p>
                <p>The standard chunk of Lorem Ipsum used since the 1500s is reproduced below
                for those interested. Sections 1.10.32 and 1.10.33 from "de Finibus Bonorum et
                Malorum" by Cicero are also reproduced in their exact original form, accompanied
                by English versions from the 1914 translation by H. Rackham.</p>""",
                width = column_width, sizing_mode='stretch_both',
                style={"width":'100%',"text-align":'left',"margin":'0 auto'})

    source = Div(text="""<small><center>*Observed Trips: <a href="http://www.cmap.illinois.gov/data/transportation/travel-survey">
                2007-08 Travel Tracker Survey</a></center></small>""",width = column_width)

    mode_content = row(column(h_4,Spacer(height=25),
           row(purpose_selection,width=column_width),
           purp_title,purpBarChart,Spacer(height=25),
           row(type_selection,width=column_width),
           type_title,typeBarChart,source))


    return mode_content

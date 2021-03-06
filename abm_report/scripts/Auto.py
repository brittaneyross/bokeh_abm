import pandas as pd
import numpy as np
import os, sys

#bokeh modules
from bokeh.plotting import figure,gmap
from bokeh.core.properties import value
from bokeh.transform import factor_cmap, dodge
from bokeh.layouts import layout, column, row
from bokeh.models import Panel, Spacer, HoverTool, ColumnDataSource, FactorRange,NumeralTickFormatter
from bokeh.models.widgets import Div, Tabs, Paragraph, Dropdown, Button, PreText, Toggle, TableColumn, DataTable

def auto_ownership(ao_counts,survey_income,survey_size,survey_workers,
                    ctpp_income,ctpp_size,ctpp_workers,
                    model_income,model_size,model_workers):

    full_width = 2000
    column_width = 1400
    bar_height = 500
    census_color = "#EFF1EF"
    survey_color = '#9EA499'
    cmap_color = '#495667'
    #graphic functions
    TOOLS = "reset,hover,save"

    #make src data
    def make_group_bar(df):

        groups = df.index.values.tolist()
        census = df['Census'].values.tolist()
        survey = df['Survey'].values.tolist()
        model = df['Model'].values.tolist()

        data = {'Group': groups,
               'Census': census,
               'Survey': survey,
               'Model': model}

        src = ColumnDataSource(data=data)

        TOOLS = "hover"

        p = figure(x_range=FactorRange(*groups),title="Figure 1 - Auto Ownership Distribution",
                   plot_width = column_width, plot_height = bar_height, tools="hover")

        p.vbar(x=dodge('Group',-0.25,range=p.x_range),top='Census', width=0.25, source=src,
               color=census_color, legend=value("Census"))

        p.vbar(x=dodge('Group',0,range=p.x_range),top='Survey', width=0.25, source=src,
               color=survey_color, legend=value("Survey"))

        p.vbar(x=dodge('Group',0.25,range=p.x_range),top='Model', width=0.25, source=src,
               color=cmap_color, legend=value("Model"))

        p.select_one(HoverTool).tooltips = [
             ('Census - Household Total',"@Census{0,}"),
             ('Survey - Household Total',"@Survey{0,}"),
             ('Model - Household Total',"@Model{0,}")
        ]

        # Styling
        p = bar_style(p)

        p.legend.click_policy="hide"

        return p

    #make groupbed bar chart
    #plot_height = full_width/4

    def bar_style(p):

        p.xgrid.visible = False
        p.ygrid.visible = False

        p.yaxis.formatter = NumeralTickFormatter(format="0,")

        return p


    # #css_classes= ["well"],
    #style={"width":'100%',"text-align":'left',"margin":'0 auto'}

    #left side column
    left_col = Div(text="""<h4>place holder</h4>""")
    right_col = Div(text="""<h4>figures</h4>""")

    h_2 = Div(text="""<h2># Auto Ownership</h2><hr>
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
                width=column_width,sizing_mode='scale_both')

    #Auto Ownership Graph
    ao_graph = make_group_bar(ao_counts)
    #
    source = Div(text="""Sources - Census: <a href="http://data5.ctpp.transportation.org/ctpp/Browse/browsetables.aspx">
                2006 - 2010 CTPP 5-Year Data Set</a> | Survey: <a href="http://www.cmap.illinois.gov/data/transportation/travel-survey">
                2007-08 Travel Tracker Survey</a>""",width = column_width, css_classes = ["caption", "text-center"])

    h_2_1 = row(column(ao_graph,source, width = column_width))

    #---------------------------------------------------------------------------------------------------------------
    #Auto Ownership by Household Characteristic Tables
    h_2_2 = Div(text = """<h2># | Auto Ownership By Household Characteristics</h2><hr>
                <p>ontrary to popular belief, Lorem Ipsum is not simply random text. It
                has roots in a piece of classical Latin literature from 45 BC, making it
                over 2000 years old. Richard McClintock, a Latin professor at Hampden-Sydney
                College in Virginia, looked up one of the more obscure Latin words,
                consectetur, from a Lorem Ipsum passage, and going through the cites
                of the word in classical literature, discovered the undoubtable source.
                Lorem Ipsum comes from sections 1.10.32 and 1.10.33 of "de Finibus Bonorum
                et Malorum" (The Extremes of Good and Evil) by Cicero, written in 45 BC.</p>""",
                width = column_width, sizing_mode='scale_both')


    #Tables
    #ADD FORMATS
    tbl_income = Div(text="<h4><center>Auto Ownership By Household Income</center></h4><hr>",width=column_width,css_classes = ["text-center"])

    s1_html = Div(text="<h5>Table 1 - Survey Income</h5>"+survey_income.to_html(index=False,
              classes=["table-bordered", "table-hover","text-center","table-condensed","thead-dark"],
              float_format='{:20,.1f}%'.format), css_classes = ["caption"])

    c1_html = Div(text="<h5>Table 2 - CTPP Income</h5>"+ctpp_income.to_html(index=False,
              classes=["table-bordered", "table-hover","text-center","table-condensed","thead-dark"],
              float_format='{:20,.1f}%'.format), css_classes = ["caption"])

    m1_html = Div(text="<h5>Table 3 - Model Income</h5>"+model_income.to_html(index=False,
              classes=["table-bordered", "table-hover","text-center","table-condensed","thead-dark"],
              float_format='{:20,.1f}%'.format), css_classes = ["caption"])


    tbl_size = Div(text="<h4><center>Auto Ownership By Household Size</center></h4><hr>",width=column_width)

    s2_html = Div(text="<h5>Table 4 - Survey Household Size</h5>"+survey_size.to_html(index=False,
              classes=["table-bordered", "table-hover","text-center","table-condensed","thead-dark"],
              float_format='{:20,.1f}%'.format), css_classes = ["caption"])

    c2_html = Div(text="<h5>Table 5 - CTPP Household Size</h5>"+ctpp_size.to_html(index=False,
              classes=["table-bordered", "table-hover","text-center","table-condensed","thead-dark"],
              float_format='{:20,.1f}%'.format), css_classes = ["caption"])

    m2_html = Div(text="<h5>Table 6 - Model Household Size</h5>"+model_size.to_html(index=False,
              classes=["table-bordered", "table-hover","text-center","table-condensed","thead-dark"],
              float_format='{:20,.1f}%'.format), css_classes = ["caption"])

    tbl_workers = Div(text="<h4><center>Auto Ownership By Workers In Household</center></h4><hr>",width=column_width)

    s3_html = Div(text="<h5>Table 7 - Survey Workers</h5>"+survey_workers.to_html(index=False,
              classes=["table-bordered", "table-hover","text-center","table-condensed","thead-dark"],
              float_format='{:20,.1f}%'.format), css_classes = ["caption"])

    c3_html = Div(text="<h5>Table 8 - CTPP Workers</h5>"+ctpp_workers.to_html(index=False,
              classes=["table-bordered", "table-hover","text-center","table-condensed","thead-dark"],
              float_format='{:20,.1f}%'.format), css_classes = ["caption"])

    m3_html = Div(text="<h5>Table 9 - Model Workers</h5>"+model_workers.to_html(index=False,
              classes=["table-bordered", "table-hover","text-center","table-condensed","thead-dark"],
              float_format='{:20,.1f}%'.format), css_classes = ["caption"])

    ao = row(column(h_2,h_2_1,Spacer(height = 25),h_2_2,Spacer(height = 25),tbl_income,
                          row(s1_html,Spacer(width=50),c1_html,Spacer(width=50),m1_html),
                          Spacer(height = 25),tbl_size,
                          row(s2_html,Spacer(width=50),c2_html,Spacer(width=50),m2_html),
                          Spacer(height = 25),tbl_workers,
                          row(s3_html,Spacer(width=50),c3_html,Spacer(width=50),m3_html),
                          css_classes = ["col-lg-12"], width = column_width))

    return ao

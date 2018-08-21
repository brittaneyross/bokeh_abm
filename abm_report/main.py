# Pandas for data management
import pandas as pd

from os.path import dirname, join
# Bokeh basics
from bokeh.io import curdoc
from bokeh.models.widgets import Tabs

#bokeh modules
from bokeh.plotting import figure,gmap
from bokeh.core.properties import value
from bokeh.transform import factor_cmap, dodge
from bokeh.layouts import layout, column, row
from bokeh.models import Panel, Spacer, HoverTool, ColumnDataSource, FactorRange,NumeralTickFormatter
from bokeh.models.widgets import Div, Tabs, Paragraph, Dropdown, Button, PreText, Toggle, TableColumn, DataTable


ao_counts = pd.read_csv(join(dirname(__file__),'data','aoCounts.csv'),index_col=[0])
#
# survey_income = pd.read_csv(join(dirname(__file__),'data','income_survey.csv'))
# survey_size = pd.read_csv(join(dirname(__file__),'data','size_survey.csv'))
# survey_workers = pd.read_csv(join(dirname(__file__),'data','workers_survey.csv'))
#
# ctpp_income = pd.read_csv(join(dirname(__file__),'data','income_ctpp.csv'))
# ctpp_size = pd.read_csv(join(dirname(__file__),'data','size_ctpp.csv'))
# ctpp_workers = pd.read_csv(join(dirname(__file__),'data','workers_ctpp.csv'))
#
# model_income = pd.read_csv(join(dirname(__file__),'data','income_model.csv'))
# model_size = pd.read_csv(join(dirname(__file__),'data','size_model.csv'))
# model_workers = pd.read_csv(join(dirname(__file__),'data','workers_model.csv'))

def auto_ownership():

    full_width = 2000
    column_width = 1000
    census_color = "#EFF1EF"
    survey_color = '#9EA499'
    cmap_color = '#495667'
    #graphic functions
    TOOLS = "reset,hover,save"

    #make src data
    def make_src(df):

        groupby = df.index.values.tolist()
        census = df['Census'].values.tolist()
        survey = df['Survey'].values.tolist()
        model = df['Model'].values.tolist()

        data = {'Group': groupby,
               'Census': census,
               'Survey': survey,
               'Model': model}

        return ColumnDataSource(data=data), groupby, data

    #make groupbed bar chart
    #plot_height = full_width/4
    def makeGroupBar(src, groups, data):

        p = figure(x_range=FactorRange(*groups),title="Figure 1 - Auto Ownership Distribution",
                   plot_width = column_width, plot_height = column_width/2,
                   tools="hover",toolbar_location = None)

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
        p = style(p)

        p.legend.click_policy="hide"

        return p

    def style(p):

        p.xgrid.visible = False
        p.ygrid.visible = False

        p.yaxis.formatter = NumeralTickFormatter(format="0,")

        return p


    # #css_classes= ["well"],
    #style={"width":'100%',"text-align":'left',"margin":'0 auto'}

    #left side column
    left_col = Div(text="""<h4>place holder</h4>""")
    right_col = Div(text="""<h4>figures</h4>""")

    h_2 = Div(text="""<h2># Auto Ownership</h2>
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
    # ao_src = make_src(ao_counts)
    # ao_graph = makeGroupBar(ao_src[0], ao_src[1], ao_src[2])
    #
    # source = Div(text="""Sources - Census: <a href="http://data5.ctpp.transportation.org/ctpp/Browse/browsetables.aspx">
    #             2006 - 2010 CTPP 5-Year Data Set</a> | Survey: <a href="http://www.cmap.illinois.gov/data/transportation/travel-survey">
    #             2007-08 Travel Tracker Survey</a>""",width = column_width, css_classes = ["caption", "text-center"])
    #
    # h_2_1 = row(column(ao_graph,source, width = column_width))

    #---------------------------------------------------------------------------------------------------------------
    #Auto Ownership by Household Characteristic Tables
    h_2_2 = Div(text = """<h2># | Auto Ownership By Household Characteristics</h2>
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
    tbl_income = Div(text="<h4><center>Auto Ownership By Household Income</center></h4>",width=column_width,css_classes = ["text-center"])

    # s1_html = Div(text="<h5>Table 1 - Survey Income</h5>"+survey_income.to_html(index=False,
    #           classes=["table-bordered", "table-hover","text-center","table-condensed","thead-dark"],
    #           float_format='{:20,.1f}%'.format), css_classes = ["caption"])
    #
    # c1_html = Div(text="<h5>Table 2 - CTPP Income</h5>"+ctpp_income.to_html(index=False,
    #           classes=["table-bordered", "table-hover","text-center","table-condensed","thead-dark"],
    #           float_format='{:20,.1f}%'.format), css_classes = ["caption"])
    #
    # m1_html = Div(text="<h5>Table 3 - Model Income</h5>"+model_income.to_html(index=False,
    #           classes=["table-bordered", "table-hover","text-center","table-condensed","thead-dark"],
    #           float_format='{:20,.1f}%'.format), css_classes = ["caption"])
    #
    #
    # tbl_size = Div(text="<h4><center>Auto Ownership By Household Size</center></h4>",width=column_width)
    #
    # s2_html = Div(text="<h5>Table 4 - Survey Household Size</h5>"+survey_size.to_html(index=False,
    #           classes=["table-bordered", "table-hover","text-center","table-condensed","thead-dark"],
    #           float_format='{:20,.1f}%'.format), css_classes = ["caption"])
    #
    # c2_html = Div(text="<h5>Table 5 - CTPP Household Size</h5>"+ctpp_size.to_html(index=False,
    #           classes=["table-bordered", "table-hover","text-center","table-condensed","thead-dark"],
    #           float_format='{:20,.1f}%'.format), css_classes = ["caption"])
    #
    # m2_html = Div(text="<h5>Table 6 - Model Household Size</h5>"+model_size.to_html(index=False,
    #           classes=["table-bordered", "table-hover","text-center","table-condensed","thead-dark"],
    #           float_format='{:20,.1f}%'.format), css_classes = ["caption"])
    #
    # tbl_workers = Div(text="<h4><center>Auto Ownership By Workers In Household</center></h4>",width=column_width)
    #
    # s3_html = Div(text="<h5>Table 7 - Survey Workers</h5>"+survey_workers.to_html(index=False,
    #           classes=["table-bordered", "table-hover","text-center","table-condensed","thead-dark"],
    #           float_format='{:20,.1f}%'.format), css_classes = ["caption"])
    #
    # c3_html = Div(text="<h5>Table 8 - CTPP Workers</h5>"+ctpp_workers.to_html(index=False,
    #           classes=["table-bordered", "table-hover","text-center","table-condensed","thead-dark"],
    #           float_format='{:20,.1f}%'.format), css_classes = ["caption"])
    #
    # m3_html = Div(text="<h5>Table 9 - Model Workers</h5>"+model_workers.to_html(index=False,
    #           classes=["table-bordered", "table-hover","text-center","table-condensed","thead-dark"],
    #           float_format='{:20,.1f}%'.format), css_classes = ["caption"])

    # ao = [  column(row(Spacer(),height = 50),
    #         row(column(Spacer(), css_classes = ["col-lg-3", "text-center"]),
    #         column(left_col, css_classes = ["col-lg-3", "text-center"]),
    #         #
    #         # Center column with report content
    #            row(column(h_2,h_2_1,h_2_2,tbl_income,
    #                       row(s1_html,Spacer(width=50),c1_html,Spacer(width=50),m1_html),
    #                       tbl_size,
    #                       row(s2_html,Spacer(width=50),c2_html,Spacer(width=50),m2_html),
    #                       tbl_workers,
    #                       row(s3_html,Spacer(width=50),c3_html,Spacer(width=50),m3_html),
    #                       css_classes = ["col-lg-12"], width = column_width)),
    #         #
    #         #Right Side Panel
    #            column(right_col, css_classes = ["col-lg-3","text-center"]),
    #
    #         #Page Attributes
    #            css_classes = ["container-fluid"], width = 1800))]

    ao = [row(Spacer(),height = 50),
            row(column(Spacer(), css_classes = ["col-lg-3", "text-center"]),
            column(left_col, css_classes = ["col-lg-3", "text-center"]),
            #
            # Center column with report content
               row(column(h_2)))]

    return ao

#sys.path.insert(0,join(os.getcwd(),'abm_report','scripts'))
#print(join(os.getcwd(),'abm_report','scripts'))

#Tabs from scripts
#from scripts.Auto import auto_ownership
#where data should exit
#data_cwd = join(dirname(__file__),'data')

def test_tab():

    h_1 = Div(text = """<h1><center>Intro Text</center></h1>""")

    l_1 = layout(children=[h_1])

    tab_1 = Panel(child=l_1, title = '# Introduction')

    return tab_1

ao = auto_ownership()
    #flow = Flow()
    #modechoice = ModeChoice(person_trips,survey_trips)
    #tpurp = TripPurpose(person_trips,survey_trips)

    #l_2 = layout(children=ao+flow+modechoice+tpurp)
l_2 = layout(children=[ao])
tab2 =  Panel(child=l_2, title = '# Model Calibration')

# Create each of the tabs
tab1 = test_tab()

# Put all the tabs into one application
tabs = Tabs(tabs = [tab1,tab2], sizing_mode = "stretch_both")
#tabs = Tabs(tabs = [tab1])

# Put the tabs in the current document for display
curdoc().add_root(tabs)

# Pandas for data management
import pandas as pd

from os.path import dirname, join
# Bokeh basics
from bokeh.io import curdoc
#bokeh modules
from bokeh.plotting import figure
from bokeh.core.properties import value
from bokeh.transform import factor_cmap, dodge
from bokeh.layouts import layout, column, row
from bokeh.models import Panel, Spacer, HoverTool, ColumnDataSource, FactorRange,NumeralTickFormatter
from bokeh.models.widgets import Div, Tabs

from scripts.Auto import auto_ownership

ao_counts = pd.read_csv(join(dirname(__file__),'data','aoCounts.csv'),index_col=[0])

survey_income = pd.read_csv(join(dirname(__file__),'data','income_survey.csv'))
survey_size = pd.read_csv(join(dirname(__file__),'data','size_survey.csv'))
survey_workers = pd.read_csv(join(dirname(__file__),'data','workers_survey.csv'))

ctpp_income = pd.read_csv(join(dirname(__file__),'data','income_ctpp.csv'))
ctpp_size = pd.read_csv(join(dirname(__file__),'data','size_ctpp.csv'))
ctpp_workers = pd.read_csv(join(dirname(__file__),'data','workers_ctpp.csv'))

model_income = pd.read_csv(join(dirname(__file__),'data','income_model.csv'))
model_size = pd.read_csv(join(dirname(__file__),'data','size_model.csv'))
model_workers = pd.read_csv(join(dirname(__file__),'data','workers_model.csv'))


#get tab contents
#auto ownership content
ao = auto_ownership(ao_counts,survey_income,survey_size,survey_workers,
                    ctpp_income,ctpp_size,ctpp_workers,
                    model_income,model_size,model_workers)
    #flow = Flow()

def test_tab():

    h_1 = Div(text = """<h1><center>Intro Text</center></h1>""")

    l_1 = layout(children=[h_1])

    tab_1 = Panel(child=l_1, title = '# Introduction')

    return tab_1

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

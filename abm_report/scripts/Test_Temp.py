from bokeh.models.widgets import Div, Tabs
from bokeh.layouts import layout
from bokeh.models import Panel
import os, sys

def test_tab():

    h_1 = Div(text = """<h1><center>Intro Text</center></h1>""")

    l_1 = layout(children=[h_1])

    tab_1 = Panel(child=l_1, title = '# Introduction')

    return tab_1

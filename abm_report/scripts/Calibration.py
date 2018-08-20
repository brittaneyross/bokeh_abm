import os
import pandas as pd

from bokeh.models import Panel
from bokeh.layouts import layout

from Auto import AutoOwnership
from Flows import Flow
from Mode import ModeChoice
from Purpose import TripPurpose

def Calibration_tab(ao_counts,survey_dir,model_dir,ctpp_dir,person_trips,survey_trips):
    
    ao = AutoOwnership(ao_counts,survey_dir,model_dir,ctpp_dir)
    flow = Flow()
    modechoice = ModeChoice(person_trips,survey_trips)
    tpurp = TripPurpose(person_trips,survey_trips)
    
    l_2 = layout(children=ao+flow+modechoice+tpurp)

    return Panel(child=l_2, title = '# Model Calibration')
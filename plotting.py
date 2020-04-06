import numpy as np
import pandas as pd
import datetime as dt

from bokeh.io import show, output_notebook, output_file, push_notebook, save
from bokeh.plotting import figure, curdoc

from bokeh.models import CategoricalColorMapper, HoverTool, ColumnDataSource, Panel, CDSView, GroupFilter, BasicTickFormatter
from bokeh.models.widgets import CheckboxGroup, Slider, RangeSlider, DateRangeSlider, Button, Tabs

from bokeh.layouts import column, row, WidgetBox
from bokeh.palettes import Category20b, Category20c, Category20

from bokeh.application.handlers import FunctionHandler
from bokeh.application import Application

output_file('corona-by-state.html')

# Load in data and inspect
ds = pd.read_csv('./us-states.csv')
ds['date'] = pd.to_datetime(ds['date'])

# Full list of states
STATES = list(ds['state'].unique())

# Sort the list in-place (alphabetical order)
STATES.sort()

def parse_dates(date):
    return date.toordinal()

ds['date_num'] = ds['date'].apply(parse_dates)

palette60 = Category20b[20] + Category20c[20] + Category20[20]

color_df = pd.DataFrame(zip(STATES,palette60),columns=['state','color'])

ds = pd.merge(ds,color_df, how='left',on='state')

ds = ds.sort_values(['state','date'])

color_dict = dict(zip(STATES,palette60))

def make_dataset(states_list, start = dt.date(2020, 1, 21), end = dt.date.today(), thresh = 0):
    
    data = ds[(ds['date_num'] >= start.toordinal()) & (ds['date_num'] <= end.toordinal())]
    data = data[data['cases'] >= thresh]
    data = data[data['state'].isin(states_list)]
    
    # Overall dataframe
    data = data.sort_values(['date', 'state'])

    return ColumnDataSource(data)

def style(p):
    # Title 
    p.title.align = 'center'
    p.title.text_font_size = '18pt'

    # Axis titles
    p.xaxis.axis_label_text_font_size = '14pt'
    p.xaxis.axis_label_text_font_style = 'bold'
    p.yaxis.axis_label_text_font_size = '14pt'
    p.yaxis.axis_label_text_font_style = 'bold'

    # Tick labels
    p.xaxis.major_label_text_font_size = '12pt'
    p.yaxis.major_label_text_font_size = '12pt'
    #p.yaxis.formatter = PrintfTickFormatter(format='%4.0e')
    #p.yaxis.formatter = LogTickFormatter()
    p.yaxis.formatter = BasicTickFormatter(use_scientific=True, power_limit_low=1)

    # Legend
    p.legend.location = 'top_left'
    p.legend.label_text_font_size = '8pt'
    p.legend.spacing = -9
    p.legend.title = 'states, in order of first case'

    # Toolbar
    p.toolbar.autohide = True
    
    return p

def make_plot(src, y_scale='linear'):
    # Blank plot with correct labels
    p = figure(plot_width = 700, plot_height = 650, 
                title = 'COVID-19 Cases by State',
                x_axis_label = 'Date', y_axis_label = 'Number of Cases',
                x_axis_type = 'datetime', y_axis_type=y_scale)

    # Plot data
#         for state in src.data['state']:
#             view = CDSView(source=src, filters=[GroupFilter(column_name='state', group=state)])
#             color = color_dict[state]
#             p.line('date','cases', source = src, 
#                    line_color = color, alpha = 0.7,  legend = 'state', line_width = 3,
#                    hover_line_color = color, hover_alpha = 1.0, view=view)

#         p.line('date','cases', source = src, 
#                line_color = 'red', alpha = 0.7,  legend = 'state', line_width = 3,
#                hover_line_color = 'blue', hover_alpha = 1.0)

    p.circle('date','cases', source = src,  legend = 'state', line_width = 0, size = 10,
            fill_color = 'color', alpha = 0.7,
            hover_fill_color = 'color', hover_fill_alpha = 1.0)

    # Hover tool
    hover = HoverTool(tooltips=[('State', '@state'), 
                                ('Date', '@date'),
                                ('Cases', '@cases')],
                        mode='mouse')

    p.add_tools(hover)


    # Styling
#         if y_scale == 'linear':
    p = style(p)

    return p

def update(attr, old, new):
    states_to_plot = [states_select1.labels[i] for i in states_select1.active] + \
                        [states_select2.labels[i] for i in states_select2.active] + \
                        [states_select3.labels[i] for i in states_select3.active]
    
    new_src = make_dataset(states_to_plot,
                            start = range_select.value_as_datetime[0],
                            end = range_select.value_as_datetime[1],
                            thresh = thresh_select.value)

    src.data.update(new_src.data)
    
def activate_all_update(event):
    states_select1.active = list(range(18)) # 54 "states", 3 even columns of 18
    states_select2.active = list(range(18))
    states_select3.active = list(range(18))
    
    states_to_plot = [states_select1.labels[i] for i in states_select1.active] + \
                        [states_select2.labels[i] for i in states_select2.active] + \
                        [states_select3.labels[i] for i in states_select3.active]

    new_src = make_dataset(states_to_plot,
                            start = range_select.value_as_datetime[0],
                            end = range_select.value_as_datetime[1],
                            thresh = thresh_select.value)

    src.data.update(new_src.data)
    
def deactivate_all_update(event):
    states_select1.active = []
    states_select2.active = []
    states_select3.active = []
    
    states_to_plot = [states_select1.labels[i] for i in states_select1.active] + \
                        [states_select2.labels[i] for i in states_select2.active] + \
                        [states_select3.labels[i] for i in states_select3.active]
    
    new_src = make_dataset(states_to_plot,
                            start = range_select.value_as_datetime[0],
                            end = range_select.value_as_datetime[1],
                            thresh = thresh_select.value)

    src.data.update(new_src.data)

# Create widgets
states_select1 = CheckboxGroup(labels=STATES[0:18], active = [0,1])
states_select1.on_change('active', update)
states_select2 = CheckboxGroup(labels=STATES[18:36], active = [])
states_select2.on_change('active', update)
states_select3 = CheckboxGroup(labels=STATES[36:54], active = [])
states_select3.on_change('active', update)
#     states_selection = CheckboxGroup(labels=STATES, active = [0,1])
#     states_selection.on_change('active', update)

thresh_select = Slider(start = 0, end = 1000, 
                        step = 1, value = 0,
                        title = 'Case Count Minimum')
thresh_select.on_change('value', update)

range_select = DateRangeSlider(start = dt.date(2020, 1, 21), end = dt.date.today(), value = (dt.date(2020, 1, 21), dt.date.today()),
                            step = 1, title = 'Date Range')
range_select.on_change('value', update)

select_all = Button(label="select all")
select_all.on_click(activate_all_update)
unselect_all = Button(label="unselect all")
unselect_all.on_click(deactivate_all_update)


# Initialize source
initial_states = [states_select1.labels[i] for i in states_select1.active] + \
                        [states_select2.labels[i] for i in states_select2.active] + \
                        [states_select3.labels[i] for i in states_select3.active]

src = make_dataset(initial_states,
                        start = range_select.value[0],
                        end = range_select.value[1],
                        thresh = thresh_select.value)

# Plot
plot_lin_s = make_plot(src, y_scale='linear')
plot_log_s = make_plot(src, y_scale='log')

# Put controls in a single element
controls_row = row(WidgetBox(states_select1,width=140),
                    WidgetBox(states_select2,width=120),
                    WidgetBox(states_select3,width=120))
controls_col = WidgetBox(range_select, thresh_select, select_all, unselect_all)

# Create a row layout
layout_lin_s = row(column(controls_col, controls_row), plot_lin_s)
layout_log_s = row(column(controls_col, controls_row), plot_log_s)
# Make a tab with the layout 
tab_lin_s = Panel(child=layout_lin_s, title = 'by State, Linear Scale')
tab_log_s = Panel(child=layout_log_s, title = 'by State, Log Scale')
tabs = Tabs(tabs=[tab_lin_s,tab_log_s])

curdoc().add_root(tabs)
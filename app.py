import dash as dash
import dash_core_components as dcc 
import dash_html_components as html 
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go 

import scipy.stats as stats
import numpy as np




# create dash objects
app = dash.Dash()
server = app.server

# load external css 
app.css.append_css({
    'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'
})

# global variables
conf_interval_values = [0.99, 0.95, 0.90, 0.80] 

# define app layout
app.layout = html.Div([
    html.Div([
        html.H1('Ping Pong Winning Probability App'),
        #html.P('this is some new text!'),
        html.P('Check the probability of winning a ping pong game based on the win/loss history of two players')
    ], className='twelve columns'),
    
    html.Div([
        html.Div(id='data_column', children = [
            html.H3("Enter Win/Loss Data"),
            
            html.Div([
                html.H4("Priors"),
                html.P("Prior Wins"),
                dcc.Input(id='prior_wins', value=5, type='number'),
                html.P("Prior Losses"),
                dcc.Input(id='prior_losses', value=5, type='number')
            ], className='four columns'),
            
            html.Div([
                html.H4("Observed"),
                html.P("Observed Wins"),
                dcc.Input(id='observed_wins', value=0, type='number'),
                html.P("Observed Losses"),
                dcc.Input(id='observed_losses', value=0, type='number')
            ], className='four columns')
            
        ], className="four columns"),
        
        html.Div([
            html.H3("Run Analysis"),
            
            html.P("Confidence Interval"),
            dcc.Dropdown(id='conf_interval_selector', value=0.95,
            options=[{'label': val, 'value': val} for val in conf_interval_values],
            clearable=False, searchable=False),
            
            html.Button("Run Analysis", id="run_analysis_button"),
            
            html.Button("Update Priors", id="update_priors_button")
            
        ], className="two columns"),
        
        html.Div([
            html.H3("Analysis Results"),
            dcc.Graph(id='pdf_graph')
        ], className="six columns")
    
    ], className='twelve columns'),

    html.Div([
        html.A('Github', href='https://github.com/jginsberg3/ping_pong_stats_app', target="_blank")
    ])

])


# dash dynamic functions
@app.callback(
    Output(component_id='pdf_graph', component_property='figure'),
    [Input(component_id='run_analysis_button', component_property='n_clicks')],
    [State(component_id=box, component_property='value') for box in ['prior_wins', 'prior_losses', 'observed_wins', 'observed_losses']] +    # list comprehension to get similar State() for all four boxes
    [State(component_id='conf_interval_selector', component_property='value')]
)
def update_graph(n_clicks, prior_wins, prior_losses, observed_wins, observed_losses, conf_interval):
    '''updates the graph based on the latest inputted data.'''
    
    # update the priors with the observed data to get the posterior
    posterior_beta = stats.beta(prior_wins + observed_wins, prior_losses + observed_losses)
    
    # get range of values for plotting using the PDF
    x_plot = np.linspace(0, 1, 200)
    y_plot = [posterior_beta.pdf(i) for i in x_plot]
    
    # get the confidence intervals using the PPF
    conf_interval_val = 1 - conf_interval
    lb = posterior_beta.ppf(0 + conf_interval_val / 2)
    ub = posterior_beta.ppf(1 - conf_interval_val / 2)
    
    # set up plotly trace for PDF graph  
    posterior_trace = go.Scatter(
        x = x_plot,
        y = y_plot,
        mode='lines',
        name='posterior_trace'
        #fill='tozeroy',
        #line=dict(color=(colors['aqua blue']))
    )
    
    # set up plotly traces for lower/upper bound vertical lines
    # get height of lines
    line_height = max(y_plot)   # get the max height of the PDF curve from above
    
    # set up plotly trace for LB line
    lb_trace = go.Scatter(
        x = [lb, lb],
        y = [0, line_height],
        mode = 'lines',
        name='Lower Confidence Bound',
        line={'color':'#f73d3d', 'width':2},
        text = ['Lower Confidence Bound', 'Lower Confidence Bound'],
        #hoverinfo = 'text'
        )
    # set up plotly trace for UB line
    ub_trace = go.Scatter(
        x = [ub, ub],
        y = [0, line_height],
        mode = 'lines',
        name='Upper Confidence Bound',
        line={'color':'#f73d3d', 'width':2},
        text = ['Upper Confidence Bound','Upper Confidence Bound'],
        #hoverinfo = 'text'
        )
    
    # put all traces into a list
    data = [posterior_trace, lb_trace, ub_trace]
    
    # define plot layout
    layout = go.Layout(
        title='Winning Probability Distribution',
        yaxis= dict(
            title='Likelihood'
            #hoverformat=',.1f'
        ),
        xaxis = dict(
            title='Probability of Winning',
            tickvals=[round(0.1 * i,2) for i in range(0,11)]  
            #tickformat='.2%',
            #hoverformat='.2%'
        ),
        showlegend=False
        #plot_bgcolor=colors['light_latte'],
        #paper_bgcolor=colors['light_ceramic']
    )
    
    # return a dict with data and layout --> this will be passed into the 'figure' property of the dcc.Graph
    return {'data': data,'layout': layout}
                                


@app.callback(
    Output(component_id='data_column', component_property='children'),
    [Input(component_id='update_priors_button', component_property='n_clicks')],
    [State(component_id=box, component_property='value') for box in ['prior_wins', 'prior_losses', 'observed_wins', 'observed_losses']]
)
def update_priors(n_clicks, prior_wins, prior_losses, observed_wins, observed_losses):
    '''updates the priors by taking the current priors, adding the current observed data, and setting the results as the new priors.  then sets the observed data to 0.'''
    
    # create the new priors
    new_prior_wins = prior_wins + observed_wins
    new_prior_losses = prior_losses + observed_losses

    # return the updated app layout with the new priors and observed data 
    return [html.H3("Data Column"),
    
    html.Div([
        html.H4("Priors"),
        html.P("Prior Wins"),
        dcc.Input(id='prior_wins', value=new_prior_wins, type='number'),
        html.P("Prior Losses"),
        dcc.Input(id='prior_losses', value=new_prior_losses, type='number')
    ], className='four columns'),
    
    html.Div([
        html.H4("Observed"),
        html.P("Observed Wins"),
        dcc.Input(id='observed_wins', value=0, type='number'),
        html.P("Observed Losses"),
        dcc.Input(id='observed_losses', value=0, type='number')
    ], className='four columns')]


if __name__ == '__main__':
    app.run_server(debug=True, threaded=True)
    
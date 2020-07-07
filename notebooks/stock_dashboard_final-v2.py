#!/usr/bin/env python
# coding: utf-8

# In[11]:


import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

import plotly.graph_objs as go
import pandas as pd
from datetime import datetime

import yfinance as yf

# Read data
df = pd.read_csv('../DATA/chilean_stocks.csv', index_col='Date')
df = df.groupby(by=['Ticker', 'Name']).sum().reset_index()[['Ticker','Name']].set_index('Ticker')

available_tickers = []
for tic in df.index:
    available_tickers.append({'label':df.loc[tic]['Name'], 'value':tic})

# Release memory
del df

app = dash.Dash(
    __name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}]
)

available_columns = ['Open', 'High', 'Low', 'Close', 'Volume', 'Pct Change - Close', 'Cummulative Returns']

app.layout = html.Div([
    html.H1('Bolsa de Santiago - Principales Acciones - Dashboard',
            style={'textAlign': 'center'},
           ),
    html.Div([html.H3(html.Label('Seleccionar la Acción')),
            dcc.Dropdown(
                id='ticker-selected',
                options=available_tickers,
                value='LTM.SN',
                multi=True,
                placeholder="Acción",
                clearable=False,
            )
    ],style={'width': '48%', 'display': 'inline-block'},),
    html.Div([html.H3(html.Label('Elija Información a visualizar')),
            dcc.Dropdown(
                id='y-selected',
                options=[{'label': i, 'value': i} for i in available_columns],
                value='Close',
                placeholder="Información a visualizar",
                clearable=False,
            )
    ],style={'width': '48%', 'display': 'inline-block'},),
    html.Div([
        html.H3('Seleccione fecha de inicio y final:'),
        dcc.DatePickerRange(
            id='my_date_picker',
            min_date_allowed=datetime(2018, 1, 1),
            max_date_allowed=datetime.today(),
            start_date=datetime(2020, 1, 1),
            end_date=datetime.today()
        )
    ], style={'display':'inline-block'}),
    html.Div([
        html.Button(
            id='submit-button',
            n_clicks=0,
            children='Submit',
            style={'fontSize':24, 'marginLeft':'30px'}
        ),
    ], style={'display':'inline-block'}),
    # Graph 
    html.Hr(),
    html.Div([dcc.Graph(id='graph-stock',
                        figure={
                            'data': [
                                {'x': [0,0], 'y': [0,0]}
                            ]
                        }),                         
             ],),
    html.Div([dcc.Graph(id='table-stock',
                        figure={
                            'data': [
                                {'x': [0,0], 'y': [0,0]}
                            ]
                        }),                         
             ],),
    html.Hr(),
])

@app.callback(Output('graph-stock', 'figure'),
              [Input('submit-button', 'n_clicks')],
              [State('ticker-selected', 'value'),
               State('y-selected', 'value'),
               State('my_date_picker', 'start_date'),
               State('my_date_picker', 'end_date'),
              ]
             )


def update_graph(n_clicks, tickers, col, start_date, end_date):
    start = datetime.strptime(start_date[:10], '%Y-%m-%d')
    end = datetime.strptime(end_date[:10], '%Y-%m-%d')
    traces = []
    title = ''
    if type(tickers)==str: tickers = [tickers]
    #tickers.append('BOLSASTGO.SN')
    for accion in tickers:
        df_ticker = yf.Ticker(accion)
        # get company name

        try:
            longname = df_ticker.info['longName']
            industry = df_ticker.info['industry']
            payoutRatio = df_ticker.info['payoutRatio']
        except:
            longname = accion
            industry = 'N/A'
            payoutRatio = 0 
        # get historical market data
        df = df_ticker.history(start=start, end=end, interval='1d')
        df['Ticker'] = accion
        df['Name'] = longname
        df['Industry'] = industry
        df['PayoutRatio'] = payoutRatio
        df['Pct Change - Close'] = df.Close.pct_change()
        df['Cummulative Returns'] = ((1 + df['Pct Change - Close']).cumprod() - 1)    

        data = go.Scatter(x = df.index, y=df[col], mode='lines+markers', 
                          name=accion,
                          text=longname, 
                          hovertext=["x", "text", col],
                          hoverinfo=["y"],
                          xaxis='x2',
                          yaxis='y2',
                          marker=dict(symbol = 'pentagon-dot',
                                      opacity = 0.8,
                                      line   = dict(width=2),
                                     ),
                         )
        traces.append(data)
        title = title + accion+'/'
    layout = go.Layout(title = title+' - '+'<b>'+col+'</b>'+'<br>'+'Desde : '+start_date[:10]                        + ' Hasta : '+end_date[:10],
                       title_x=0.5,
                       xaxis = dict(title='Fecha'),
                       yaxis = dict(title=col),
                       hovermode="x unified",
                       hoverlabel=dict(bgcolor="white", 
                                       font_size=10, 
                                       font_family="Rockwell"
                                      ),
                       template='presentation',
                       height=600,
                       autosize=True,  
                      )
    fig = go.Figure(data=traces,layout=layout)
    fig.update_xaxes(rangeslider_visible=True,
                     rangeselector=dict(buttons=list([
                         dict(count=1, label="1m", step="month", stepmode="backward"),
                         dict(count=6, label="6m", step="month", stepmode="backward"),
                         dict(count=1, label="YTD", step="year", stepmode="todate"),
                         dict(count=1, label="1y", step="year", stepmode="backward"),
                         dict(count=3, label="3y", step="year", stepmode="backward"),
                         dict(count=5, label="5y", step="year", stepmode="backward"),
                         dict(step="all")])))
    return fig

@app.callback(Output('table-stock', 'figure'),
              [Input('submit-button', 'n_clicks')],
              [State('ticker-selected', 'value'),
               State('y-selected', 'value'),
               State('my_date_picker', 'start_date'),
               State('my_date_picker', 'end_date'),
              ]
             )

def update_table(n_clicks, tickers, col, start_date, end_date):
    start = datetime.strptime(start_date[:10], '%Y-%m-%d')
    end = datetime.strptime(end_date[:10], '%Y-%m-%d')
    df_table = pd.DataFrame()
    if type(tickers)==str: tickers = [tickers]
    #tickers.append('BOLSASTGO.SN')
    for accion in tickers:
        df_ticker = yf.Ticker(accion)
        # get company name
        try:
            longname = df_ticker.info['longName']
            industry = df_ticker.info['industry']
            payoutRatio = df_ticker.info['payoutRatio']
        except:
            longname = accion
            industry = 'N/A'
            payoutRatio = 0 
        # get historical market data
        df = df_ticker.history(start=start, end=end, interval='1d')
        df['Ticker'] = accion
        df['Name'] = longname
        df['Industry'] = industry
        df['PayoutRatio'] = payoutRatio
        df['Pct Change - Close'] = df.Close.pct_change()
        df['Cummulative Returns'] = ((1 + df['Pct Change - Close']).cumprod() - 1)
        df_table = df_table.append(df)
    
    df_table.reset_index(inplace=True)
    df_table.sort_values(["Name", "Date"], axis=0, ascending=False, inplace=True) 
    df_table['Fecha'] = df_table['Date'].apply(lambda x:datetime.strftime(x,'%d/%m/%Y'))
    df_table = df_table[['Fecha','Name','Industry', 'Open', 'High', 'Low', 'Close', 'Volume', 'Pct Change - Close','Cummulative Returns']]
    table = go.Table(header=dict(values=list(df_table.columns),
                                 font=dict(size=10),
                                 #fill_color='paleturquoise',
                                 align='left'),
                     cells=dict(values=[df_table[k].tolist() for k in df_table.columns],
                                align = "left",
                                font=dict(size=10),
                               ),
                    )
    layout = go.Layout(title = 'Detalle de Información - '+'<b>'+col+'<b>', title_x=0.5,)
    fig = go.Figure(data=table, layout=layout)
    
    return fig
              
if __name__ == '__main__':
    app.run_server()


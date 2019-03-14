import dash
from flask import Flask
from dash.dependencies import Output, Event
import dash_core_components as dcc
import dash_html_components as html
import plotly
import random
import plotly.graph_objs as go
import pandas as pd
from query_athena import faz_query, chama_modelo
import time

#https://github.com/plotly/dash-wind-streaming/blob/master/app.py
#app = dash.Dash(__name__, external_stylesheets=external_css)

external_css = ["https://cdnjs.cloudflare.com/ajax/libs/skeleton/2.0.4/skeleton.min.css",
                "https://fonts.googleapis.com/css?family=Raleway:400,400i,700,700i",
                "https://fonts.googleapis.com/css?family=Product+Sans:400,400i,700,700i"]


app = dash.Dash(__name__, external_stylesheets=external_css)
server = app.server

app.layout = html.Div([
  
     

    html.Div([
        html.Div([
            html.H3("Monitoramento de sinal elétrico")
        ], className='Title'),
        html.Div([
            dcc.Graph(id='live-graph', animate=True),
        ], className='teste'),
        dcc.Interval(id='graph-update', interval=4000, n_intervals=0),
    ], className='row wind-speed-row'),

], )



@app.callback(Output('live-graph', 'figure'),
              events=[Event('graph-update', 'interval')])

def update_graph_scatter():
    
	endpoint_ = 'exdeploy-endpoint'
    
    try:
        
        df, ss = faz_query()
      
        resp = chama_modelo(ss, endpoint_ )
        print('ok')
        
        resp = resp['0']
        max_time = max(df['time'])
        print('resposta do modelo:', resp)
        

        df2 = pd.read_csv('dados/resp_modelo.txt')
        df2.columns = ['time', 'resp_modelo']
        

        ultimo_tempo = float( df.head(1)['time'])
        print('ultimo tempo:', ultimo_tempo)


        if max(df2['time']) < max(df['time'])+1:
            print('salvando a resposta do modelo')
            with open('dados/resp_modelo.txt','a') as fd:
                fd.write( '\n' + str(max_time+1) + ',' + str(resp))

        df2 = pd.read_csv('dados/resp_modelo.txt')
        df2.columns = ['time', 'resp_modelo']


        valor_modelo = float(df2[df2['time']==ultimo_tempo]['resp_modelo'].iloc[0])
        valor_real = float(df[df['time']==ultimo_tempo]['v2'].iloc[0])
        print('resp do modelo no ultimo tempo',valor_modelo)
        print('resp real no ultimo tempo',valor_real)

        erro_modelo = abs(valor_modelo - valor_real)
        print('erro do modelo', erro_modelo)

        df3 = pd.read_csv('dados/erro_modelo.txt')
        print(df3.head())
        tempo_max_erro = max(df3['time'])
        print(tempo_max_erro)

        if ultimo_tempo > tempo_max_erro:
            print('salvando erro do modelo')
            with open('dados/erro_modelo.txt','a') as fd:
                fd.write( '\n' + str(ultimo_tempo) + ',' + str(erro_modelo))

        
        X = df.time.values
        Y1 = df.v2.values
        
        X2 = df3.time.values[-100:]
        Y2 = df3.erro_modelo.values[-100:]
        
        
        data = plotly.graph_objs.Scatter(
                x=X,
                y=Y1,
                name='sinal',
                mode= 'lines'
                )
        
        data2 = plotly.graph_objs.Scatter(
                x=X2,
                y=Y2,
                name='erro do modelo',
                mode= 'lines'
                )
        
        data_erro = plotly.graph_objs.Scatter(
                x=X2,
                y=[0.25]*len(X2),
                name='limite erro',
                mode= 'lines',
                line = dict(dash = 'dot')
                )
        

        layout = go.Layout(#annotations= lista_anot,
                            xaxis=dict(range=[min(X),max(X)], 
                                        title = 'Tempo (s)'
                                        ),
                             yaxis=dict(#range=[0,1],
                                 title='Corrente (A)'),
                            )


        return {'data': [data, data2, data_erro],
                'layout' : layout
                }

    except Exception as e:
        with open('errors.txt','a') as f:
            f.write(str(e))
            f.write('\n')




#for css in external_css:
#    app.css.append_css({"external_url": css})


#external_js = ['https://cdnjs.cloudflare.com/ajax/libs/materialize/0.100.2/js/materialize.min.js',
#               'https://pythonprogramming.net/static/socialsentiment/googleanalytics.js']
#for js in external_js:
#    app.scripts.append_script({'external_url': js})


if __name__ == '__main__':
    app.run_server(debug=True)




#pip install dash==0.30.0 dash-html-components==0.13.2 dash-core-components==0.38.0 dash-table==3.1.6
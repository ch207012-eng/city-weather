# consumer_dashboard/app.py
import time
from dotenv import load_dotenv
import dash
from dash import dcc, html
import plotly.graph_objs as go
from kafka_consumer_thread import start_consumer_thread, shared_store

load_dotenv()

start_consumer_thread()

app = dash.Dash(__name__)
server = app.server

CITIES = ["St Paul", "Duluth", "St Cloud", "Rochester"]

def city_card(city):
    return html.Div([
        html.H3(city),
        html.Div(id={'type':'current-stats','index':city}),
        dcc.Graph(id={'type':'timeseries','index':city}, config={'displayModeBar': False})
    ], style={'border':'1px solid #ddd','padding':'10px','margin':'10px','width':'45%','display':'inline-block','verticalAlign':'top'})

app.layout = html.Div([
    html.H1("City Weather Dashboard (MN)"),
    html.Div([city_card(c) for c in CITIES]),
    dcc.Interval(id='interval-component', interval=5*1000, n_intervals=0)
])

@app.callback(
    [dash.dependencies.Output({'type':'current-stats','index':dash.dependencies.ALL}, 'children'),
     dash.dependencies.Output({'type':'timeseries','index':dash.dependencies.ALL}, 'figure')],
    [dash.dependencies.Input('interval-component', 'n_intervals')]
)
def update_all(n):
    current_children = []
    figures = []
    for city in CITIES:
        data = shared_store.get(city, [])
        if data:
            times = [time.strftime("%H:%M:%S", time.localtime(item['timestamp'])) for item in data]
            temps = [item['temp'] for item in data]
            precips = [item['precip'] for item in data]
            winds = [item['wind'] for item in data]
            current_children.append(
                html.Div([
                    html.Div(f"Temperature (F): {temps[-1]}"),
                    html.Div(f"Precip (in last 1h): {precips[-1]}"),
                    html.Div(f"Wind (mph): {winds[-1]}")
                ])
            )
            fig = {
                'data': [
                    go.Scatter(x=times, y=temps, name='Temp (F)', mode='lines+markers'),
                    go.Scatter(x=times, y=precips, name='Precip (in)', mode='lines+markers', yaxis='y2'),
                    go.Scatter(x=times, y=winds, name='Wind (mph)', mode='lines+markers', yaxis='y3')
                ],
                'layout': go.Layout(
                    title=f"{city} - Recent Weather",
                    xaxis={'title':'Time'},
                    yaxis={'title':'Temp (F)'},
                    yaxis2=dict(title='Precip (in)', overlaying='y', side='right', position=0.95),
                    yaxis3=dict(title='Wind (mph)', overlaying='y', side='right', position=1.0, anchor='x'),
                    legend={'orientation':'h'},
                    margin={'l':40,'r':40,'t':40,'b':40}
                )
            }
        else:
            current_children.append(html.Div("No data yet."))
            fig = {'data': [], 'layout': go.Layout(title=f"{city} - No Data")}
        figures.append(fig)
    return current_children, figures

if __name__ == "__main__":
    app.run_server(debug=True, host='0.0.0.0', port=8050)

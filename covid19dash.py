import pandas as pd
import numpy as np 
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
from dash.dependencies import Input, Output,State
import requests
import dash_bootstrap_components as dbc
import flask
from sqlalchemy import create_engine
import pymysql
from plotly.subplots import make_subplots
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler,PolynomialFeatures
from sklearn.svm import SVR
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score,mean_squared_error



#vertabanı baglantı 

sqlEngine = create_engine('mysql+pymysql://root:@127.0.0.1', pool_recycle=3600)

dbConnection = sqlEngine.connect()

df = pd.read_sql("select * from koronavirus.kumulatif_veriler", dbConnection);
df_location = pd.read_sql("select * from koronavirus.mekansal", dbConnection);
yas_cinsiyet = pd.read_sql("select * from koronavirus.yas_cinsiyet", dbConnection);
gunluk_vaka = pd.read_sql("select * from koronavirus.gunluk_vaka",dbConnection);
gunluk_olum = pd.read_sql("select * from koronavirus.gunluk_olum",dbConnection);

pd.set_option('display.expand_frame_repr', False)

 
dbConnection.close()

ulkeler1 = df["Country"].unique()
ulkeler2 = gunluk_vaka.columns
ulkeler2[2:]
#df["Days Since"]=df.index-df.index.min()
#
#
#df_ulkeler = []
#
#for i in ulkeler1:
#    ulke = df[df["Country"] == i]
#    df_ulkeler.append(ulke)
#    
#
#frames = []
#
#for i in df_ulkeler:
#    i.reset_index(inplace = True)
#    i["Days Since"] = i.index
#    frames.append(i)
#    
#
#df = pd.concat(frames)

    



#vaka
vaka_yas_cinsiyet = yas_cinsiyet[yas_cinsiyet["death"] == "0" ]

#olen
olen_yas_cinsiyet = yas_cinsiyet[yas_cinsiyet["death"] == "1" ]

#iylesenleri topla 
recovered_df = df.groupby(["Country"]).sum()
recovered_df.reset_index(inplace = True)
recovered_df = recovered_df.rename(columns = {"Country" : "country"})
recovered_df.drop(["Confirmed","Deaths","index"],axis = 1,inplace = True)
recovered_df["recovered_size"] = recovered_df["Recovered"]/10000

df_location = pd.merge(recovered_df, df_location, on="country")




#mapbox acces
mapbox_access_token = "pk.eyJ1IjoiY2V0aW5maWtyaSIsImEiOiJjazk0YmJjeWkwM3cyM21uM2k2NG93Y3RiIn0.zfRLRQCsPl7oUDfU94LlDg"

#vaka haritası

map_confirmed = go.Scattermapbox(
        customdata = df_location.loc[:,["confirmed","deaths","recovered"]],
        lat = df_location["lat"],
        lon = df_location["lon"],
        text = df_location["country"],
        hovertemplate = "<b>%{text}<b><br><br>"+
                        "Vaka Sayısı : %{customdata[0]}<br>"+
                        "<extra></extra>",
        mode = "markers",
        showlegend = True,
        marker = go.scattermapbox.Marker(
                size = df_location["confirmed_size"],
                color = "green",
                opacity = 0.7
                
                ),name = "vaka"

        
        ) 

map_deaths = go.Scattermapbox(
        customdata = df_location.loc[:,["confirmed","deaths","recovered"]],
        lat = df_location["lat"],
        lon = df_location["lon"],
        text = df_location["country"],
        hovertemplate = "<b>%{text}<b><br><br>"+
                        "Ölüm Sayısı : %{customdata[1]}<br>"+
                        "<extra></extra>",
        mode = "markers",
        showlegend = True,
        marker = go.scattermapbox.Marker(
                size = df_location["deaths_size"],
                color = "red",
                opacity = 0.7
                
                ),name = "ölüm"

        
        ) 
        
#####       
#map_recovered = go.Scattermapbox(
#        customdata = recovered_df.loc[:,["Recovered"]],
#        lat = df_location["lat"],
#        lon = df_location["lon"],
#        text = df_location["country"],
#        hovertemplate = "<b>%{text}<b><br><br>"+
#                        "İyileşen Sayısı : %{customdata[2]}<br>"+
#                        "<extra></extra>",
#        mode = "markers",
#        showlegend = True,
#        marker = go.scattermapbox.Marker(
#                size = recovered_df["recovered_size"],
#                color = "blue",
#                opacity = 0.7
#                
#                ),name = "iyileşen"
#
#        
#        ) 
   
    
    
data = [map_confirmed,map_deaths]
fig = go.Figure(data = data)
fig.update_layout(
    mapbox=dict(
        accesstoken=mapbox_access_token,
        bearing=0,
        center=go.layout.mapbox.Center(
            lat=45,
            lon=-73
        ),
        pitch=0,
        zoom=5
    ),width = 1300 , height = 800
)

fig.show()
        
####        

#yas vaka grafigi 
        
fig2 = make_subplots(rows = 1 ,cols = 2)
trace0 = go.Histogram(x=vaka_yas_cinsiyet["age"],
    histnorm='percent',
    xbins = dict(
            start = 10,
            end = 90,
            size = 2
            ),
    marker_color='#bf1b4c',
    opacity=0.7,name = "vaka-yas")


trace1 = go.Histogram(
    x=olen_yas_cinsiyet["age"],
    histnorm='percent',
    xbins = dict(
            start = 10,
            end = 90,
            size = 4
            ),
    marker_color='#ebba34',
    opacity=0.75,name = "olum-yas"
)

fig2.append_trace(trace0,1,1)
fig2.append_trace(trace1,1,2)
fig2.show()


        
#fig2 = go.Figure()
#fig2.add_trace(go.Histogram(
#    x=vaka_yas_cinsiyet["age"],
#    histnorm='percent',
#    xbins = dict(
#            start = 10,
#            end = 90,
#            size = 2
#            ),
#    marker_color='#bf1b4c',
#    opacity=0.75
#))
#     
#fig2.show()        
#        
##yas olum grafigi
#
#
#fig3 = go.Figure()
#fig3.add_trace(go.Histogram(
#    x=olen_yas_cinsiyet["age"],
#    histnorm='percent',
#    xbins = dict(
#            start = 10,
#            end = 90,
#            size = 4
#            ),
#    marker_color='#27e336',
#    opacity=0.75
#))
#     
#fig3.show()        

#cinsiyet vaka 

x_vaka_cins = vaka_yas_cinsiyet.groupby("gender").count().index
y_vaka_cins = vaka_yas_cinsiyet.groupby("gender").count()["index"]
y_vaka_cins = y_vaka_cins.astype(float)
#vaka oran hesaplama
y_vaka_cins[0] = y_vaka_cins[0]/(y_vaka_cins[0]+y_vaka_cins[1])
y_vaka_cins[1] = 1-y_vaka_cins[0]




fig4 = go.Figure()
fig4.add_trace(go.Bar(x = x_vaka_cins,
                       y = y_vaka_cins,
                       name = "Vaka-Cinsiyet", marker_color = 'rgb(55, 83, 109)'))

x_olum_cins = olen_yas_cinsiyet.groupby("gender").count().index
y_olum_cins = olen_yas_cinsiyet.groupby("gender").count()["index"]

#ölün oran 
y_olum_cins = y_olum_cins.astype(float)
y_olum_cins[0] = y_olum_cins[0]/(y_olum_cins[0]+y_olum_cins[1])
y_olum_cins[1] = 1 - y_olum_cins[0]


fig4.add_trace(go.Bar(x = x_olum_cins,
                       y = y_olum_cins,
                       name = "Ölüm-Cinsiyet", marker_color = 'rgb(26, 118, 255)'))



LOGO = "https://www.deu.edu.tr/file/2019/01/logo.png"

#nav_item1 = dbc.NavItem(dbc.NavLink("Grafikler",href = "/dash/"))
#nav_item2 = dbc.NavItem(dbc.NavLink("Analiz",href = "/page-1"))


dropdown_grafikler = dbc.DropdownMenu(children = [
        dbc.DropdownMenuItem("Kümülatif Veriler", href = "/dash/"),
        dbc.DropdownMenuItem("Harita", href = "/map"),
        dbc.DropdownMenuItem("Günlük Veriler", href = "/daily"),
        dbc.DropdownMenuItem("Diğer", href = "/others"),
        dbc.DropdownMenuItem("Hepsi", href = "/all")
        ],
        nav = True,
        in_navbar = True,
        label = "Grafikler")

dropdown_analiz = dbc.DropdownMenu(children = [
        dbc.DropdownMenuItem("Basit Doğrusal Regresyon",href = "/linear_reg"),
        dbc.DropdownMenuItem("Polinomal Regresyon",href = "/poly_reg"),
        dbc.DropdownMenuItem("Destek Vektör Regresyonu",href = "/sv_reg"),
        dbc.DropdownMenuItem("Rassal Orman Regresyonu",href = "/rf_reg")
        
        ],
        nav = True,
        in_navbar = True,
        label = "Tahmin")


navbar = dbc.Navbar(dbc.Container(
    [
        html.A(
            dbc.Row(
                [
                    dbc.Col(dbc.NavbarBrand("Koronavirüs Dashboard", className="ml-2")),
                ],
                align="center",
                no_gutters=True,
            ),
            href="/dash/",
        ),
        dbc.NavbarToggler(id="navbar-toggler"),
        dbc.Collapse(dbc.Nav([dropdown_grafikler,dropdown_analiz],className = "ml-auto",navbar = True),id="navbar-collapse", navbar=True),
    ],
    
),color="dark",
    dark=True)









######
#dash     
#####    
    
#flask server 

app = dash.Dash(__name__,external_stylesheets=[dbc.themes.BOOTSTRAP])

SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
    "margin-top" : "57px"
    
    
}

sidebar_lin_reg = html.Div(
    [
        html.P(
            "Ülke Seç", className="lead"
        ),
        
        dbc.Nav(vertical=True),
        dcc.Dropdown(id = "ulke",
                        options = [{"label" : i , "value" : i}  for i in ulkeler1],
                        value = "Ülke Seç"),
        html.P(
            "Bağımlı Değişken", className="lead"
        ),
        dcc.Dropdown(id = "bagımlı-degisken",
                     options = [{"label" : i , "value" : i } for i in ["Vaka","Ölüm","İyileşen"]])
                     
        
    ],
     style = SIDEBAR_STYLE,
    id="sidebar"
)


sidebar_poly_reg = html.Div(
        [
        html.P(
            "Ülke Seç", className="lead"),
                
        dbc.Nav(vertical = True),
        dcc.Dropdown(id = "ulke",
                     options = [{"label" : i , "value" : i}  for i in ulkeler1],
                     value = "Ülke Seç"),
        html.P(
            "Bağımlı Değişken", className="lead"
        ),            
        dcc.Dropdown(id = "bagımlı-degisken",
                     options = [{"label" : i , "value" : i } for i in ["Vaka","Ölüm","İyileşen"]]),
        
        html.P(
            "Polinom Derecesi", className="lead"
        ),
        dcc.Input(id = "degree" , type = "number" , placeholder = "Derece")  
                
        
                ],
        
             style = SIDEBAR_STYLE,
             id="sidebar"
        
        
        )

sidebar_svr = html.Div(
        [
        html.P(
            "Ülke Seç", className="lead"),
                
        dbc.Nav(vertical = True),
        dcc.Dropdown(id = "ulke",
                     options = [{"label" : i , "value" : i}  for i in ulkeler1],
                     value = "Ülke Seç"),
        html.P(
            "Bağımlı Değişken", className="lead"
        ),            
        dcc.Dropdown(id = "bagımlı-degisken",
                     options = [{"label" : i , "value" : i } for i in ["Vaka","Ölüm","İyileşen"]]),
        
        html.P(
            "Kernel Fonksiyonu", className="lead"
        ),
        dcc.Dropdown(id = "kernel",
                     options = [{"label" : i , "value" : i} for i in ["linear","poly","rbf"]]) 
                
        
                ],
        
             style = SIDEBAR_STYLE,
             id="sidebar"
        
        
        )

side_bar_rfreg = html.Div(
        [
        html.P(
            "Ülke Seç", className="lead"),
                
        dbc.Nav(vertical = True),
        dcc.Dropdown(id = "ulke",
                     options = [{"label" : i , "value" : i}  for i in ulkeler1],
                     value = "Ülke Seç"),
        html.P(
            "Bağımlı Değişken", className="lead"
        ),            
        dcc.Dropdown(id = "bagımlı-degisken",
                     options = [{"label" : i , "value" : i } for i in ["Vaka","Ölüm","İyileşen"]]),
        
        html.P(
            "Ağaç Sayısı", className="lead"
        ),
        dcc.Input(id = "n-estimators",type = "number", value = 1) 
                
        
                ],
        
             style = SIDEBAR_STYLE,
             id="sidebar"
        
        
        )





app.config.suppress_callback_exceptions = True

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])





#navbar boostrap

url_bar_and_content_div = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])


layout_index = html.Div([navbar,
        html.Div([
                html.Div([dcc.Dropdown(id = "ulke",
                        options = [{"label" : i , "value" : i}  for i in ulkeler1],
                        value = "Ülke Seç")],style  = {"margin-top" : "10px"}),
                dcc.Checklist(id = "kolon" , options = [{"label" : i , "value" : i} for i in ["Vaka","Ölüm","İyileşen"]],value = "Vaka",labelStyle={ "margin-left" : "10px" ,"margin-top": "10px",'display': 'inline-block'})
                
                ],style = {"textAlign" : "center"}),
                dcc.Graph(id = "vaka-grafigi")
                
                
                
    ]
)
        
        
        
layout_map  = html.Div([navbar,
        html.Div([html.H4("Harita")],style={'textAlign': 'center',"margin-top" : "10px"}),
        html.Div([
                dcc.Checklist(id = "harita" , options = [{"label" : i , "value" : i } for i in ["Vaka","Ölüm"]],labelStyle = {"margin-left" : "10px","margin-top" : "10px"}),
                ],style = {"textAlign" : "center"}),
        html.Div([
                dcc.Graph(figure = fig,id = "vaka-haritası")
                ],style = {"margin-left" : "100px"})
                       ])        
        

layout_daily = html.Div([navbar,
                html.Div([html.H4("Günlük Veriler")],style={'textAlign': 'center',"margin-top" : "10px"}),
        html.Div([
                html.Div([dcc.Dropdown(id = "ulke1",
                        options = [{"label" : i , "value" : i}  for i in ulkeler2[2:]],
                        value = "Ülke Seç")],style  = {"margin-top" : "10px"}),
                dcc.Checklist(id = "kolon1" , options = [{"label" : i , "value" : i} for i in ["Vaka","Ölüm"]],value = "Vaka",labelStyle={ "margin-left" : "10px" ,"margin-top": "10px",'display': 'inline-block'})
                
                ],style = {"textAlign" : "center"}),
        
        html.Div([
                dcc.Graph(id = "gunluk-veriler")
                ])         
                        ])


layout_others = html.Div([navbar,
        html.Div([html.H4("Yaş-Vaka-Ölüm Histogramı")],style={'textAlign': 'center'}),
        html.Div([
                dcc.Graph(figure = fig2 , id = "yas-vaka")]),
        html.Div([html.H4("Cinsiyet-Vaka-Ölüm")],style={'textAlign': 'center'}),
        html.Div([
                dcc.Graph(figure = fig4)
                ])          
                         
                         ])


layout_all = html.Div([navbar,
        html.Div([
                html.Div([dcc.Dropdown(id = "ulke",
                        options = [{"label" : i , "value" : i}  for i in ulkeler1],
                        value = "Ülke Seç")],style  = {"margin-top" : "10px"}),
                dcc.Checklist(id = "kolon" , options = [{"label" : i , "value" : i} for i in ["Vaka","Ölüm","İyileşen"]],value = "Vaka",labelStyle={ "margin-left" : "10px" ,"margin-top": "10px",'display': 'inline-block'})
                
                ],style = {"textAlign" : "center"}),
                dcc.Graph(id = "vaka-grafigi"),
        html.Div([html.H4("Harita")],style={'textAlign': 'center',"margin-top" : "10px"}),
        html.Div([
                dcc.Checklist(id = "harita" , options = [{"label" : i , "value" : i } for i in ["Vaka","Ölüm"]],labelStyle = {"margin-left" : "10px","margin-top" : "10px"}),
                ],style = {"textAlign" : "center"}),
        html.Div([
                dcc.Graph(figure = fig,id = "vaka-haritası")
                ],style = {"margin-left" : "100px"}),
        html.Div([html.H4("Günlük Veriler")],style={'textAlign': 'center',"margin-top" : "10px"}),
        html.Div([
                html.Div([dcc.Dropdown(id = "ulke1",
                        options = [{"label" : i , "value" : i}  for i in ulkeler2[2:]],
                        value = "Ülke Seç")],style  = {"margin-top" : "10px"}),
                dcc.Checklist(id = "kolon1" , options = [{"label" : i , "value" : i} for i in ["Vaka","Ölüm"]],value = "Vaka",labelStyle={ "margin-left" : "10px" ,"margin-top": "10px",'display': 'inline-block'})
                
                ],style = {"textAlign" : "center"}),
        
        html.Div([
                dcc.Graph(id = "gunluk-veriler")
                ]),
                
        html.Div([html.H4("Yaş-Vaka-Ölüm Histogramı")],style={'textAlign': 'center'}),
        html.Div([
                dcc.Graph(figure = fig2 , id = "yas-vaka")]),
        html.Div([html.H4("Cinsiyet-Vaka")],style={'textAlign': 'center'}),
        html.Div([
                dcc.Graph(figure = fig4)
                ])
                
                
                
        
        
        ]
)

        
layout_reg = html.Div([html.Div([navbar]),
                      html.Div([sidebar_lin_reg]),
                      html.Div([
                              dcc.Graph(id = "linear-reg")
                              ],style = {"margin-left" : "300px"}),
                    html.Div(children = [html.H5("Gün:"),
                            dcc.Input(id = "day" , type = "number" , value = 0),
                            html.H5("Tahmin:"),
                            html.Div(id = "prediction1")
                            
                            
                            ],style = {"margin-left" : "300px","float" : "left"}),
                    html.Div(children = [
                            html.H5("RMSE Değeri:"),
                            html.Div(id = "rmse"),
                            html.H5("R2 Değeri:",style ={"margin-top":"30px"}),
                            html.Div(id = "r2")
                            
                            ],style = {"margin-left" : "600px","float": "left"})
                      
        

])
        
        
layout_poly = html.Div([html.Div([navbar]),
                        html.Div([sidebar_poly_reg]),
                        html.Div([
                                dcc.Graph(id = "poly-reg")
                                ],style = {"margin-left" : "300px "}),
                        html.Div(children = [
                            html.H5("Gün:"),
                            dcc.Input(id = "day" , type = "number" , value = 0),
                            html.H5("Tahmin:"),
                            html.Div(id = "prediction2")
                                
                                
                                ],style = {"margin-left" : "300px","float" : "left"}),
                        html.Div(children = [
                            html.H5("RMSE Değeri:"),
                            html.Div(id = "rmse_poly"),
                            html.H5("R2 Değeri:",style ={"margin-top":"30px"}),
                            html.Div(id = "r2_poly")
                            
                            ],style = {"margin-left" : "600px","float": "left"})
        
                        
                        
                        ])    
        
    
layout_svr = html.Div([html.Div([navbar]),
                        html.Div([sidebar_svr]),
                        html.Div([
                                dcc.Graph(id = "svm-reg")
                                ],style = {"margin-left" : "300px "}),
                        html.Div(children = [
                                html.H5("Gün:"),
                                dcc.Input(id = "day" , type = "number" , value = 0),
                                html.H5("Tahmin:"),
                                html.Div(id = "prediction3")
                                
                                
                                ],style = {"margin-left" : "300px","float" : "left"}),
                        html.Div(children = [
                            html.H5("RMSE Değeri:"),
                            html.Div(id = "rmse_svr"),
                            html.H5("R2 Değeri:",style ={"margin-top":"30px"}),
                            html.Div(id = "r2_svr")
                            
                            ],style = {"margin-left" : "600px","float": "left"})
                        
                        
                        ])    
        
        
        
        
layout_rfreg = html.Div([html.Div([navbar]),
                        html.Div([side_bar_rfreg]),
                        html.Div([
                                dcc.Graph(id = "rf-reg")
                                ],style = {"margin-left" : "300px "}),
                        html.Div(children = [
                                html.H5("Gün:"),
                                dcc.Input(id = "day" , type = "number" , value = 0),
                                html.H5("Tahmin:"),
                                html.Div(id = "prediction4")
                                
                                
                                ],style = {"margin-left" : "300px","float" : "left"}),
                        html.Div(children = [
                            html.H5("RMSE Değeri:"),
                            html.Div(id = "rmse_rf"),
                            html.H5("R2 Değeri:",style ={"margin-top":"30px"}),
                            html.Div(id = "r2_rf")
                            
                            ],style = {"margin-left" : "600px","float": "left"})
                        
                        
                        ])  
        
        
    
    
    
        
#
                        
                        
def serve_layout():
    if flask.has_request_context():
        return url_bar_and_content_div
    return html.Div([
        url_bar_and_content_div,
        layout_index,
        layout_reg
    ])


app.layout = serve_layout                        
                        
                        
# Index callbacks
@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == "/linear_reg":
        return layout_reg
    if pathname == "/map":
        return layout_map
    if pathname == "/daily":
        return layout_daily
    if pathname == "/others":
        return layout_others
    if pathname == "/all":
        return layout_all
    if pathname == "/poly_reg":
        return layout_poly
    if pathname == "/sv_reg":
        return layout_svr
    if pathname == "/rf_reg":
        return layout_rfreg
    else:
        return layout_index
                        
                        
                        
            
                        
                        
                        
                        
                        
                        
                        
                
@app.callback(Output(component_id = "vaka-grafigi" , component_property = "figure"),
              [Input("ulke","value"),
               Input("kolon","value")])



def update_graph1(ulke,kolon):
    ulke = df[df["Country"] == ulke]
    data = []
    if "Vaka" in kolon :
        data.append({"x":ulke["Date"] , "y" : ulke["Confirmed"], "type" : "line" , "name" : "vaka" })
    if "Ölüm" in kolon :
        data.append({"x":ulke["Date"] , "y" : ulke["Deaths"],"type" : "line", "name" : "ölüm"})
    if "İyileşen" in kolon:
        data.append({"x":ulke["Date"] , "y" : ulke["Recovered"],"type" : "line", "name" : "iyileşen"})
        
    figure = {
            
            "data" : data

            }
        

    return figure
        



@app.callback(Output(component_id = "vaka-haritası" , component_property = "figure"),
              [Input("harita","value")])

def update_map(harita):
    
    data = []
    
    if "Vaka" in harita :
        map_confirmed = go.Scattermapbox(
        customdata = df_location.loc[:,["confirmed","deaths","recovered"]],
        lat = df_location["lat"],
        lon = df_location["lon"],
        text = df_location["country"],
        hovertemplate = "<b>%{text}<b><br><br>"+
                        "Vaka Sayısı : %{customdata[0]}<br>"+
                        "<extra></extra>",
        mode = "markers",
        showlegend = True,
        marker = go.scattermapbox.Marker(
                size = df_location["confirmed_size"],
                color = "green",
                opacity = 0.7
                
                ),name = "vaka"

        
        )
        data.append(map_confirmed)
        
        
    if "Ölüm" in harita:
        map_deaths = go.Scattermapbox(
        customdata = df_location.loc[:,["confirmed","deaths","recovered"]],
        lat = df_location["lat"],
        lon = df_location["lon"],
        text = df_location["country"],
        hovertemplate = "<b>%{text}<b><br><br>"+
                        "Ölüm Sayısı : %{customdata[1]}<br>"+
                        "<extra></extra>",
        mode = "markers",
        showlegend = True,
        marker = go.scattermapbox.Marker(
                size = df_location["deaths_size"],
                color = "red",
                opacity = 0.7
                
                ),name = "ölüm"

        
        )
        
        data.append(map_deaths)
        
        

    
        
    fig = go.Figure(data = data)
    fig.update_layout(
            mapbox=dict(
    accesstoken=mapbox_access_token,
    bearing=0,
    center=go.layout.mapbox.Center(),
    pitch=0,
    zoom=1
    ),width = 1500 , height = 800)
        


    return fig
    

@app.callback(Output(component_id = "gunluk-veriler" , component_property = "figure"),
              [Input("ulke1","value"),
               Input("kolon1","value")])


def update_graph2(ulke1,kolon1):
    ulke_vaka = gunluk_vaka.loc[:,["date",ulke1]]
    ulke_olum = gunluk_olum.loc[:,["date",ulke1]]
    data = []
    
    if "Vaka" in kolon1 :
        data.append({"x":ulke_vaka["date"] , "y" : ulke_vaka.iloc[:,1], "type" : "line" , "name" : "vaka" })
    if "Ölüm" in kolon1 :
        data.append({"x":ulke_olum["date"] , "y" : ulke_olum.iloc[:,1], "type" : "line" , "name" : "olum" })

        
        
    figure = {
            
            "data" : data

            }
        

    return figure
        


@app.callback([Output(component_id = "linear-reg" , component_property = "figure"),
              Output(component_id = "rmse" , component_property = "children"),
              Output(component_id = "r2" , component_property = "children")],
              [Input("ulke","value"),
               Input("bagımlı-degisken","value")])
    
def linear_reg_graph(ulke,bagımlı_degisken):
    ulke = df[df["Country"] == ulke]
    data = []
    
    
    lr = LinearRegression()
    
    
    
    if "Vaka" in bagımlı_degisken:
        x_train,x_test,y_train,y_test = train_test_split(ulke[["Days Since"]],ulke[["Confirmed"]],test_size = 0.33,random_state = 0)
        x_train = x_train.sort_index()
        y_train = y_train.sort_index()
        model = lr.fit(x_train,y_train)
        prediction = model.predict(x_test)
        prediction = pd.DataFrame(prediction,columns = ["Confirmed"])
        data.append({"x": x_train["Days Since"] , "y" : y_train["Confirmed"] , "type" : "line" , "name" : "vaka" })
        data.append({"x" : x_test["Days Since"] , "y" : prediction["Confirmed"] , "type" : "line" , "name" : "linear-regression"})
        #rmse 
        rmse = np.sqrt(mean_squared_error(y_test,prediction))
        #r2
        r2 = r2_score(y_test,prediction)
        
        
    if "Ölüm" in bagımlı_degisken :
        x_train,x_test,y_train,y_test = train_test_split(ulke[["Days Since"]],ulke[["Deaths"]],test_size = 0.33,random_state = 0)
        x_train = x_train.sort_index()
        y_train = y_train.sort_index()
        model = lr.fit(x_train,y_train)
        prediction = model.predict(x_test)
        prediction = pd.DataFrame(prediction,columns = ["Deaths"])
        data.append({"x": x_train["Days Since"] , "y" : y_train["Deaths"] , "type" : "line" , "name" : "olum" })
        data.append({"x" : x_test["Days Since"] , "y" : prediction["Deaths"] , "type" : "line" , "name" : "linear-regression"})
        #rmse 
        rmse = np.sqrt(mean_squared_error(y_test,prediction))
        #r2
        r2 = r2_score(y_test,prediction)
        
    if "İyileşen" in bagımlı_degisken:
        x_train,x_test,y_train,y_test = train_test_split(ulke[["Days Since"]],ulke[["Recovered"]],test_size = 0.33,random_state = 0)
        x_train = x_train.sort_index()
        y_train = y_train.sort_index()
        model = lr.fit(x_train,y_train)
        prediction = model.predict(x_test)
        prediction = pd.DataFrame(prediction,columns = ["Recovered"])
        data.append({"x": x_train["Days Since"] , "y" : y_train["Recovered"] , "type" : "line" , "name" : "iyilesen" })
        data.append({"x" : x_test["Days Since"] , "y" : prediction["Recovered"] , "type" : "line" , "name" : "linear-regression"})
        #rmse 
        rmse = np.sqrt(mean_squared_error(y_test,prediction))
        #r2
        r2 = r2_score(y_test,prediction)
        
    figure = {
            
            "data" : data

            }
        

    return figure,rmse,r2


@app.callback(Output("prediction1","children"),
              [Input("ulke","value"),
               Input("bagımlı-degisken","value"),
               Input("day","value")])

def lin_reg_prediction(ulke,bagımlı_degisken,day):
    ulke = df[df["Country"] == ulke]
    
    
    lr = LinearRegression()

    
    if "Vaka" in bagımlı_degisken:
        x_train,x_test,y_train,y_test = train_test_split(ulke[["Days Since"]],ulke[["Confirmed"]],test_size = 0.33,random_state = 0)
        
        model = lr.fit(x_train,y_train)
        tahmin = model.predict([[day]])

        

        


    if "Ölüm" in bagımlı_degisken :
        x_train,x_test,y_train,y_test = train_test_split(ulke[["Days Since"]],ulke[["Deaths"]],test_size = 0.33,random_state = 0)

        model = lr.fit(x_train,y_train)
        tahmin = model.predict([[day]])

        



        
    if "İyileşen" in bagımlı_degisken:
        x_train,x_test,y_train,y_test = train_test_split(ulke[["Days Since"]],ulke[["Recovered"]],test_size = 0.33,random_state = 0)

        model = lr.fit(x_train,y_train)
        tahmin = model.predict([[day]])

        
        

        
    return "{}".format(tahmin[0][0])


@app.callback([Output("poly-reg","figure"),
              Output(component_id = "rmse_poly" , component_property = "children"),
              Output(component_id = "r2_poly" , component_property = "children")],
              [Input("ulke","value"),
               Input("bagımlı-degisken","value"),
               Input("degree","value")])




def poly_reg(ulke,bagımlı_degisken,degree):
    ulke = df[df["Country"] == ulke]
    
    data = []
    
    
    lr = LinearRegression()
    poly_reg = PolynomialFeatures(degree = degree)
    
    
    
    if "Vaka" in bagımlı_degisken:
        x_train,x_test,y_train,y_test = train_test_split(ulke[["Days Since"]],ulke[["Confirmed"]],test_size = 0.33,random_state = 0)
        x_train = x_train.sort_index()
        y_train = y_train.sort_index()
        x_test = x_test.sort_index()
        y_test = y_test.sort_index()
        x_poly = poly_reg.fit_transform(x_train)
        model = lr.fit(x_poly,y_train)
        prediction = model.predict(poly_reg.fit_transform(x_test))
        prediction = pd.DataFrame(prediction,columns = ["Confirmed"])
        data.append({"x": x_train["Days Since"] , "y" : y_train["Confirmed"] , "type" : "line" , "name" : "vaka" })
        data.append({"x" : x_test["Days Since"] , "y" : prediction["Confirmed"] , "type" : "line" , "name" : "Polinomal Regresyon"})
        #rmse 
        rmse = np.sqrt(mean_squared_error(y_test,prediction))
        #r2
        r2 = r2_score(y_test,prediction)

      
    if "Ölüm" in bagımlı_degisken :
        x_train,x_test,y_train,y_test = train_test_split(ulke[["Days Since"]],ulke[["Deaths"]],test_size = 0.33,random_state = 0)
        x_train = x_train.sort_index()
        y_train = y_train.sort_index()
        x_test = x_test.sort_index()
        y_test = y_test.sort_index()   
        x_poly = poly_reg.fit_transform(x_train)
        model = lr.fit(x_poly,y_train)
        prediction = model.predict(poly_reg.fit_transform(x_test))
        prediction = pd.DataFrame(prediction,columns = ["Deaths"])
        data.append({"x": x_train["Days Since"] , "y" : y_train["Deaths"] , "type" : "line" , "name" : "olum" })
        data.append({"x" : x_test["Days Since"] , "y" : prediction["Deaths"] , "type" : "line" , "name" : "Polinomal Regresyon"})

        #rmse 
        rmse = np.sqrt(mean_squared_error(y_test,prediction))
        #r2
        r2 = r2_score(y_test,prediction)

       
    if "İyileşen" in bagımlı_degisken:
        x_train,x_test,y_train,y_test = train_test_split(ulke[["Days Since"]],ulke[["Recovered"]],test_size = 0.33,random_state = 0)
        x_train = x_train.sort_index()
        y_train = y_train.sort_index()
        x_test = x_test.sort_index()
        y_test = y_test.sort_index()
        x_poly = poly_reg.fit_transform(x_train)
        model = lr.fit(x_poly,y_train)
        prediction = model.predict(poly_reg.fit_transform(x_test))
        prediction = pd.DataFrame(prediction,columns = ["Recovered"])
        data.append({"x": x_train["Days Since"] , "y" : y_train["Recovered"] , "type" : "line" , "name" : "iyilesen" })
        data.append({"x" : x_test["Days Since"] , "y" : prediction["Recovered"] , "type" : "line" , "name" : "Polinomal Regresyon"})
        
        #rmse 
        rmse = np.sqrt(mean_squared_error(y_test,prediction))
        #r2
        r2 = r2_score(y_test,prediction)        
        

        
    figure = {
            
            "data" : data

            }
        

    return figure,rmse,r2


@app.callback(Output("prediction2","children"),
              [Input("ulke","value"),
               Input("bagımlı-degisken","value"),
               Input("day","value"),
               Input("degree","value")])




def poly_reg_predict(ulke,bagımlı_degisken,day,degree):
    ulke = df[df["Country"] == ulke]
    
    
    
    lr = LinearRegression()
    poly_reg = PolynomialFeatures(degree = degree)
    
    
    
    if "Vaka" in bagımlı_degisken:
        x_train,x_test,y_train,y_test = train_test_split(ulke[["Days Since"]],ulke[["Confirmed"]],test_size = 0.33,random_state = 0)
        x_poly = poly_reg.fit_transform(x_train)
        model = lr.fit(x_poly,y_train)
        tahmin = model.predict(poly_reg.fit_transform([[day]]))

        
    if "Ölüm" in bagımlı_degisken :
        x_train,x_test,y_train,y_test = train_test_split(ulke[["Days Since"]],ulke[["Deaths"]],test_size = 0.33,random_state = 0)
  
        x_poly = poly_reg.fit_transform(x_train)
        model = lr.fit(x_poly,y_train)
        tahmin = model.predict(poly_reg.fit_transform([[day]]))
        

        
    if "İyileşen" in bagımlı_degisken:
        x_train,x_test,y_train,y_test = train_test_split(ulke[["Days Since"]],ulke[["Recovered"]],test_size = 0.33,random_state = 0)

        x_poly = poly_reg.fit_transform(x_train)
        model = lr.fit(x_poly,y_train)
        tahmin = model.predict(poly_reg.fit_transform([[day]]))

        
        

    return "{}".format(tahmin[0][0])
    
    









    
@app.callback([Output(component_id = "svm-reg", component_property = "figure"),
              Output(component_id = "rmse_svr" , component_property = "children"),
              Output(component_id = "r2_svr" , component_property = "children")],
              [Input("ulke","value"),
               Input("bagımlı-degisken","value"),
               Input("kernel","value")])



def svm_reg(ulke,bagımlı_degisken,kernel):
    ulke = df[df["Country"] == ulke]
    data = []
    
    svr_reg = SVR(kernel = kernel)
    sc = StandardScaler()

    
    
    if "Vaka" in bagımlı_degisken:
        x_train,x_test,y_train,y_test = train_test_split(ulke[["Days Since"]],ulke[["Confirmed"]],test_size = 0.33,random_state = 0)
        X_train = sc.fit_transform(x_train)
        X_test = sc.fit_transform(x_test)
        Y_train = sc.fit_transform(y_train)
        Y_test = sc.fit_transform(y_test)
        
        X_train = np.sort(X_train,axis = None)
        X_test = np.sort(X_test,axis = None)
        Y_train = np.sort(Y_train,axis = None)
        Y_test = np.sort(Y_test,axis = None)
        x_train = x_train.sort_index()
        y_train = y_train.sort_index()
        x_test = x_test.sort_index()
        y_test = y_test.sort_index()        
        
        x_shape = X_train.shape
        y_shape = Y_train.shape
        x_test_shape = X_test.shape
        
        
        X_train = X_train.reshape(x_shape[0],1)
        Y_train = Y_train.reshape(y_shape[0])
        X_test = X_test.reshape(x_test_shape[0],1)

        model = svr_reg.fit(X_train,Y_train)
        prediction = model.predict(X_test)
        rmse = np.sqrt(mean_squared_error(Y_test,prediction))
        #r2
        r2 = r2_score(Y_test,prediction)
        
        #unscale 
        X_train = sc.inverse_transform(X_train)
        Y_train = sc.inverse_transform(Y_train)
        X_test = sc.inverse_transform(X_test)
        prediction = sc.inverse_transform(prediction)
        
        
        prediction = pd.DataFrame(prediction,columns = ["Confirmed"])
        X_train = pd.DataFrame(X_train,columns = ["Days Since"])
        Y_train = pd.DataFrame(Y_train,columns = ["Confirmed"])
        X_test = pd.DataFrame(X_test,columns = ["Days Since"])
        data.append({"x": x_train["Days Since"] , "y" : Y_train["Confirmed"] , "type" : "line" , "name" : "vaka" })
        data.append({"x" : x_test["Days Since"] , "y" : prediction["Confirmed"] , "type" : "line" , "name" : "Destek Vektör Regresyon"})
        

        
        
    if "Ölüm" in bagımlı_degisken :
        x_train,x_test,y_train,y_test = train_test_split(ulke[["Days Since"]],ulke[["Deaths"]],test_size = 0.33,random_state = 0)
        X_train = sc.fit_transform(x_train)
        X_test = sc.fit_transform(x_test)
        Y_train = sc.fit_transform(y_train)
        Y_test = sc.fit_transform(y_test)
        
        X_train = np.sort(X_train,axis = None)
        X_test = np.sort(X_test,axis = None)
        Y_train = np.sort(Y_train,axis = None)
        Y_test = np.sort(Y_test,axis = None)
        x_train = x_train.sort_index()
        y_train = y_train.sort_index()
        x_test = x_test.sort_index()
        y_test = y_test.sort_index()  
        
        x_shape = X_train.shape
        y_shape = Y_train.shape
        x_test_shape = X_test.shape
        
        
        X_train = X_train.reshape(x_shape[0],1)
        Y_train = Y_train.reshape(y_shape[0])
        X_test = X_test.reshape(x_test_shape[0],1)

        model = svr_reg.fit(X_train,Y_train)
        prediction = model.predict(X_test)
        
        rmse = np.sqrt(mean_squared_error(Y_test,prediction))
        #r2
        r2 = r2_score(Y_test,prediction) 
        
        #unscale 
        X_train = sc.inverse_transform(X_train)
        Y_train = sc.inverse_transform(Y_train)
        X_test = sc.inverse_transform(X_test)
        prediction = sc.inverse_transform(prediction)
        
        
        prediction = pd.DataFrame(prediction,columns = ["Deaths"])
        X_train = pd.DataFrame(X_train,columns = ["Days Since"])
        Y_train = pd.DataFrame(Y_train,columns = ["Deaths"])
        X_test = pd.DataFrame(X_test,columns = ["Days Since"])
        data.append({"x": X_train["Days Since"] , "y" : Y_train["Deaths"] , "type" : "line" , "name" : "ölum" })
        data.append({"x" : X_test["Days Since"] , "y" : prediction["Deaths"] , "type" : "line" , "name" : "Destek Vektör Regresyon"})



       
    if "İyileşen" in bagımlı_degisken:
        x_train,x_test,y_train,y_test = train_test_split(ulke[["Days Since"]],ulke[["Recovered"]],test_size = 0.33,random_state = 0)
        X_train = sc.fit_transform(x_train)
        X_test = sc.fit_transform(x_test)
        Y_train = sc.fit_transform(y_train)
        Y_test = sc.fit_transform(y_test)
        
        X_train = np.sort(X_train,axis = None)
        X_test = np.sort(X_test,axis = None)
        Y_train = np.sort(Y_train,axis = None)
        Y_test = np.sort(Y_test,axis = None)
        
        x_train = x_train.sort_index()
        y_train = y_train.sort_index()
        x_test = x_test.sort_index()
        y_test = y_test.sort_index()  
        
        x_shape = X_train.shape
        y_shape = Y_train.shape
        x_test_shape = X_test.shape
        
        
        X_train = X_train.reshape(x_shape[0],1)
        Y_train = Y_train.reshape(y_shape[0])
        X_test = X_test.reshape(x_test_shape[0],1)

        model = svr_reg.fit(X_train,Y_train)
        prediction = model.predict(X_test)
        
        rmse = np.sqrt(mean_squared_error(Y_test,prediction))
        #r2
        r2 = r2_score(Y_test,prediction)
        
        #unscale 
        X_train = sc.inverse_transform(X_train)
        Y_train = sc.inverse_transform(Y_train)
        X_test = sc.inverse_transform(X_test)
        prediction = sc.inverse_transform(prediction)
        
        
              
        prediction = pd.DataFrame(prediction,columns = ["Recovered"])
        X_train = pd.DataFrame(X_train,columns = ["Days Since"])
        Y_train = pd.DataFrame(Y_train,columns = ["Recovered"])
        X_test = pd.DataFrame(X_test,columns = ["Days Since"])
        data.append({"x": X_train["Days Since"] , "y" : Y_train["Recovered"] , "type" : "line" , "name" : "iyilesen" })
        data.append({"x" : X_test["Days Since"] , "y" : prediction["Recovered"] , "type" : "line" , "name" : "Destek Vektör Regresyon"})


        
    figure = {
            
            "data" : data

            }
        

    return figure,rmse,r2
    


@app.callback(Output("prediction3","children"),
              [Input("ulke","value"),
               Input("bagımlı-degisken","value"),
               Input("day","value"),
               Input("kernel","value")])


def svr_predict(ulke,bagımlı_degisken,day,kernel):
    ulke = df[df["Country"] == ulke]

        
    svr_reg = SVR(kernel = kernel)
    sc = StandardScaler()

    
    
    if "Vaka" in bagımlı_degisken:
        x_train,x_test,y_train,y_test = train_test_split(ulke[["Days Since"]],ulke[["Confirmed"]],test_size = 0.33,random_state = 0)
        X_train = sc.fit_transform(x_train)
        X_test = sc.fit_transform(x_test)
        Y_train = sc.fit_transform(y_train)
        Y_test = sc.fit_transform(y_test)
        
        X_train = np.sort(X_train,axis = None)
        X_test = np.sort(X_test,axis = None)
        Y_train = np.sort(Y_train,axis = None)
        Y_test = np.sort(Y_test,axis = None)
        
        x_shape = X_train.shape
        y_shape = Y_train.shape
        x_test_shape = X_test.shape
        
        
        X_train = X_train.reshape(x_shape[0],1)
        Y_train = Y_train.reshape(y_shape[0])
        X_test = X_test.reshape(x_test_shape[0],1)

        model = svr_reg.fit(X_train,Y_train)
        tahmin = model.predict([[day]])
        tahmin = sc.inverse_transform(tahmin)
        
    if "Ölüm" in bagımlı_degisken :
        x_train,x_test,y_train,y_test = train_test_split(ulke[["Days Since"]],ulke[["Deaths"]],test_size = 0.33,random_state = 0)
        X_train = sc.fit_transform(x_train)
        X_test = sc.fit_transform(x_test)
        Y_train = sc.fit_transform(y_train)
        Y_test = sc.fit_transform(y_test)
        
        X_train = np.sort(X_train,axis = None)
        X_test = np.sort(X_test,axis = None)
        Y_train = np.sort(Y_train,axis = None)
        Y_test = np.sort(Y_test,axis = None)
        
        x_shape = X_train.shape
        y_shape = Y_train.shape
        x_test_shape = X_test.shape
        
        
        X_train = X_train.reshape(x_shape[0],1)
        Y_train = Y_train.reshape(y_shape[0])
        X_test = X_test.reshape(x_test_shape[0],1)

        model = svr_reg.fit(X_train,Y_train)
        tahmin = model.predict([[day]])
        tahmin = sc.inverse_transform(tahmin)
        
    if "İyileşen" in bagımlı_degisken:
        x_train,x_test,y_train,y_test = train_test_split(ulke[["Days Since"]],ulke[["Recovered"]],test_size = 0.33,random_state = 0)
        X_train = sc.fit_transform(x_train)
        X_test = sc.fit_transform(x_test)
        Y_train = sc.fit_transform(y_train)
        Y_test = sc.fit_transform(y_test)
        
        X_train = np.sort(X_train,axis = None)
        X_test = np.sort(X_test,axis = None)
        Y_train = np.sort(Y_train,axis = None)
        Y_test = np.sort(Y_test,axis = None)
        
        x_shape = X_train.shape
        y_shape = Y_train.shape
        x_test_shape = X_test.shape
        
        
        X_train = X_train.reshape(x_shape[0],1)
        Y_train = Y_train.reshape(y_shape[0])
        X_test = X_test.reshape(x_test_shape[0],1)

        model = svr_reg.fit(X_train,Y_train)
        tahmin = model.predict([[day]])
        tahmin = sc.inverse_transform(tahmin)
        

        

    return "{}".format(tahmin[0])



@app.callback([Output("rf-reg","figure"),
               Output(component_id = "rmse_rf" , component_property = "children"),
              Output(component_id = "r2_rf" , component_property = "children")],
              [Input("ulke","value"),
               Input("bagımlı-degisken","value"),
               Input("n-estimators","value")])


def rf_reg(ulke,bagımlı_degisken,n_estimators):
    ulke = df[df["Country"] == ulke]
    data = []
    
    rf_reg = RandomForestRegressor(random_state = 0 , n_estimators = n_estimators)
    
    if "Vaka" in bagımlı_degisken:
        x_train,x_test,y_train,y_test = train_test_split(ulke[["Days Since"]],ulke[["Confirmed"]],test_size = 0.33,random_state = 0)
        x_train = x_train.sort_index()
        y_train = y_train.sort_index()
        x_test = x_test.sort_index()
        y_test = y_test.sort_index()
        
        model = rf_reg.fit(x_train,y_train)
        prediction = model.predict(x_test)
        
        prediction = pd.DataFrame(prediction,columns = ["Confirmed"])
        data.append({"x": x_train["Days Since"] , "y" : y_train["Confirmed"] , "type" : "line" , "name" : "vaka" })
        data.append({"x" : x_test["Days Since"] , "y" : prediction["Confirmed"] , "type" : "line" , "name" : "rassal orman regresyonu"})
        rmse = np.sqrt(mean_squared_error(y_test,prediction))
        #r2
        r2 = r2_score(y_test,prediction)        
        
    
    if "Ölüm" in bagımlı_degisken :
        x_train,x_test,y_train,y_test = train_test_split(ulke[["Days Since"]],ulke[["Deaths"]],test_size = 0.33,random_state = 0)
        x_train = x_train.sort_index()
        y_train = y_train.sort_index()
        x_test = x_test.sort_index()
        y_test = y_test.sort_index()
        model = rf_reg.fit(x_train,y_train)
        prediction = model.predict(x_test)
        
        prediction = pd.DataFrame(prediction,columns = ["Deaths"])
        data.append({"x": x_train["Days Since"] , "y" : y_train["Deaths"] , "type" : "line" , "name" : "olum" })
        data.append({"x" : x_test["Days Since"] , "y" : prediction["Deaths"] , "type" : "line" , "name" : "rassal orman regresyonu"})
        
        rmse = np.sqrt(mean_squared_error(y_test,prediction))
        #r2
        r2 = r2_score(y_test,prediction)
    
    
    if "İyileşen" in bagımlı_degisken:
        x_train,x_test,y_train,y_test = train_test_split(ulke[["Days Since"]],ulke[["Recovered"]],test_size = 0.33,random_state = 0)
        x_train = x_train.sort_index()
        y_train = y_train.sort_index()  
        x_test = x_test.sort_index()
        y_test = y_test.sort_index()
        model = rf_reg.fit(x_train,y_train)
        prediction = model.predict(x_test)
        
        
        prediction = pd.DataFrame(prediction,columns = ["Recovered"])
        data.append({"x": x_train["Days Since"] , "y" : y_train["Recovered"] , "type" : "line" , "name" : "iyilesen" })
        data.append({"x" : x_test["Days Since"] , "y" : prediction["Recovered"] , "type" : "line" , "name" : "rassal orman regresyonu"})
        rmse = np.sqrt(mean_squared_error(y_test,prediction))
        #r2
        r2 = r2_score(y_test,prediction)        
 
    
    figure = {
            
            "data" : data

            }
        

    return figure,rmse,r2
    
    
@app.callback(Output("prediction4","children"),
              [Input("ulke","value"),
               Input("bagımlı-degisken","value"),
               Input("day","value"),
               Input("n-estimators","value")])



def rf_reg_predict(ulke,bagımlı_degisken,day,n_estimators):
    ulke = df[df["Country"] == ulke]
    
    
    rf_reg = RandomForestRegressor(random_state = 0 , n_estimators = n_estimators)
    
    if "Vaka" in bagımlı_degisken:
        x_train,x_test,y_train,y_test = train_test_split(ulke[["Days Since"]],ulke[["Confirmed"]],test_size = 0.33,random_state = 0)            
        model = rf_reg.fit(x_train,y_train)
        prediction = model.predict([[day]])
        
    if "Ölüm" in bagımlı_degisken :
        x_train,x_test,y_train,y_test = train_test_split(ulke[["Days Since"]],ulke[["Deaths"]],test_size = 0.33,random_state = 0)
       
        model = rf_reg.fit(x_train,y_train)
        prediction = model.predict([[day]])
    
    if "İyileşen" in bagımlı_degisken:
        x_train,x_test,y_train,y_test = train_test_split(ulke[["Days Since"]],ulke[["Recovered"]],test_size = 0.33,random_state = 0)

        model = rf_reg.fit(x_train,y_train)
        prediction = model.predict([[day]])
        
    return "{}".format(prediction[0])
        
        
    








if __name__ == '__main__':
    app.run_server(debug=False)





# -*- coding: utf-8 -*-
"""
Created on Sat Dec 31 00:37:14 2022

@author: Julien
"""

#%% Import des données 
import yfinance as yf
import numpy as np
import streamlit as st


st.set_page_config(
    page_icon = "a",
    page_title = "Analyse actions",
    
    layout = "wide"
)

st.markdown("<h1 style='text-align: center; color: steelblue; font-family: Droid Serif'>Analyse d'action</h1>", 
            unsafe_allow_html=True)

Ticker_yahoo = st.text_input( label = 'Ticker yahoo finance :')

# Ticker_yahoo = 'AI.PA'

if Ticker_yahoo != "" :
    try:
        data = yf.Ticker(Ticker_yahoo)
        dataDF = data.history(period = 'max', interval='1d')
        
       
        name = data.info['shortName']
        currency = data.fast_info['currency']
        
        # name = 'No data'
        # currency = 'No data'
        
        div = data.dividends
        div.index = div.index.year
        div = div.groupby('Date').sum()
        
        #%% 
        
        cours_corrige = dataDF['Close'] > 0
        dataDF = dataDF[cours_corrige]
        
        #%% Liste de jour
        
        t0 = dataDF.index[0]
        time_days = []
        
        for d in dataDF.index:
            dt = d - t0
            dt = dt.days
            time_days.append(dt)
        
        #%%
        
        x = np.array(time_days)
        y = np.array(dataDF['Close'])
        
        log_y = np.log(y)
        
        #%% reg linéaire
        
        coefficients = np.polyfit(time_days, np.log(dataDF['Close']), 1)
        
        y_rl = np.exp(coefficients[1]) * np.exp(coefficients[0]*np.array(time_days))
        
        dataDF['Reg_lin'] = y_rl
        
        e_t = np.std(log_y-np.log(y_rl))
        
        y1 = coefficients[1]+e_t
        y2 = coefficients[1]+2*e_t
        y3 = coefficients[1]-e_t
        y4 = coefficients[1]-2*e_t
        
        y_rl1 = np.exp(y1) * np.exp(coefficients[0]*np.array(time_days))
        y_rl2 = np.exp(y2) * np.exp(coefficients[0]*np.array(time_days))
        y_rl3 = np.exp(y3) * np.exp(coefficients[0]*np.array(time_days))
        y_rl4 = np.exp(y4) * np.exp(coefficients[0]*np.array(time_days))
        
        dataDF['+1'] = y_rl1
        dataDF['+2'] = y_rl2
        dataDF['-1'] = y_rl3
        dataDF['-2'] = y_rl4
        
        
        
        #%% Calcul du % d'évolution de la regression linéaire par an
        
        dta=dt/365.25
        dv=(np.exp((np.log(y_rl[-1]/y_rl[0])/dta))-1)*100
        
        v = dataDF['Close'][-1]
        position = ( np.log(v) - coefficients[0]*x[-1] - coefficients[1] )/e_t
        
        
        #%% Représentation graphique
        
        import plotly.graph_objects as go
                                          
        fig = go.Figure()
        fig.add_trace(go.Scatter(x = dataDF.index, y = dataDF["Close"], name='Value',
                                 line=dict(color='steelblue', width=1)))
        
        
        fig.add_trace(go.Scatter(x = dataDF.index, y = dataDF["Reg_lin"], name = 'Linear regression',
                                 line=dict(color='green', width=1)))
        
        fig.add_trace(go.Scatter(mode = "markers+text",
                                 x = [dataDF.index[-1]],
                                 y = [dataDF["Reg_lin"][-1]],
                                 text = [str(int(dataDF["Reg_lin"][-1]))],
                                 textposition = "middle right",
                                 marker = dict(color = "green"),
                                 showlegend = False))
                      
                      
        fig.add_trace(go.Scatter(x = dataDF.index, y = dataDF["+1"], name='-2σ, -1σ, +1σ, +2σ,',
                                 line = dict(color = 'firebrick', width=1,
                                      dash = 'dash')))
        
        fig.add_trace(go.Scatter(mode = "markers+text",
                                 x = [dataDF.index[-1]],
                                 y = [dataDF["+1"][-1]],
                                 text = [str(int(dataDF["+1"][-1]))],
                                 textposition = "middle right",
                                 marker = dict(color = "firebrick"),
                                 showlegend = False))
        
        fig.add_trace(go.Scatter(x = dataDF.index, y = dataDF["+2"], name='+2σ',
                                 showlegend = False,
                                 line = dict(color = 'firebrick', width=1,
                                      dash = 'dash')))
        
        fig.add_trace(go.Scatter(mode = "markers+text",
                                 x = [dataDF.index[-1]],
                                 y = [dataDF["+2"][-1]],
                                 text = [str(int(dataDF["+2"][-1]))],
                                 textposition = "middle right",
                                 marker = dict(color = "firebrick"),
                                 showlegend = False))
        
        fig.add_trace(go.Scatter(x = dataDF.index, y = dataDF["-1"], name='-1σ',
                                 showlegend = False,
                                 line = dict(color = 'firebrick', width=1,
                                      dash = 'dash')))
        
        fig.add_trace(go.Scatter(mode = "markers+text",
                                 x = [dataDF.index[-1]],
                                 y = [dataDF["-1"][-1]],
                                 text = [str(int(dataDF["-1"][-1]))],
                                 textposition = "middle right",
                                 marker = dict(color = "firebrick"),
                                 showlegend = False))
        
        fig.add_trace(go.Scatter(x = dataDF.index, y = dataDF["-2"], name='-2σ',
                                 showlegend = False,
                                 line = dict(color = 'firebrick', width=1,
                                      dash = 'dash')))
        
        fig.add_trace(go.Scatter(mode = "markers+text",
                                 x = [dataDF.index[-1]],
                                 y = [dataDF["-2"][-1]],
                                 text = [str(int(dataDF["-2"][-1]))],
                                 textposition = "middle right",
                                 marker = dict(color = "firebrick"),
                                 showlegend = False))
        
        fig.update_yaxes(type = "log", title = currency)
        
        fig.update_layout(
            height= 700,
            width = 1400,
            title = name,
            title_font_family = "Droid Serif",
            title_font_color = "steelblue",
            title_font_size = 23,    
            title_x = 0.5,    
            font_color = "Black",
            #layout="wide"
        )
        
        st.write(fig)
        #%%
        st.write(f"L'évolution de la droite de regression linéaire est de {round(dv,1)} % par an")
        
        st.write(f"Le cours de l'action est actuellement à {round(position,2)} écart type")
        
        st.write(f"L'indice de Lagrange est de {(dv*(1-e_t)*-position):.1f}")
        #%% Cours sur un an 
        col1, col2 = st.columns([1,1])
        
        with col1:
            data_one_year = data.history(period = '1y', interval = '1d')
            data_one_year['initial'] = data_one_year['Close'][0]
            
            fig2 = go.Figure()
            
            fig2.add_trace(go.Scatter(x = data_one_year.index, y = data_one_year['Close'], name='Value',
                                     line = dict(color='steelblue', width=1)))
            
            fig2.add_trace(go.Scatter(x = data_one_year.index, y = data_one_year['initial'], name = 'Value one year ago',
                                     line = dict(color='red', width=1)))
            
            fig2.update_yaxes(title = currency)
            fig2.update_layout(
                # height= 600,
                # width = 800,
                showlegend=False,
                title = "Cotation sur un an",
                title_x = 0.5,
                title_font_family = "Droid Serif",
                title_font_color = "steelblue",
                title_font_size = 18,
                )
        
            st.write(fig2)
        
        
        #%%
        
        with col2:
        
            fig3 = go.Figure(data=[
                go.Bar(name = 'Dividends', x = div.index, y = div)])
            fig3.update_yaxes(title = currency)    
            fig3.update_traces(marker_color = 'steelblue')
            fig3.update_layout(
                # height= 600,
                # width = 700,
                showlegend = False,
                title = "Dividendes",
                title_x = 0.5,
                title_font_family = "Droid Serif",
                title_font_color = "steelblue",
                title_font_size = 18)
            st.write(fig3)
            
    except:
        st.write("Symbole non reconnu")


# -*- coding: utf-8 -*-
"""
Created on Tue Jul 26 17:24:50 2022

@author: GeneralDeGaulle
"""

#%%
import pandas as pd
import os
import numpy as np


#%%
import get_new_df_data
#import get_new_df_data


#%% identifier s'il y a une doublette de vol à réconcilier
# to find flights which have been split by adsb-exchange.com at midnight UTC.
# then "y_split_flights_reconciliation.py" to be used
def fct_check_reconciliation(df_new_flt_and_last):
    df_vols_tbc = df_new_flt_and_last.copy()

    df_vols_tbc.loc[:,"next_flight_departure"] = df_vols_tbc["airport_departure"].shift(1)
    df_vols_tbc.loc[:,"next_flight_departure_date"] = df_vols_tbc["departure_date_utc"].shift(1)
    df_vols_tbc.loc[:,"diff_with_next"] = df_vols_tbc["next_flight_departure_date"] - df_vols_tbc["arrival_date_utc"]
    df_vols_tbc.loc[:,"next_flight_csv"] = df_vols_tbc["path_csv"].shift(1)

    df_vols_tbc_1 = df_vols_tbc[(df_vols_tbc["airport_arrival"] == "A/C in cruise") &
                              (df_vols_tbc["next_flight_departure"] == "A/C in cruise") &
                              (df_vols_tbc["airport_departure"] != "A/C in cruise")]

    df_vols_tbc_2 = df_vols_tbc[(df_vols_tbc["arrival_date_utc"].dt.strftime("%Hh%M") == "23h59")]


    df_vols_to_be_merged_1 = df_vols_tbc_1[(df_vols_tbc_1["arrival_date_utc"].dt.strftime("%H") >= "23") &
                             (df_vols_tbc_1["diff_with_next"].dt.seconds/3600 <= 4)]

    df_vols_to_be_merged_2 = df_vols_tbc_2[(df_vols_tbc_2["diff_with_next"].dt.seconds/3600 <= 1)]


    df_vols_to_be_merged = pd.concat([df_vols_to_be_merged_1, df_vols_to_be_merged_2])

    return df_vols_to_be_merged


#%% concat all flights
def fct_concat_all_flights(df_avion, path):
    df_all_flights = pd.DataFrame()
    list_ac = df_avion["registration"].values

    for ac in list_ac:
        path_ac = os.path.join(path, "output", ac, ac +"_flight_data_all.csv")
        df = pd.read_csv(path_ac, delimiter = ",")
        df_all_flights = pd.concat([df_all_flights, df])

    df_all_flights["departure_date_utc"] = pd.to_datetime(df_all_flights["departure_date_utc"], utc=True)
    df_all_flights["arrival_date_utc"] = pd.to_datetime(df_all_flights["arrival_date_utc"], utc=True)
    df_all_flights = df_all_flights.sort_values(by=["departure_date_utc"], ascending = False)
    df_all_flights = df_all_flights.reset_index(drop=True)

    df_all_flights["routes"] = df_all_flights["airport_departure"] + " - " + df_all_flights["airport_arrival"]
    df_all_flights["routes"] = df_all_flights["routes"].astype('category')

    list_colonnes = df_all_flights.columns.tolist()

    for aircraft in list_ac:
        nom = df_avion[df_avion["registration"] == aircraft].proprio.values[0]
        df_all_flights.loc[df_all_flights["registration"] == aircraft, "propriétaire"] = nom

    #pour mettre le propriétaire en premier
    df_all_flights = df_all_flights.loc[:,["propriétaire" ] + list_colonnes]

    path_all_ac = os.path.join(path, "output", "all_flights_data.csv")
    df_all_flights.to_csv(path_all_ac, index=False, encoding="utf-8-sig")


#%%


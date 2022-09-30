import numpy as np
import pandas
import plotly.express as px
import pandas as pd
import os
from copy import deepcopy


def data_analysis(df_customers_db: pandas.DataFrame, df_suppliers_db: pandas.DataFrame) -> (dict, pd.DataFrame):

    df_customers = deepcopy(df_customers_db)
    df_suppliers = deepcopy(df_suppliers_db)

    index_max_demand = df_customers['Fixed Demand'].idxmax()
    index_min_demand = df_customers['Fixed Demand'].idxmin()
    index_max_supply = df_suppliers['Maximum Supply'].idxmax()
    index_min_supply = df_suppliers['Maximum Supply'].idxmin()

    mean_values, df_distances = calculate_distance(df_customers, df_suppliers)

    statistics = {'maximum_demand': {'Name': df_customers['Name'][index_max_demand],
                                     'Value': df_customers['Fixed Demand'].max()},
                  'minimum_demand': {'Name': df_customers['Name'][index_min_demand],
                                     'Value': df_customers['Fixed Demand'].min()},
                  'maximum_supply': {'Name': df_suppliers['Name'][index_max_supply],
                                     'Value': df_suppliers['Maximum Supply'].max()},
                  'minimum_supply': {'Name': df_suppliers['Name'][index_min_supply],
                                     'Value': df_suppliers['Maximum Supply'].min()},
                  'sum_demand': df_customers['Fixed Demand'].sum(),
                  'sum_supply': df_suppliers['Maximum Supply'].sum(),
                  }

    statistics.update(mean_values)

    plot_data_analysis(df_customers, df_suppliers)

    return statistics, df_distances


def calculate_distance(df_customers: pandas.DataFrame, df_suppliers: pandas.DataFrame) -> (dict, pd.DataFrame):

    mean_values = {}
    df_distances = pd.DataFrame(np.ones([len(df_customers), len(df_suppliers)]), columns=df_suppliers['Name'].values,
                                index=df_customers['Name'].values)

    for supplier in df_suppliers.transpose():
        for customer in df_customers.transpose():
            pi_rad = np.pi / 180
            x1 = float(df_customers['Longitude'][customer]) * pi_rad
            y1 = float(df_customers['Latitude'][customer]) * pi_rad
            x2 = float(df_suppliers['Longitude'][supplier]) * pi_rad
            y2 = float(df_suppliers['Latitude'][supplier]) * pi_rad

            delta_x = abs(x1 - x2)
            delta_y = abs(y1 - y2)

            a = (np.sin(delta_y / 2) ** 2 + np.cos(y1)) * np.cos(y2) * np.sin(delta_x / 2) ** 2

            c = 2 * np.arctan(np.sqrt(a) / np.sqrt(1 - a))

            earth_ray = 6371
            distance = earth_ray * c
            df_distances[df_suppliers['Name'][supplier]][df_customers['Name'][customer]] = distance

        mean_values[df_suppliers['Name'][supplier]] = df_distances[df_suppliers['Name'][supplier]].mean()

    return mean_values, df_distances


def plot_data_analysis(df_customers: pd.DataFrame, df_suppliers: pd.DataFrame):

    df_customers['ID'] = ['Customer'] * len(df_customers)
    df_suppliers['ID'] = ['Supplier'] * len(df_suppliers)
    df_customers['Size'] = [demand * 30 / df_customers['Fixed Demand'].max()
                            for demand in df_customers['Fixed Demand'].values.tolist()]
    df_suppliers['Size'] = [supply * 30 / df_suppliers['Maximum Supply'].max()
                            for supply in df_suppliers['Maximum Supply'].values.tolist()]

    df_customers.drop(['Fixed Demand'], axis=1, inplace=True)
    df_suppliers.drop(['Maximum Supply'], axis=1, inplace=True)

    df_all = pd.concat([df_customers, df_suppliers])

    fig = px.scatter(df_all, x="Longitude", y="Latitude", color="ID", size='Size', text='Name')

    if os.path.exists('static/fig.jpeg'):
        os.remove('static/fig.jpeg')

    fig.write_image('static/fig.jpeg')

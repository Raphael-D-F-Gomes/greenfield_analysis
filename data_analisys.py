import numpy as np
import pandas
import plotly.express as px
import pandas as pd
import os
from copy import deepcopy


def data_analysis(df_customers: pandas.DataFrame, df_suppliers: pandas.DataFrame):
    """
    This method calculates the mais statistics for a greenfield analysis. A plot that
    shows a position analysis is saved to be printed in the web page.

    Args:
        df_customers (pandas.DataFrame): dataframe with customers information
        df_suppliers (pandas.DataFrame): dataframe with suppliers information

    Returns:
         (dict): main statistics
         (pandas.DataFrame): information about suppliers and customers
    """

    customers = deepcopy(df_customers)
    suppliers = deepcopy(df_suppliers)

    mean_values = {}
    for supplier in suppliers.transpose():
        distance = 0
        for customer in customers.transpose():
            pi_rad = np.pi / 180
            x1 = float(customers['Longitude'][customer]) * pi_rad
            y1 = float(customers['Latitude'][customer]) * pi_rad
            x2 = float(suppliers['Longitude'][supplier]) * pi_rad
            y2 = float(suppliers['Latitude'][supplier]) * pi_rad

            delta_x = abs(x1 - x2)
            delta_y = abs(y1 - y2)

            a = (np.sin(delta_y / 2) ** 2 + np.cos(y1)) * np.cos(y2) * np.sin(delta_x / 2) ** 2

            c = 2 * np.arctan(np.sqrt(a) / np.sqrt(1 - a))

            distance += 6371 * c

        mean_values[suppliers['Name'][supplier]] = distance / len(customers)

    index_max_demand = customers['Fixed Demand'].idxmax()
    index_min_demand = customers['Fixed Demand'].idxmin()
    index_max_supply = suppliers['Maximum Supply'].idxmax()
    index_min_supply = suppliers['Maximum Supply'].idxmin()

    statistics = {'maximum_demand': {'Name': customers['Name'][index_max_demand],
                                     'Value': customers['Fixed Demand'].max()},
                  'minimum_demand': {'Name': customers['Name'][index_min_demand],
                                     'Value': customers['Fixed Demand'].min()},
                  'maximum_supply': {'Name': suppliers['Name'][index_max_supply],
                                     'Value': suppliers['Maximum Supply'].max()},
                  'minimum_supply': {'Name': suppliers['Name'][index_min_supply],
                                     'Value': suppliers['Maximum Supply'].min()},
                  'sum_demand': customers['Fixed Demand'].sum(),
                  'sum_supply': suppliers['Maximum Supply'].sum(),
                  }

    statistics.update(mean_values)

    customers['ID'] = ['Customer'] * len(customers)
    suppliers['ID'] = ['Supplier'] * len(suppliers)
    customers['Size'] = [demand * 30 / customers['Fixed Demand'].max()
                         for demand in customers['Fixed Demand'].values.tolist()]
    suppliers['Size'] = [supply * 30 / suppliers['Maximum Supply'].max()
                         for supply in suppliers['Maximum Supply'].values.tolist()]

    customers.drop(['Fixed Demand'], axis=1, inplace=True)
    suppliers.drop(['Maximum Supply'], axis=1, inplace=True)

    df_all = pd.concat([customers, suppliers])

    fig = px.scatter(df_all, x="Longitude", y="Latitude", color="ID", size='Size')

    if os.path.exists('static/fig.jpeg'):
        os.remove('static/fig.jpeg')

    fig.write_image('static/fig.jpeg')

    return statistics, df_all

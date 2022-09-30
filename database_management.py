import sqlite3
import pandas as pd
import numpy as np


def inserting_data(customers, suppliers):
    """
        This method insert data in the database

        Args:
            customers (pandas.DataFrame): customers information
            suppliers (pandas.DataFrame): suppliers information
    """

    conn = sqlite3.connect('greenfield_analysis_data.db')

    cursor = conn.cursor()

    for name in customers.transpose():
        if customers['Status'][name] == 'Include':
            cursor.execute("""
                                INSERT INTO CUSTOMERS (NAME, FIXED_DEMAND, LATITUDE, LONGITUDE)
                                VALUES (?, ?, ?, ?);
                            """, (customers['Name'][name], customers['Fixed Demand'][name],
                                  customers['Latitude'][name], customers['Longitude'][name]))

        elif customers['Status'][name] == 'Exclude':
            cursor.execute("""
                                DELETE FROM CUSTOMERS
                                WHERE NAME = (?) AND FIXED_DEMAND = (?) AND LATITUDE = (?) AND LONGITUDE = (?);
                           """, (customers['Name'][name], customers['Fixed Demand'][name],
                                 customers['Latitude'][name], customers['Longitude'][name]))

    for name in suppliers.transpose():

        if suppliers['Status'][name] == 'Include':
            cursor.execute("""
                                INSERT INTO SUPPLIERS (NAME, MAXIMUM_SUPPLY, LATITUDE, LONGITUDE)
                                VALUES (?, ?, ?, ?);
                            """, (suppliers['Name'][name], suppliers['Maximum Supply'][name],
                                  suppliers['Latitude'][name], suppliers['Longitude'][name]))

        elif suppliers['Status'][name] == 'Exclude':
            cursor.execute("""
                                DELETE FROM SUPPLIERS
                                WHERE NAME = (?) AND MAXIMUM_SUPPLY = (?) AND LATITUDE = (?) AND LONGITUDE = (?);
                           """,  (suppliers['Name'][name], suppliers['Maximum Supply'][name],
                                  suppliers['Latitude'][name], suppliers['Longitude'][name]))

    conn.commit()
    print('Dados foram inseridos com sucesso')
    conn.close()


def exporting_data():
    """
        This method export data from the database

        Returns:
            df_customers (pandas.DataFrame): customers information
            df_suppliers (pandas.DataFrame): suppliers information
    """
    df_suppliers = pd.DataFrame()
    df_customers = pd.DataFrame()

    conn = sqlite3.connect('greenfield_analysis_data.db')

    cursor_customers = conn.execute("""
                        SELECT NAME, FIXED_DEMAND, LATITUDE, LONGITUDE
                        FROM CUSTOMERS
                    """, )

    cursor_suppliers = conn.execute("""
                            SELECT NAME, MAXIMUM_SUPPLY, LATITUDE, LONGITUDE
                            FROM SUPPLIERS
                        """, )

    list_customers = cursor_customers.fetchall()
    list_suppliers = cursor_suppliers.fetchall()

    if list_customers:
        customers = [[row[0], row[1], row[2], row[3]] for row in list_customers]
        customers_columns = ['Name', 'Fixed Demand', 'Latitude', 'Longitude']
        df_customers = pd.DataFrame(np.array(customers), columns=customers_columns)
    if list_suppliers:
        suppliers = [[row[0], row[1], row[2], row[3]] for row in list_suppliers]
        suppliers_columns = ['Name', 'Maximum Supply', 'Latitude', 'Longitude']
        df_suppliers = pd.DataFrame(np.array(suppliers), columns=suppliers_columns)

    if not df_customers.empty:
        df_customers['Fixed Demand'] = df_customers['Fixed Demand'].astype(float)
        df_customers['Latitude'] = df_customers['Latitude'].astype(float)
        df_customers['Longitude'] = df_customers['Longitude'].astype(float)

    if not df_suppliers.empty:
        df_suppliers['Maximum Supply'] = df_suppliers['Maximum Supply'].astype(float)
        df_suppliers['Latitude'] = df_suppliers['Latitude'].astype(float)
        df_suppliers['Longitude'] = df_suppliers['Longitude'].astype(float)

    conn.close()

    return df_customers, df_suppliers

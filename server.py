import pandas as pd
from flask import Flask, render_template, request
import os
from error_analysis import ErrorAnalysis
import sys
from html_generator import html_generator
from insert_data import inserting_data, exporting_data
from copy import deepcopy
from data_analisys import data_analysis


app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def home():
    """
        Home Page
    """
    return render_template("homepage.html")


@app.route('/error_report', methods=['GET', 'POST'])
def error_report():
    """
        Web page that calculate statistics, manage database, show data analysis
    """
    if request.method == 'POST':

        df_customers_db = pd.DataFrame()
        df_suppliers_db = pd.DataFrame()
        statistics = {}

        file = request.files['upload_file']
        file_name = file.filename
        if not os.path.exists('upload_file'):
            os.mkdir('upload_file')

        path = 'upload_file/' + file_name
        file.save(path)
        expected_sheets = ['Locations', 'Customers', 'Suppliers']
        expected_columns = {'Customers': ['Name', 'Fixed Demand', 'Status'],
                            'Suppliers': ['Name', 'Maximum Supply', 'Status'],
                            'Locations': ['Name', 'Latitude', 'Longitude', 'Status']}
        error_analysis = ErrorAnalysis(path, expected_sheets, expected_columns)
        alerts, errors = error_analysis.errors_search()

        if not errors:
            df_customers = deepcopy(error_analysis.customers)
            df_suppliers = deepcopy(error_analysis.suppliers)
            df_locations = deepcopy(error_analysis.locations)
            customers_names = df_customers['Name'].values.tolist()
            suppliers_names = df_suppliers['Name'].values.tolist()

            df_customers['Latitude'] = [df_locations['Latitude'][name] for name in customers_names]
            df_customers['Longitude'] = [df_locations['Longitude'][name] for name in customers_names]
            df_suppliers['Latitude'] = [df_locations['Latitude'][name] for name in suppliers_names]
            df_suppliers['Longitude'] = [df_locations['Longitude'][name] for name in suppliers_names]

            customers_db, suppliers_db = exporting_data()

            customers_info = [(customers_db['Name'][i], customers_db['Latitude'][i], customers_db['Longitude'][i])
                              for i in range(len(customers_db))]

            suppliers_info = [(suppliers_db['Name'][i], suppliers_db['Latitude'][i], suppliers_db['Longitude'][i])
                              for i in range(len(suppliers_db))]

            for name in df_customers.transpose():
                customers_tuple = (df_customers['Name'][name], df_customers['Latitude'][name],
                                   df_customers['Longitude'][name])
                if customers_tuple in customers_info and df_customers['Status'][name] == 'Include':
                    df_customers.drop([name], axis=0, inplace=True)

            for name in df_suppliers.transpose():
                suppliers_tuple = (df_suppliers['Name'][name], df_suppliers['Latitude'][name],
                                   df_suppliers['Longitude'][name])
                if suppliers_tuple in suppliers_info and df_suppliers['Status'][name] == 'Include':
                    df_suppliers.drop([name], axis=0, inplace=True)

            inserting_data(df_customers, df_suppliers)

            df_customers_db, df_suppliers_db = exporting_data()

            if not df_suppliers_db.empty and not df_customers_db.empty:
                statistics, df_all = data_analysis(df_customers_db, df_suppliers_db)

        html_generator(alerts, errors, df_customers_db, df_suppliers_db, statistics)

        os.remove(path)

        return render_template('html_report.html')


if __name__ == '__main__':

    app.run(debug=True)

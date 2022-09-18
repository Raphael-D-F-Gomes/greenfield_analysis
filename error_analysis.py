import pandas as pd
import openpyxl


class ErrorAnalysis:

    def __init__(self, path, expected_sheets, expected_columns):
        """
            This class verifies inconsistencies in the excel file used for greenfield analysis

            Args:
                 path (str): excel file path
                 expected_sheets (list): names of the expected tables
                 expected_columns (dict): names of the expected columns in each table
        """
        self.excel_path = path
        self.expected_sheets = expected_sheets
        self.expected_columns = expected_columns
        self.customers = None
        self.suppliers = None
        self.locations = None
        self.customers_names = None
        self.suppliers_names = None
        self.locations_names = None

    def sheet_analysis(self):
        """
        This method verifies if the archive have all the tables expected and if there is any table not expected

        Returns:
            list: list of alerts
            list: list of errors
        """
        wb = openpyxl.load_workbook(self.excel_path)
        sheet_names = wb.sheetnames
        alert = []
        error = []

        alert += [f'Table {sheet} is not a expected table'
                  for sheet in sheet_names if sheet not in self.expected_sheets]

        error += [f'Table {sheet} is not in archive tables'
                  for sheet in self.expected_sheets if sheet not in sheet_names]

        return alert, error

    def columns_analysis(self):
        """
            This method verifies if all the tables have all the expected columns and if there is any table with not
            expected columns

            Returns:
                list: list of alerts
                list: list of errors
        """
        alert = []
        error = []
        self.customers = pd.read_excel(self.excel_path, sheet_name='Customers')
        self.locations = pd.read_excel(self.excel_path, sheet_name='Locations')
        self.suppliers = pd.read_excel(self.excel_path, sheet_name='Suppliers')

        self.customers_names = self.customers['Name'].values.tolist()
        self.locations_names = self.locations['Name'].values.tolist()
        self.suppliers_names = self.suppliers['Name'].values.tolist()

        customer_columns = list(self.customers)
        location_columns = list(self.locations)
        suppliers_columns = list(self.suppliers)

        error += [f'There is no {column} column in Customers table'
                  for column in self.expected_columns['Customers'] if column not in customer_columns]
        error += [f'There is no {column} column in suppliers table'
                  for column in self.expected_columns['Suppliers'] if column not in suppliers_columns]
        error += [f'There is no {column} column in locations table'
                  for column in self.expected_columns['Locations'] if column not in location_columns]

        alert += [f'Column {column} is not a expected column in customers table'
                  for column in customer_columns if column not in self.expected_columns['Customers']]
        alert += [f'Column {column} is not a expected column in suppliers table'
                  for column in suppliers_columns if column not in self.expected_columns['Suppliers']]
        alert += [f'Column {column} is not a expected column in locations table'
                  for column in location_columns if column not in self.expected_columns['Locations']]

        return alert, error

    def names_analysis(self):
        """
        Thie method verifies inconsistencies in the column names in the tables

        Returns:
            list: list of alerts
            list: list of errors
        """
        error = []
        alert = []

        duplicates = self.suppliers['Name'].duplicated().tolist()
        if any(duplicates):
            alert += [f"Name {self.suppliers['Name'][i]} is duplicated in Suppliers"
                      for i in range(len(self.suppliers_names)) if duplicates[i]]
            self.suppliers.drop_duplicates('Name', inplace=True)

        duplicates = self.locations[['Name', 'Status']].duplicated().tolist()
        if any(duplicates):
            alert += [f"Name {self.locations['Name'][i]} is duplicated with the same status in Locations"
                      for i in range(len(self.locations_names)) if duplicates[i]]
            self.locations.drop_duplicates(['Name', 'Status'], inplace=True)

        duplicates = self.customers['Name'].duplicated().tolist()
        if any(duplicates):
            alert += [f"Name {self.customers['Name'][i]} is duplicated in Customers"
                      for i in range(len(self.customers_names)) if duplicates[i]]
            self.customers.drop_duplicates('Name', inplace=True)

        duplicates = self.locations['Name'].duplicated().tolist()
        if any(duplicates):
            alert += [f"Name {self.locations['Name'][i]} is duplicated in Locations"
                      for i in range(len(self.locations_names)) if duplicates[i]]
            self.locations.drop_duplicates('Name', inplace=True)

        self.customers.set_index('Name', inplace=True, drop=False)
        self.locations.set_index('Name', inplace=True, drop=False)
        self.suppliers.set_index('Name', inplace=True, drop=False)

        error += [f'Name {name} in Customers does not exist in Locations table'
                  for name in self.customers_names if name not in self.locations_names]
        error += [f'Name {name} in Suppliers does not exist in Locations table'
                  for name in self.suppliers_names if name not in self.locations_names]

        if error:
            return alert, error

        error += [f'Status divergence in the name {name} between tables Customers and Locations'
                  for name in self.customers_names if self.customers['Status'][name] != self.locations['Status'][name]]

        error += [f'Status divergence in the name {name} between tables Suppliers and Locations'
                  for name in self.suppliers_names if self.suppliers['Status'][name] != self.locations['Status'][name]]

        return alert, error

    def values_analysis(self):
        """
            This method verifies inconsistencies in the values of each table

            Returns:
                list: list of alerts
                list: list of errors
        """
        alert = []
        error = []

        error += [f' Negative value for Maximum Supply from the supplier {name}'
                  for name in self.suppliers_names if self.suppliers['Maximum Supply'][name] < 0]
        error += [f' Negative value for Fixed Demand from the customer {name}'
                  for name in self.customers_names if self.customers['Fixed Demand'][name] < 0]

        alert += [f' Null value for Maximum Supply from the supplier {name}'
                  for name in self.suppliers_names if self.suppliers['Maximum Supply'][name] == 0]
        alert += [f' Null value for Fixed Demand from the customer {name}'
                  for name in self.customers_names if self.customers['Fixed Demand'][name] == 0]

        if (self.suppliers['Status'] == 'Exclude').all():
            alert += ['All values for status in the table suppliers are Exclude']

        if (self.customers['Status'] == 'Exclude').all():
            alert += ['All values for status in the table customers are Exclude']

        if (self.locations['Status'] == 'Exclude').all():
            alert += ['All values for status in the table locations are Exclude']

        alert += [f'Location {name} latitude is not in the correct format' for name in self.locations_names
                  if abs(self.locations['Latitude'][name]) > 90]

        alert += [f'Location {name} longitude is not in the correct format' for name in self.locations_names
                  if abs(self.locations['Longitude'][name]) > 180]

        error += [f'Status {status} in Locations is not supported, status must be Exclude or Include'
                  for status in self.locations['Status'].values.tolist() if status not in ['Exclude', 'Include']]

        error += [f'Status {status} in Suppliers is not supported, status must be Exclude or Include'
                  for status in self.suppliers['Status'].values.tolist() if status not in ['Exclude', 'Include']]

        error += [f'Status {status} in Customers is not supported, status must be Exclude or Include'
                  for status in self.customers['Status'].values.tolist() if status not in ['Exclude', 'Include']]

        return alert, error

    def errors_search(self):
        """
            This method execute all the verication methods searchinf for inconsistencies

            Returns:
                list: list with all alerts
                list: list with all errors
        """
        alerts = []
        errors = []

        alert, error = self.sheet_analysis()
        alerts += alert
        errors += error

        if errors:
            return alerts, errors

        alert, error = self.columns_analysis()
        alerts += alert
        errors += error

        if errors:
            return alerts, errors

        alert, error = self.names_analysis()
        alerts += alert
        errors += error

        if errors:
            return alerts, errors

        alert, error = self.values_analysis()
        alerts += alert
        errors += error

        return alerts, errors

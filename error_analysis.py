import pandas as pd
import openpyxl


class ErrorAnalysis:

    def __init__(self, path, expected_sheets, expected_columns):

        self.excel_path: str = path
        self.expected_sheets: list = expected_sheets
        self.expected_columns: dict = expected_columns
        self.customers: pd.DataFrame = pd.read_excel(self.excel_path, sheet_name='Customers')
        self.locations: pd.DataFrame = pd.read_excel(self.excel_path, sheet_name='Locations')
        self.suppliers: pd.DataFrame = pd.read_excel(self.excel_path, sheet_name='Suppliers')
        self.customers_names: list = self.customers['Name'].values.tolist()
        self.locations_names: list = self.locations['Name'].values.tolist()
        self.suppliers_names: list = self.suppliers['Name'].values.tolist()

    def sheet_analysis(self, alerts, errors) -> (list, list):

        wb = openpyxl.load_workbook(self.excel_path)
        sheet_names = wb.sheetnames

        alerts += [f'Table {sheet} is not a expected table'
                   for sheet in sheet_names if sheet not in self.expected_sheets]

        errors += [f'Table {sheet} is not in archive tables'
                   for sheet in self.expected_sheets if sheet not in sheet_names]

        return alerts, errors

    def columns_analysis(self, alerts, errors) -> (list, list):

        customer_columns = list(self.customers)
        location_columns = list(self.locations)
        suppliers_columns = list(self.suppliers)

        errors += [f'There is no {column} column in Customers table'
                   for column in self.expected_columns['Customers'] if column not in customer_columns]
        errors += [f'There is no {column} column in suppliers table'
                   for column in self.expected_columns['Suppliers'] if column not in suppliers_columns]
        errors += [f'There is no {column} column in locations table'
                   for column in self.expected_columns['Locations'] if column not in location_columns]

        alerts += [f'Column {column} is not a expected column in customers table'
                   for column in customer_columns if column not in self.expected_columns['Customers']]
        alerts += [f'Column {column} is not a expected column in suppliers table'
                   for column in suppliers_columns if column not in self.expected_columns['Suppliers']]
        alerts += [f'Column {column} is not a expected column in locations table'
                   for column in location_columns if column not in self.expected_columns['Locations']]

        return alerts, errors

    def check_duplicates(self, alerts) -> (list, list):

        duplicates = self.suppliers['Name'].duplicated().tolist()
        if any(duplicates):
            alerts += [f"Name {self.suppliers['Name'][i]} is duplicated in Suppliers"
                      for i in range(len(self.suppliers_names)) if duplicates[i]]
            self.suppliers.drop_duplicates('Name', inplace=True)

        duplicates = self.locations[['Name', 'Status']].duplicated().tolist()
        if any(duplicates):
            alerts += [f"Name {self.locations['Name'][i]} is duplicated with the same status in Locations"
                      for i in range(len(self.locations_names)) if duplicates[i]]
            self.locations.drop_duplicates(['Name', 'Status'], inplace=True)

        duplicates = self.customers['Name'].duplicated().tolist()
        if any(duplicates):
            alerts += [f"Name {self.customers['Name'][i]} is duplicated in Customers"
                      for i in range(len(self.customers_names)) if duplicates[i]]
            self.customers.drop_duplicates('Name', inplace=True)

        duplicates = self.locations['Name'].duplicated().tolist()
        if any(duplicates):
            alerts += [f"Name {self.locations['Name'][i]} is duplicated in Locations"
                      for i in range(len(self.locations_names)) if duplicates[i]]
            self.locations.drop_duplicates('Name', inplace=True)

        return alerts

    def check_names_inconsistency(self, alerts, errors) -> (list, list):

        self.customers.set_index('Name', inplace=True, drop=False)
        self.locations.set_index('Name', inplace=True, drop=False)
        self.suppliers.set_index('Name', inplace=True, drop=False)

        errors += [f'Name {name} in Customers does not exist in Locations table'
                   for name in self.customers_names if name not in self.locations_names]
        errors += [f'Name {name} in Suppliers does not exist in Locations table'
                   for name in self.suppliers_names if name not in self.locations_names]

        if errors:
            return alerts, errors

        errors += [f'Status divergence in the name {name} between tables Customers and Locations'
                   for name in self.customers_names if self.customers['Status'][name] != self.locations['Status'][name]]

        errors += [f'Status divergence in the name {name} between tables Suppliers and Locations'
                   for name in self.suppliers_names if self.suppliers['Status'][name] != self.locations['Status'][name]]

        return alerts, errors

    def check_supply_and_demand_inconsistency(self, alerts, errors) -> (list, list):

        errors += [f' Negative value for Maximum Supply from the supplier {name}'
                  for name in self.suppliers_names if self.suppliers['Maximum Supply'][name] < 0]
        errors += [f' Negative value for Fixed Demand from the customer {name}'
                  for name in self.customers_names if self.customers['Fixed Demand'][name] < 0]

        alerts += [f' Null value for Maximum Supply from the supplier {name}'
                  for name in self.suppliers_names if self.suppliers['Maximum Supply'][name] == 0]
        alerts += [f' Null value for Fixed Demand from the customer {name}'
                  for name in self.customers_names if self.customers['Fixed Demand'][name] == 0]

        return alerts, errors

    def check_status_inconsistency(self, alerts, errors) -> (list, list):

        if (self.suppliers['Status'] == 'Exclude').all():
            alerts += ['All values for status in the table suppliers are Exclude']

        if (self.customers['Status'] == 'Exclude').all():
            alerts += ['All values for status in the table customers are Exclude']

        if (self.locations['Status'] == 'Exclude').all():
            alerts += ['All values for status in the table locations are Exclude']

        errors += [f'Status {status} in Locations is not supported, status must be Exclude or Include'
                   for status in self.locations['Status'].values.tolist() if status not in ['Exclude', 'Include']]

        errors += [f'Status {status} in Suppliers is not supported, status must be Exclude or Include'
                   for status in self.suppliers['Status'].values.tolist() if status not in ['Exclude', 'Include']]

        errors += [f'Status {status} in Customers is not supported, status must be Exclude or Include'
                   for status in self.customers['Status'].values.tolist() if status not in ['Exclude', 'Include']]

        return alerts, errors

    def check_coordenates_inconsistency(self, alerts, errors) -> (list, list):

        alerts += [f'Location {name} latitude is not in the correct format' for name in self.locations_names
                   if abs(self.locations['Latitude'][name]) > 90]

        alerts += [f'Location {name} longitude is not in the correct format' for name in self.locations_names
                   if abs(self.locations['Longitude'][name]) > 180]

        return alerts, errors

    def errors_search(self) -> (list, list):

        alerts = []
        errors = []

        alerts, errors = self.sheet_analysis(alerts, errors)

        if errors:
            return alerts, errors

        alerts, errors = self.columns_analysis(alerts, errors)

        if errors:
            return alerts, errors

        alerts = self.check_duplicates(alerts)

        alerts, errors = self.check_names_inconsistency(alerts, errors)

        if errors:
            return alerts, errors

        alerts, errors = self.check_supply_and_demand_inconsistency(alerts, errors)

        alerts, errors = self.check_coordenates_inconsistency(alerts, errors)

        alerts, errors = self.check_supply_and_demand_inconsistency(alerts, errors)

        return alerts, errors

def html_generator(alerts, errors, df_customers, df_suppliers, statistics):
    """
        This method generates a html report with all the errors and alerts found,
        data analysis and database status

        Args:
            alerts (list): list of alerts
            errors (list): list of errors
            df_customers (pandas.DataFrame): customers information
            df_suppliers (pandas.DataFrame): suppliers information
            statistics (dict): main statistics
    """

    error_title = 'Errors founded:' if errors else 'No errors were founded'
    error_text = ''.join([f'<p>\n* {error}</p>' if errors else '' for error in errors])
    alert_title = '\nAlerts founded:' if alerts else 'No alerts were founded'
    alert_text = ''.join([f'<p>\n* {alert}</p>' if alerts else '' for alert in alerts])

    if df_customers.empty or df_suppliers.empty:
        database_text = '''
                            <h4> Database is empty </h4>
                        '''
    else:

        statistics_title = 'Main Statistics:'
        maximum_demand = f"* The client {statistics['maximum_demand']['Name']}" \
                         f"has the maximum fixed demand of {statistics['maximum_demand']['Value']}"
        maximum_supply = f"* The supplier {statistics['maximum_supply']['Name']}" \
                         f"has the maximum supply of {statistics['maximum_supply']['Value']}"
        minimum_demand = f"* The client {statistics['minimum_demand']['Name']}" \
                         f"has the minimum demand of {statistics['minimum_demand']['Value']}"
        minimum_supply = f"* The client {statistics['minimum_supply']['Name']}" \
                         f"has the maximum demand of {statistics['minimum_supply']['Value']}"
        sum_demands = f"* The sum of all fixed demands are: {statistics['sum_demand']}"
        sum_supply = f"* The sum of all maximum supplies are: {statistics['sum_supply']}"

        mean_distance = ''.join([f'<p>* The mean distance between the customers'
                                 f'and the supplier {name} is: {round(statistics[name], 2)} Km</p>'
                                 for name in df_suppliers['Name'].values.tolist()])

        database_text = f"""
                            <h1> Main statistcs for Greenfield analysis </h1>
                            <h3> Costumers fixed demands </h3>
                            <p> {maximum_demand} </p>
                            <p> {minimum_demand} </p>
                            <p> {sum_demands} </p>
                            
                            <h3> Suppliers maximum supply </h3>
                            <p> {maximum_supply} </p>
                            <p> {minimum_supply} </p>
                            <p> {sum_supply} </p>
                            
                            <h3> Mean distance between Clients and Suppliers </h3>
                            <p> {mean_distance} </p>
                            
                            <h1> Position analysis between Costumers and Suppliers </h1>
                            
                            <img src="static/fig.jpeg" />
                            
                            <h1> Database </h1>
                            <h2> Customers </h2>
                            {df_customers.to_html()}
                            <h2> Suppliers</h2>
                            {df_suppliers.to_html()}
                        """

    html = f"""
                <!DOCTYPE html>
                <html lang="en">
                    <head>
                        <meta charset="UTF-8">
                        <title> Error Report </title>
                    </head>
                    <body>
                        <h1> Errors and Alerts found in the file </h1>
                        <h2> {error_title} </h2>
                        <p> {error_text} </p>
                        <h2> {alert_title} </h2>
                        <p> {alert_text} </p>
                        
                    {database_text}
                                
                    </body>
                </html>

            """

    with open('templates/html_report.html', 'w') as f:
        f.write(html)

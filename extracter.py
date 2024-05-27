import pandas as pd
from sqlalchemy import create_engine

class DataFetcher:
    def __init__(self):
        # Initialize dictionaries to hold database connections and dataframes
        self.connections = {}
        self.dataframes = {}

    def add_database_connection(self, name, connection_string):
        # Create a database engine and store it in the connections dictionary
        engine = create_engine(connection_string)
        self.connections[name] = engine

    def add_csv_file(self, name, filepath):
        # Load a CSV file into a dataframe and store it in the dataframes dictionary
        df = pd.read_csv(filepath)
        self.dataframes[name] = df

    def add_excel_file(self, name, filepath, sheet_name=0):
        # Load an Excel file into a dataframe and store it in the dataframes dictionary
        df = pd.read_excel(filepath, sheet_name=sheet_name)
        self.dataframes[name] = df

    def add_json_file(self, name, filepath):
        # Load a JSON file into a dataframe and store it in the dataframes dictionary
        df = pd.read_json(filepath)
        self.dataframes[name] = df

    def fetch_from_database(self, db_name, query, dataframe_name):
        # Fetch data from a database using a SQL query and store it in the dataframes dictionary
        if db_name in self.connections:
            engine = self.connections[db_name]
            df = pd.read_sql_query(query, engine)
            self.dataframes[dataframe_name] = df
        else:
            raise ValueError(f"No database connection named {db_name}")

    def filter_dataframe(self, dataframe_name, filter_condition):
        # Apply a filter condition to a dataframe and update the dataframe in the dictionary
        if dataframe_name in self.dataframes:
            df = self.dataframes[dataframe_name].query(filter_condition)
            self.dataframes[dataframe_name] = df
        else:
            raise ValueError(f"No dataframe named {dataframe_name}")

    def join_dataframes(self, left_name, right_name, on, how='inner', joined_name='joined_df'):
        # Join two dataframes on a specified column and store the result in the dataframes dictionary
        if left_name in self.dataframes and right_name in self.dataframes:
            df_left = self.dataframes[left_name]
            df_right = self.dataframes[right_name]
            joined_df = df_left.merge(df_right, on=on, how=how)
            self.dataframes[joined_name] = joined_df
        else:
            raise ValueError(f"Dataframe(s) {left_name} or {right_name} do not exist")

    def groupby_and_aggregate(self, dataframe_name, groupby_columns, agg_funcs, aggregated_name='aggregated_df'):
        # Group a dataframe by specified columns and apply aggregation functions, then store the result
        if dataframe_name in self.dataframes:
            df = self.dataframes[dataframe_name]
            agg_df = df.groupby(groupby_columns).agg(agg_funcs).reset_index()
            self.dataframes[aggregated_name] = agg_df
        else:
            raise ValueError(f"No dataframe named {dataframe_name}")

    def combine_dataframes(self, names, combined_name='combined_df'):
        # Concatenate multiple dataframes and store the result in the dataframes dictionary
        dfs = [self.dataframes[name] for name in names if name in self.dataframes]
        combined_df = pd.concat(dfs, ignore_index=True)
        self.dataframes[combined_name] = combined_df

    def save_to_file(self, dataframe_name, filepath, file_format='csv'):
        # Save a dataframe to a file in the specified format (CSV, Excel, JSON)
        if dataframe_name in self.dataframes:
            df = self.dataframes[dataframe_name]
            if file_format == 'csv':
                df.to_csv(filepath, index=False)
            elif file_format == 'excel':
                df.to_excel(filepath, index=False)
            elif file_format == 'json':
                df.to_json(filepath, orient='records')
            else:
                raise ValueError(f"Unsupported file format {file_format}")
        else:
            raise ValueError(f"No dataframe named {dataframe_name}")

    def save_to_database(self, dataframe_name, db_name, table_name):
        # Save a dataframe to a database table
        if dataframe_name in self.dataframes and db_name in self.connections:
            df = self.dataframes[dataframe_name]
            engine = self.connections[db_name]
            df.to_sql(table_name, engine, if_exists='replace', index=False)
        else:
            raise ValueError(f"Dataframe {dataframe_name} or database {db_name} does not exist")

# Example Usage
if __name__ == "__main__":
    df = DataFetcher()

    # Add connections to databases and load files into dataframes
    df.add_database_connection('db1', 'sqlite:///example.db')  # Example for SQLite
    df.add_csv_file('csv1', 'example.csv')
    df.add_excel_file('excel1', 'example.xlsx', sheet_name='Sheet1')
    df.add_json_file('json1', 'example.json')

    # Fetch data from the database and apply a filter to a CSV dataframe
    df.fetch_from_database('db1', 'SELECT * FROM table_name', 'db_table')
    df.filter_dataframe('csv1', 'column_name == "some_value"')

    # Join dataframes on a common column
    df.join_dataframes('db_table', 'csv1', on='common_column')

    # Group and aggregate data
    df.groupby_and_aggregate('joined_df', ['group_column'], {'agg_column': 'sum'})

    # Combine multiple dataframes into one
    df.combine_dataframes(['csv1', 'excel1', 'json1'])

    # Save the resulting dataframe to different file formats
    df.save_to_file('joined_df', 'output.csv')
    df.save_to_file('joined_df', 'output.xlsx', file_format='excel')
    df.save_to_file('joined_df', 'output.json', file_format='json')

    # Save the resulting dataframe to a database table
    df.save_to_database('joined_df', 'db1', 'joined_table')

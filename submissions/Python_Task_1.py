import pandas as pd
from datetime import time

def generate_car_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """
    Creates a DataFrame for id combinations.

    Args:
        df (pandas.DataFrame): Input DataFrame.

    Returns:
        pandas.DataFrame: Matrix generated with 'car' values,
                          where 'id_1' and 'id_2' are used as indices and columns respectively.
    """
    # Pivot the DataFrame to create the desired matrix
    result_matrix = df.pivot(index='id_1', columns='id_2', values='car')

    # Fill NaN values with 0
    result_matrix = result_matrix.fillna(0)

    # Set diagonal values to 0
    for idx in result_matrix.index:
        result_matrix.at[idx, idx] = 0

    return result_matrix



def get_type_count(df: pd.DataFrame) -> dict:
    """
    Categorizes 'car' values into types and returns a dictionary of counts.

    Args:
        df (pandas.DataFrame): Input DataFrame.

    Returns:
        dict: A dictionary with car types as keys and their counts as values.
    """
    # Categorize 'car' values into types and count occurrences
    type_counts = df['car'].apply(lambda x: 'low' if x <= 15 else ('medium' if 15 < x <= 25 else 'high'))
    result_dict = type_counts.value_counts().to_dict()

    return result_dict


def get_bus_indexes(df: pd.DataFrame) -> list:
    """
    Returns the indexes where the 'bus' values are greater than twice the mean.

    Args:
        df (pandas.DataFrame): Input DataFrame.

    Returns:
        list: List of indexes where 'bus' values exceed twice the mean.
    """
    # Get indexes where 'bus' values exceed twice the mean
    bus_indexes = df[df['bus'] > 2 * df['bus'].mean()].index.tolist()

    return bus_indexes


def filter_routes(df: pd.DataFrame) -> list:
    """
    Filters and returns routes with average 'truck' values greater than 7.

    Args:
        df (pandas.DataFrame): Input DataFrame.

    Returns:
        list: List of route names with average 'truck' values greater than 7.
    """
    # Filter routes based on average 'truck' values
    filtered_routes = df.groupby('route')['truck'].mean()
    filtered_routes = filtered_routes[filtered_routes > 7].index.tolist()

    return filtered_routes


def multiply_matrix(matrix: pd.DataFrame) -> pd.DataFrame:
    """
    Multiplies matrix values with custom conditions.

    Args:
        matrix (pandas.DataFrame): Input matrix DataFrame.

    Returns:
        pandas.DataFrame: Modified matrix with values multiplied based on custom conditions.
    """
    # Multiply matrix values based on custom conditions
    modified_matrix = matrix.applymap(lambda x: x * 0.75 if x > 20 else x * 1.25)

    return modified_matrix


format='%A %H:%M:%S'

def time_check(df: pd.DataFrame) -> pd.Series:
    """
    Verify the completeness of the time data by checking whether the timestamps for each unique (id, id_2) pair
    cover a full 24-hour period and span all 7 days of the week.

    Args:
        df (pandas.DataFrame): Input DataFrame with columns id, id_2, startDay, startTime, endDay, endTime.

    Returns:
        pd.Series: Boolean series indicating if each (id, id_2) pair has incorrect timestamps.
    """
    # Combine 'startDay' and 'startTime' to create 'startTimestamp' column
    df['startTimestamp'] = pd.to_datetime(df['startDay'] + ' ' + df['startTime'], format='%A %H:%M:%S')

    # Combine 'endDay' and 'endTime' to create 'endTimestamp' column
    df['endTimestamp'] = pd.to_datetime(df['endDay'] + ' ' + df['endTime'], format='%A %H:%M:%S')

    # Calculate the difference between end and start timestamps
    time_difference = df['endTimestamp'] - df['startTimestamp']

    # Check if each (id, id_2) pair has correct timestamps
    completeness_check = (time_difference == pd.Timedelta(days=6, hours=23, minutes=59, seconds=59))

    # Create a multi-index boolean series
    result_series = completeness_check.groupby([df['id'], df['id_2']]).all()

    return result_series

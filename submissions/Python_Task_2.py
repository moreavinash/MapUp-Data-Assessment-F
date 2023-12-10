import pandas as pd

def calculate_distance_matrix(df):
    """
    Calculate a distance matrix based on the dataframe, df.

    Args:
        df (pandas.DataFrame): DataFrame containing columns id_start, id_end, and distance.

    Returns:
        pandas.DataFrame: Distance matrix
    """
    # Create a list of unique IDs
    unique_ids = list(set(df['id_start'].unique()) | set(df['id_end'].unique()))

    # Create an empty matrix filled with infinity values
    distance_matrix = pd.DataFrame(float('inf'), index=unique_ids, columns=unique_ids, dtype=float)

    # Fill in the matrix with distances
    for index, row in df.iterrows():
        distance_matrix.at[row['id_start'], row['id_end']] = row['distance']
        distance_matrix.at[row['id_end'], row['id_start']] = row['distance']

    # Set diagonal values to 0
    for i in unique_ids:
        distance_matrix.at[i, i] = 0

    # Floyd-Warshall algorithm to calculate cumulative distances
    for k in unique_ids:
        for i in unique_ids:
            for j in unique_ids:
                if distance_matrix.at[i, k] + distance_matrix.at[k, j] < distance_matrix.at[i, j]:
                    distance_matrix.at[i, j] = distance_matrix.at[i, k] + distance_matrix.at[k, j]

    return distance_matrix


def unroll_distance_matrix(distance_matrix):
    """
    Unroll a distance matrix into a DataFrame with three columns: id_start, id_end, and distance.

    Args:
        distance_matrix (pandas.DataFrame): Distance matrix with cumulative distances.

    Returns:
        pandas.DataFrame: Unrolled distance matrix
    """
    # Create an empty list to store unrolled data
    distance_matrix = calculate_distance_matrix(distance_matrix)
    unrolled_data = []

    # Iterate over the rows and columns of the distance matrix
    for i in distance_matrix.index:
        for j in distance_matrix.columns:
            if i != j:
                unrolled_data.append({
                    'id_start': i,
                    'id_end': j,
                    'distance': distance_matrix.at[i, j]
                })

    # Create a DataFrame from the unrolled data
    unrolled_df = pd.DataFrame(unrolled_data)

    return unrolled_df


def find_ids_within_ten_percentage_threshold(df, reference_value):
    """
    Find IDs within 10% (including ceiling and floor) of the reference value's average distance.

    Args:
        df (pandas.DataFrame): DataFrame with columns id_start, id_end, and distance.
        reference_value (int): Reference value from the id_start column.

    Returns:
        pandas.DataFrame: DataFrame containing IDs within 10% of the reference value's average distance.
    """
    # Calculate the average distance for the reference value
    reference_avg_distance = df[df['id_start'] == reference_value]['distance'].mean()

    # Calculate the threshold range (10% of the reference average distance)
    threshold_range = 0.1 * reference_avg_distance

    # Filter IDs within the threshold range
    filtered_df = df[
        (df['distance'] >= (reference_avg_distance - threshold_range)) &
        (df['distance'] <= (reference_avg_distance + threshold_range))
    ]

    # Sort the resulting DataFrame by id_start column
    result_df = filtered_df.sort_values(by='id_start')

    return result_df



def calculate_toll_rate(distance_matrix):
    """
    Calculate toll rates based on vehicle types and add columns to the input DataFrame.

    Args:
        distance_matrix (pandas.DataFrame): DataFrame with cumulative distances.

    Returns:
        pandas.DataFrame: DataFrame with added columns for toll rates based on vehicle types.
    """
    # Define rate coefficients for each vehicle type
    rate_coefficients = {'moto': 0.8, 'car': 1.2, 'rv': 1.5, 'bus': 2.2, 'truck': 3.6}

    # Create a copy of the distance_matrix to avoid modifying the original DataFrame\
    distance_matrix = unroll_distance_matrix(distance_matrix)
    df = distance_matrix.copy()

    # Add columns for each vehicle type
    for vehicle_type, rate in rate_coefficients.items():
        df[vehicle_type] = df['distance'] * rate

    return df


def calculate_time_based_toll_rates(df):
    """
    Calculate toll rates for different time intervals within a day.

    Args:
        df (pandas.DataFrame): DataFrame with columns id_start, id_end, distance.

    Returns:
        pandas.DataFrame: DataFrame with added columns for time-based toll rates.
    """
    # Add start_day and end_day columns

    df = find_ids_within_ten_percentage_threshold(df,1001400) 

    df['start_day'] = 'Monday'
    df['end_day'] = 'Sunday'

    # Convert start_time and end_time to datetime objects
    df['start_time'] = pd.to_datetime('00:00:00', format='%H:%M:%S').time()
    df['end_time'] = pd.to_datetime('23:59:59', format='%H:%M:%S').time()

    # Weekday time intervals
    weekday_intervals = [
        ('00:00:00', '10:00:00', 0.8),
        ('10:00:00', '18:00:00', 1.2),
        ('18:00:00', '23:59:59', 0.8),
    ]

    # Weekend time intervals
    weekend_intervals = [
        ('00:00:00', '23:59:59', 0.7),
    ]

    # Apply discount factors based on time intervals
    for start_time, end_time, discount_factor in weekday_intervals:
        mask = (df['start_time'] <= pd.to_datetime(start_time, format='%H:%M:%S').time()) & \
               (df['end_time'] >= pd.to_datetime(end_time, format='%H:%M:%S').time()) & \
               (df['start_day'].isin(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']))
        df.loc[mask, 'distance'] *= discount_factor

    for start_time, end_time, discount_factor in weekend_intervals:
        mask = (df['start_time'] <= pd.to_datetime(start_time, format='%H:%M:%S').time()) & \
               (df['end_time'] >= pd.to_datetime(end_time, format='%H:%M:%S').time()) & \
               (df['start_day'].isin(['Saturday', 'Sunday']))
        df.loc[mask, 'distance'] *= discount_factor

    return df[['id_start', 'id_end', 'distance', 'start_day', 'start_time', 'end_day', 'end_time']]


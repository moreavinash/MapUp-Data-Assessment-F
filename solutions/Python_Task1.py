import pandas as pd

def generate_car_matrix(dataframe):
    # Pivot the DataFrame to have id_2 values as columns, id_1 values as index, and car values as data
    result_df = dataframe.pivot(index='id_1', columns='id_2', values='car')

    # Fill NaN values with 0
    result_df = result_df.fillna(0)

    # Set diagonal values to 0
    for idx in result_df.index:
        result_df.at[idx, idx] = 0

    return result_df

#loading the data into data frame
df = pd.read_csv('datasets\dataset-1.csv')

# Generate the car matrix using the defined function
result_matrix = generate_car_matrix(df)

# Display the result
print(result_matrix)

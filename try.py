import pandas as pd
import os

def verify_and_read_txt(filepath):
    # Check if the file is a .txt file
    if not filepath.endswith('.txt'):
        raise ValueError("The file is not a .txt file")

    # Check if the file exists
    if not os.path.isfile(filepath):
        raise FileNotFoundError("The file does not exist")

    # Define possible sets of valid columns
    valid_columns_set1 = ['rsid', 'chromosome', 'position', 'allele1', 'allele2']
    valid_columns_set2 = ['rsid', 'chromosome', 'position', 'genotype']

    # Read the first 100 lines of the file
    with open(filepath, 'r') as file:
        for i, line in enumerate(file):
            if i >= 100:
                break
            # Check if all valid columns from set 1 are in the line
            if all(column in line for column in valid_columns_set1):
                return valid_columns_set1
            # Check if all valid columns from set 2 are in the line
            if all(column in line for column in valid_columns_set2):
                return valid_columns_set2

    return []

def read_genetic_data(filepath):
    columns = verify_and_read_txt(filepath)
    if not columns:
        raise ValueError("The file does not contain the expected columns")

    # Read the data into a DataFrame
    df = pd.read_csv(filepath, sep='\t', comment='#', names=columns, dtype=str)

    # If the file contains a genotype column, split it into allele1 and allele2
    if 'genotype' in df.columns:
        df[['allele1', 'allele2']] = df['genotype'].apply(lambda x: pd.Series(list(x)))
        df.drop(columns=['genotype'], inplace=True)

    return df.to_dict(orient='records')

if __name__ == '__main__':
    df = read_genetic_data('__AncestoryData.txt')
    genome_data = df.to_dict(orient='records')
    print(df.head())
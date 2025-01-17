import pandas as pd

def filter_gazprom_news(input_file, output_file, keyword="Газпром"):
    """
    Filters a dataset to include only news articles containing the specified keyword in the title, text, or snippet.

    Args:
        input_file (str): Path to the input CSV file containing the dataset.
        output_file (str): Path to save the filtered dataset.
        keyword (str): Keyword to filter news articles (default is "Газпром").

    Returns:
        None: Saves the filtered dataset to the specified output file.
    """
    # Load the dataset
    try:
        df = pd.read_csv(input_file)
    except Exception as e:
        print(f"Error loading file: {e}")
        return

    # Ensure required columns exist
    required_columns = ['title', 'text', 'snippet']
    if not all(column in df.columns for column in required_columns):
        print(f"The dataset must contain the following columns: {required_columns}")
        return

    # Filter rows containing the keyword
    filtered_df = df[
        df['title'].str.contains(keyword, na=False, case=False) |
        df['text'].str.contains(keyword, na=False, case=False) |
        df['snippet'].str.contains(keyword, na=False, case=False)
    ]

    # Convert publication date if available
    if 'pubdate' in filtered_df.columns:
        try:
            filtered_df['pubdate'] = pd.to_datetime(filtered_df['pubdate'], unit='s')
        except Exception as e:
            print(f"Error converting publication date: {e}")

    # Save the filtered dataset
    try:
        filtered_df.to_csv(output_file, index=False)
        print(f"Filtered dataset saved to {output_file}")
    except Exception as e:
        print(f"Error saving file: {e}")

filter_gazprom_news("Lenta_sample.csv", "gazprom_news_2020.csv")
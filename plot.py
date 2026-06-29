
# from matplotlib.dates import date2num
import os
import glob
import pandas as pd
import matplotlib.pyplot as plt


os.makedirs("plots", exist_ok=True)

def load_excel_data(file_path):
    """Loads an excel file and ensures the 'month' index is treated as timestamps."""
    df = pd.read_excel(file_path)
    # The grouping column is typically named 'month'
    if 'month' in df.columns:
        df['month'] = df['month'].astype(str)
        # pd.to_datetime handles the string parsing perfectly on its own here
        df['month'] = pd.to_datetime(df['month'])
        df = df.set_index('month')
    return df

def plot_languages(source_name, file_path):
    """Plots trends in specific languages used in text."""
    df = load_excel_data(file_path)
    
    # Drop total/sum row or column if it exists to avoid skewing the scale
    columns_to_plot = [col for col in df.columns if col != 'sum']
    
    plt.figure(figsize=(10, 5))
    for col in columns_to_plot:
        plt.plot(df.index, df[col], marker='o', label=col)
        
    plt.title(f"Language Word Counts Over Time - {source_name}")
    plt.xlabel("Month")
    plt.ylabel("Word Counts")
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"plots/{source_name}_languages.png")
    plt.close()

def plot_alphabets(source_name, file_path):
    """Plots proportions of Armenian, Russian, and English letters used."""
    df = load_excel_data(file_path)
    
    
    plt.figure(figsize=(10, 5))
    for col in ['arm', 'rus', 'eng']:
        if col in df.columns:
            if 'tot' in df.columns:
                percentage = (df[col] / df['tot']) * 100
                plt.plot(df.index, percentage, marker='s', label=f"{col} (%)")
                plt.ylabel("Percentage of Total Letters (%)")
            else:
                plt.plot(df.index, df[col], marker='s', label=col)
                plt.ylabel("Letter Counts")
                
    plt.title(f"Alphabet Representation Over Time - {source_name}")
    plt.xlabel("Month")
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"plots/{source_name}_alphabets.png")
    plt.close()

def plot_lengths(source_name, file_path):
    """Plots monthly averages of word and letter lengths."""
    df = load_excel_data(file_path)
    
    plt.figure(figsize=(10, 5))
    if 'words' in df.columns:
        plt.plot(df.index, df['words'], marker='^', color='purple', label='Avg Words/Comment')
    if 'letters' in df.columns:
        plt.plot(df.index, df['letters'], marker='v', color='orange', label='Avg Letters/Comment')
        
    plt.title(f"Average Comment Lengths Over Time - {source_name}")
    plt.xlabel("Month")
    plt.ylabel("Average Count")
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"plots/{source_name}_lengths.png")
    plt.close()

def plot_word_sets(source_name, file_path):
    """Plots the tracking of designated semantic word sets."""
    df = load_excel_data(file_path)
    
    
    columns_to_plot = [col for col in df.columns if col != 'total words']
    
    plt.figure(figsize=(12, 6))
    for col in columns_to_plot:
        plt.plot(df.index, df[col], marker='x', label=col)
        
    plt.title(f"Word Set Frequencies Over Time - {source_name}")
    plt.xlabel("Month")
    plt.ylabel("Frequency")
    # Position legend outside if there are too many Armenian keywords tracking
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.tight_layout()
    plt.savefig(f"plots/{source_name}_word_sets.png")
    plt.close()

def main():
    excel_dir = "excels"
    if not os.path.exists(excel_dir):
        print(f"Directory '{excel_dir}' not found. Run your analysis script first.")
        return

    # Find all generated Excel files
    excel_files = glob.glob(os.path.join(excel_dir, "*.xlsx"))
    
    if not excel_files:
        print("No Excel files found inside the 'excels' folder.")
        return


    for file_path in excel_files:
        file_name = os.path.basename(file_path)
        
        # Parse out source names and mapping types dynamically based on your generation patterns
        if "languages.xlsx" in file_name:
            source_name = file_name.replace("languages.xlsx", "")
            print(f"Plotting Languages for {source_name}...")
            plot_languages(source_name, file_path)
            
        elif "alphabets.xlsx" in file_name:
            source_name = file_name.replace("alphabets.xlsx", "")
            print(f"Plotting Alphabets for {source_name}...")
            plot_alphabets(source_name, file_path)
            
        elif "lenghts.xlsx" in file_name:
            source_name = file_name.replace("lenghts.xlsx", "")
            print(f"Plotting Length Distributions for {source_name}...")
            plot_lengths(source_name, file_path)
            
        elif "word_sets.xlsx" in file_name:
            source_name = file_name.replace("word_sets.xlsx", "")
            print(f"Plotting Word Sets for {source_name}...")
            plot_word_sets(source_name, file_path)

    print("Check the 'plots/' directory.")

if __name__ == "__main__":
    main()
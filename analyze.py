
# source_1 = r"C:\Users\Admin\PycharmProjects\Lezu\comments.csv" #PanArmenian TV
# source_2 = r"C:\Users\Admin\PycharmProjects\Lezu\erger2.csv" #erger
# source_3 = r"C:\Users\Admin\PycharmProjects\Lezu\5000haytni.csv" #qaxaqakan
# source_4 = r"C:\Users\Admin\PycharmProjects\Lezu\blogerner.csv" #blogerner

# source_1 = r"C:\Users\Admin\PycharmProjects\Lezu\comments_cleaned.csv" #PanArmenian TV
# source_2 = r"C:\Users\Admin\PycharmProjects\Lezu\erger2_cleaned.csv" #erger
# source_3 = r"C:\Users\Admin\PycharmProjects\Lezu\5000haytni_cleaned.csv" #qaxaqakan
# source_4 = r"C:\Users\Admin\PycharmProjects\Lezu\blogerner_cleaned.csv" #blogerner

import pandas as pd
import numpy as np
from wordfreq import top_n_list
rus = set(top_n_list("ru", 30000, wordlist='best'))
eng = set(top_n_list("en", 30000, wordlist='best'))

import os
os.makedirs("excels", exist_ok=True)



source_1 = r"data\source_1.csv"
source_2 = r"data\source_2.csv"
source_3 = r"data\source_3.csv"
source_4 = r"data\source_4.csv"


sources = {"source1":source_1,"source2":source_2,"source3":source_3, "source4":source_4}


class Analyze_csv:
    def __init__(self, csv_file):
        self.df = pd.read_csv(csv_file)
        self.df = self.df.reset_index()
        

        self.lang_indexes = {
            0:"English",
            1:"Lating but not English",
            2:"Russian",
            3:"Cyrillic not Russian",
            4:"Armenian",
            5:"Other"
        }

    
    #helper functions
    def get_word_lang(self, word:str, eng: dict, rus:dict) -> int:
        """
        returns 
        0 English word
        1 Latin not English word
        2 Russian word
        3 Cyrillic not Russian word
        4 Armenian word
        5 All others
        
        :param word: string of word to determine language
        :param eng: dictionary of English words to determine weather the word is English.
        :param rus: dictionary of Russian words to determine weather the word is Russian.
        """
        word = ''.join(c for c in word if c.isalpha()) #clear punctuation

        if all(['\u0530' <= char <= '\u058F' for char in word]): #Armenian
            return 4
        if all(char.isascii() for char in word):
            if word in eng:
                return 0 #English
            else:
                return 1 #Latin
        if all(['\u0400' <= char <= '\u04FF' for char in word]): 
            if word in rus:
                return 2 #Russian
            else:
                return 3 #Cyrillic
        return 5
        
    def get_comment_lang(self, comment:str, eng: dict, rus:dict):
        """
        returns 
        0 English comment
        1 Latin not English comment
        2 Russina comment
        3 Cyrillic not Russian comment
        4 Armenian comment
        5 other
        
        :type comment: str
        :param eng: Description
        :type eng: dictionary of English words to determine weather the word is English.
        :param rus: dictionary of Russian words to determine weather the word is Russian.
        :type rus: dict
        """
        words = comment.split()
        lang = False
        for word in words:
            if self.get_word_lang(word, eng, rus) is None:
                continue

            if lang is not False: 
                if lang != self.get_word_lang(word, eng, rus):
                    return 5
            else:
                lang = self.get_word_lang(word, eng, rus)
        return lang
    
    #main functions
    def word_sets_frequency(self, word_sets):
        """
        Imput csv file contains date (of the publicaton of the comment) on the second column, 
        and the comment on the third.
        for eash set in the word_sets, returns the number of the set's word for each month.
        
        :param csv_file: csv file adress
        :param words: dictionary of word set name and as key and list of words as value
        """
        df = self.df

        def count_words(text):
              
            if word_sets and text and isinstance(text, str):
                text = text.lower()
                ans = [0] * (len(word_sets)+1)
                ans[-1] += len(text.split())
                for i, set_name in enumerate(word_sets.keys()):

                    for word in word_sets[set_name]:
                        ans[i] += text.count(word.lower().strip())
                        
                return ans
            print("no sets or text were given")
            return [0] * (len(word_sets)+1)

        df["text"] = df.iloc[:, 3]
        df["date"] = pd.to_datetime(df.iloc[:,2])
        df["month"] = df["date"].dt.to_period("M")
        df["word_counts"] = df["text"].apply(count_words)
        sets = [str(x) for x in word_sets.keys()] + ["total words"]


        df[sets] = pd.DataFrame(df["word_counts"].tolist(), index=df.index)

        
        ans = df.groupby("month")[sets].sum()

        return ans

    def letter_consist(self):
        """
        Imput csv file contains date (of the publicaton of the comment) on the second column 
        and the comment on the third.
        returns mean proportions ({} letters / total letters) for Armenian, English, Russian letters for each month.
        
        :param csv_file: csv file adress
        :param words: dictionary of word set name and as key and list of words as value
        """
        df = self.df

        def count_letters(text):
            armenian_count = 0
            russian_count = 0
            english_count = 0
            total = 0
            if not isinstance(text, str):
                return [0,0,0,0]
            
            for char in text:
                if char.isalpha():
                    total += 1

                # Armenian letters: Unicode range U+0530 to U+058F
                if '\u0530' <= char <= '\u058F':
                    armenian_count += 1
                # Russian (Cyrillic) letters: Unicode range U+0400 to U+04FF
                elif '\u0400' <= char <= '\u04FF':
                    russian_count += 1
                # English letters: A-Z and a-z
                elif char.isalpha() and char.isascii():
                    english_count += 1
            
            return [armenian_count, russian_count, english_count, total]

        df["published_at"] = pd.to_datetime(df.iloc[:,2])
        df["month"] = df["published_at"].dt.to_period("M")

        df['counts'] = df.iloc[:,3].apply(count_letters)

        df[['arm', 'rus', 'eng', 'tot']] = pd.DataFrame(
        df['counts'].tolist(), index=df.index
        )
        monthly_sum = df.groupby('month')[['arm', 'rus', 'eng', 'tot']].sum()

        return monthly_sum

    def language_words_consist(self):
        """"""
        from wordfreq import top_n_list
        rus = set(top_n_list("ru", 30000, wordlist='best'))
        eng = set(top_n_list("en", 30000, wordlist='best'))


        def get_words_counts(text):
            """
            Takes text and returns a list with coresponding counts in text:
            English words
            Latin words that aren't English
            Russian words
            Cyrillic words that aren't Russian
            Armenain words
            Words in other languages
            
            :param text: Description
            """
            ans = [0]*7
            words = [word.lower() for word in text.split()]

            for word in words:
                index = self.get_word_lang(word, eng, rus)
                if index is not None:

                    ans[index] += 1

            ans[6] = sum(ans)

            return ans
        
        df = self.df
        
        df["published_at"] = pd.to_datetime(df.iloc[:,2])
        df["month"] = df["published_at"].dt.to_period("M")

        df['counts'] = df.iloc[:,3].apply(get_words_counts)

        df[['real_eng', 'pseudo_eng', 'real_rus', 'pseudo_rus', 'armenian', 'other', 'sum']] = pd.DataFrame(
        df['counts'].tolist(), index=df.index
        )
        monthly_sum = df.groupby('month')[['real_eng', 'pseudo_eng', 'real_rus', 'pseudo_rus', 'armenian', 'other', 'sum']].sum()

        return monthly_sum
    
    def lenght_distributions(self):
        """
        returns dataframe with monthly average:
        word lenghts of comments 
        letter lenghts of comments
        word lenghts of comments (for only Latin comments)
        letter lenghts of comments (for only Latin comments)

        word lenghts of comments (for only Russian comments)
        letter lenghts of comments (for only Russian comments)

        word lenghts of comments (for only Armenian comments)
        letter lenghts of comments (for only Armenian comments)

          
        """
        df = self.df
        def count_letters(text):
            total = 0
            for char in text:
                if char.isalpha():
                    total += 1
            return total
        def count_words(text):
            return len(text.split())
        
        def get_comment_letter_lang(text):
            """
            Returns 0 for only Latin text, 1 for only Cyrillic text, 
            2 for only Armenian text without considering punctuation and other signs.
            """
            has_latin, has_cyrillic, has_armenian = False, False, False

            for char in text:
                if not char.isalpha():
                    continue   
                code_point = ord(char)

                # Check Latin (Basic Latin + Latin-1 Supplement + Latin Extended)
                # A-Z: 65-90, a-z: 97-122, extended: 192-687
                if (65 <= code_point <= 90) or (97 <= code_point <= 122) or (192 <= code_point <= 687):
                    has_latin = True
                # Check Cyrillic (Cyrillic block: 0x0400-0x04FF)
                elif 0x0400 <= code_point <= 0x04FF:
                    has_cyrillic = True
                # Check Armenian (Armenian block: 0x0530-0x058F)
                elif 0x0530 <= code_point <= 0x058F:
                    has_armenian = True

            if has_latin and not has_cyrillic and not has_armenian:
                return 0
            elif has_cyrillic and not has_latin and not has_armenian:
                return 1
            elif has_armenian and not has_latin and not has_cyrillic:
                return 2
            else:
                # Mixed or no letters found
                return -1
            
        df['letters'] = df.iloc[:,3].apply(count_letters)
        df['words'] = df.iloc[:,3].apply(count_words)
        df['alphabet'] = df.iloc[:,3].apply(get_comment_letter_lang)


        df['month'] = pd.to_datetime(df.iloc[:,2]).dt.to_period('M')
        grouped_month_alphabet = df.groupby(['month', 'alphabet']).agg({
        'words': 'mean',
        'letters': 'mean'
        }).reset_index()

        grouped_month = df.groupby(['month']).agg({
        'words': 'mean',
        'letters': 'mean'
        }).reset_index()

        


        df_clean = df[df['alphabet'] != -1]


        numpy_arrays = {
        "time": df["month"].dt.to_timestamp(),
        "all_words": df["words"].to_numpy(),
        "all_letters": df["letters"].to_numpy(),
        "armlatrus_words": df_clean["words"].to_numpy(),
        "armlatrus_letters": df_clean["letters"].to_numpy(),
        'latin_words': df_clean[df_clean['alphabet'] == 0]['words'].to_numpy(),
        'latin_letters': df_clean[df_clean['alphabet'] == 0]['letters'].to_numpy(),
        'cyrillic_words': df_clean[df_clean['alphabet'] == 1]['words'].to_numpy(),
        'cyrillic_letters': df_clean[df_clean['alphabet'] == 1]['letters'].to_numpy(),
        'armenian_words': df_clean[df_clean['alphabet'] == 2]['words'].to_numpy(),
        'armenian_letters': df_clean[df_clean['alphabet'] == 2]['letters'].to_numpy(),
        }
        
        # for array_name in numpy_arrays:
        #     array = numpy_arrays[array_name]
        #     print(array_name, "mean", np.mean(array))

        return grouped_month_alphabet, grouped_month, numpy_arrays


# word_gorup_name:words_of_the_group
sets = {"ես":{" ես ", " իմ "}, "մենք":{" մեր ", " մենք "}, "դու":{" դու ", " քո "},
        "ատել":{"ատել", "ատում", "զզվել", "զզվում", "տհաճ"}, "սիրել":{"սեր", "ներել", "բարի"},
        "հայ":{"հայ", "հող", "հերող", "աղգ"}, "ադր":{"թուրք", "ադրբեջան", "թշնամի"},
        "պատերազմ": {"պատերազմ", "կռիվ", "խփել"}, "խաղաղություն":{"խաղաղ", "անվտանգ"},
        "տղա":{"տղա"}, "աղջիկ":{"աղջիկ"},
        
  "բացասական": {
    "սպանել",
    "ատել",
    "վախ",
    "ցավ",
    "տխրություն",
    "կործանել",
    "կորուստ",
    "չարություն",
    "նախանձ",
    "ստել",
    "դավաճանել",
    "վիրավորել",
    "զայրույթ",
    "ատելություն",
    "խաբել",
    "վեճ",
    "թշնամանք",
    "ահաբեկում",
    "վհատություն",
    "հուսահատություն",
    "մենակություն",
    "սարսափ",
    "ամոթ",
    "խղճահարություն",
    "տանջանք",
    "ցասում",
    "կասկած",
    "անարդարություն",
    "դաժանություն",
    "կոպտություն",
    "վիրավորանք",
    "վնաս",
    "տառապանք",
    "վտանգ",
    "սուտ",
    "դժբախտություն",
    "ատելաբանական",
    "կեղծիք",
    "մեղք",
    "ավեր",
    "խավար"
  },
  "դրական": {
    "սիրել",
    "երջանկություն",
    "խաղաղություն",
    "բարություն",
    "ուրախություն",
    "հույս",
    "ընկերություն",
    "օգնել",
    "սեր",
    "հաջողություն",
    "վստահություն",
    "համերաշխություն",
    "խնամք",
    "գոհունակություն",
    "ոգևորություն",
    "հպարտություն",
    "հարգանք",
    "նվիրում",
    "ազնվություն",
    "արդարություն",
    "իմաստություն",
    "ջերմություն",
    "համբերություն",
    "հավատ",
    "խիզախություն",
    "երախտագիտություն",
    "ազատություն",
    "ներշնչում",
    "լույս",
    "հաջողակ",
    "կենսուրախություն",
    "բարեկամություն",
    "հավասարակշռություն",
    "հոգատարություն",
    "սատարել",
    "ստեղծել",
    "զարգացում",
    "առաջընթաց",
    "լավատեսություն",
    "կատարելագործում"
  }
}


    
def save():
    for source_name in sources.keys():
        print(f"started for {source_name}")
        source_link = sources[source_name]
        source = Analyze_csv(source_link)

        languages = source.language_words_consist()
        languages.to_excel(f"excels/{source_name}languages.xlsx")
        alphabets = source.letter_consist()
        alphabets.to_excel(f"excels/{source_name}alphabets.xlsx")
        grouped_month_alphabet, lenght_frame, numpy_arrays = source.lenght_distributions()
        lenght_frame.to_excel(f"excels/{source_name}lenghts.xlsx")
        print(np.mean(numpy_arrays["all_words"]), source_name)
        word_sets = source.word_sets_frequency(word_sets=sets)
        word_sets.to_excel(f"excels/{source_name}word_sets.xlsx")


#For the distributions of the words
def cmments_per_months(sources):
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(2,2)
    ax_flat = ax.flatten()
    for i, file_name in enumerate(sources.keys()):
        df = pd.read_csv(sources[file_name])
        df = df.reset_index()
        df["date"] = pd.to_datetime(df.iloc[:,2])
        df["month"] = df["date"].dt.to_period("M").dt.to_timestamp()

        comments_per_month = df.groupby("month").size()
        print(comments_per_month.iloc)

        ax_flat[i].plot(comments_per_month)
        ax_flat[i].set_title(f"աղբյուր{i+1}")

    plt.show()

if __name__=="__main__":
    for source_name in sources.keys():
        print(f"started for {source_name}")
        source_link = sources[source_name]
        source = Analyze_csv(source_link)
        word_sets = source.word_sets_frequency(word_sets=sets)
        word_sets.to_excel(f"excels/{source_name}word_sets.xlsx")

    save()
    cmments_per_months(sources)
        




# import matplotlib.pyplot as plt

# for i, source_name in enumerate(sources.keys()):
#     print(f"started for {source_name}")
#     source_link = sources[source_name]
#     source = Analyze_csv(source_link)

#     lenght_frame, grouped_month, numpy_arrays = source.lenght_distributions()
#     plt.plot(grouped_month["month"].dt.to_timestamp(), grouped_month["words"], label=f"Աղբյուր{i+1}")

    
# plt.title("մեկնաբանությունների միջին բառային երկարության փոփոխությունը աղբյուրներում ժամանակի ընթացքում։")
# plt.legend()
# plt.grid(True)
# plt.show()
    




# print(source.get_comment_lang("հայերեն", eng, rus))
# print(source.get_comment_lang("havayi coment", eng, rus))
# print(source.get_word_lang("badrzcev", eng, rus))
# print(source.get_word_lang("full", eng, rus))



# print(source.language_words_consist())
# print(source.letter_consist())

#source.word_sets_frequency(male_female).to_excel("tempqaxaqakan.xlsx")


# Get the results
# grouped_df, hist_data, len_words, len_letters = source.lenght_distributions()

# print(np.mean(len_letters))
# print(np.mean(len_words))
# print(len_letters)
# print(len_words)
#print(grouped_df)



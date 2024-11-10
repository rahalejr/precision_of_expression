import argparse
import threading
from llm_functions import pos_lemma, correct_def, realization
from transformers import BertModel, BertTokenizer
from parameters import books, algorithmic
from nltk.corpus import stopwords
from functions import *
import pandas as pd
import string


stop_words = set(stopwords.words('english'))

model = BertModel.from_pretrained('bert-base-uncased')


def process(author = 'lawrence', book=None):

    book_list = books[author]['books']
    if book:
        texts = [b for b in book_list if b['tag'] == book]


    for book_dict in texts:

        with open(f"books/txt/{book_dict['tag']}.txt", 'r') as file:
            paragraphs = format_text(file.read())
        
        # x = (len(paragraphs) // 10) * 10
        # y = 10
        # num = x / y

        # threads = []
        # for i in range(num):
        #     start = i * y
        #     end = (i+1) * y - 1
        #     t = threading.Thread(target=inner, args=(paragraphs[start, end], book_dict, author))
        #     threads.append(t)
        #     t.start()

        # # join all threads
        # for t in threads:
        #     t.join()

        df = inner(paragraphs, book_dict, author)

        df.to_csv(f"data/{book_dict['tag']}.csv", index=False)


def inner(paragraphs, book_dict, author):

    df = pd.DataFrame(columns=['word', 'part_of_speech', 'frequency', 'similarity', 'synonym', 'syn_frequency', 'syn_sim', 
                               'author', 'age', 'book', 'year', 'conditioned_context', 'larger_context', 'modified', 'sentence_type'])

    for count, paragraph in enumerate(paragraphs):
            print(f"Progress: {round(count/len(paragraphs)*100)}%")
            words = paragraph.split(' ')
            if len(words) < parameters['window'] + 1:
                continue
            for i in range(len(words)): 
                punct_front, word_str, punct_back = remove_punctuation(words[i])
                if word_str.lower() in stop_words or (word_str.lower() == 'nymphete'):
                    continue
                start, end = window(i,len(words))
                context = words[start:end]
                context_str = ' '.join(context)

                try:
                    if algorithmic:
                        pos = lesk_pos(word_str, context_str)
                    else:
                        dict = pos_lemma(word_str, context_str)
                        pos = dict['part_of_speech']
                        # lemmatized = dict['lemmatized']
                except ValueError:
                    continue

                try:
                    is_usable = usable(word_str, context_str)
                    is_infrequent = infrequent(word_str) 
                except NameError:
                    continue

                if is_usable and is_infrequent:
                    
                    try:
                        word = Word(word_str, context_str) if algorithmic else Word(word_str, context_str, True, pos)
                    except ValueError or TypeError:
                        continue
                    
                    word_ind = context.index(words[i])
                    if algorithmic:
                        synonyms = [syn for syn in word.match[2] if frequent(syn, pos)]
                    else:
                        synonyms = [syn for syn in word.match[2] if frequent(syn)]
                    if not synonyms:
                        continue

                    # creating a list of similarity scores for each synonym / key word substitution pair
                    substitutions, syn_lemmas, word_similarity, sentences = [], [], [], []
                    for syn in synonyms:
                        if algorithmic:
                            punctuated_syn = f'{punct_front}{syn}{punct_back}'
                            substituted = context.copy()
                            substituted[word_ind] = punctuated_syn
                            substitutions.append(cosim(' '.join(substituted), context_str))
                            word_similarity.append(cosim(word_str, syn))
                            sentences.append(' '.join(substituted))
                        else:
                            try:
                                sub_dict = realization(word_str, syn, context_str, pos)
                                if sub_dict == 'too long':
                                    continue
                                substituted = sub_dict['new_context']
                                syn_lemma = sub_dict['lemmatized']
                            except ValueError:
                                continue
                            sentences.append(substituted)
                            substitutions.append(compare_contexts(word_str, syn_lemma, context_str, substituted))
                            word_similarity.append(cosim(word_str, syn_lemma))
                            syn_lemmas.append(syn_lemma)
                            
                    if len(sentences) == 0:
                        continue
                    best_fit = substitutions.index(max(substitutions))
                    synonym = syn_lemmas[best_fit]

                    row =   {'word': word_str, 'part_of_speech': pos_expand[pos], 'frequency': freq(word_str), 
                            'similarity': substitutions[best_fit], 'synonym': synonym, 'syn_frequency': freq(synonym), 'syn_sim': word_similarity[best_fit], 
                            'author': books[author]['name'], 'age': book_dict['year'] - books[author]['born'], 
                            'book': book_dict['title'], 'year': book_dict['year'], 'sentence': context_str, 'modified': sentences[best_fit], 'sentence_type': 'Metaphor?'}

                    df.loc[len(df)] = row
                    print(f'{len(df)} rows')
    return df


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('author')
    parser.add_argument('book')
    args = parser.parse_args()

    process(args.author, args.book)
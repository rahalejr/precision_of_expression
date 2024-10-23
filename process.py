from llm_functions import pos_lemma, correct_def, realization
from parameters import books, algorithmic
from nltk.corpus import stopwords
from functions import *
import pandas as pd
import string


stop_words = set(stopwords.words('english'))



def process(author = 'lawrence'):

    for book_dict in books[author]['books']:

        df = pd.DataFrame(columns=['word', 'part_of_speech', 'frequency', 'similarity', 'synonym', 'syn_sim', 'author', 'age', 'book', 'year', 'sentence', 'modified', 'sentence_type'])

        with open(f"books/txt/{book_dict['tag']}.txt", 'r') as file:
            paragraphs = format_text(file.read())
            
        for count, paragraph in enumerate(paragraphs):
            print(f"Progress: {round(count/len(paragraphs)*100)}%")
            words = paragraph.split(' ')
            if len(words) < parameters['window'] + 1:
                continue
            for i in range(len(words)): 
                punct_front, word_str, punct_back = remove_punctuation(words[i])
                if word_str.lower() in stop_words:
                    continue
                start, end = window(i,len(words))
                context = words[start:end]
                context_str = ' '.join(context)

                try:
                    if algorithmic:
                        pos = lesk_pos(word_str, context_str)
                    else:
                        dict = pos_lemma(word_str, context_str)
                        pos, lemmatized = dict['part_of_speech'], dict['lemmatized']
                except ValueError:
                    continue

                try:
                    is_usable = usable(word_str, context_str)
                    is_infrequent = infrequent(word_str, pos) if algorithmic else infrequent(lemmatized) 
                except NameError:
                    continue

                if is_usable and is_infrequent:
                    
                    try:
                        word = Word(word_str, context_str) if algorithmic else Word(word_str, context_str, True, pos, lemmatized)
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
                    substitutions, word_similarity, sentences = [], [], []
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
                                substituted = realization(word_str, syn, context_str, pos)
                            except ValueError:
                                continue
                            sentences.append(substituted)
                            substitutions.append(cosim(substituted, context_str))
                            word_similarity.append(cosim(lemmatized, syn))
                            
                    if len(sentences) == 0:
                        continue
                    best_fit = substitutions.index(max(substitutions))

                    row =   {'word': word_str, 'part_of_speech': pos_expand[pos], 'frequency': freq(word_str, pos), 
                            'similarity': substitutions[best_fit], 'synonym': synonyms[best_fit], 'syn_sim': word_similarity[best_fit], 
                            'author': books[author]['name'], 'age': book_dict['year'] - books[author]['born'], 
                            'book': book_dict['title'], 'year': book_dict['year'], 'sentence': context_str, 'modified': sentences[best_fit], 'sentence_type': 'Metaphor?'}

                    df.loc[len(df)] = row

        df.to_csv(f"data/{book_dict['tag']}.csv", index=False)

if __name__ == '__main__':
    process()
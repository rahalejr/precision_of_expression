from tenacity import retry, stop_after_attempt, wait_fixed
from transformers import BertModel, BertTokenizer
import torch
from llm_functions import correct_def, realization
from parameters import parameters, pos_expand
from secret import thesaurus, openai_key
from nltk.stem import WordNetLemmatizer
from wordfreq import word_frequency
from numpy.linalg import norm
import requests as rq
from numpy import dot
import openai
import spacy
import re

from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import words, wordnet
from nltk.wsd import lesk
import nltk

tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertModel.from_pretrained('bert-base-uncased')

lemmatizer = WordNetLemmatizer().lemmatize
nlp = spacy.load("en_core_web_sm")

openai.api_key = openai_key


def format_text(text):
    text = text.replace('_','')
    text = text.replace ('--', ',')
    paragraphs = [p.replace('\n', ' ') for p in text.split('\n\n')]
    return [p.replace('  ', ' ') for p in paragraphs]


def nltk_pos(word, sentence):
    return dict(nltk.pos_tag(word_tokenize(sentence)))[word]


def lesk_pos(word, sentence):
    context = word_tokenize(sentence)
    try:
        return lesk(context, word).pos()
    except:
        raise ValueError


def lemmatize(word, pos):
        return lemmatizer(word, pos)


def infrequent(word, pos=None):
    # requires lesk_pos
    # word = lemmatize(word, pos) if pos else word
    return word_frequency(word, 'en') < parameters['freq_threshold']

def frequent(word, pos=None):
    # requires lesk_pos
    # word = lemmatize(word, pos) if pos else word
    return word_frequency(word, 'en') > parameters['syn_threshold']

def freq(word, pos=None):
    # requires lesk_pos
    # word = lemmatize(word, pos)
    return word_frequency(word, 'en')


def usable(word, sentence):
    try:
        return wordnet.synsets(word) and nltk_pos(word, sentence) != 'NNP'
    except:
        raise NameError

@retry(wait=wait_fixed(3), stop=stop_after_attempt(5))
def get_embedding(text, model="text-embedding-ada-002"):
    return openai.Embedding.create(input = [text], model=model)['data'][0]['embedding']


def cosim(embed1, embed2):
    return torch.nn.functional.cosine_similarity(torch.tensor(embed1), torch.tensor(embed2), dim=0)


def word_embed(word, sentence=None):
    if not sentence:
        sentence = word
    input_ids = torch.tensor(tokenizer.encode(sentence)).unsqueeze(0)
    outputs = model(input_ids)
    last_hidden_states = outputs[0]
    tokenized_sentence = tokenizer.tokenize(sentence)
    token_index = tokenized_sentence.index(word)
    word_embedding = last_hidden_states[0][token_index]
    return word_embedding

def compare_contexts(word, syn, context1=None, context2=None):
    word_embedded = word_embed(word, context1)
    syn_embedded = word_embed(syn, context2)

    return cosim(word_embedded, syn_embedded)

def window(i, n):
    length = parameters['window']
    half = round(length/2)
    if i < half:
        left, right = 0, length
    elif n - i < half:
        left, right = -length + n, n
    else:
        left, right = i - half + 1, i + half
    return left, right


def remove_punctuation(word):
    return re.match(r'^(\W*)(.*?)(\W*)$', word).groups()
        

class Word:

    def __init__(self, word, sentence, llm=False, pos=None):
        self.word = word
        self.frequency =  word_frequency(self.word.lower(), 'en')
        self.sentence = sentence
        context = word_tokenize(sentence)
        self.llm = llm
        self.lesk = lesk(context, word)
        self.pos = pos if llm else self.lesk.pos()
        self.definition = None if llm else self.lesk.definition()

        self.resp = rq.get(f'https://www.dictionaryapi.com/api/v3/references/thesaurus/json/{self.word}?key={thesaurus}')
        if not self.resp.json() or type(self.resp.json()[0]) == str:
            raise ValueError
        
        self.definitions = self.possible_forms()
        self.match = self.closest_match()

    def possible_forms(self):
        definitions = []

        for entry in self.resp.json():
            part_of_speech = entry.get('fl', '')
            for definition in entry.get('def', []):
                for sense in definition.get('sseq', []):
                    for item in sense:
                        if item[0] == 'sense':
                            definition_text = item[1]['dt'][0][1]
                            synonyms = []
                            for syn_list in item[1].get('syn_list', []):
                                for syn in syn_list:
                                    synonyms.append(syn.get('wd', ''))
                            def_tuple = (definition_text, part_of_speech, synonyms)
                            if def_tuple not in definitions:
                                definitions.append(def_tuple)
        return definitions
    
    def closest_match(self):
        if self.llm:
            try:
                return self.definitions[correct_def(self.word, self.sentence, [d[0] for d in self.definitions])]
            except TypeError:
                raise ValueError
        else:
            sims = [cosim(self.definition, i[0]) for i in self.definitions]
            # update pos to reflect this instead
            return self.definitions[sims.index(max(sims))]
    
    def synonyms(self):
        return self.match[3]


if __name__ == '__main__':
    window(8,13)
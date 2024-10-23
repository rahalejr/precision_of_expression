from prompts import pos_lemma_prompt, correct_def_prompt, realization_prompt
from tenacity import retry, stop_after_attempt, wait_fixed
from parameters import pos_contract
from secret import openai_key
import openai
import math


# @retry(wait=wait_fixed(1), stop=stop_after_attempt(5))
def pos_lemma(word, context):

    prompt = str({'word': word, 'context': context})

    for _ in range(3):

        output = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": pos_lemma_prompt},
                {"role": "user", "content": prompt},
            ],
            max_tokens=3000,
            temperature=1,
            frequency_penalty=0.5,
            presence_penalty=0.5
        ).choices[0].message.content

        try:
            output = format_output(output)
            dict = eval(output)
            if not dict:
                raise ValueError
            if dict['part_of_speech'] in ['noun', 'verb', 'adjective', 'adverb'] and dict['lemmatized']:
                dict['part_of_speech'] = pos_contract[dict['part_of_speech']]
                return dict
        except:
            continue
    
    raise ValueError


# @retry(wait=wait_fixed(1), stop=stop_after_attempt(5))
def correct_def(word, context, definitions):

    prompt = str({
        'word': word, 
        'context': context,
        'definitions': ' '.join([f'\n{i+1}: {definition}' for i, definition in enumerate(definitions)])
        })

    for _ in range(3):
        output = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": correct_def_prompt},
                {"role": "user", "content": prompt},
            ],
            max_tokens=3000,
            temperature=1,
            frequency_penalty=0.5,
            presence_penalty=0.5
        ).choices[0].message.content

        try:
            output = format_output(output)
            ind = eval(output)
            if not ind:
                return None
            if type(ind) == int:
                return ind - 1
        except:
            continue
    
    raise ValueError



# @retry(wait=wait_fixed(1), stop=stop_after_attempt(5))
def realization(word, syn, context, pos):

    prompt = str({
        'word': syn, 
        'context': context.replace(word, '{word}'),
        'pos': pos
        })

    for _ in range(3):

        output = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": realization_prompt},
                {"role": "user", "content": prompt},
            ],
            max_tokens=3000,
            temperature=1,
            frequency_penalty=0.5,
            presence_penalty=0.5
        ).choices[0].message.content

        try:
            output = format_output(output)
            replaced = eval(output)

            if syn in replaced:
                syn_length = len(syn.split()) - 1
            else:
                syn_length = len([i for i in replaced.lower().split() if i not in context.lower().split()]) - 1
            if len(context.split()) + syn_length != len(replaced.split()):
                continue
            if type(replaced) == str:
                return replaced
        except:
            continue
    
    raise ValueError


def format_output(output):
    output = output.replace('`','')
    output = output.replace('json','')
    return output.replace('\n','')
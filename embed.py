import pandas as pd
import numpy as np
import torch

from transformers import BertModel, BertTokenizer
model = BertModel.from_pretrained('bert-base-uncased',
           output_hidden_states = True,)
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')


def bert_text_preparation(text, tokenizer):
    """
    Preprocesses text input in a way that BERT can interpret.
    """
    marked_text = "[CLS] " + text + " [SEP]"
    tokenized_text = tokenizer.tokenize(marked_text)
    indexed_tokens = tokenizer.convert_tokens_to_ids(tokenized_text)
    segments_ids = [1]*len(indexed_tokens)
    # convert inputs to tensors
    tokens_tensor = torch.tensor([indexed_tokens])
    segments_tensor = torch.tensor([segments_ids])
    return tokenized_text, tokens_tensor, segments_tensor


def get_bert_embeddings(tokens_tensor, segments_tensor, model):
    """
    Obtains BERT embeddings for tokens.
    """
    # gradient calculation id disabled
    with torch.no_grad():
        # obtain hidden states
        outputs = model(tokens_tensor, segments_tensor)
        hidden_states = outputs[2]
    # concatenate the tensors for all layers
    # use "stack" to create new dimension in tensor
    token_embeddings = torch.stack(hidden_states, dim=0)
    # remove dimension 1, the "batches"
    token_embeddings = torch.squeeze(token_embeddings, dim=1)
    # swap dimensions 0 and 1 so we can loop over tokens
    token_embeddings = token_embeddings.permute(1,0,2)
    # intialized list to store embeddings
    token_vecs_sum = []
    # "token_embeddings" is a [Y x 12 x 768] tensor
    # where Y is the number of tokens in the sentence
    # loop over tokens in sentence
    for token in token_embeddings:
    # "token" is a [12 x 768] tensor
    # sum the vectors from the last four layers
        sum_vec = torch.sum(token[-4:], dim=0)
        token_vecs_sum.append(sum_vec)
    return token_vecs_sum


def subtoken_inds(word, tokenized):
    parts = [0 if token[0:2] == '##' else 1 for token in tokenized]
    indices = [0]
    for i in range(1,len(tokenized)):
        if parts[i] == 0:
            indices += [indices[i-1]]
        else:
            indices += [indices[i-1]+1]
    for i in range(max(indices)):
        word_inds = [j for j,k in enumerate(indices) if k == i]
        if word == ''.join([tokenized[j] for j in word_inds]).replace('#',''):
            return (min(word_inds), max(word_inds)+1)
    return


def mean_embed(embeddings):
    return np.mean(np.array(embeddings), axis=0)


def get_word_embed(word, sentence):
    tokenized, tokens_tensor, segments_tensor = bert_text_preparation(sentence, tokenizer)
    embeds = get_bert_embeddings(tokens_tensor, segments_tensor, model)
    word_inds = subtoken_inds(word, tokenized)
    subword_embeds = [i.tolist() for i in embeds[word_inds[0]:word_inds[1]]]
    return mean_embed(subword_embeds)
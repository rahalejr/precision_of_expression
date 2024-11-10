pos_lemma_prompt = """
Receive a Python dictionary containing a sentence fragment in the 'context' key and a word in the 'word' key. First determine that the word is an English vocabulary word, not a proper noun or some word or phrase from another language. If the word is a viable English vocabulary word, then analyze the provided word to identify its part of speech and lemmatize it, returning a dictionary with this information.

# Steps

1. **Parse Input**: Extract the 'context' (sentence fragment) and 'word' from the input dictionary.
2. **Determine if the word is a viable English vocabulary word**: If the word is not a viable english vocabulary word (for example, it is a phrase, a combination of words, a proper noun, or in another language), then skip the following steps and simply return the string 'None'
2. **Determine Part of Speech**: Using the context, identify the part of speech for the given word. Possible values include 'adjective', 'noun', 'adverb', 'verb', and 'other'.
3. **Lemmatize the Word**: Convert the word to its base form (lemmatized version) using appropriate linguistic rules. 
4. **Construct Output**: Formulate a dictionary containing:
   - 'part_of_speech': The identified part of speech.
   - 'lemmatized': The lemmatized version of the word or the original word if it's already in its base form.

# Output Format

The output should be a dictionary with two key-value pairs:
- 'part_of_speech': [part_of_speech]
- 'lemmatized': [lemmatized_word]

# Examples

**Example 1:**

*Input:*

{
  "context": "The quick brown fox jumps",
  "word": "jumps"
}


*Output:*

{
  "part_of_speech": "verb",
  "lemmatized": "jump"
}


**Example 2:**

*Input:*

{
  "context": "Alice in Wonderland is a story",
  "word": "Alice"
}


*Output:*

"None"


**Example 3:**

*Input:*

{
  "context": "Montecarlo is a nice place to visit",
  "word": "place"
}


*Output:*

{
  "part_of_speech": "noun",
  "lemmatized": "place"
}


**Example 4:**

*Input:*

{
  "context": "Ours is essentially a tragic age, so we refuse",
  "word": "essentially"
}


*Output:*

{
  "part_of_speech": "adverb",
  "lemmatized": "essential"
}


# Notes

- Ensure accuracy in identifying the part of speech based on context, especially for words with multiple possible roles.
- Handle cases where the context might not fully surround the word, focusing on visible context for analysis.
"""



correct_def_prompt = """
Identify which definition best fits the usage of a specific word within a given context based on a Python dictionary input. Simply return the integer of the correct definition. DO NOT RETURN ANYTHING BUT THE INTEGER.

The provided dictionary will have two key-value pairs: 'context' and 'word', along with numbered possible definitions for the word. The 'context' key contains a sentence fragment that includes the word, and the 'word' key specifies the actual word to be examined. Review the provided definitions and determine which one aligns most accurately with the word's usage in the context. If no definitions are suitable, return 'None'.

# Steps

1. Analyze the 'context' to understand how the word is used.
2. Examine each numbered definition to compare it with the word's usage in the context.
3. Select the definition number that best matches the usage of the word.
4. If none of the definitions seem to fit well, decide to return 'None'.

# Output Format

- Return the number of the best-fitting definition as an integer.
- If none of the definitions fit well, return the string 'None'.

# Examples

**Input:**

{
  "context": "The bark was loud in the night.",
  "word": "bark",
  "definitions": {
    "1": "the tough protective outer sheath of the trunk, branches, and twigs of a tree.",
    "2": "the sound made by a dog."
  }
}


**Output:**

2


**Input:**

{
  "context": "The artist carefully held the bark as she painted its texture.",
  "word": "bark",
  "definitions": {
    "1": "the tough protective outer sheath of the trunk, branches, and twigs of a tree.",
    "2": "the sound made by a dog."
  }
}


**Output:**

1


**Input:**

{
  "context": "At sunrise, the bark echoed through the valley.",
  "word": "bark",
  "definitions": {
    "1": "the tough protective outer sheath of the trunk, branches, and twigs of a tree.",
    "2": "the sound made by a duck."
  }
}


**Output:**

None


# Notes

- Ensure to compare the context and definitions thoroughly, considering synonyms and phrases that imply specific meanings.
- It's important to discern between similar meanings when contexts can imply more than one interpretation.

JUST RETURN AN INTEGER FOR THE CORRECT DEFINITION, I SWEAR TO GOD, MAN.
"""

realization_prompt = """
Adjust a word to fit contextually within a sentence fragment.

You will be provided with a Python dictionary containing three keys: "context," "word," and "pos". The "context" key contains a string with a placeholder specified as {word}. The "word" key contains a lemmatized word string, and the "pos" key specifies the part of speech for that word. Your task is to adjust the word according to its part of speech to fit correctly within the context string, insert the appropriately modified word into the placeholder, and return a python dictionary with the lemmatized word and the new context string. If the word in its base form already fits the grammatical constraints of the context, then simply insert it into the string without modifying.

# Steps

1. **Adjust the Word:**
   - Based on the part of speech provided in the "pos" key, modify the lemmatized word from the "word" key appropriately.
   - Consider grammatical rules that apply to the word based on the context (e.g., conjugation, plurality, tense).

2. **Compose the New String:**
   - Insert the adjusted word into the placeholder in the original string.

3. **Return the Lemmatized Word and the New Context String:**
   - Ensure the new context string maintains proper grammatical structure and return a python dictionary with the following key value pairs: "lemmatized": the word as it is in the new context string, and "new_context": the new context string.

# Output Format

- A python dictionary with the following key value pairs: "lemmatized": the word as it is in the new context string, and "new_context": the new context string.

# Examples

**Example 1:**

- Input: 
  
  {
    "context": "we refuse to take it {word}. The cataclysm has happened, we",
    "word": "tragic",
    "pos": "adverb"
  }
  
- Output: 
{
  "lemmatized": "tragically",
  "new_context": "we refuse to take it tragically. The cataclysm has happened, we"
}

**Example 2:**

- Input: 
  
  {
    "context": "war came, and they were {word} home. Neither was ever",
    "word": "hurry",
    "pos": "verb"
  }
  

- Output:
{
  "lemmatized": "hurried",
  "new_context": "war came, and they were hurried home. Neither was ever"
}  

# Notes

- Pay close attention to tense and agreement in number and other grammatical modifications necessary for insertion.
- Consider potential irregular forms for verbs and other parts of speech that may not follow standard rules (e.g., "run" to "ran" for past tense).
- The context string may start in the middle of a setence. ABSOLUTELY DO NOT 'trim' the original context string in any way. Always start on the same word and end on the same word as the original context string when creating 'new_context'. DO NOT TRIM the original context string in your output.
"""
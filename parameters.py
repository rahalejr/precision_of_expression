parameters = {
    'freq_threshold': .000005,
    'syn_threshold': .00001,
    'window': 11,
}

 # method for analysis (llm or algorithmic)
algorithmic = False

pos_expand = {'n': 'noun', 'v': 'verb', 'a': 'adjective', 's': 'adjective', 'r': 'adverb'}
pos_contract = {'noun': 'n', 'verb': 'v', 'adjective': 'a', 'adverb': 'r'}

books = {
    'lawrence': {
        'name': 'D.H. Lawrence',
        'born'   : 1885,
        'books'  : [
        #     {
        #         'title'   : 'Sons and Lovers',
        #         'tag'     : 'sonsandlovers',
        #         'year'    : 1913 
        # },
        # {
        #         'title'   : 'The Rainbow',
        #         'tag'     : 'therainbow',
        #         'year'    : 1915
        # },
        # {
        #         'title'   : 'Women in Love',
        #         'tag'     : 'womeninlove',
        #         'year'    : 1920
                
        # },
        {
                'title'     : "Lady Chatterly's Lover",
                'tag'       : 'ladychatterly',
                'year'      : 1928
        }]
    }
}
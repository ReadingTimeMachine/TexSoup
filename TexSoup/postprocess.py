# post processing utils
from TexSoup.data import TexNamedEnv, TexCmd

def clean_slash_commands(soup, only_clean_document = True):
    if only_clean_document:
        # combine \command, \ as just \command\
        for iss,s in enumerate(soup.all):
            #if type(s.expr) == TexSoup.data.TexNamedEnv: # parts of the text
            if type(s.expr) == TexNamedEnv: # parts of the text
                if 'begin' in s.expr.begin and 'document' in s.expr.begin:
                    for isss,ss in enumerate(s.all):
                        if str(ss) == '\\ ': # just a lone bracket
                            #if type(s.all[isss-1].expr) == TexSoup.data.TexCmd: # is a command, update it
                            if type(s.all[isss-1].expr) == TexCmd: # is a command, update it
                                soup.all[iss].all[isss-1].name += '\\ ' # add 
                                soup.all[iss].all[isss].delete() # delete this node
    else:
        # combine \command, \ as just \command\
        for iss,s in enumerate(soup.all):
            #if type(s.expr) == TexSoup.data.TexNamedEnv: # parts of the text
            if type(s.expr) == TexNamedEnv: # parts of the text
                for isss,ss in enumerate(s.all):
                    if str(ss) == '\\ ': # just a lone bracket
                        #if type(s.all[isss-1].expr) == TexSoup.data.TexCmd: # is a command, update it
                        if type(s.all[isss-1].expr) == TexCmd: # is a command, update it
                            soup.all[iss].all[isss-1].name += '\\ ' # add 
                            soup.all[iss].all[isss].delete() # delete this node
    return soup

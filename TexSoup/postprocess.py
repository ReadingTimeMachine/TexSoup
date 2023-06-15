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

def get_replacement_tex(tex_doc, soup, isss, s, verbose=False, strip=True):
    """
    tex_doc : this is the *original* tex document, NOT the one that generated from the soup
    """
    ind1 = s.position
    if ind1 == -1: ind1 = 0 # newline
    if str(s) not in tex_doc[ind1:]: # has been reformated
        if isss < len(soup.all)-1:
            next_el = soup.all[isss+1]
            ind2 = next_el.position
            icount = 1
            while ind2 == -1 and icount < len(soup.all)-isss: # for new-lines
                next_el = soup.all[isss+icount]
                ind2 = next_el.position
                icount+=1
            if icount == len(soup.all)-isss: # hit the end
                ind2 = len(tex_doc)
        else: # last one
            ind2 = len(tex_doc)
        strout = tex_doc[ind1:ind2]
        if strip:
            strout = strout.rstrip()
    else:
        strout = str(s)
        
    if verbose:
        print(str(s))
        print('')
        print(strout)
        print('----------------------')
    return strout
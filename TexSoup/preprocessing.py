# Pre-processing for any fixes that need to be applied before generation of soup
import re

def process_begin_end(tex_doc,
                     search_weirdos_begin = r'\\begin(\s*){(\s*)[A-Za-z]*(\s*)}',
                     search_weirdos_end = r'\\end(\s*){(\s*)[A-Za-z]*(\s*)}'):
    """
    tex_doc : raw text input
    search_weirdos_begin : things like \begin {equation} or \end { document}
    search_weirdos_end : same deal, but for \end statements
    """
    ind = 0
    tex_doc_out = tex_doc
    while ind < len(tex_doc):
        if re.search(search_weirdos_begin, tex_doc[ind:]):
            istart,iend = re.search(search_weirdos_begin, tex_doc[ind:]).span()
            text = tex_doc[ind:][istart:iend]
            text_replace = "".join(text.split())
            #print(text, text_replace)
            tex_doc_out = tex_doc_out.replace(text,text_replace)
            ind += iend
        else:
            ind += len(tex_doc[ind:])

    tex_doc = tex_doc_out
    ind = 0
    while ind < len(tex_doc):
        if re.search(search_weirdos_end, tex_doc[ind:]):
            istart,iend = re.search(search_weirdos_end, tex_doc[ind:]).span()
            text = tex_doc[ind:][istart:iend]
            text_replace = "".join(text.split())
            #print(text, text_replace)
            tex_doc_out = tex_doc_out.replace(text,text_replace)
            ind += iend
        else:
            ind += len(tex_doc[ind:])
    tex_doc = tex_doc_out
    return tex_doc

# utils
def error_and_quit(message,ignore_quit=False,warn=True):
    if warn: print(message)
    if not ignore_quit: sys.exit()

#https://stackoverflow.com/questions/29991917/indices-of-matching-parentheses-in-python
def find_closing(text,dopen='(',dclose=')', debug=True,
                 remove_newline=False, check_closing=True):
    istart = []  # stack of indices of opening parentheses
    d = {}
    error = False
    #print('------text------')
    #print(text)
    #print('----------------')
    if remove_newline: text = text.strip('\n')
    text = text + '     '
    for i, c in enumerate(text):
        if c == dopen:
            istart.append(i)
        if c == dclose:
            try:
                d[istart.pop()] = i
            except IndexError:
                if debug: print('Too many closing parentheses')
                error=True
    if len(istart)!=0:  # check if stack is empty afterwards or left over openers?
        if debug: print('Too many opening parentheses, check 2')
        error=True
    if error and not check_closing: error = False
    return d, error

def split_function_with_delimiters(l,function='\\footnote',
                                   dopen='{',dclose='}',
                                   debug=False, 
                                  remove_newline=False,
                                  check_closing=True,
                                  start_after_function=False,
                                  verbose=False,
                                  return_bracket_index=False):
    if function not in l: # no function
        if debug: print('function not in text:', function)
        return -1, -1
    ind1 = l.index(function)
    if start_after_function:
        ind1 = ind1+len(function)
    tt = l[ind1:]
    # find first bracket
    if dopen not in l[ind1:]: # no first bracket
        if debug: print('no opening bracket in text')
        return -1,-1
    ind2 = l[ind1:].index(dopen)
    tt2 = l[ind1+ind2:]
    d,error = find_closing(tt2,dopen=dopen,dclose=dclose,
                           debug=debug,
                           remove_newline=remove_newline,
                          check_closing=check_closing)
    if error:
        if debug: print('error in find_closing')
        return ind1,-1
    try:
        ind3 = ind1+ind2+d[0]+1
    except:
        ind3 = -1; ind1 = -1
        if verbose: print(d)
        if verbose: print('in split_function_with_delimiters: no d[0]')
    if start_after_function: ind1 = ind1-len(function)
    if not return_bracket_index:
        return ind1,ind3 # ind1 starts at the start of the function, ind3 at its closing bracket
    else:
        return ind2,ind3 # ind2 start of braket, ind3 is end of bracket


def search_spc(l,function='\\footnote',
                                   dopen='{',dclose='}', error_tag='',
                                              start_after_function=False,
                                              error_out = True,
                                              return_bracket_index=False,
                                              verbose=False):
    error=False
    ind1,ind2 = split_function_with_delimiters(l,
                                                   function=function,
                                                   dopen=dopen,
                                                   dclose=dclose,
                                                   debug=False,
                                                  check_closing=False,
                                              start_after_function=start_after_function,
                                              return_bracket_index=return_bracket_index,
                                              verbose=verbose)
    if ind1 == -1 or ind2 == -1: # re-run w/o check closing
        if verbose: print(error_tag+' :not found, trying again w/o checking closing...')
        ind1,ind2 = split_function_with_delimiters(l,
                                                   function=function,
                                                   dopen=dopen,
                                                   dclose=dclose,
                                                   debug=False,
                                                  check_closing=False,
                                                  start_after_function=start_after_function,
                                                  return_bracket_index=return_bracket_index,
                                                  verbose=verbose)
        if ind1 == -1 or ind2 == -1: # re-run w/o check closing
            ind1,ind2 = split_function_with_delimiters(l,
                                                       function=function,
                                                       dopen=dopen,
                                                       dclose=dclose,
                                                       debug=verbose,
                                                      check_closing=False,
                                                      start_after_function=start_after_function,
                                                      return_bracket_index=return_bracket_index,
                                                      verbose=verbose)
            if error_out:
                print(function)
                print('---------')
                print(l)
                error_and_quit(error_tag+' : couldnt figure it out!')
            else:
                if verbose: print(error_tag+' : couldnt figure it out!')
                error=True
    if error_out:
        return ind1,ind2 # ind1 starts at the start of the function, ind3 at its closing bracket
    else:
        return ind1,ind2,error
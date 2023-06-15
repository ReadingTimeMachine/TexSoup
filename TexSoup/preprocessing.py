# Pre-processing for any fixes that need to be applied before generation of soup
import re
import numpy as np

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


def spc(l,function='\\footnote',
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
    
    
def get_newcommands_and_newenvs(text, 
                                search = r'(\\newcommand)|(\\renewcommand)|(\\environment)|(\\newenvironment)|(\\renewenvironment)|(\\def)',
                                verbose = False):

    # -------------- search for new commands/environments ---------
    ind = 0
    news = []
    while ind<len(text):
        s = re.search(search, text[ind:])
        if s:
            news.append((s.group(0),ind+s.span()[0],ind+s.span()[1]))
            ind += s.span()[1]
        else: # nothing left!
            ind += len(text[ind:])


    # NOTE: all of this below is in no way elegant and should be dealt with
    newcommands = []
    for c,start,end in news:
        if ('\\newcommand' in c) or ('\\renewcommand' in c):
            ind1,ind2,err = spc(text[start:],function=c,
                                dopen='{',dclose='}',
                               error_out=False)
            if not err:
                if ind1==-1 or ind2==-1:
                    err = True
                    error.append( ('error') )
                    continue
                cc = "".join(text[start:][ind1:ind2].split())
                #cc = text[start:][ind1:ind2].replace(' ','')
                if '\\newcommand' in c:
                    ic = cc.index('\\newcommand')+len('\\newcommand')
                elif '\\renewcommand' in c:
                    ic = cc.index('\\renewcommand')+len('\\renewcommand')
                else:
                    if verbose: print('something has gone super wrong!')
                    err=True
                if not err:
                    char = cc[ic]
                    if char == '*': # stared version, \newcommand*{\cmd}[nargs]{defn}
                        ic += 1
                        char = cc[ic]
                    if char == '{': # "typical"
                        # get out interior
                        nc = text[start:start+ind2]
                        ind11 = nc.index('{')
                        # get actual command
                        ncc = nc[ind11+1:-1]
                        # get rest of command
                        ind11,ind22,err = spc(text[start+ind2:],function='',
                                          dopen='{',dclose='}', error_out=False)
                        if not err:
                            nc2 = text[start:start+ind22+ind2]
                            newcommands.append( (ncc,nc2,start,start+ind2+ind22) )
                        else:
                            newcommands.append( ('error'))
                            continue
                    elif char == '\\': # weirder - \newcommand\foo[]{}
                        # get out interior
                        nc = text[start:start+ind2]
                        i2 = nc.index('{') # assumes \def\foo{defn}
                        # is there a '[' ? like \newcommand\foo[nargs]{defn}
                        i4 = i2 + 1
                        try:
                            i4 = nc.index('[')
                        except:
                            pass
                        # also need to check for commandds like \newcommand\[{\begin{equation}}
                        if i4 < i2: # have a [
                            if ']' in nc[:i2]: # have closed! otherwise \[ is the command
                                i2 = i4
                        nc2 = nc[:i2]
                        i3 = nc2[::-1].index('\\')
                        ncc = '\\'+nc2[len(nc2)-i3:]                        
                        newcommands.append( (ncc,nc,start,start+ind2) )
                else:
                    newcommands.append(('error'))
                    continue


        elif '\\def' in c:
            # check one thing -- for the whole start to spell out define
            # want to search for \def NOT \define as the start
            if text[start:start+len('\\define')] == '\\define':
                err = True
            else:
                ind1,ind2,err = spc(text[start:],function=c,
                                    dopen='{',dclose='}',
                                   error_out=False)
            if not err:
                # get out interior
                nc = text[start:start+ind2]
                # find actual command
                i2 = nc.index('{')
                nc2 = nc[:i2]
                i3 = nc2[::-1].index('\\')
                ncc = '\\'+nc2[len(nc2)-i3:]
                newcommands.append( (ncc,nc,start,start+ind2) )
            else:
                newcommands.append(('error'))
                continue


    # also grab possible environments
    # check no blank \environment
    errEnv = False
    for c in news:
        if '\\environment' in c:
            errEnv = True

    if errEnv:
        newcommands.append(('error'))
        # HERE continue        

    newenvironments = []
    #print('here')
    for c,start,end in news:
        if ('\\newenvironment' in c) or ('\\renewenvironment' in c):
            #\newenvironment{nam}[args]{begdef}{enddef} --> "nam"
            ind1,ind2,err = spc(text[start:],function=c,
                                dopen='{',dclose='}',
                               error_out=False)
            if not err:
                # get environment name
                i1 = text[start:][ind1:ind2].index('{')+1
                i2 = text[start:][ind1:ind2].index('}')
                envname = text[start:][ind1:ind2][i1:i2]

                # should be two other {}'s -- one of two
                ind11,ind22,err = spc(text[start:][ind2:],
                                      function='',
                                      dopen='{',dclose='}',
                                     error_out=False)
                if not err:
                    ind22 += ind2
                    # should be two other {}'s -- two of two
                    ind111,ind222,err = spc(text[start:][ind22:],
                                            function='',dopen='{',
                                            dclose='}',
                                           error_out=False)
                    if not err:
                        ind222 += ind22
                        newenvironments.append( (envname, text[start:][ind1:ind222], 
                                                 start, start+ind222) )
                    else:
                        newenvironments.append( ('error'))
                        #print('err here1')
                        continue
                else:
                    newenvironments.append(('error'))
                    #print('err here2')
                    continue
            else:
                newenvironments.append(('error'))
                #print('err here3')
                continue
                
    return newcommands, newenvironments


def find_args_newcommands(newcommands, error_out = False, verbose=False):
    # counting arguments
    args = []
    err = False
    for i,nn in enumerate(newcommands):
        nnc = nn[1]
        ind = 0
        nums = []
        while ind < len(nnc): # loop through the whole thing
            if '#' in nnc[ind:]: # have some inputs!
                ind = nnc[ind:].index('#')+ind # find next, keep index of whole
                if ind==0 or (nnc[ind-1]!='\\' and ind<len(nnc)-1): # zero index, not escaped, >1 left
                    if nnc[ind+1].isdigit(): # #1
                        nums.append(int(nnc[ind+1]))
                        if ind<len(nnc)-2: # like #11, should only be #1-#9 if there is extra 
                                           # number, we could have an issue
                            if nnc[ind+2].isdigit():
                                if verbose: 
                                    print('more dig','||', nnc, 
                                                  '||', nnc[ind+2], '||', 
                                                  nnc[ind+2:])
                                    print('')
                        ind+=2 # add 2 because #(DIGIT)
                    else: # not digit, moving on... could be ## !
                        ind += 1
                else:
                    ind += 1
            else:
                ind += len(nnc[ind:])
        if len(nums)>0:
            nums = np.max(nums)
        else:
            nums=0
        #print(nums)
        nout = list(nn).copy()
        nout.extend([nums])
        args.append(nout)

    errArgs = [False]
    for ia,a in enumerate(args):
        if a[-1]>0:
            # check for [NUM] and not from something like \def\command#1
            if '['+str(a[-1]) + ']' not in a[1] and '#' not in a[0] and '@' not in a[1]:
                if '\\def' not in a[1] and '{#' + str(a[-1]) + '}' not in a[1]: # sometimes \def\command{#(DIGIT)}
                    # is it just an add one?
                    if '[' + str(a[-1]+1) +']' not in a[1]:
                        if verbose:
                            print(a)
                            print(f)
                        # just add and hope its all OK
                        i2 = a[1].split('[')[-1].split(']')[0]
                        if verbose: print(i2)
                        try:
                            args[ia][-1] = int(i2) 
                        except:
                            if verbose:
                                print('error in trying to get args:', a, ff)
                            errArgs = [True,a]
                    else:
                        args[ia][-1] = a[-1]+1

    if errArgs[0]:
        if error_out:
            print('error in args for newcommands!')
            import sys; sys.exit()
        err = True
        
    if error_out:
        return args
    else:
        return args, err
    
    
def find_args_newenvironments(newenvironments, error_out = False, verbose =False):
    # arguments of new environments not in commands
    args_env = []
    err = False
    for i,nn in enumerate(newenvironments):
        nnc = nn[1]
        ind = 0
        nums = []
        while ind < len(nnc): # loop through the whole thing
            if '#' in nnc[ind:]: # have some inputs!
                ind = nnc[ind:].index('#')+ind # find next, keep index of whole
                if ind==0 or (nnc[ind-1]!='\\' and ind<len(nnc)-1): # zero index, not escaped, >1 left
                    if nnc[ind+1].isdigit(): # #1
                        nums.append(int(nnc[ind+1]))
                        if ind<len(nnc)-2: # like #11, should only be #1-#9 if there is extra 
                                           # number, we could have an issue
                            if nnc[ind+2].isdigit():
                                if verbose:
                                    print('more dig','||', nnc, '||', nnc[ind+2], '||', nnc[ind+2:])
                                    print('')
                        ind+=2 # add 2 because #(DIGIT)
                    else: # not digit, moving on... could be ## !
                        ind += 1
                else:
                    ind += 1
            else:
                ind += len(nnc[ind:])
        if len(nums)>0:
            nums = np.max(nums)
        else:
            nums=0
        #print(nums)
        nout = list(nn).copy()
        nout.extend([nums])
        args_env.append(nout)
        
    for ia,a in enumerate(args_env):
        if a[-1]>0:
            # check for [NUM] and not from something like \def\command#1
            if '['+str(a[-1]) + ']' not in a[1] and '#' not in a[0] and '@' not in a[1]:
                if '\\def' not in a[1] and '{#' + str(a[-1]) + '}' not in a[1]: # sometimes \def\command{#(DIGIT)}
                    # is it just an add one?
                    if '[' + str(a[-1]+1) +']' not in a[1]:
                        if verbose:
                            print(a)
                            print(f)
                        # just add and hope its all OK
                        i2 = a[1].split('[')[-1].split(']')[0]
                        if verbose: print(i2)
                        args_env[ia][-1] = int(i2)        
                    else:
                        args_env[ia][-1] = a[-1]+1
                        
    # no real errors now, but could change
    if error_out:
        return args_env
    else:
        return args_env, err
    

    
def generate_find_replace_newcommands(args_newcommands, verbose=False):
    # go through and find if there is begin/end in there
    # note: at this point all beginnings/endings should be fixed
    find_replace = []
    comments = []
    for ic,nc in enumerate(args_newcommands):
        if nc == 'error':
            continue
        n,fn,i1,i2,nArgs = nc
        if nArgs == 0: # no arguements
            if '\\begin' in fn and not ('\\end' in fn):
                i = fn.index(n+'}') + len(n+'}')
                ind1,ind2,err = spc(fn[i:],
                                function='',dopen='{',
                                dclose='}',
                               error_out=False)
                if not err:
                    cmd = fn[i:][ind1+1:ind2-1]
                    find_replace.append((n,cmd,nArgs))
                comments.append(fn)

            elif '\\end' in fn and not ('\\begin' in fn):
                i = fn.index(n+'}') + len(n+'}')
                ind1,ind2,err = spc(fn[i:],
                                function='',dopen='{',
                                dclose='}',
                               error_out=False)
                if not err:
                    cmd = fn[i:][ind1+1:ind2-1]
                    find_replace.append((n,cmd,nArgs))
                comments.append(fn)
            elif '\\def' in fn: # def statement
                pass
            else: # have both
                print('have both')
                import sys; sys.exit()
        else:
            find_replace.append((n,fn,nArgs))
            comments.append(fn)  
    return comments, find_replace
    
def replace_newcommands(text, args_newcommands, verbose = False, replace_comments = True):
    
    comments, find_replace = generate_find_replace_newcommands(args_newcommands, 
                                                               verbose=verbose)

    # find/replace -- require a whitespace after
    for instr, outstr,nArgs in find_replace:
        if nArgs == 0: 
            ind = 0
            text_out = []
            search_cmd = re.escape(instr) + '(\\s{1,})'

            while ind < len(text):
                if re.search(search_cmd, text[ind:]):
                    istart,iend1 = re.search(search_cmd, text[ind:]).span()
                    # get the command specifically
                    _,iend = re.search(re.escape(instr),text[ind:][istart:iend1]).span()
                    #iend += iend1
                    i1 = istart
                    i2 = istart+iend
                    # make sure we are not in a command
                    inCommand = False
                    for n,fn,i1c,i2c,ncc in args_newcommands:
                        if i1+ind >= i1c and i2+ind <= i2c: # inside
                            inCommand = True

                    if not inCommand: # not in a command
                        text_out.append(text[ind:][:istart])
                        text_out.append(outstr)
                        ind += i2
                    else: # in command, move on
                        ind += i2
                else: # not in there anymore
                    text_out.append(text[ind:])
                    ind += len(text[ind:])

            text = "".join(text_out)
        else: # has arguments -- need to parse these as well for replacement
            ind = 0
            text_out = []
            search_cmd = re.escape(instr) + r'(\s*){' # include bracket in search
            while ind < len(text):
                if re.search(search_cmd, text[ind:]): # start of command
                    istart,iend = re.search(search_cmd, text[ind:]).span()
                    args = {} # get all arguments and store their values
                    err = False
                    #if icount > 0: import sys; sys.exit()
                    for ia in range(nArgs): # loop through all expected arguments
                        # search for matching brakets, starting at starting {
                        ind1,ind2,err = spc(text[ind+iend-1:],
                                        function='',dopen='{',
                                        dclose='}',
                                       error_out=False)
                        if not err: # found it!
                            args[ia+1] = text[ind:][iend-1:][ind1+1:ind2-1]
                            # now we have to update everything for the next look at args
                            iend += ind2
                        else: # have an issue, carry on
                            if verbose: print('have issue finding {} for replacement args')
                            iend += 1
                            break
                        #import sys; sys.exit()
                        #if ia>0: import sys; sys.exit()
                    #import sys; sys.exit()
                    # replace
                    outstr_mod = outstr
                    for k,v in args.items():
                        outstr_mod = outstr_mod.replace('#'+str(k), v)
                    # now get just inside part
                    ind1,ind2,err = spc(outstr_mod[::-1],
                        function='',dopen='}',
                        dclose='{',
                       error_out=False)
                    outstr_mod = outstr_mod[::-1][ind1+1:ind2-1][::-1]
                    #if nArgs > 1: import sys; sys.exit()

                    inCommand = False
                    i1 = istart
                    i2 = iend-1
                    for n,fn,i1c,i2c,ncc in args_newcommands:
                        if i1+ind >= i1c and i2+ind <= i2c: # inside
                            inCommand = True

                    if not inCommand:      
                        text_out.append(text[ind:][:istart])
                        text_out.append(outstr_mod)
                    ind += iend-1
                    if verbose: 
                        print('args for:', outstr)
                        print(args)
                    #import sys; sys.exit()
                else:
                    text_out.append(text[ind:])
                    ind += len(text[ind:])
            text = "".join(text_out)
            
    # finally, replace comments
    if verbose: print('')
    if replace_comments:
        for c in comments:
            text = text.replace(c, '%'+c)
            if verbose:
                print(c, 'gets commented')

    return text

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
import re

def get_indexes(pattern:str, string:str) -> list[tuple]:
    # Se pueden utilizar patrones con positive/negative lookbehind y lookahead
    references = re.finditer(pattern, string)
    indexes = [(reference.start(), reference.end()) for reference in references]
    if(len(indexes)==0):
        return None
    else:
        return indexes

def get_indexes_blocks(string:str, patternStart:str, patternEnd:str):
    # Se pueden utilizar patrones con positive/negative lookbehind y lookahead
    pattern = rf'({patternStart}.*?{patternEnd})'
    matches = re.finditer(pattern, string, re.DOTALL)
    indexes = [(match.start(), match.end())for match in matches]
    if(len(indexes)==0):
        return None
    else:
        return indexes
    
def replace_pattern(pattern:str, substitute: str, string:str)->str:
    new_string = re.sub(pattern, substitute, string)
    return new_string

def split_with_pattern(pattern:str, string:str):
    new = re.split(pattern, string)
    return new


def splitp_lookbehind_and_lookhead(patternbehind:str, pattern:str, patternahead:str, string:str):
    # Se utiliza dos tecnicas positive lookbehind and positive lookhead
    # Se asegura que antes del patron or debe de existir un ) y despues un (
    # no pueden manejar patrones no fijos [.]+
    # negative lookbehin "(?<!pattern)" negative lookahead "(?!pattern)"
    # positive lookbehin "(?<=pattern)" positive lookahead "(?=pattern)"
    open_ = fr"(?<={patternbehind})"
    close_ = fr"(?={patternahead})"
    completed = open_ + pattern + close_
    elements = re.split(completed, string)
    return elements

def indexes_avoiding_head_and_tail(patternhead:list, patterntail:list, pattern:str, string:str)->list[tuple]:
    # Se pueden utiliza patrones con positive/negative lookbehind/ahead
    template = ""
    for h,t in iter(zip(patternhead, patterntail)):
        template += "(" + h + ".*?"+ t +")"
        template += "|"
    template = template[:-1]
    matches = re.finditer(template, string, re.DOTALL)
    indexesHT = [(match.start(),match.end()) for match in matches]
    matches = re.finditer(pattern, string, re.DOTALL)
    indexes = [(match.start(),match.end()) for match in matches]
    target = []
    for i,s in indexes:
        cond = False
        for inf,sup in indexesHT:
            if(inf<i and sup>s):
                cond = True
                break
        if(not cond):
            target.append((i,s))
    if(target == []):
        return None
    else:
        return target


def get_elements_notin_indexes(indexes:list[tuple],string:str)->list:
    partes = []
    indice_actual = 0
    for inicio, fin in indexes:
        if indice_actual < inicio:
            partes.append(string[indice_actual:inicio])
        indice_actual = fin
    if indice_actual < len(string):
        partes.append(string[indice_actual:])
    return partes
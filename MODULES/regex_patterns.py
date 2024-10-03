

class Types:
    __slots__ = ('seqof','real', 'int', 'nat', 'nat0', 'char')
    def __init__(self):
        self.seqof = r'\bseq\s+of\s+\b'
        self.real = r'\breal\b'
        self.int = r'\bint\b'
        self.nat = r'\bnat\b'
        self.nat0 = r'\bnat0\b'
        self.char = r'\bchar\b'


class Blocks:
    __slots__ = ('_process', 'process_','_forall','forall_','_exists','exists_')
    def __init__(self, option):
        if(option == 'process'):
            self._process = r"\bprocess\b"
            self.process_ = r"\bend_process\b"
        elif(option == 'quantifiers'):
            self._forall = r'forall'
            self.forall_ = r"(?<!')\.(?!')"
            self._exists = r'exists'
            self.exists_ = r"(?<!')\.(?!')"
        else:
            raise ValueError("Error: opción no reconocida {'process','quatifiers'}")

class Specification:
    __slots__ = ('process','end_process','aux','ext','pre','post', 'wr','rd','sept','sepv','inport','outport')
    def __init__(self, option:str):
        if(option == 'keys'):
            self.process = r'\bprocess\b\s*'
            self.aux = r'\baux\b\s*'
            self.ext = r'\bext\b\s*'
            self.pre = r'\bpre\b\s*'
            self.post = r'\bpost\b\s*'
            self.end_process = r'\bend_process\b\s*'
        elif(option == 'ports'):
            self.wr = r'\bwr\b\s*'
            self.rd = r'\brd\b\s*'
            self.sept = ':'
            self.sepv = ','
            self.inport = r"(?<=\()[\w\d\s,:]+(?=\))"
            self.outport = r"(?<=\))[\w\d\s,:]+"
        else:
            raise ValueError("Error: opción no reconocida {'keys','ports'}")
        
class Operator:
    def __init__(self, option:str):
        if(option in {'logic'}):
            self.implies_ = r'\s+implies\s+'
            self.and_ = r'\s+and\s+'
            self.or_ = r'\s+or\s+'
        elif(option in {'set'}):
            self.inset_ = r'\s+inset\s+'
            self.notin_ = r'\s+notin\s+'
        elif(option in {'relational'}):
            self.equality_ = r"(?<!')\s*=\s*(?!')"
            self.inequality_ = r"(?<!')\s*<>\*"
            self.le_ = r"(?<!')\s*<=\s*(?!')"
            self.ge_ = r"(?<!')\s*>=\s*(?!')"
            self.less_ = r"(?<!')\s*<\s*(?!')"
            self.greater_ = r"(?<!')\s*>\s*(?!')"
        else:
            raise ValueError("Error: opción no valida {'logic', 'set', 'relational'}")

class Delimiters:
    __slots__ = ('_evaluation','evaluation_','_disyuntos','disyuntos_','_function','function_')
    def __init__(self, option):
        if(option == 'evaluation'):
            self._evaluation = r"(?<!')\{(?!')"
            self.evaluation_ = r"(?<!')\}(?!')"
        elif(option == 'disyuntos'):
            self._disyuntos = r"(?<!')\((?!')"
            self.disyuntos_ = r"(?<!')\)(?!')"
        elif(option == 'domain'):
            self._domain = r"(?<!')\[(?!')"
            self.domain_ = r"(?<!')\](?!')"

class Mutations:
    __slots__ = ('less','equal','greater')
    def __init__(self):
        self.less = " < "
        self.equal = " = "
        self.greater = " > "

class Set:
    __slots__ = ('in_','not_')
    def __init__(self):
        op = Operator('set')
        self.in_ = "[\w\d\[\]\.\(\)']+" + op.inset_ + "(\{)[^\}]+(\})"
        self.not_ = "[\w\d\[\]\.\(\)']+" + op.notin_ + "(\{)[^\}]+(\})"


class Universal:
    __slots__ = ('pattern','domainnum','domaininds','domainelems')
    def __init__(self, option:str):
        if(option == 'generation'):
            self.pattern = r'\bforall\b\[[^\]]+\]\s*\|\s*[^\}\.]+\.'
        elif(option == 'evaluation'):
            self.pattern = r'\bforall\b\[[^\]]+\]\s*\|\s*[^\.]+\.'
        else:
            raise ValueError("Pattern Universal")
        self.domainnum = r'\{[^\}]+\}'
        self.domaininds = r'\binds\b\([^\)]+\)'
        self.domainelems = r'\belems\b\([^\)]+\)'

class Existential:
    __slots__ = ('pattern','domainnum')
    def __init__(self, option:str):
        if(option == 'generation'):
            self.pattern = r'\bforall\b\[[\]]+\s*\|\s*[^\}\.]+\.'
        else:
            raise ValueError("Pattern Universal")
        self.domainnum = r'\{[^\}]+\}'

class Functions:
    __slots__ = ('len')
    def __init__(self, option):
        op = Operator('relational')
        if(option=='len'):
            self.len = rf'len\([\w\d]+\){op.equality_}[\d]+'
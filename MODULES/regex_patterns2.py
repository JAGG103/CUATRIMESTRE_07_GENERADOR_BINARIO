class Type:
    __slots__ = ('seqof','real', 'int', 'nat', 'nat0', 'char')
    def __init__(self):
        self.seqof = r'\bseq\s+of\s+\b'
        self.real = r'\breal\b'
        self.int = r'\bint\b'
        self.nat = r'\bnat\b'
        self.nat0 = r'\bnat0\b'
        self.char = r'\bchar\b'

class Block:
    __slots__ = ('process', 'endprocess')
    def __init__(self):
        self.process = r"\bprocess\b"
        self.endprocess = r"\bend_process\b"

class Specification:
    __slots__ = ('process','end_process','aux','ext','pre','post', 'wr','rd','instdom','separator','inport','outport')
    def __init__(self):
        # Inicios de linea
        self.process = rf"{Block().process}\s*"
        self.aux = r'\baux\b\s*'
        self.ext = r'\bext\b\s*'
        self.pre = r'\bpre\b\s*'
        self.post = r'\bpost\b\s*'
        self.end_process = rf'{Block().endprocess}\s*'
        # Modos de lectura o escritura
        self.wr = r'\bwr\b\s*'
        self.rd = r'\brd\b\s*'
        # Puertos
        self.instdom = ':'
        self.separator = ','
        self.inport = rf"(?<=\()[\w\d{self.separator}{self.instdom}]+(?=\))"
        self.outport = fr"(?<=\))[\w\d{self.separator}{self.instdom}]+"

class Operator:
    __slots__ = ('implies','and_','or_','not_','inset','notin','equality','inequality','le','ge','less','greater')
    def __init__(self):
        self.implies = r'\s+implies\s+'
        self.and_ = r'\s+and\s+'
        self.or_ = r'\s+or\s+'
        self.not_ = r'\b\s*not\s+\b' 
        self.inset = r'\s+inset\s+'
        self.notin = r'\s+notin\s+'
        self.equality = r"(?<!')\s*=\s*(?!')"
        self.inequality = r"(?<!')\s*<>\s*(?<!')"
        self.le = r"(?<!')\s*<=\s*(?!')"
        self.ge = r"(?<!')\s*>=\s*(?!')"
        self.less = r"(?<!')\s*<\s*(?!['>])"
        self.greater = r"(?<!['<])\s*>\s*(?!')"

class Mutation:
    __slots__ = ('less','equal','greater')
    def __init__(self):
        self.less = " < "
        self.equal = " = "
        self.greater = " > "

class Delimiter:
    __slots__ = ('disyuntos','enddisyuntos','arg','endarg')
    def __init__(self):
        self.disyuntos = r"(?<!')\((?!')"
        self.enddisyuntos = r"(?<!')\)(?!')"
        self.arg = r"(?<!')\((?<!')"
        self.endarg = r"(?<!')\)(?<!')"

class Function:
    __slots__ = ('lenght')
    def __init__(self):
        self.lenght = r"\blen\b"


class Quantifier:
    __slots__ = ('forall','exists','endquant','evaluation','endevaluation','domain','enddomain','num','endnum','inds','elems','endie','itervar','suchthat','to')
    def __init__(self):
        self.forall = r'\bforall\b'
        self.exists = r'exists'
        self.endquant = r"(?<!');(?!')"

        self.evaluation = r"(?<!')\{(?!')"
        self.endevaluation = r"(?<!')\}(?!')"

        self.domain = r"(?<!')\[(?!')"
        self.enddomain = r"(?<!')\](?!')"
        self.num = r"(?<!')\{(?<!')"
        self.endnum = r"(?<!')\}(?<!')"
        self.inds = rf'\binds\b\{Delimiter().arg}'
        self.elems = rf"\belems\b{Delimiter().arg}"
        self.endie = rf"{Delimiter().endarg}"
        self.itervar = rf"(?<={self.domain})[\w\d]+(?={Specification().instdom})"
        self.suchthat = r"(?<!')\s*\|\s*(?!')"
        self.to = r"\.{3}"



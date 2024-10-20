from MODULES.regex_functions import get_indexes_blocks, split_with_pattern, get_indexes, indexes_avoiding_head_and_tail, get_elements_notin_indexes, splitp_lookbehind_and_lookhead

from MODULES.regex_patterns2 import Block, Operator, Specification, Quantifier, Delimiter

class Analyzer:
    __slots__ = ('name','init', 'inport','inaux','outport','outaux','prels', 'testconditions','defconditions')

    def __init__(self, specification:str):
        self.name = str()
        self.init = {}
        self.inport = {}
        self.inaux = {}
        self.outport = {}
        self.outaux = {}
        self.prels = []
        self.testconditions = []
        self.defconditions = []
        
        processInit, processUT = self.get_processes(specification)
        self.get_init(processInit)
        postls = self.get_info_processUT(processUT)
        self.get_testconditions_defconditions(self.prels, postls)

    # GET_PROCESSES
    def get_processes(self, specification):
        block = Block()
        indexes = get_indexes_blocks(specification, block.process, block.endprocess)
        processInit = specification[indexes[0][0]:indexes[0][1]]
        processUT = specification[indexes[1][0]:indexes[1][1]]
        return processInit, processUT
    
    # GET_INIT
    def get_init(self, processInit:str):
        operator = Operator()
        init = {}
        lines = processInit.split('\n')
        lines.pop(0)
        lines.pop(-1)
        if(lines!=[]):
            for line in lines:
                clave, valor = split_with_pattern(operator.equality, line)
                valor = eval(valor)
                init.update({clave:valor})
        self.init = init

    # GET_INFO_PROCESSUT
    def get_info_processUT(self, processUT:str)->list:
        specification = Specification()
        inds = get_indexes(specification.post, processUT)
        prepost = processUT[:inds[0][0]]
        postpost = processUT[inds[0][0]:]
        linesls = prepost.split('\n')
        inds = get_indexes(specification.end_process, postpost)
        linesls += [postpost[:inds[0][0]].replace('\n','')]
        for line in linesls:
            if(len(line)==0):
                continue
            elif(get_indexes(specification.process, line)!=None):
                self.name = self.get_process_name(line)
                self.inport, self.outport = self.get_ports(line)
            elif(get_indexes(specification.aux,line)!=None):
                self.inaux, self.outaux = self.get_ports(line)
            elif(get_indexes(specification.ext, line)!=None):
                self.get_external_variables(line)
            elif(get_indexes(specification.pre, line)!=None):
                self.get_pre(line)
            elif(get_indexes(specification.post, line)!=None):
                postls = self.return_post(line)
            else:
                raise ValueError(f"Elemento en la especificación que no corresponde {line}")
        return postls
    
    # GET_testconditions_defconditions
    def get_testconditions_defconditions(self, prels, postls):
        tcs,dcs = [],[]
        patterns = [rf"\b{variable}\b" for variable in self.outport['variables']]
        patterns_= [rf"\b{variable}\b" for variable in self.outaux['variables']]  
        patterns = r"|".join(patterns + patterns_)
        fss = self.return_functional_scenarios(prels, postls)
        for fs in fss:
            tc, dc = [],[]
            for atom in fs:
                if(get_indexes(patterns, atom)):
                    dc.append(atom)
                else:
                    tc.append(atom)
            tcs += [tc]
            dcs += [dc]
        self.testconditions = tcs
        self.defconditions = dcs
        
        
    
    # AUXILIARES
    def return_functional_scenarios(self, prels:list, postls:list)->list[list]:
        fss = []
        for i in range(len(postls)):
            fss.append(prels + postls[i])
        return fss

    def get_pre(self, line:str):
        quantifier = Quantifier()
        operator = Operator()
        specification = Specification()

        inds = get_indexes(specification.pre, line)
        line = line[inds[0][1]:]
        inds = indexes_avoiding_head_and_tail([quantifier.forall, quantifier.exists],[quantifier.endquant, quantifier.endquant], operator.and_, line)
        if(inds):
            self.prels = get_elements_notin_indexes(inds, line)
        elif(line != ''):
            self.prels = [line]
        
        
            
    def return_post(self, line:str):
        specification = Specification()
        delimiter = Delimiter()
        operator = Operator()
        quantifier = Quantifier()
        inds = get_indexes(specification.post, line)
        poststr = line[inds[0][1]:]
        postls = splitp_lookbehind_and_lookhead(delimiter.enddisyuntos, operator.or_, delimiter.disyuntos, poststr)
        postls = [e[1:-1] for e in postls]
        indexesgen = (indexes_avoiding_head_and_tail([quantifier.forall, quantifier.exists],[quantifier.endquant, quantifier.endquant], operator.and_, element) for element in postls)
        for i in range(len(postls)):
            indexes = next(indexesgen)
            postls[i] = get_elements_notin_indexes(indexes, postls[i])
        return postls

    def get_process_name(self, line:str) -> str:
        specification = Specification()
        processinds = get_indexes(specification.process, line)
        startport = get_indexes(specification.startport, line)
        name = line[processinds[0][1]:startport[0][0]]
        return name


    def get_ports(self, line:str)->tuple[dict]:
        specification = Specification()
        ip = get_indexes(specification.inport, line)
        op = get_indexes(specification.outport, line)
        if(ip and op):
            inportstr = line[ip[0][0]:ip[0][1]]
            outportstr = line[op[0][0]:op[0][1]]
        elif(ip):
            inportstr = line[ip[0][0]:ip[0][1]]
            outportstr = None
        elif(op):
            inportstr = None
            outportstr = line[op[0][0]:op[0][1]]
        else:
            inportstr = None
            outportstr = None
        inport = self.turn_ports_to_dict(inportstr)
        outport = self.turn_ports_to_dict(outportstr)
        return inport, outport
        

    def turn_ports_to_dict(self, port:str|None)->dict:
        specification = Specification()
        variables, types = [],[]
        if(port):
            portls = port.split(specification.separator)
            for element in portls:
                variable, typee = element.split(specification.instdom)
                variables += [variable]
                types += [typee]
        port = {'variables':variables, 'types':types}
        return port


    def get_external_variables(self, line:str):
        specification = Specification()

        inport = {'variables':[], 'types':[]}
        outport = {'variables':[], 'types':[]}
        indexes = get_indexes(specification.ext, line)
        extstr = line[indexes[0][1]:]
        if(extstr!=''):
            extls = extstr.split(specification.separator)
            for element in extls:
                indexesrd = get_indexes(specification.rd, element)
                indexeswr = get_indexes(specification.wr, element)
                if(indexesrd!=None):
                    info = element[indexesrd[0][1]:]
                    variable,typee = info.split(specification.instdom)
                    variable = '_'+variable
                    inport['variables'].append(variable)
                    inport['types'].append(typee)
                elif(indexeswr!=None):
                    info = element[indexeswr[0][1]:]
                    variable,typee = info.split(specification.instdom)
                    outport['variables'].append(variable)
                    outport['types'].append(typee)
                    variable = '_'+variable
                    inport['variables'].append(variable)
                    inport['types'].append(typee)
                else:
                    raise ValueError("Entrada no valida wr o rd")
        self.inport['variables'] += inport['variables']
        self.inport['types'] += inport['types']
        self.outport['variables'] += outport['variables']
        self.outport['types'] += outport['types']
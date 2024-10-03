from MODULES.regex_patterns import Blocks, Specification, Operator, Delimiters
from MODULES.regex_functions import get_indexes_blocks, split_with_pattern, get_indexes, indexes_avoiding_head_and_tail, get_elements_notin_indexes, splitp_lookbehind_and_lookhead

class Analyzer:
    __slots__ = ('init', 'inPort','inAuxPort','outPort','outAuxPort','prels', 'testConditions','defConditions')

    def __init__(self, specification:str):
        self.init = {}
        self.inPort = {}
        self.inAuxPort = {}
        self.outPort = {}
        self.outAuxPort = {}
        self.prels = []
        self.testConditions = []
        self.defConditions = []
        
        processInit, processUT = self.get_processes(specification)
        self.get_init(processInit)
        postls = self.get_info_processUT(processUT)
        self.get_testconditions_defconditions(self.prels, postls)

    # GET_PROCESSES
    def get_processes(self, specification):
        indexes = get_indexes_blocks(specification, Blocks('process')._process, Blocks('process').process_)
        processInit = specification[indexes[0][0]:indexes[0][1]]
        processUT = specification[indexes[1][0]:indexes[1][1]]
        return processInit, processUT
    
    # GET_INIT
    def get_init(self, processInit:str):
        init = {}
        lines = processInit.split('\n')
        lines.pop(0)
        lines.pop(-1)
        if(lines!=[]):
            for line in lines:
                clave, valor = split_with_pattern(Operator('relational').equality_, line)
                valor = eval(valor)
                init.update({clave:valor})
        self.init = init

    # GET_INFO_PROCESSUT
    def get_info_processUT(self, processUT:str)->list:
        linesls = processUT.split('\n')
        for line in linesls:
            if(len(line)==0 or get_indexes(Specification('keys').end_process,line)):
                continue
            elif(get_indexes(Specification('keys').process, line)!=None):
                self.inPort, self.outPort = self.get_ports(line)
            elif(get_indexes(Specification('keys').aux,line)!=None):
                self.inAuxPort, self.outAuxPort = self.get_ports(line)
            elif(get_indexes(Specification('keys').ext, line)!=None):
                self.get_external_variables(line)
            elif(get_indexes(Specification('keys').pre, line)!=None):
                self.get_pre(line)
            elif(get_indexes(Specification('keys').post, line)!=None):
                postls = self.return_post(line)
            else:
                raise ValueError(f"Elemento en la especificación que no corresponde {line}")
        return postls
    
    # GET_TESTCONDITIONS_DEFCONDITIONS
    def get_testconditions_defconditions(self, prels, postls):
        tcs,dcs = [],[]
        patterns = [rf"\b{variable}\b" for variable in self.outPort['variables']]
        patterns_= [rf"\b{variable}\b" for variable in self.outAuxPort['variables']]  
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
        self.testConditions = tcs
        self.defConditions = dcs
        
        
    
    # AUXILIARES
    def return_functional_scenarios(self, prels:list, postls:list)->list[list]:
        fss = []
        for i in range(len(postls)):
            fss.append(prels + postls[i])
        return fss

    def get_pre(self, line:str):
        quan = Blocks('quantifiers')
        logic = Operator('logic')
        specification = Specification('keys')

        inds = get_indexes(specification.pre, line)
        line = line[inds[0][1]:]
        indexes = indexes_avoiding_head_and_tail([quan._forall,quan._exists],[quan.forall_,quan.exists_],logic.and_,line)
        if(len(indexes)>0):
            self.prels = get_elements_notin_indexes(indexes, line)
            
    def return_post(self, line:str):
        inds = get_indexes(Specification('keys').post, line)
        poststr = line[inds[0][1]:]
        postls = splitp_lookbehind_and_lookhead(Delimiters('disyuntos').disyuntos_, Operator('logic').or_, Delimiters('disyuntos')._disyuntos, poststr)
        postls = [e[1:-1] for e in postls]
        indexesgen = (indexes_avoiding_head_and_tail([Blocks('quantifiers')._forall, Blocks('quantifiers')._exists],[Blocks('quantifiers').forall_, Blocks('quantifiers').exists_], Operator('logic').and_, element) for element in postls)
        for i in range(len(postls)):
            indexes = next(indexesgen)
            postls[i] = get_elements_notin_indexes(indexes, postls[i])
        return postls


    def get_ports(self, line:str)->tuple[dict]:
        specification = Specification('ports')
        ip = get_indexes(specification.inport, line)
        op = get_indexes(specification.outport, line)
        if(ip!=None and op!=None):
            inportstr = line[ip[0][0]:ip[0][1]]
            outportstr = line[op[0][0]:op[0][1]]
        elif(ip!=None):
            inportstr = line[ip[0][0]:ip[0][1]]
            outportstr = None
        else:
            inportstr = None
            outportstr = None
        inport = self.turn_ports_to_dict(inportstr)
        outport = self.turn_ports_to_dict(outportstr)
        return inport, outport
        

    def turn_ports_to_dict(self, port:str|None)->dict:
        variables, types = [],[]
        if(port):
            portls = port.split(Specification('ports').sepv)
            for element in portls:
                variable, typee = element.split(Specification('ports').sept)
                variables += [variable]
                types += [typee]
        port = {'variables':variables, 'types':types}
        return port


    def get_external_variables(self, line:str):
        specification = Specification('keys')
        ext = specification.ext
        specification = Specification('ports')
        inport = {'variables':[], 'types':[]}
        outport = {'variables':[], 'types':[]}
        indexes = get_indexes(ext, line)
        extstr = line[indexes[0][1]:]
        if(extstr!=''):
            extls = extstr.split(specification.sepv)
            for element in extls:
                indexesrd = get_indexes(specification.rd, element)
                indexeswr = get_indexes(specification.wr, element)
                if(indexesrd!=None):
                    info = element[indexesrd[0][1]:]
                    variable,typee = info.split(specification.sept)
                    variable = '_'+variable
                    inport['variables'].append(variable)
                    inport['types'].append(typee)
                elif(indexeswr!=None):
                    info = element[indexeswr[0][1]:]
                    variable,typee = info.split(specification.sept)
                    outport['variables'].append(variable)
                    outport['types'].append(typee)
                    variable = '_'+variable
                    inport['variables'].append(variable)
                    inport['types'].append(typee)
                else:
                    raise ValueError("Entrada no valida wr o rd")
        self.inPort['variables'] += inport['variables']
        self.inPort['types'] += inport['types']
        self.outPort['variables'] += outport['variables']
        self.outPort['types'] += outport['types']
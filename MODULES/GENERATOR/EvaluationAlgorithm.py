from MODULES.regex_functions import get_indexes, get_elements_notin_indexes, replace_pattern, split_with_pattern

from MODULES.GENERATOR.auxiliary import Quantifiers, Evaluate, Flags
from MODULES.regex_patterns2 import Operator

class EvaluationAlgorithm:
    def __init__(self, evaluations:dict, init:dict):
        self.init_ = self.main(evaluations, init)
        

    def main(self,evaluations:dict, init:dict)->dict:
        for variable in init.keys():
            globals()[variable] = init[variable]

        functions = [self.evaluate_universal, self.evaluate_existential]
        names = ['universal evaluation','existential evaluation']
        for i in range(len(names)):
            for predicate in evaluations[names[i]]:
                functions[i](predicate, init)

        for variable in init.keys():
            init[variable] = eval(variable)
        return init
    

    def evaluate_existential(self, predicate:str, init_:dict):
        # Este operador realizara los efectos siempre que la causa se cumpla, el numero de veces que la implicación se cumpla
        existential = Quantifiers(predicate)
        self.auxiliary_existential(existential, init_)
            
    def evaluate_universal(self, predicate:str, init_:dict):
        # Este operador realizara el efecto una vez si se cumple el efecto.
        universal = Quantifiers(predicate)
        self.auxiliary_universal(universal, init_,)


    def auxiliary_existential(self, quantifier:Quantifiers, init_:dict):
        # Función auxiliar que utiliza un objeto de la clase 'Quantifiers' para obtener información de este predicado, obtener las causas y efectos, para posteriormente evaluar
        operatorobj = Operator()
        flags = Flags()

        for atom in quantifier.atoms:
            atom = atom[1:-1]
            inds = get_indexes(operatorobj.implies, atom)
            causes = atom[:inds[0][0]]
            efect = atom[inds[0][1]:]
            inds_and = get_indexes(operatorobj.and_, causes)
            inds_or = get_indexes(operatorobj.or_, causes)
            if(inds_and):
                subatoms, operator = get_elements_notin_indexes(inds_and, causes), flags.AND
            elif(inds_or):
                subatoms, operator = get_elements_notin_indexes(inds_or, causes), flags.OR
            else:
                subatoms, operator = [causes], flags.NONE
            start = eval(quantifier.start)
            end = eval(quantifier.end.replace("\\", "\\\\"))
            errors = list()
            for i in range(start, end):
                errors_ = list()
                element = str(i) if quantifier.domaint in {flags.DOMAINNUM, flags.DOMAININDS} else f"{quantifier.domain}[{i}]"
                for atom in subatoms:
                    # Recupera los valores de las variables del proceso init y los guarda en el diccionario init_
                    for variable in init_.keys():
                        init_[variable] = eval(f"{variable}")
                    # --------------------------------------
                    atom = replace_pattern(quantifier.itervar, element, atom)
                    option = flags.SET if get_indexes(operatorobj.inset+'|'+operatorobj.notin, atom) else flags.REL
                    pattern = rf"{operatorobj.inset}|{operatorobj.notin}|{operatorobj.less}|{operatorobj.greater}|{operatorobj.equality}|{operatorobj.le}|{operatorobj.ge}|{operatorobj.inequality}"
                    inds = get_indexes(pattern, atom)
                    operator_ = atom[inds[0][0]:inds[0][1]]
                    left, right = split_with_pattern(pattern, atom)
                    error_ = Evaluate().relational_eval(left, right, operator_, init_) if option==flags.REL else Evaluate().set_eval(left, right, operator_, init_)
                    errors_ += [error_] 
                errors.append(sum(errors_) if operator in {flags.AND, flags.NONE} else min(errors_))
            error = min(errors)
            self.auxiliary_evaluations(efect, init_.keys(), error)


    def auxiliary_universal(self, quantifier:Quantifiers, init_:dict):
        # Función auxiliar que utiliza un objeto de la clase 'Quantifiers' para obtener información de este predicado, obtener las causas y efectos, para posteriormente evaluar
        operatorobj = Operator()
        flags = Flags()

        start = eval(quantifier.start)
        end = eval(quantifier.end.replace("\\", "\\\\"))
        # Iteración sobre los elementos del dominio
        for i in range(start, end):
            element = str(i) if quantifier.domaint in {flags.DOMAINNUM, flags.DOMAININDS} else f"{quantifier.domain}[{i}]"
            # Iteración sobre los Conjuntivos (evaluaciones)
            for atom in quantifier.atoms:
                errors_ = list()
                atom = atom[1:-1]
                inds = get_indexes(operatorobj.implies, atom)
                causes = atom[:inds[0][0]]
                efect = atom[inds[0][1]:]
                inds_and = get_indexes(operatorobj.and_, causes)
                inds_or = get_indexes(operatorobj.or_, causes)
                if(inds_and):
                    subatoms, operator = get_elements_notin_indexes(inds_and, causes), flags.AND
                elif(inds_or):
                    subatoms, operator = get_elements_notin_indexes(inds_or, causes), flags.OR
                else:
                    subatoms, operator = [causes], flags.NONE
                    
                try:
                    for atom in subatoms:
                        # Recupera los valores de las variables del proceso init y los guarda en el diccionario init_
                        for variable in init_.keys():
                            init_[variable] = eval(f"{variable}")
                        # ---------------------------------------
                        option = flags.SET if get_indexes(operatorobj.inset+'|'+operatorobj.notin, atom) else flags.REL
                        atom = replace_pattern(quantifier.itervar, element, atom)
                        efect = replace_pattern(quantifier.itervar, element, efect)
                        pattern = rf"{operatorobj.less}|{operatorobj.greater}|{operatorobj.equality}|{operatorobj.le}|{operatorobj.ge}|{operatorobj.inequality}|{operatorobj.inset}|{operatorobj.notin}"
                        inds = get_indexes(pattern, atom)
                        operator_ = atom[inds[0][0]:inds[0][1]]
                        left, right = split_with_pattern(pattern, atom)
                        error_ = Evaluate().relational_eval(left, right, operator_, init_) if option==flags.REL else Evaluate().set_eval(left, right, operator_, init_)
                        errors_ += [error_]
                    error = sum(errors_) if operator in {flags.AND, flags.NONE} else min(errors_)
                    self.auxiliary_evaluations(efect, init_.keys(), error)
                except IndexError:
                    pass


    def auxiliary_evaluations(self, efect:str, globvars:list, error:float):
        # Función que permite modificar los valores de las variables globales dentro de las evaluaciones
        operatorobj = Operator()

        if(error == 0.0):
            left, right = split_with_pattern(operatorobj.equality, efect)
            for globvar in globvars:
                modvar = rf"\b{globvar}\b(?!\[)"
                modele = rf"\b{globvar}\b(?=\[)"
                inds_modvar = get_indexes(modvar, left)
                inds_modele = get_indexes(modele, left)
                if(inds_modvar):
                    globals()[globvar] = eval(right)
                elif(inds_modele):
                    pinds = r"(?<=\[)\d+(?=\])"
                    inds = get_indexes(pinds, left)
                    position = left[inds[0][0]:inds[0][1]]
                    globals()[globvar][int(position)] = eval(right)


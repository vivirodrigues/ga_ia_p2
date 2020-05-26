import numpy as np

"""

Links que podem ser uteis:

https://www.geeksforgeeks.org/crossover-in-genetic-algorithm/


"""





"""

Classe do Elemento de cada solucao

Dependendo das abordagens e alteracoes vai ser bom ter isso separado em uma classe no futuro



"""
class element:

    def __init__(self, idd, geracao, genome):
        self.idd = idd
        self.geracao = geracao
        self.genome = genome
        self.score = None


    def __repr__(self):
        return "(id="+str(self.idd)+",geracao="+str(self.geracao)+",score="+str(self.score)+")"


"""

Classe responsavel por controlar todo o funcionamento do algoritmo genetico
Eh preciso fazer override dos metodos random_genome() e evaluate(). (pode ser feito diretamente ou com as funcoes set_evaluate() e set_random_genome())

"""
class GeneticAlgorithm:


    """
    
    define parametros iniciais e cria populacao aleatoria
    os parametros podem ser alterados pelos setters

    """
    def __init__(self, random_genome_func):
        self.population = []
        self.historic = []
        self.mutation_rate = 0
        self.population_size = 50
        self.iteration_limit = 100
        self.elements_created = 0
        self.crossover_type = 0
        self.best_element_total = None
        self.max_possible_score = float('inf')
        self.iteration_counter = 0
        self.stop_criteria_type = 0
        self.probs_type = 0

        self.cut_half_population = False
        self.set_random_genome(random_genome_func)
        self.create_initial_population()



    """
    
    executa o loop principal do algoritmo genetico

    """
    def run(self):



        while self.check_stop():
            self.calculate_score()


            self.population.sort(key=lambda x: x.score, reverse=True) # ordena por score




            if self.cut_half_population:
                self.population = self.population[0:len(self.population)//2] # descarta pior metade da populacao



            if self.best_element_total==None or self.population[0].score > self.best_element_total.score: # salva melhor elemento
                self.best_element_total = self.population[0]

            self.do_log()



            self.new_population()


            self.iteration_counter +=1

            if self.best_element_total.score >= self.max_possible_score:
                break

        return self.best_element_total


    def new_population(self):


        probs = self.get_probs()

        newPop = []

        while len(newPop)<self.population_size:
            parents = np.random.choice(self.population,size=2,p=probs) #seleciona parents

            new_element = element(self.elements_created, self.iteration_counter, self.crossover(parents[0].genome, parents[1].genome))

            new_element.genome = self.active_mutate(new_element.genome)
            newPop.append(new_element)
            self.elements_created += 1

        self.population = newPop

    def get_probs(self):
        if self.probs_type == 0:
            return self.probs_roulette()
        elif self.probs_type == 1:
            return self.probs_equal()

    def probs_equal(self):
        return [1/len(self.population)]*len(self.population)


    def probs_roulette(self):
        probs = [0]*len(self.population) # gera array de probs para selecionar parents
        for i in range(len(probs)):
            probs[i] = self.population[i].score
        div = sum(probs)

        if div!=0:
            for i in range(len(probs)):
                probs[i] /= div
        else:
            probs = [1/len(probs)]*len(probs)
        return probs

    def do_log(self):

            score_geracao_medio = 0
            score_geracao_max = float('-inf')
            score_geracao_min = float('inf')
            for i in range(len(self.population)):
                score_geracao_medio += self.population[i].score
                score_geracao_min = min(score_geracao_min, self.population[i].score)
                score_geracao_max = max(score_geracao_max, self.population[i].score)
            score_geracao_medio /= len(self.population)
            self.historic.append({"geracao":self.iteration_counter,"max":score_geracao_max,"min":score_geracao_min,"avg":score_geracao_medio,"best":self.best_element_total.score})


    def check_stop(self):
        if self.stop_criteria_type==0:
            return self.stop_criteria_double()
        elif self.stop_criteria_type==1:
            return self.stop_criteria_iteration()
        elif self.stop_criteria_type==2:
            return self.stop_criteria_score()

    def stop_criteria_double(self):
        s = self.population[0].score
        if s==None:
            s = 0
        return self.iteration_counter<self.iteration_limit or s>=self.max_possible_score

    def stop_criteria_iteration(self):
        return self.iteration_counter<self.iteration_limit

    def stop_criteria_score(self):
        s = self.population[0].score
        if s==None:
            s = 0
        return s>=self.max_possible_score

    def set_probs_type(self, e):
        self.probs_type = e

    def set_cut_half_population(self, e):
        self.cut_half_population = e

    def set_max_score(self, e):
        self.max_possible_score = e

    def set_iteration_limit(self, e):
        self.iteration_limit = e

    def set_population_size(self, e):
        self.population_size = e

    def set_mutation_rate(self, e):
        self.mutation_rate = e

    # Faz o override da funcao evaluate
    def set_evaluate(self, e):
        self.evaluate = e

    # Faz o override da funcao random_genome
    def set_random_genome(self, e):
        self.random_genome = e

    def set_mutate(self, e):
        self.mutate = e

    def set_stop_criteria_type(self, e):
        self.stop_criteria_type = e

    # gera uma populacao nova
    # o metodo random_genome precisa ter sido override
    def create_initial_population(self):
        for _ in range(self.population_size):
            self.population.append(element(self.elements_created, 0, self.random_genome()))
            self.elements_created += 1


    # set do crossover type.
    # atualmente aceita 3 valores
    def set_crossover_type(self, e):
        self.crossover_type = e


    # chama o metodo de crossover que esta sendo utilizado
    def crossover(self, genA, genB):
        if self.crossover_type==0:
            return self.crossover_uniform(genA, genB)
        elif self.crossover_type==1:
            return self.crossover_single_point(genA, genB)
        elif self.crossover_type==2:
            return self.crossover_two_point(genA, genB)


    # CROSSOVER (Uniform Crossover)
    def crossover_uniform(self, genA, genB):
        new = np.array([],dtype=int)
        for i in range(len(genA)):
            if np.random.random()<0.5:
                new = np.append(new, genA[i])
            else:
                new = np.append(new, genB[i])
        return new

    # CROSSOVER (Single Point Crossover)
    def crossover_single_point(self, genA, genB):
        p = np.random.randint(low=1,high=len(genA)-1) # comeca em 1 e termina em len-1 para não poder simplesmente copiar o elemento
        return np.append(genA[0:p],genB[p:])

    # CROSSOVER (Two-Point Crossover)
    def crossover_two_point(self, genA, genB):
        c1 = c2 = np.random.randint(low=0,high=len(genA)) # gera um valor inteiro aleatorio de 0 a len(genoma)
        while c2==c1: # enquanto c1 e c2 forem iguais, gera valores novos para c2. isso garante que o corte tenha posicoes diferentes
            c2 = np.random.randint(low=0,high=len(genA))

        if c1>c2: # cooloca o menor na posicao c1
            c1, c2 = c2,c1

        new = np.append(np.append(genA[0:c1],genB[c1:c2]),genA[c2:]) # concatena o genomaA+genomaB+genomaA utilizando os cortes para definir onde cortar e contatenar

        return new



    #chama a funcao que calcula o score para cada elemento da populacao
    def calculate_score(self):
        for e in self.population:
            e.score = self.evaluate(e.genome)



    # a mutacao troca o valor dos bits entre 0 e 1
    def active_mutate(self,gen):
        if self.mutation_rate<=0: # se a taxa de mutacao for 0, return sem fazer anda
            return gen
        for i in range(len(gen)): # percore o genoma
            if np.random.random()<self.mutation_rate: # gera um numero aleatorio com distribuicao uniforme, se for menor que a taxa de mutacao ativa
                gen = self.mutate(i, gen) # chama o metodo mutate e passa o valor atual daquela posicao do genoma
        return gen # retorna novo genoma




    # Precisa ser override
    # Gera um genoma completamente aleatorio (Usado principalmente na primeira geracao)
    def random_genome(self):
        raise Exception("Should be override")


    # esse metodo eh obrigatoriamente override
    # calcula o fitness
    def evaluate(self):
        raise Exception("Should be override")


    # esse metodo eh obrigatoriamente override
    # faz a mutacao de uma posicao do genoma
    def mutate(self):
        raise Exception("Should be override")
# takes a list[] of tupples and returns a new list in a different order

import numpy as np
import math

#from skopt import gp_minimize
from itertools import combinations


class Matchmaking:
    def __init__(self, jugadores):
        self.jugadores_iniciales = jugadores
        self.initial_x = np.array(jugadores, dtype=np.dtype('bool,int'))
        self.initial_x['f0'][0:5] = False
        self.jugadores_finales = []
        self.X0 = np.array(0)
        self.index = np.array(0)

    def get_best(self, n_best=1, n_players=None):
        # Retorna un np.array con los mejores n_best resultados
        if self.index.shape == ():
            self.index = self.X0[:, n_players].argsort()
        return self.X0[self.index][0:n_best, :]

    def get_new_names(self, n_names=1, n_players=None):
        # Retorna una lista con listas de nombres
        w0 = self.get_best(n_names, n_players)[:, 0:n_players]
        names = []
        for i in range(n_names):
            index = w0[i].argsort()
            namesi = list(np.array(self.jugadores_iniciales)
                          [:, 0][index])
            names.append(namesi)
        return names

    def reinitX0(self, n_players):
        # inicializar X0 (todas las combinaciones posibles)
        aux = list(range(n_players))
        n_half_players = math.floor(n_players/2)
        combs = np.array(list(combinations(aux, n_half_players)))
        x0 = np.zeros((n_players, combs.shape[0]), dtype=bool).T
        y0 = np.zeros(combs.shape[0], dtype=int)[np.newaxis].T
        self.X0 = np.hstack((x0, y0))
        for idx, comb in enumerate(combs):
            self.X0[idx][comb] = True

    def loss_function(self, x):
        # initial_x is a np.array shape=(10,) (bool,mmr)x10 where bool = 0 radiant
        #       dtype=[('f0', '?'), ('f1', '<i8')]
        #x = np.array(x)
        team1 = (x == 0)*self.initial_x['f1']
        team2 = (x == 1)*self.initial_x['f1']
        half_players = len(self.initial_x['f1'])/2
        loss = abs(team1.sum()-team2.sum()) + \
            abs((np.array(x).sum()-half_players))*20000
        return loss

    # callback handler
    def on_step(self, res):
        print("res.x: ", res.x)
        print("res.fun: ", res.fun)
        if res.fun < 0:
            print('Interrupting!')
            return True

    # expensive and ineficcient
    # def solve1(self):
    #     bounds = []
    #     for i in range(10):
    #         bounds.append((0, 1))

    #     res = gp_minimize(self.loss_function,        # the function to minimize
    #                       bounds,               # the bounds on each dimension of x
    #                       n_calls=1000,         # the number of evaluations of f
    #                       n_random_starts=1000,  # the number of random initialization points
    #                       random_state=123,   # the random seed
    #                       callback=self.on_step)

    #     return res

    def solve(self, n_best=1):
        '''
        1) Encuentra todas las combinaciones posibles
        2) suma todos los mmr de equipo 1
        3) suma todos los mmr de equipo 2
        4) crea un vector con la diferencia y guarda en la ultima columna de self.X0
        '''


        # Actualiza el valor de self.X0 con loss en la ultima columna

        n_players = len(self.initial_x['f1'])

        # Actualiza X0 para todas las combinaciones
        if self.X0.shape == ():
            self.reinitX0(n_players)
        x0 = self.X0[:, 0:n_players]
        # Actualiza el ultimo valor de X0 correspondiente al loss
        sum1 = (x0.T*self.initial_x['f1'][np.newaxis].T).T.sum(axis=1)
        w2 = x0.T == False
        sum2 = (w2*self.initial_x['f1'][np.newaxis].T).T.sum(axis=1)
        self.X0[:, n_players] = abs(sum1-sum2)
        return self.get_new_names(n_best, n_players)

    @staticmethod
    def get_avg_mmr(players_list, players_tuples):
        sum = 0
        for player in players_list:
            for el in players_tuples:
                mmr = el[1] if el[0] == player else 0
                sum += mmr
        return sum/len(players_list)

    @staticmethod
    def get_sum(players_list, players_tuples):
        sum = 0
        for player in players_list:
            for el in players_tuples:
                mmr = el[1] if el[0] == player else 0
                sum += mmr
        return sum


def main():
    jugadores_10 = [("Pijama", 3225), ("Blob", 3350), ("Lordpires", 2950),
                    ("Salchichon", 2925), ("Xyrix", 3200), ("Endtime", 2900),
                    ("Cold", 3225), ("Oche", 3000), ("Saga", 3275),
                    ("Exilos", 2850)
                    ]
    jugadores_9 = [("Pijama", 3225), ("Blob", 3350), ("Lordpires", 2950),
                   ("Salchichon", 2925), ("Xyrix", 3200), ("Endtime", 2900),
                   ("Cold", 3225), ("Oche", 3000), ("Saga", 3275)
                   ]
    jugadores_8 = [("Pijama", 3225), ("Blob", 3350), ("Lordpires", 2950),
                   ("Salchichon", 2925), ("Xyrix", 3200), ("Endtime", 2900),
                   ("Cold", 3225), ("Oche", 3000)
                   ]
    jugadores_5 = [("Pijama", 3225), ("Blob", 3350), ("Lordpires", 2950),
                   ("Salchichon", 2925), ("Xyrix", 3200)
                   ]
    match = Matchmaking(jugadores_9)
    players = match.solve()[0]
    n = len(players)
    n12 = math.ceil(n/2) #must use ceil to separate teams
    sum_team1 = match.get_sum(players[0:n12], jugadores_10)
    sum_team2 = match.get_sum(players[n12:], jugadores_10)
    print(f'Team 1: {players[0:n12]} mmr_sum: {sum_team1}')
    print(f'Team 2: {players[n12:]} mmr_sum: {sum_team2}')
    print(f'mmr difference: {abs(sum_team1-sum_team2)}')


if __name__ == "__main__":
    main()

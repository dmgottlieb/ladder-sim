import random
from math import e
import sys
from statistics import pstdev

THRESHOLD = [999,5,5,5,5,5,5,5,5,5,5,4,4,4,4,4,3,3,3,3,3,2,2,2,2,2]
NGAMES = 100
EXPECTED_CUM_DIST = [0.0025, 0.0025, 0.0033, 0.005, 0.01, 0.02, 0.03, 0.04, 0.05, 0.07, 0.09, 0.12, 0.14, 0.2, 0.25, 0.3, 0.4, 0.45, 0.5, 0.5, 0.5, 1, 1, 1, 1, 1] # Comes from Battle.Net forums, end of March 2015

EXPECTED_DIST = [0.0025,
 0.0,
 0.0007999999999999999,
 0.0017000000000000001,
 0.005,
 0.01,
 0.009999999999999998,
 0.010000000000000002,
 0.010000000000000002,
 0.020000000000000004,
 0.01999999999999999,
 0.03,
 0.020000000000000018,
 0.06,
 0.04999999999999999,
 0.04999999999999999,
 0.10000000000000003,
 0.04999999999999999,
 0.04999999999999999,
 0.0,
 0.0,
 0.5,
 0,
 0,
 0,
 0]

class Season(object):
    def __init__(self, nplayers, G=100, alpha=2, beta=0.5):
        self.nplayers = nplayers
        self.G = G
        self.alpha = alpha
        self.beta = beta
        
        self.trial_id = "Players=" + str(nplayers) + ", G=" + str(G) + ", alpha=" + str(alpha) + ", beta=" + str(beta)
        
        self.AddPlayers(nplayers,G,alpha,beta)
        
        self.totalgames = 0
        self.finaltotal = sum([P.ngames for P in self.liveplayers]) / 2
        
    def AddPlayers(self,nplayers,G,alpha,beta):
        self.liveplayers = [Player(G,alpha,beta) for i in range(0,nplayers)]
        self.liveranks = [[] for i in range(0,26)]
        self.deadplayers = []
        self.deadranks = [[] for i in range(0,26)]
        self.liveranks[25].extend(self.liveplayers)
        
    def RunSeason(self):
        
        print "Simulating approx. " + str(self.finaltotal) + " games."
        print "Mean " + str(2 * self.finaltotal / self.nplayers) + " games per player." 
        print "Standard deviation " + str(pstdev([P.ngames for P in self.liveplayers]))
        
        while len(self.liveplayers) >= 2:
            self.PlayAGame()
            
            barlength = 38
            blocks = barlength * self.totalgames / self.finaltotal
            percent = 100*self.totalgames / self.finaltotal 
            text = "\rPercent: [{0}] {1}%".format( "=" * blocks + " " * (barlength - blocks), percent)
                
            sys.stdout.write(text)
            sys.stdout.flush()
                
        self.histogram = [len(R) for R in self.deadranks]
        print "\n" + str(self.totalgames) + " games simulated."
        
    def PlayAGame(self):
        # Choose a player
        A = random.choice(self.liveplayers)
        rank = A.rank
        self.liveranks[rank].remove(A)
        
        i = 0
        
        while True:
            try:
                B = random.choice(self.liveranks[rank - i])
                self.liveranks[rank - i].remove(B)
                break
            except IndexError: 
                i += 1
        
        winner, loser = DetermineWinner(A, B)
        
        winner.AddWin()
        loser.AddLoss()
        
        
        for P in (winner, loser):
            self.liveranks[P.rank].append(P)
            
            if P.ngames == 0:
                self.liveplayers.remove(P)
                self.deadplayers.append(P)
                self.liveranks[P.rank].remove(P)
                self.deadranks[P.rank].append(P)
                
        self.totalgames += 1
        
    def PlotRanks(self):
        from matplotlib import pyplot as plt
        data = [P.rank for P in self.deadplayers]

        n, bins, patches = plt.hist(data, range(0,26), normed=1, histtype='stepfilled', label="Histogram")
        plt.hist(data, bins, normed=1, histtype='step', cumulative=1, label="Cumulative distribution")
        
        plt.step(bins, EXPECTED_CUM_DIST, label="Expected cumulative distribution")
        
        plt.legend(loc=2,title=self.trial_id)
        
        plt.setp(patches, 'facecolor', 'b', 'alpha', 0.75)


        plt.show()
        
    def PlotSkills(self):
        from matplotlib import pyplot as plt
        data = [P.skill for P in self.deadplayers]
        
        n, bins, patches = plt.hist(data,bins=range(0,10), normed=1, histtype='stepfilled', label="Histogram")
        plt.setp(patches, 'facecolor', 'b', 'alpha', 0.75)


        plt.show()

class Player(object): 
    
    def __init__(self, G=100, alpha=2, beta=0.5):
        self.skill = random.gammavariate(alpha, beta) 
        self.ngames = int(self.skill*G / (alpha*beta)) + 1
        self.rank = 25
        self.stars = 0
        self.streak = 0

    def AddWin(self):
        
        self.stars += 1
        self.streak += 1
        if self.streak >= 3:
            self.stars += 1
        
        if self.stars > THRESHOLD[self.rank]:
            self.rank = self.rank - 1
            self.stars = self.stars - THRESHOLD[self.rank]
        
    def AddLoss(self):
        
        if self.rank <= 20:
            self.stars = self.stars -1
            self.streak = 0
        
        if self.stars < 0:
            self.rank =  min(self.rank + 1, 20)
            self.stars = THRESHOLD[self.rank]
            if self.rank == 20:
                self.stars = 0

        
def DetermineWinner(A, B): 
    
    A.ngames = A.ngames - 1
    B.ngames = B.ngames - 1 
    
    chance = DetermineWinChance(A, B)
    roll = random.random()
    
    if roll < chance:
        return A,B
    else: 
        return B,A
    
        
    
def DetermineWinChance(A, B): 
    
    c = 2.9444389791664403 # Normalize so that a difference of 1 on the skill scale corresponds to 95% win rate. 
    
    delta = A.skill - B.skill
    return 1 / (1 + e ** (-delta * c))
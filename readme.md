# ladder-sim

A script for numerically simulating outcomes on the Hearthstone competitive play ladder. 

To simulate a season of Ranked play on the ladder, create a new Season object. 
Parameters of Season object (pass to initializer):

* `nplayers`: number of players to simulate
* `G`: desired average number of games per player
* `alpha`: the shape parameter α of the gamma distribution used for player skill
* `beta`: the rate parameter β of the gamma distribution used for player skill

For example, 

	S = Season(10000, 100, 2.0, 0.5)

will create a new Season with 10,000 players playing an average 100 games each, and with skill values drawn from the given distribution. 
(The defaults are such that you'll get the same result with `S = Season(10000)`.)

Once you've initialized the Season with desired parameters, you then want to run the simulation: 

	S.RunSeason()

You should get something like the below: 

	Simulating approx. 503396 games.
	Mean 100 games per player.
	Standard deviation 71.1387186233
	Percent: [===================================== ] 99%
	503394 games simulated in 70.517105seconds (0.000140083324394 seconds per game).

As you can see, the simulation of 10,000 players *times* 100 games takes about 70s on my machine. 

Once you've run the simulation, you can display some analytics about the results: 

* `S.PlotRanks()`: display a histogram of the ladder rankings produced by the simulation, along with the reported actual distribution for comparison ([see](http://us.battle.net/hearthstone/en/forum/topic/16858985939)). 

	!(./img/plotranks-demo.png)

* `S.PlotSkills()`: display a histogram of skill distribution in the simulated player population. The scale is a renormalized Elo scale where a difference of 1.0 gives a 95% chance to win. 

	!(./img/plotskills-demo.png)


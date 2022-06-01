# ProbLog examples
This directory contains examples from ProbLog converted to the input language of our system. Many of these examples are taken from the ProbLog website's [tutorial](https://dtai.cs.kuleuven.be/problog/tutorial/various/01_montyhall.html) section where a lot more instances can be found. Note that there are some constructions in ProbLog that are not supported by our system (for examples the first [Monty Hall](https://dtai.cs.kuleuven.be/problog/tutorial/various/01_montyhall.html) encoding).

The translations of the alarm and second coin tossing example can be found in folder `plingo`.
## Instances
### Simple
Just a simple encoding showcasing both ways to write probabilistic facts in our system
```
plingo examples/problog/simple.plp --frontend=problog
```

### Tossing coins
Basic example from [here](https://dtai.cs.kuleuven.be/problog/tutorial/basic/01_coins.html). 
Suppose we have two coins. The first coin is fair (when tossed, it will land on heads with 50% probability), the second coin is biased (it will land on heads with 60% probability). What is now the probability that, if we toss the coins, both will land on heads? 
We can run this with
```
plingo examples/problog/tossing_coins.plp --frontend=problog
```
Note that we do not need any command line options, as the queries are inside the encoding like in ProbLog. As excepted we find that the probability for heads on both coins is 0.30.
```
Solving...
Answer: 1
heads2 heads1 twoHeads
Optimization: 0
Answer: 2

Optimization: 40546
Answer: 3
heads2
Optimization: 0
Answer: 4
heads1
Optimization: 40546


twoHeads: 0.30000
heads2: 0.60000
heads1: 0.50000
```

### Alarm
This is taken from [[1]](#1). There are two persons, Mary and John, and a burglary can happen with probability 0.1. An earthquake can happen with probability 0.2. Any of those two events will trigger an alarm which either person hears with probability 0.7. What is the probability of an earthquake or a burglary, given that the alarm has been triggered
```
plingo examples/problog/alarm.plp --frontend=problog
```
This gives us the following (conditional) probabilities
```
earthquake: 0.71429
burglary: 0.35714
hears_alarm(mary): 0.70000
hears_alarm(john): 0.70000
```

### Monty Hall (Alternative Encoding)
This example is taken from the ProbLog [Tutorial](https://dtai.cs.kuleuven.be/problog/tutorial/various/01_montyhall.html) website as well. Unlike the P-log encoding it has encoded explicitly the two options to switch or not to switch doors after Monty has opened a door.
```
plingo examples/problog/monty_hall_alternative.plp --frontend=problog
``` 

## References
<a id="1">[1]</a>
D. Fierens et al. (2015).
Inference and learning in probabilistic logic programs using weighted boolean formulas.
Theory and Practice of Logic Programming, 15(3), 385–401.
<a id="2">[2]</a>
J. Lee, S. Talsania, and Y. Wang (2017).
Computing LPMLN Using ASP and MLN Solvers.
Journal of Theory and Practice of Logic Programming, 17(5-6), 942-960.

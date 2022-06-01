# P-log examples
This directory contains the five examples from [[1]](#1) plus a variant of the Monty Hall problem taken from [[2]](#2). To run any of the examples add the `--frontend=plog` option.
The folder `plog2.0` contains some shorts examples and tests from the most recent [plog implementation](https://github.com/iensen/plog2.0) plus an incomplete script to convert instances in the plog2.0 format.

## Instances
### Dice
This is the introductory example from [[1]](#1) demonstrating how P-log programs can be input and calculated with our system. 
```
plingo examples/plog/dice.plp --frontend=plog --all
```

### Monty Hall
P-log encoding of the famous Monty Hall Problem
```
plingo examples/plog/monty_hall.plp --frontend=plog --all
```
There is also a variation with four door and assigned probabilities
```
plingo examples/plog/monty_hall_variant.plp --frontend=plog --all
```

### Simpson's paradox
Simpson's paradox is a phenomenom where some event seems more likely in the general population but less likely in every subpopulation (or vice versa). In this case we are looking at a patient who is wondering whether he should take a drug or not. For both females and males not taking the drug has a higher recovery rate. However, when looking at the entire population the recovery rate seems to be lower when taking the drug. One way to resolve this paradox is by using the causal reasoning of P-log. For adjusting whether or not the patient takes the drug, set constant `do_drug` to `t` or `f` (default is `do_drug=t`). 
```
plingo examples/plog/simpsons_paradox.plp --frontend=plog --all -c do_drug=t
```

### Moving robot
This encoding contains a robot and three doors that are reachable from the robot's position. The doors can be open or closed but the robot cannot open the doors. It is known that the robot navigation is usually successful. However, a malfunction can cause the robot to go off course and enter any one of the open rooms. The basic encoding contains some additional information that can be activated through the constant `x`. While `x=0` contains only the basic encoding, when `x=1`  there is an additional fact that the robot goes into room `r0`.
```
plingo examples/plog/moving_robot.plp --frontend=plog --all -c x=1
```
Accordingly, the output states that the robot is in room `r0`.
```
Solving...
Answer: 1
in(1,r0)
No soft weights in program. Cannot calculate probabilites
SATISFIABLE
```
For `x=2` the robot is now addtionally malfunctioning which activates the random selection rule. 
```
plingo examples/plog/moving_robot.plp --frontend=plog --all -c x=2
```
Now it is uncertain in what room the robot will land and there are three possible worlds with equal probability. 
```
Solving...
Answer: 1
in(1,r0)
Optimization: 109861
Answer: 2
in(1,r1)
Optimization: 109861
Answer: 3
in(1,r2)
Optimization: 109861


Probability of Answer 1: 0.33333
Probability of Answer 2: 0.33333
Probability of Answer 3: 0.33333
```
Finally, `x=3` adds more probabilistic information changing the probability distribution.


### Bayesian squirrel
This is an example used to illustrate the notion of Bayesian learning where you start with a "prior density" on a set of candidate models and update it in light of new observations. We describe here the Bayesian squirrel. The squirrel has hidden its acorns in one of two patches, say Patch 1 and Patch 2, but can’t remember which. The squirrel is 80% certain the food is hidden in Patch 1. Also, it knows there is a 20% chance of finding food per day when it looking in the right patch (and, of course, a 0% probability if it’s looking in the wrong patch).

The squirrel looks for food every day starting with "Day 1" and predict its chances to find the acorns for the next day. For simplicity we have made two extra assumptions in our encoding. 
    1. The squirrel has looked for the acorns in patch `p1` every day since the beginning
    2. She has not found her food in all past days
The instance can be run with the constant `days` that specifies for which day the squirrel wants to predict whether to find the acorns. You can run it with
```
plingo examples/plog/bayesian_squirrel.plp --frontend=plog --all -c days=1
```
With these assumptions it can be seen that the squirrel's initial belief for finding the food in patch `p1` decreases every day.
## References
<a id="1">[1]</a>
M. Gelfond C. Baral and J.N. Rushton (2009).
Probabilistic reasoning with answer sets.
Theory and Practice of Logic Programming, 9(1),57–144.

<a id="2">[2]</a>
J. Lee, Z. Yang (2017).
LPMLN, Weak Constraints and P-log.
Proceedings of the 31st AAAI Conference on Artificial Intelligence, 1170–1177.

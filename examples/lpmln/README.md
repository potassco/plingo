# LP^MLN Examples

This directory contains two examples taken from LP^MLN [[1]](#1) [[3]](#3).


## Instances
### Birds
This example is taken from [[1]](#1). Imagine there are two databases who provide inconsistent information. With LP^MLN this can be resolved. To get all stable models and their probabilities
```
python plingo.py examples/birds.lp --all
```
or if additional evidence should be provided
```
python plingo.py examples/birds.lp --evid=examples/birds_evid.lp --all
```
The translation of the birds example to the plingo language can be found in file `birds_plingo.lp`.

### Firing Squad
This example is originally from Pearl's causal model [[2]](#2) and shows counterfactual reasoning. The LP^MLN encoding stems from [[3]](#3). There are two rifleman A and B. Either one of them shooting causes the prisoner's death (D). The court orders the execution (U) with probability 0.7 which in turn causes the Captain to give the order to shoot (C). Further, rifleman A is nervous (W) with probability 0.2. The nervousness causes him to shoot as well. We are looking to answer the query "Given that the prisoner is dead, what is the probability that the prisoner would be alive if Rifleman A had not shot?". 
With the command
```
python plingo.py examples/firing_squad.lp --evid=examples/firing_squad_evid.lp --q ds
```
we obtain `ds: 0.92105`, which means there is a 8% chance that the prisoner would be alive.
## References
<a id="1">[1]</a>
J. Lee and Y. Wang (2016).
Weighted Rules under the Stable Model Semantics.
Proceedings of the 15th International Conference on Principles of Knowledge Representation and Reasoning, 145-154.

<a id="2">[2]</a>
J. Pearl (2000).
Causality: Models, Reasoning and Inference.
Volume 29.

<a id="3">[3]</a>
J. Lee, S. Talsania, and Y. Wang (2017).
Computing LPMLN Using ASP and MLN Solvers.
Journal of Theory and Practice of Logic Programming, 17(5-6), 942-960.

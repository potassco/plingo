# Plingo
A probabilistic extension for clingo based on LP^MLN.

## Introduction
LPMLN is a probabilistic logic language that provides a simple way to add weights to ASP-style rules. This not only make it possible to reason with uncertainty but also to resolve inconsistencies in the rules. In that way meaningful information can be extracted from a program even if there are two or more contradicting rules.
Further the Maximum a posteriori (MAP) estimate, the most probable stable model, can be inferred from a program using LPMLN.


## Installation

- Clone the repository

```
git clone https://github.com/nrueh/plingo.git
```

- Move to the repository

```
cd plingo
```

- Install project and requirements with pip. 
  
```
pip install .
```


## Usage

`plingo` is an extension of [clingo](https://potassco.org/clingo/), therefore it counts with all of clingo's functionality with new options.

Run the following command and look at `plingo`'s options under Plingo Options:

```
plingo -h
```

#### MAP estimate

```
plingo examples/lpmln/birds.lp
```
```
plingo version 1.0
Reading from examples/birds.lp
Solving...
Answer: 1

Optimization: 300000
Answer: 2
residentBird(jo) bird(jo)
Optimization: 100000
OPTIMUM FOUND

Models       : 2
  Optimum    : yes
Optimization : 100000
Calls        : 1
Time         : 0.005s (Solving: 0.00s 1st Model: 0.00s Unsat: 0.00s)
CPU Time     : 0.005s
```
#### Marginal probabilities
To list all stable models, add the flag `--all`. 

```
plingo examples/lpmln/birds.lp --all
```
```
plingo version 1.0
Reading from examples/birds.lp
Solving...
Answer: 1

Optimization: 300000
Answer: 2
residentBird(jo) bird(jo)
Optimization: 100000
Answer: 3
migratoryBird(jo) bird(jo)
Optimization: 200000


Probability of Answer 1: 0.09003
Probability of Answer 2: 0.66524
Probability of Answer 3: 0.24473


OPTIMUM FOUND

Models       : 3
  Optimum    : yes
Calls        : 1
Time         : 0.006s (Solving: 0.00s 1st Model: 0.00s Unsat: 0.00s)
CPU Time     : 0.006s
```

## Input
Syntactically, LPMLN differs between "soft" rules and "hard" rules, where "soft" rules have a (real number) weight and "hard" rules the weight "alpha". 

Weights can be added by the theory atom `&weight/1` to the body of a rule. The argument has to be an integer or a string containing a float or an expression like `2/3`. For example
```
a(X) :- b(X), &weight(5).
b(X) :- &weight("-2/3").
```
Further it is possible to use the theory atoms `&log/1` or `&problog/1` which only accept strings as arguments. The atom `&log/1` uses the natural logarithm `log(p)` of its argument `p` as weight. The atom `&problog/1` uses the natural logarithm of `p/(1-p)` as its weight.
Rules that do not have any weight in the body are assumed to be hard rules.

To compute LPMLN programs, a rule in an LPMLN program is converted to ASP with weak constraints

By default, only soft rules are converted. To convert hard rules as well, the `--hr` flag can be added on the command line. This option essentially makes hard rules optional, whereas in the default setting all hard rules have to be satisfied as usually in ASP.

## Examples
A number of examples can be found in the directory `examples`. There are also two sub-directories containing examples from the other probabilistic logic languages ProbLog and P-log.

## Commandline options
- `--all`

    Enumerates all stable models and prints their probabilities.

- `--evid=file`

    Provides an evidence file to the program (`.lp` file with clingo syntax rules)

- `--hr`

    Converts hard rules as well. Useful for debugging or resolving inconsistencies in the program.

- `--plog`

    Necessary when calculating P-log programs.

- `--query='atom'`

    Adds a query atom `atom`, e.g. using the example from above `--query='bird(jo)'`. The argument has to be inside single quotation marks (otherwise the command-line might not be able to parse it correctly).

- `--two-solve-calls`

    Uses two solve calls: The first one finds the minimal bound for weak constraints priorities higher than 0. The second one solves for probabilistic stable models of LP^MLN.

- `--unsat`

    Uses the conversion with `unsat` atoms


### Approximation algorithm
For large problems it is infeasible to determine all stable models. 
Plingo offers an option to determine approximate probabilities using
answer set enumeration by optimality (ASEO) [[1]](#1).

For approximation of probabilistic queries it is recommended to use the `--opt-enum` option together with `--balanced=N`.

- `--opt-enum`

    Enumerates stable models by optimality. 
    This can be used for approximating probabilities and queries.
    Recommended to use along with -q1 to suppress printing of intermediate models
    
- `--balanced=N`

    Approximates a query in a balanced way, i.e. it will determine N stable models containing the query, and N stable models *not* containing the query. This overwrites clingo's `--models` option. Works only for a single ground query atom!
- `--use-backend`

    Adds constraints for query approximation in backend instead of using assumptions.

## References
<a id="1">[1]</a>
J. Pajunen and T. Janhunen. (2021).
Solution Enumeration by Optimality in Answer Set Programming.
Theory and Practice of Logic Programming, 21(6), 750-767.

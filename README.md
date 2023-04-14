# Plingo

A system for **probabilistic reasoning in clingo**.

The system is based on LP^MLN, and provides **front-ends** for different probabilistic logic languages:
- *lpmln* [[1]](#1)
- *p-log* [[2]](#2)
- *problog* [[3]](#3).

While the basic **syntax** of *plingo* is the same as the one of *clingo*, its **semantics** relies on re-interpreting the cost of a stable model at priority level `0` as a measure of its probability.

Solving exploits the relation between most probable stable models and optimal stable models [[4]](#4); it relies on *clingo*'s optimization and enumeration modes, as well as an **approximation method** based on answer set enumeration in the order of optimality [[5]](#5).

The *plingo* system can be used to solve two **reasoning tasks**:
- MPE inference: find a most probable explanation (stable model)
- Marginal inference: find all stable models and their probabilities

A number of **examples** can be found [here](https://github.com/potassco/plingo/tree/main/examples). There are also sub-directories containing examples using our front-ends for the other probabilistic logic languages.

## Installation

#### With coda

```
conda install -c potassco plingo
```

#### With pip

```
pip install plingo
```

#### From source

```
git clone https://github.com/potassco/plingo.git
cd plingo
pip install .
```


## Usage

`plingo` is an extension of clingo, therefore it counts with all of clingo's functionality with new options.

Run the following command and look at `plingo`'s latest options under Plingo Options:

```
plingo -h
```

#### Command line options


- `--all`

    Enumerates all stable models and prints their probabilities.

- `--evid=file`

    Provides an evidence file to the program (`.lp` file with clingo syntax rules)

- `--frontend=mode`

    Specifies which frontend to use (`lpmln`, `lpmln-alt`, `problog`, `plog`).
    Mode `lpmln-alt` is the alternative definition where hard rules have to be satisfied.
    When using mode `lpmln` hard rules are also translated which can be useful for debugging or resolving inconsistencies in the program.

- `--problog=output'`

    Uses reificiation to translate a plingo program to a program which be can be given as input to the ProbLog system.
    The ProbLog program is saved under the path given in `output`.
    The input can also be given in any of the frontends (`lpmln`, `lpmln-alt`, `problog`, `plog`).


- `--query='atom'`

    Adds a query atom `atom`, e.g. using the example from above `--query='bird(jo)'`. The argument has to be inside single quotation marks (otherwise the command-line might not be able to parse it correctly).

- `--two-solve-calls`

    Uses two solve calls: The first one finds the minimal bound for weak constraints priorities higher than 0. The second one solves for probabilistic stable models of LP^MLN.

- `--unsat`

    Uses the conversion with `unsat` atoms

#### Examples

##### MPE


Find a most probable stable model


```
plingo examples/lpmln/birds.plp --frontend lpmln-alt
```
```
plingo version 1.1.0
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

##### Marginal probabilities

To list all stable models, add the flag `--all`.

```
plingo examples/lpmln/birds.plp --all --frontend lpmln-alt
```
```
plingo version 1.1.0
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

#### Approximation algorithm
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

#### Using ProbLog as a solver
With the `--problog` option it is possible to translate a plingo program to a problog program
which can be solved by the ProbLog system (https://github.com/ML-KULeuven/problog).
This can also be combined with using any of the frontends.
The input file needs to contain at least one query when using marginal inference.
```
plingo examples/lpmln/birds.plp examples/lpmln/birds_query.plp --frontend=lpmln-alt --problog=problog.lp >/dev/null; problog problog.lp
```
```
show(residentBird(jo)): 0.66524095
```


## Input Language
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


## References
<a id="1">[1]</a>
J. Lee and Y. Wang. (2016).
Weighted Rules under the Stable Model Semantics


<a id="2">[2]</a>
C. Baral and M. Gelfond and J.N. Rushton. (2009),
Probabilistic Reasoning with Answer Sets

<a id="3">[3]</a>
L. De Raedt and A. Kimmig and H. Toivonen
ProbLog: A Probabilistic Prolog and its Applications in Link Discovery

<a id="4">[4]</a>
J. Lee and Z. Yang (2017).
LPMLN, Weak Constraints and P-log

<a id="5">[5]</a>
J. Pajunen and T. Janhunen. (2021).
Solution Enumeration by Optimality in Answer Set Programming.
Theory and Practice of Logic Programming, 21(6), 750-767.




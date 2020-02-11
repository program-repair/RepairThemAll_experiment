# RepairThemAll Experiment

This repository contains the raw results of the execution of 11 repair tools on 5 bug benchmarks presented in the following paper:

```bibtex
@inproceedings{RepairThemAll2019,
  author    = {Thomas Durieux and Fernanda Madeiral and Matias Martinez and Rui Abreu},
  title     = {{Empirical Review of Java Program Repair Tools: A Large-Scale Experiment on 2,141 Bugs and 23,551 Repair Attempts}},
  booktitle = {Proceedings of the 27th ACM Joint European Software Engineering Conference and Symposium on the Foundations of Software Engineering (ESEC/FSE '19)},
  year      = {2019},
  url       = {https://arxiv.org/abs/1905.11973}
}
```

Benchmark:

* Bears
* Bugs.jar
* [Defects4J version 1.4.0](https://github.com/rjust/defects4j/tree/v1.4.0)
* IntroClassJava
* QuixBugs

The execution framework that has been used is available at: https://github.com/program-repair/RepairThemAll

## Repository Structure

The repository is structured as follow:

```
├── docs: content for the website
├── results: 
│   └── <benchmark>
│       └── <project>
│           └── <bug_id>
│               └── <repair tool>
│                   └── <seed>
│                       ├── grid5k.stderr.log: stderr of the execution
│                       ├── grid5k.stdout.log: stdout of the execution (without the repair)
│                       ├── repair.log: repair log
│                       ├── result.json: standardize output 
│                       └── detailed-result.json: raw output of the repair tool, if it generates a json file
└── script
    └── get_patched_bugs.py: the script that are used to generate the table for the paper
```


## Patched Bugs

The data of this repository is also available as a website: http://program-repair.org/RepairThemAll_experiment

| Repair Tools | Bears   | Bugs.jar  | Defects4J | IntroClassJava | QuixBugs | Total    |
| ------------ | -------:| ---------:| ---------:| --------------:| --------:| --------:|
| ARJA         | 12 (4%) | 21 (1%)   | 86 (21%)  | 23 (7%)        | 4 (10%)  | 146 (6%) |
| GenProg-A    | 1 (0%)  | 9 (0%)    | 45 (11%)  | 18 (6%)        | 4 (10%)  | 77 (3%)  |
| Kali-A       | 15 (5%) | 24 (2%)   | 72 (18%)  | 5 (1%)         | 2 (5%)   | 118 (5%) |
| RSRepair-A   | 1 (0%)  | 6 (0%)    | 62 (15%)  | 22 (7%)        | 4 (10%)  | 95 (4%)  |
| Cardumen     | 13 (5%) | 12 (1%)   | 17 (4%)   | 0 (0%)         | 4 (10%)  | 46 (2%)  |
| jGenProg     | 13 (5%) | 14 (1%)   | 31 (7%)   | 4 (1%)         | 3 (7%)   | 65 (3%)  |
| jKali        | 10 (3%) | 8 (0%)    | 27 (6%)   | 5 (1%)         | 2 (5%)   | 52 (2%)  |
| jMutRepair   | 7 (2%)  | 11 (0%)   | 20 (5%)   | 24 (8%)        | 3 (7%)   | 65 (3%)  |
| Nopol        | 1 (0%)  | 72 (6%)   | 107 (27%) | 32 (10%)       | 1 (2%)   | 213 (9%) |
| DynaMoth     | 0 (0%)  | 124 (10%) | 74 (18%)  | 6 (2%)         | 2 (5%)   | 206 (9%) |
| NPEFix       | 1 (0%)  | 3 (0%)    | 9 (2%)    | 0 (0%)         | 2 (5%)   | 15 (0%)  |
| Total        | 74      | 304       | 550       | 139            | 31       | 1,098    |
| Total unique | 25 (9%) | 175 (15%) | 185 (46%) | 62 (20%)       | 12 (30%) | 459 (21%)|

Total generated patch: 67,211

Execution time 314 days, 12:29:19.419491 

## Chi-square Test of independence

|                | # Patched | # Non-Patched |
| -------------- | --------- | ------------- |
| ARJA on Defects4J  | 86 | 309 |
| ARJA on Others  | 60 | 1686 |

Chi2 value= 170.43487132271886 p-value= 5.945480330471514e-39 Degrees of freedom= 1

|                | # Patched | # Non-Patched |
| -------------- | --------- | ------------- |
| GenProg-A on Defects4J  | 45 | 350 |
| GenProg-A on Others  | 32 | 1714 |

Chi2 value= 84.90652479289551 p-value= 3.128091736130167e-20 Degrees of freedom= 1

|                | # Patched | # Non-Patched |
| -------------- | --------- | ------------- |
| Kali-A on Defects4J  | 72 | 323 |
| Kali-A on Others  | 46 | 1700 |

Chi2 value= 150.4020168750391 p-value= 1.4160845009256217e-34 Degrees of freedom= 1

|                | # Patched | # Non-Patched |
| -------------- | --------- | ------------- |
| RSRepair-A on Defects4J  | 62 | 333 |
| RSRepair-A on Others  | 33 | 1713 |

Chi2 value= 144.80217516680622 p-value= 2.372523759882535e-33 Degrees of freedom= 1

|                | # Patched | # Non-Patched |
| -------------- | --------- | ------------- |
| Cardumen on Defects4J  | 17 | 378 |
| Cardumen on Others  | 29 | 1717 |

Chi2 value= 10.701973234378928 p-value= 0.0010702132907778191 Degrees of freedom= 1

|                | # Patched | # Non-Patched |
| -------------- | --------- | ------------- |
| jGenProg on Defects4J  | 31 | 364 |
| jGenProg on Others  | 34 | 1712 |

Chi2 value= 38.10114926497659 p-value= 6.717055566199569e-10 Degrees of freedom= 1

|                | # Patched | # Non-Patched |
| -------------- | --------- | ------------- |
| jKali on Defects4J  | 27 | 368 |
| jKali on Others  | 25 | 1721 |

Chi2 value= 39.69012031778793 p-value= 2.976273080413384e-10 Degrees of freedom= 1

|                | # Patched | # Non-Patched |
| -------------- | --------- | ------------- |
| jMutRepair on Defects4J  | 20 | 375 |
| jMutRepair on Others  | 45 | 1701 |

Chi2 value= 6.76253623850222 p-value= 0.009309135821381086 Degrees of freedom= 1

|                | # Patched | # Non-Patched |
| -------------- | --------- | ------------- |
| Nopol on Defects4J  | 107 | 288 |
| Nopol on Others  | 106 | 1640 |

Chi2 value= 158.83167769741897 p-value= 2.036659201530019e-36 Degrees of freedom= 1

|                | # Patched | # Non-Patched |
| -------------- | --------- | ------------- |
| DynaMoth on Defects4J  | 74 | 321 |
| DynaMoth on Others  | 132 | 1614 |

Chi2 value= 46.25197019724452 p-value= 1.0398193445599021e-11 Degrees of freedom= 1

|                | # Patched | # Non-Patched |
| -------------- | --------- | ------------- |
| NPEFix on Defects4J  | 9 | 386 |
| NPEFix on Others  | 6 | 1740 |

Chi2 value= 17.333764012540335 p-value= 3.1356574417361234e-05 Degrees of freedom= 1


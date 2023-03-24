# bics-bsp-s1-2022-vogel-benjamin-source-files

## repository content
This repository contains the source code for my BSP-S1 project as well as a reqirements.txt document containing the libraries installed during the production process of the software. 
Furthermore you can find the source code to my report LaTeX file for my BSP-S1

## Code execution
First make sure your version of python is 3.10.7.
Then check that you have the pygame library (version 2.1.2) downlaoded.

There are two ways of executing this file:
### Execute file
Download the python file and execute it

### Execute code in a interpreter (Recommended)
Download the python source code and open it in a code interpreter.

#### In case of an error:
After making sure that the python version in use is identical to the version it was produced in. (3.10.7)
Please view the requirements.txt file. Please download the file and input "pip install -r requirements.txt". This should make sure that your python environment is identical to the one this software was produced in.

```mermaid
  classDiagram
    PokeDeck *-- Predicate
    Predicate <|-- hp
    Predicate <|-- name
    Predicate <|-- subtype
    Predicate <|-- and
    Predicate <|-- or
    Predicate <|-- not
    Predicate +test()
    class hp{

    }
    class name{

    }
    class subtype{

    }
```

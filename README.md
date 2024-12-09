# Optimizing Job Shop Scheduling in a Manufacturing Plant using Genetic Algorithm

## Overview

This project involves developing a genetic algorithm to optimize job shop scheduling in a manufacturing plant setting. The goal is to determine the optimal sequence and timing for each product to minimize the overall production time or maximize throughput while considering machine capacities and job dependencies.

## Project Details

### Requirements

- **Implementation**: A system for job shop scheduling using a genetic algorithm implemented in Python.
- **Input**: A list of jobs and the number of available machines. Each job is defined as a sequence of operations, where each operation specifies a machine and the required processing time. The sequence of operations for a given task must be performed in order.
  - Example Input:
    ```
    Job_1: M1[10] -> M2[5] -> M4[12]
    Job_2: M2[7] -> M3[15] -> M1[8]
    ```
    - Job_1 starts at machine M1 and requires 10 time units for the first phase, 5 time units at M2, and 12 time units at M4.
    - Job_2 starts at M2, needs 7 time units, then 15 time units at M3, and 8 time units at M1.

### Output

- A schedule for each machine that depicts the start and end time for each process and to which job it belongs.
- Visualization using Gantt Charts.

## Authors
Kareem Qutob
Diaa Badaha

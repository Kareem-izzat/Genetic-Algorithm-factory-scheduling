import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from collections import deque
import random
import itertools
import numpy as np
import copy
import matplotlib.animation as animation


# Interface Class
class JobShopSchedulerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Job Shop Scheduler")

        self.num_jobs_label = ttk.Label(root, text="Number of Jobs:")
        self.num_jobs_label.grid(row=0, column=0, padx=5, pady=5)
        self.num_jobs_entry = ttk.Entry(root)
        self.num_jobs_entry.grid(row=0, column=1, padx=5, pady=5)

        self.num_machines_label = ttk.Label(root, text="Number of Machines:")
        self.num_machines_label.grid(row=1, column=0, padx=5, pady=5)
        self.num_machines_entry = ttk.Entry(root)
        self.num_machines_entry.grid(row=1, column=1, padx=5, pady=5)

        self.generate_button = ttk.Button(root, text="Generate", command=self.generate_fields)
        self.generate_button.grid(row=2, column=0, columnspan=2, pady=10)

        self.job_frames = []

    def generate_fields(self):
        num_jobs = int(self.num_jobs_entry.get())
        num_machines = int(self.num_machines_entry.get())

        for frame in self.job_frames:
            frame.destroy()

        self.job_frames = []

        # Calculate the number of columns needed
        num_columns = (num_jobs // 6) + (1 if num_jobs % 6 != 0 else 0)

        for job_idx in range(num_jobs):
            col_idx = job_idx // 6
            row_idx = 3 + (job_idx % 6)

            job_frame = ttk.LabelFrame(self.root, text=f"Job {job_idx + 1}")
            job_frame.grid(row=row_idx, column=col_idx * 2, columnspan=2, padx=5, pady=5, sticky="ew")

            job_sequence_label = ttk.Label(job_frame, text="Sequence (M#[Time] -> M#[Time] -> ...):")
            job_sequence_label.grid(row=0, column=0, padx=5, pady=5)

            job_sequence_entry = ttk.Entry(job_frame)
            job_sequence_entry.grid(row=0, column=1, padx=5, pady=5)

            self.job_frames.append((job_frame, job_sequence_entry))

        # Position the submit button based on the number of columns and jobs
        self.submit_button = ttk.Button(self.root, text="Submit", command=self.collect_input)
        last_col_idx = (num_jobs - 1) // 6
        last_row_idx = 3 + ((num_jobs - 1) % 6) + 1
        self.submit_button.grid(row=last_row_idx, column=last_col_idx * 2, columnspan=2, pady=10)

    def collect_input(self):
        self.num_jobs = int(self.num_jobs_entry.get())
        self.num_machines = int(self.num_machines_entry.get())

        self.jobs = []
        self.timeMachines = []  # Initialize the timeMachines matrix
        self.availableMachines = [True] * self.num_machines  # Initialize the availableMachines array

        for job_frame, job_sequence_entry in self.job_frames:
            sequence = job_sequence_entry.get()
            job_operations = []
            time_operations = []
            for op in sequence.split('->'):
                machine, time = op.strip().split('[')
                time = time.rstrip(']')
                machine = int(machine[1:])  # Convert machine identifier to integer
                time = int(time)
                job_operations.append((machine, time))
                time_operations.append(time)
            self.jobs.append(job_operations)
            self.timeMachines.append(time_operations)  # Append the times for each machine in this job

        print(f"Number of Jobs: {self.num_jobs}")
        print(f"Number of Machines: {self.num_machines}")
        print("Jobs:")
        for job_id, job in enumerate(self.jobs, start=1):
            print(f"  Job {job_id}: {job}")

        messagebox.showinfo("Info", "Input collected successfully! Check the console output.")

# Returns initial population size, factor is selected to be 10
def populationSize(operationNumber, factor):
    return max(50, min(250, operationNumber * factor))

# Returns number of operations in all jobs 
def operationsNumber(jobsArray):
    numofOperations = 0
    for job in jobsArray:
        numofOperations = numofOperations + len(job)
    return numofOperations

# Takes 2 chromosomes and makes a reproduction randomly between them to get 2 new offsprings
def crossover(chromosome1, chromosome2):
    crossPoint = random.randint(1, len(chromosome1) - 1)
    crossChromosome1 = chromosome1[:]
    crossChromosome2 = chromosome2[:]
    crossChromosome1[crossPoint:], crossChromosome2[crossPoint:] = \
        crossChromosome2[crossPoint:], crossChromosome1[crossPoint:]

    return crossChromosome1, crossChromosome2

# Turns job array into machine array (each row represents a machine)
def machineArray(jobsArray, numOfMachines):
    # Initialize the machines array with empty lists
    machines = [[] for _ in range(numOfMachines)]

    # Iterate through each job and its operations
    for index, joblist in enumerate(jobsArray):
        for index2, job in enumerate(joblist):
            machineNumber = job[0] - 1  # Convert machine number to 0-based index
            if machineNumber < numOfMachines:
                jibTuple = (index + 1, index2 + 1)
                machines[job[0] - 1].append(jibTuple)
            else:
                raise ValueError(f"Machine number {job[0]} exceeds the number of machines specified.")

    return machines

# Function to organize jobs by machine
def generateChromosome(machineArray, numOfMachines):
    chromosome = [[] for _ in range(numOfMachines)]
    for index, jobArray in enumerate(machineArray):
        jobCopy = jobArray[:]
        random.shuffle(jobCopy)
        chromosome[index] = jobCopy

    return chromosome

# For problem size more than 6
def generatePopulationForLargeJobs(machineArray, populationSize, numOfMachines):
    population = [[] for _ in range(populationSize)]
    for i in range(populationSize):
        population[i] = generateChromosome(machineArray, numOfMachines)
    return population

# For problem size equals or less than 6
def generatePopulationForSmallJobs(machineArray):  # we will use this when the operations number are low
    population = []
    for machine in machineArray:
        jopPermuation = list(
            itertools.permutations(machine))  # this will make every permutation for every machine in the chromosme
        population.append(jopPermuation)  # append it to the popualtion
        # to combine permutation in all machines
    population = list(itertools.product(*population))
    population = [[list(job_sequence) for job_sequence in chromosome] for chromosome in population]

    return population  # this will be an array of all the possible chromosomes

# Do a mutation on a random chromosome
def mutateChromosome(chromosome):  # we will choose a random machine in chromosome and swap 2 random tuples in it
    machine = random.choice(chromosome)
    if len(machine) > 1:  # if only one job in machine we cant swap anything
        operation1, operation2 = random.sample(range(len(machine)), 2)  # choose 2 random index
        temp = machine[operation1]  # swapping
        machine[operation1] = machine[operation2]
        machine[operation2] = temp

    return chromosome

# This function prints the Gantt Chart on the terminal - used for testing 
def printTextGanttChart(gantt_data):
    print("\nGantt Chart:")
    for machine, tasks in gantt_data.items():
        print(f"Machine {machine + 1}: ", end="")
        for task in tasks:
            jobID, startTime, endTime = task
            print(f"| Job {jobID} ({startTime}-{endTime}) ", end="")
        print("|")

# Returns the fitness of an sequence of operations for jobs
def exTimeFitness(ScheduledArr):
    max = 0
    if ScheduledArr == []:
        return max
    else:
        for tuple in ScheduledArr:
            if tuple[3] > max:
                max = tuple[3]
    return max

# This Function picks two parents randomly from a set of individuals
def generateParents (population, fitnessScoreArr, ParentsNum):
    Parents = []
    tempPopulation = copy.deepcopy(population)
    counter = 0
    while counter != ParentsNum and len(Parents) < ParentsNum:
        for index, chrome in enumerate(tempPopulation):
            if random.random() < (1-fitnessScoreArr[index]):
                Parents.append(chrome)
                tempPopulation.remove(chrome)
                counter += 1
                break

    return Parents

# This function takes machines and jobs arrays and returns a VALID solution (array of tuples) scheduled
# If there is an invalid solution, the function makes it valid
def Scheduling(machines, jobs):
    MACHINES = copy.deepcopy(machines)  # copy to avoid modifying the original machines array
    CompletedJobs = []
    MachinesTimes = [0 for _ in range(len(machines))]  # Track the end time of the last job on each machine

    while MACHINES:
        jobsDone = 0
        for i in range(len(MACHINES) - 1, -1, -1):  # iterate in reverse order to handle removals safely
            if not MACHINES[i]:
                continue

            jobId, jobOrder = MACHINES[i][0]
            machineId = jobs[jobId - 1][jobOrder - 1][0] - 1

            # Check if this is the first operation of the job
            if jobOrder == 1:
                startTime = MachinesTimes[machineId]
            else:
                prevJobOrder = jobOrder - 1
                prev_machine_id = jobs[jobId - 1][prevJobOrder][0] - 1

                # Find the end time of the previous operation
                prevEndTime = None
                for completedJob in CompletedJobs:
                    if completedJob[:2] == (jobId, prevJobOrder):
                        prevEndTime = completedJob[3]
                        break

                if prevEndTime is None:
                    continue  # Skip if the previous operation is not yet completed

                startTime = max(MachinesTimes[machineId], prevEndTime)

            duration = jobs[jobId - 1][jobOrder - 1][1]
            endTime = startTime + duration

            # Ensure no overlap by adjusting start time if necessary
            if any(
                task[2] < endTime and task[3] > startTime and task[4] == machineId + 1
                for task in CompletedJobs
            ):
                startTime = max(
                    MachinesTimes[machineId],
                    max(task[3] for task in CompletedJobs if task[4] == machineId + 1)
                )
                endTime = startTime + duration

            # Schedule the operation
            completedTuple = (jobId, jobOrder, startTime, endTime, machineId + 1)
            CompletedJobs.append(completedTuple)

            # Update machine times
            MachinesTimes[machineId] = endTime

            # Remove the operation from the queue
            MACHINES[i].pop(0)
            if not MACHINES[i]:
                MACHINES.pop(i)

            jobsDone += 1

        if jobsDone == 0:
            # If no jobs were scheduled, break to avoid an infinite loop
            break

    # Ensure all jobs are scheduled
    for jobId in range(1, len(jobs) + 1):
        for jobOrder in range(1, len(jobs[jobId - 1]) + 1):
            if not any(completedJob[:2] == (jobId, jobOrder) for completedJob in CompletedJobs):
                prevJobOrder = jobOrder - 1
                if prevJobOrder > 0:
                    prevJob = next(job for job in CompletedJobs if job[:2] == (jobId, prevJobOrder))
                    startTime = prevJob[3]
                else:
                    startTime = 0

                machineId = jobs[jobId - 1][jobOrder - 1][0] - 1
                duration = jobs[jobId - 1][jobOrder - 1][1]
                endTime = startTime + duration

                # Ensure no overlap by adjusting start time if necessary
                if any(
                    task[2] < endTime and task[3] > startTime and task[4] == machineId + 1
                    for task in CompletedJobs
                ):
                    startTime = max(
                        MachinesTimes[machineId],
                        max(task[3] for task in CompletedJobs if task[4] == machineId + 1)
                    )
                    endTime = startTime + duration

                completedTuple = (jobId, jobOrder, startTime, endTime, machineId + 1)
                CompletedJobs.append(completedTuple)
                MachinesTimes[machineId] = endTime

    # Ensure the solution is repaired correctly
    assert len(CompletedJobs) == sum(len(job) for job in jobs), "Not all operations were scheduled!!"

    return CompletedJobs

# This function takes an array of 5-tuples (valid, completed and scheduled jobs) and plots the Gantt Chart for that solution
def plotGanttChart(chromosome):
    if chromosome == []:
        print("empty")
        return
    
    fig, ax = plt.subplots()
    colors = [
        'tab:blue', 'tab:orange', 'tab:green', 'tab:red', 'tab:purple',
        'tab:brown', 'tab:pink', 'tab:gray', 'tab:olive', 'tab:cyan'
    ]

    # Sort tasks by their start times and then by their machine ID
    chromosome.sort(key=lambda x: (x[2], x[4]))

    # Dictionary to track the end time of the last task on each machine
    machineEndTimes = {}

    for task in chromosome:
        jobID, order, startTime, endTime, machineID = task

        # Get the end time of the last task on this machine
        if machineID in machineEndTimes:
            lastEndTime = machineEndTimes[machineID]
        else:
            lastEndTime = 0

        # Adjust the start time if there's an overlap
        if startTime < lastEndTime:
            startTime = lastEndTime
            endTime = startTime + (endTime - startTime)

        # Update the machine end time
        machineEndTimes[machineID] = endTime

        # Plot the task
        color = colors[(jobID - 1) % len(colors)]
        rect = patches.FancyBboxPatch(
            (startTime, (machineID - 1) * 10),
            endTime - startTime,
            9,
            boxstyle="round,pad=0.1,rounding_size=1",
            facecolor=color,
            edgecolor='black'
        )
        ax.add_patch(rect)
        ax.text(
            startTime + (endTime - startTime) / 2,
            (machineID - 1) * 10 + 4.5,
            f'Job {jobID}',
            ha='center',
            va='center',
            color='white'
        )

    # Determine the overall production time
    overAllProductionTime = max(endTime for _, _, _, endTime, _ in chromosome)

    # Add a vertical line to mark the overall production time
    ax.axvline(overAllProductionTime, color='red', linestyle='--', linewidth=2)
    ax.text(overAllProductionTime, -5, f'Overall Production Time: {overAllProductionTime}',
            color='red', ha='right', va='top', fontsize=10)

    ax.set_ylim(-10, len(set(task[4] for task in chromosome)) * 10)
    ax.set_xlim(0, overAllProductionTime + 10) 
    ax.set_xlabel('Time')
    ax.set_ylabel('Machines')
    ax.set_yticks([i * 10 + 4.5 for i in range(len(set(task[4] for task in chromosome)))])
    ax.set_yticklabels([f'Machine {i+1}' for i in range(len(set(task[4] for task in chromosome)))])
    ax.grid(True, which='major', axis='x', linestyle='-', color='lightgray')  
    ax.set_title('Gantt Chart of the Final Solution')
    plt.show()

# Genetic Algorithm Function
def GA(jobsArray, machinesArr, numOfMachines, factor):

    # Initial Population Generation
    opNum = operationsNumber(jobsArray)
    print("Operations Number: ", opNum)
    if opNum > 6:
        popSize = populationSize(opNum, factor)
        population = generatePopulationForLargeJobs(machinesArr, popSize, numOfMachines)
    else:
        population = generatePopulationForSmallJobs(machinesArr)

    # GA Parameters
    TotalIterations = numOfMachines * 20  # This is the termination criterion
    numOfParents = 2
    mutationRate = 0.1
    maxAttempts = 50

    # Initial Generation
    Generation = population
    scheduledArr = []
    attempts = 0

    while True:
        attempts += 1
        gen = copy.deepcopy(Generation)
        for chrome in gen:
            schedule = Scheduling(chrome, jobsArray)
            if schedule:
                scheduledArr.append(schedule)
            else:
                Generation.remove(chrome) # Remove invalid

        if len(Generation) >= 2 or attempts > maxAttempts:
            break

    print(f"Initial scheduled solutions: {len(scheduledArr)}")
    FitnessArr = [exTimeFitness(solution) for solution in scheduledArr]
    fitnessScoreArr = [fitness / sum(FitnessArr) for fitness in FitnessArr]

    for iteration in range(TotalIterations):
        parents = generateParents(Generation, fitnessScoreArr, numOfParents)
        if len(parents) < 2:
            print(f"Skipping iteration {iteration} due to insufficient parents.")
            continue

        # Crossover and Mutation
        offspring1, offspring2 = crossover(parents[0], parents[1])
        if random.random() < mutationRate:
            mutateChromosome(offspring1)
        if random.random() < mutationRate:
            mutateChromosome(offspring2)

        # Scheduling and Fitness Calculation
        schedule1 = Scheduling(offspring1, jobsArray)
        schedule2 = Scheduling(offspring2, jobsArray)
        
        if schedule1:
            Generation.append(offspring1)
            scheduledArr.append(schedule1)
            FitnessArr.append(exTimeFitness(schedule1))
        if schedule2:
            Generation.append(offspring2)
            scheduledArr.append(schedule2)
            FitnessArr.append(exTimeFitness(schedule2))

        # Update Fitness Scores
        sumFitness = sum(FitnessArr)
        fitnessScoreArr = [fitness / sumFitness for fitness in FitnessArr]

        fitnessesAvgs = []

        print(f"Iteration {iteration+1}/{TotalIterations}: Best fitness = {min(FitnessArr)}")
        averageFitness = sum(FitnessArr) / len(FitnessArr)
        fitnessesAvgs.append(averageFitness)
        print(f"Iteration {iteration+1}/{TotalIterations}: Average fitness = {averageFitness}")

        # Early Termination Condition
        if len(set(FitnessArr)) == 1:
            print("Early convergence detected. Terminating.")
            break

    # Select Best Chromosome
    minScore = min(FitnessArr)
    minIndex = FitnessArr.index(minScore)
    bestChromosome = Generation[minIndex]

    print(f"Best fitness: {minScore}")
    plotGanttChart(scheduledArr[minIndex])

# Main function
def main():
    root = tk.Tk()
    app = JobShopSchedulerApp(root)
    root.mainloop()

    if hasattr(app, 'jobs'):
        machinesNumber = app.num_machines
        jobsArray = app.jobs
        jobNumber = app.num_jobs
        # Generate the machine array based on jobs input
        machines = machineArray(jobsArray, machinesNumber)
        print(machines)

        factor = 10

        GA(jobsArray, machines, machinesNumber, factor)

if __name__ == "__main__":
    main()
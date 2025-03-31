# Workshop: Coding and HPC Basics

## Summary
This workshop will cover the essentials of getting started with coding for research and software development, along with best practices. We will briefly discuss the local installation of R and Python before shifting our focus to high-performance computing and utilizing cluster-based resources on Koa. Through practical examples, we’ll explore fundamental coding concepts, including data structures, loading large datasets, efficient loops and multiprocessing, operationalizing code, and best practices for debugging and documentation—highlighting the role of AI in streamlining these processes. Additionally, we’ll cover key Python and R packages and how to manage environments across projects. We'll conclude with an overview of running scripts in the background and managing batch jobs on the cluster. We are going to move quickly, so I will provide resources to apply these concepts and continue learning beyond the workshop. 


## Local Installation Guide

### __Installing R and RStudio__
___
- Visit the [Cran R Project website](https://ftp.osuosl.org/pub/cran/) and download the latest version for your operating system.
- Go to the [Posit website](https://posit.co/downloads/) and download the free version of RStudio Desktop.

### Installing Anaconda and Python via Anaconda Navigator
___
- Go to the [Anaconda website](https://www.anaconda.com/download/success) and download the installer for your operating system.
  - Install Anaconda following the prompts. 

## Cluster Basics
[Koa](https://uhawaii.atlassian.net/wiki/spaces/HPC/pages/429752517/Koa), the high-performance computing (HPC) cluster at UH, is availble to all faculty, staff, and students upon completion of an onboarding session (details for which can be found [here](https://datascience.hawaii.edu/hpc/)). For those attending these workshops in person that do not already have an account, all modifications made to your Koa account during the workshop will persist; however, you will have to attend one of the bi-monthly onboarding sessions to gain permanent access to the cluster. I provide a high level overview of the resources on Koa, job scheduling, and linux CLI in this GitHub. More information on each topic can be found at the links below: 
  - [Koa Documentation](https://uhawaii.atlassian.net/wiki/spaces/HPC/pages/429752517/Koa)
  - [Slurm Quickstart User Guide](https://slurm.schedmd.com/quickstart.html)
  - [Slurm Documentation](https://slurm.schedmd.com/srun.html)
  - [Linux CLI for Beginners](https://ubuntu.com/tutorials/command-line-for-beginners#5-moving-and-manipulating-files)
  - [Mastering the Command Line: Medium Article](https://codestax.medium.com/mastering-the-command-line-a-guide-to-basic-and-intermediate-linux-commands-a990b6d09604)

### __Using Koa__
___
Koa uses **Slurm** (Simple Linux Utility for Resource Management), a job scheduler that manages how users share the cluster’s resources. Instead of running programs directly on the login node (which is only for setting up jobs and managing files), you submit jobs to Slurm, which queues them up and runs them when resources are available.

The eight primary partitions available to all users on Koa are detailed below. I recommend using the shared partition for interactive jobs whenever possible and a mix of the kill-shared and shared partitions for batch jobs.

Keep in mind that the kill-shared partition may allocate resources more quickly, as it includes nodes that are personally owned by users on the cluster. However, jobs in this partition are subject to preemption—if the owner of a node needs their compute resources, your job will be canceled and will reenter the queue. For some applications, this is not an issue, as long as you design your scripts with this possibility in mind (we will discuss this in greater detail later). However, for applications that require uninterrupted execution, it is best to use the shared partition, which cannot be preempted once allocated.

| Partition Name     | Max running jobs per user | Max pending & running jobs per user | Max wall time | Default memory        | Max nodes per job |
|--------------------|--------------------------|-------------------------------------|--------------|----------------------|------------------|
| exclusive         | no limit                 | no limit                            | 3 days       | all on assigned node(s) | 20               |
| exclusive-long    | 2                        | 5                                   | 7 days       | all on assigned node(s) | 20               |
| gpu              | no limit                 | no limit                            | 3 days       | 512 MB               | 1                |
| kill-exclusive   | no limit                 | no limit                            | 3 days       | all on assigned node(s) | 20               |
| kill-shared      | no limit                 | no limit                            | 3 days       | 512 MB               | 1                |
| sandbox         | 2                        | no limit                            | 4 hours      | 512 MB               | 2                |
| shared          | no limit                 | no limit                            | 3 days       | 512 MB               | 1                |
| shared-long     | 2                        | 5                                   | 7 days       | 512 MB               | 1                |

Koa is a rare and exceptionally powerful resource, so I strongly encourage you to make the best use of it. To support future funding and continued access, be sure to acknowledge Koa in your publications by including the suggested acknowledgment below.
  - The technical support and advanced computing resources from University of Hawaii Information Technology Services – Research Cyberinfrastructure, funded in part by the National Science Foundation CC* awards # 2201428 and # 2232862 are gratefully acknowledged.

### __Open OnDemand (OOD)__
___
There are a number of ways to request compute on Koa; however, the job request you submit will always fall into one of two categories.
  - Interactive Jobs: a job you can interact with to develop, download data, etc...
  - Batch Jobs: a job that is submitted to the cluster via the SLURM workload manager and is automatically run when resources are allocated.
    - Discussed in greater detail below, these jobs will typically make use of a .slurm file and point to a .py or .R file to be run via the command line.

The simplest method to request an interactive job is to use the graphical user interface [Open OnDemand](https://koa.its.hawaii.edu/pun/sys/dashboard). 

![image](https://github.com/user-attachments/assets/5b93b106-ed2b-4f65-8603-5045b2315aa3)

Under the "My Interactive Sessions" tab, you can select whether you would like to request a desktop GUI, Jupyter Lab session, Matlab session, or RStudio Server. 
  - Jupyter Lab and Jupyter Notebook are alternative IDEs to the VS Code setup below. (I prefer the functionality and debugging capabilities of VS Code but feel free to try them both and see which you prefer!) 

![image](https://github.com/user-attachments/assets/d483ad88-b0bf-428a-a608-c6eb8145e921)

After selecting the appropriate server/desktop, fill out the form to request your desired resources. 

![image](https://github.com/user-attachments/assets/14be8457-c037-4ace-a332-27e9f6a8ae9a)

### __Batch Jobs__
___
Batch jobs are an essential tool for efficiently leveraging the cluster resources on Koa. Below are a few example SLURM scripts demonstrating varying degrees of complexity. Feel free to adapt these scripts to suit your specific needs.

- This script batches two jobs to run Generate_Monthly_Data_1.py and Generate_Monthly_Data_2.py. It uses the SLURM array to determine which Python file is executed. The script is configured for logging, job parameters (such as memory and CPU allocation), and activates the appropriate Conda environment before executing the Python scripts.
  
```bash
#!/bin/sh

## reporting
#SBATCH --open-mode=append
# enable logging to a log directory to print intermediate output and any potential errors that occur 
#SBATCH --error=logs/%A_%a.err 
#SBATCH --output=logs/%A_%a.out
# change the following lines to have one pound sign instead of two
# if you want to receive notices about jobs
##SBATCH --mail-type=BEGIN,END,FAIL,REQUEUE,TIME_LIMIT_80
##SBATCH --mail-user=username@hawaii.edu

#SBATCH --cpus-per-task=1
#SBATCH --mem=512G


#SBATCH --job-name=cm_delta
#SBATCH --partition=shared,kill-shared
#SBATCH --time 24:00:00
#SBATCH --array=1-2

cd
module load lang/Anaconda3
module load lang/Python
source activate cm_data
cd
cd /home/ehartley/Climate_Models/Process_Raw_Data/


echo ============================================================
echo Building State-Month Data
echo ============================================================

python Generate_Monthly_Data_${SLURM_ARRAY_TASK_ID}.py
```

- This script batches jobs that run Generate_Annual_Data.py for a range of years (from 2015 to 2100) and multiple climate scenarios (ssp126, ssp245, ssp370, ssp585). The job array is used to generate a list of year-scenario pairs, which are passed as arguments to the Python script.

```bash
#!/bin/sh

## reporting
#SBATCH --open-mode=append
# enable logging to a log directory to print intermediate output and any potential errors that occur 
#SBATCH --error=logs/%A_%a.err 
#SBATCH --output=logs/%A_%a.out
# change the following lines to have one pound sign instead of two
# if you want to receive notices about jobs
##SBATCH --mail-type=BEGIN,END,FAIL,REQUEUE,TIME_LIMIT_80
##SBATCH --mail-user=username@hawaii.edu

#SBATCH --cpus-per-task=12
#SBATCH --mem=768G
#SBATCH --job-name=cm_delta
#SBATCH --partition=kill-shared
#SBATCH --time 02:00:00
#SBATCH --array=0-343

# Define years and scenarios
YEARS=({2015..2100})
SCENARIOS=(ssp126 ssp245 ssp370 ssp585)

# Create a flattened list of all (year, scenario) pairs
ARG_LIST=()
for YEAR in "${YEARS[@]}"; do
    for SCENARIO in "${SCENARIOS[@]}"; do
        ARG_LIST+=("${YEAR} ${SCENARIO}")
    done
done

# Extract year and scenario for this job
ARGS=(${ARG_LIST[${SLURM_ARRAY_TASK_ID}]} )
YEAR=${ARGS[0]}
SCENARIO=${ARGS[1]}

# Activate Conda Environment
module load lang/Anaconda3
module load lang/Python
source activate cm_data

# Move to the script directory
cd /home/ehartley/Climate_Models/Process_Raw_Data/

# Logging output
echo ============================================================
echo Running Climate Model: Year=${YEAR}, Scenario=${SCENARIO}
echo ============================================================

# Run Python script
python Generate_Annual_Data.py ${YEAR} ${SCENARIO}

```

- If you instead wanted to use R, the only modification to the process of batching jobs would be to run your `.R` file in the command line.
```bash
module load lang/R

# Move to the script directory
cd /home/ehartley/Climate_Models/Process_Raw_Data/

# Logging output
echo ============================================================
echo Running Climate Model: Year=${YEAR}, Scenario=${SCENARIO}
echo ============================================================

# Run Python script
Rscript Generate_Annual_Data.R ${YEAR} ${SCENARIO}
```

Once your `.slurm` file is constructed, you simply need to run the command below.
```bash
sbatch <filename>.slurm
```
See the [slurm documentation](https://slurm.schedmd.com/documentation.html) for further resources on submitting batch jobs. 

![Example](https://img.shields.io/badge/Example:%20Writing%20to%20Allow%20Preemption-indigo?style=for-the-badge)

### __Storage__
___
There are three primary methods of storing data on Koa. 
  - Personal "home" storage: 50 GB
    - I recommend placing all of your scripts, figures, and miscellaneous output files in this directory. 
  - Scratch Storage: 800 TB (communal)
    - Any large datasets should be stored in scratch memory.
    - This is a shared resource that anyone can use—you can store any amount of data in this directory until the total storage is full across all users. While it is communal, no one else will have access to your directory on scratch. 
    - Note: Any files stored in scratch that have not been interacted with for 90 days will be automatically purged. 
  - Group/Purchased storage
     - Storage can be purchased at a rate of $50/TB per year
    
  __*Koa does not automatically back up your work—this is one of the many reasons why the discussion of version control and documentation in Workshop 2 is so important.__  


![Example](https://img.shields.io/badge/Example:%20Requesting%20compute%20&%20exploring%20storage%20volumes-indigo?style=for-the-badge)
  - Submit an interactive job
  - Explore the "Files" tab on OOD
  - Connect to the shell through OOD and explore the home and koa_scratch directories. 

### __tmux__
___
```tmux``` (terminal multiplexer) is a powerful tool that allows users to manage multiple terminal sessions within a single window. It enables session persistence, allowing users to detach and reattach to sessions, which is especially useful for remote work on servers.
- Koa now has two potential login nodes, and any ```tmux``` session you start will be tied to the node where it was launched. If you cannot locate your session, it may exist on the other login node, or the job within the session may have completed. Sessions remain active while a script is running or a job is active on the cluster but will close if left inactive for too long.

To switch between login nodes:
```bash
ssh <username>@login-0101  # Connect to the first login node from the second
ssh <username>@login-0102  # Connect to the second login node from the first 
```
If you don't see your session on one node, try checking the other.

Within a ```tmux``` session, the primary method of interacting with the terminal is through a set of ```tmux``` specific commands. A cheatsheet on commands can be found [here](https://tmuxcheatsheet.com/) while critical commands to getting started are included below. 

```
# Starting tmux 
tmux  # Start a new session
tmux new -s mysession  # Start a new session named "mysessdion"

# Detaching & Reattaching Sessions
Ctrl-b d  # Detach from the current session
tmux ls   # List active sessions
tmux attach -t mysession  # Reattach to "mysession"

# Working Within Sessions
Ctrl-b [ # Activates scrolling mode: up arrow scrolls up while the down arrow scrolls down
Ctrl-c # Deactivates scrolling mode

# Ending tmux 
tmux kill-session -t mysession  # Kill the session named "mysession"
tmux kill-session -a   # Kill all tmux sessions 
```
  

## Introduction to the Linux Command Line

The Linux Command Line Interface (CLI) allows users to interact with the operating system using text commands. There are many functionalities of the linux CLI, this section introduces a few essential commands to get you started.
  - Note: the majority of functionalities that can be accomplished from the command line can be executed through the file navigator in VS Code. 

#### Navigating the Filesystem
__Caution: Beware of ```rm``` and ```sudo``` commands. ```rm``` will permanently delete a file/directory and you do not have ```sudo``` permissions on the cluster.__
  - If a resource suggests the use of ```sudo``` commands to install software/packages, this approach will not work on Koa. 

1. Checking Your Current Directory
```bash
pwd  # Print Working Directory
```
This command displays the full path of your current location.

2. Listing Files and Directories
```bash
ls  # List files in the current directory
ls -l  # List files with details
ls -a  # Show hidden files
```

3. Changing Directories
```bash
cd directory_name  # Move into a specific directory
cd ..  # Move up one level
cd ~  # Move to the home directory
cd /path/to/folder  # Move to a specific directory using an absolute path
```

Example:
```bash
cd /home/user/Documents  # Move to the Documents directory
```

#### Working with Files and Directories

4. Creating Files and Directories
```bash
touch filename.txt  # Create an empty file
mkdir new_directory  # Create a new directory
```

5. Viewing File Contents
```bash
cat filename.txt  # Display file contents
less filename.txt  # View file contents page by page
head filename.txt  # Show the first 10 lines
```

6. Copying, Moving, and Deleting
```bash
cp file1.txt file2.txt  # Copy a file
mv file1.txt newname.txt  # Rename or move a file
rm file.txt  # Delete a file
rmdir empty_directory  # Remove an empty directory
rm -r directory  # Remove a directory and its contents
```

#### Searching for Files

7. Using the `find` Command
   
The `find` command allows you to search for files and directories based on name, type, or other criteria.

```bash
find /path/to/search -name "filename.txt"  # Find a file by name
find /home/user/Documents -type d -name "projects"  # Find a directory named 'projects'
find . -type f -mtime -7  # Find files modified in the last 7 days
```

#### Checking File Modification Time

8. Viewing the Last Time a File Was Altered
   
The `stat` command displays detailed information about a file, including the last modification time.
- This command can be used to check whether your files on koa_scratch are approaching the 90 day removal threshold. 

```bash
stat filename.txt  # Show detailed file information, including modification time
```

Alternatively, you can use `ls` with the `-l` option to see the last modified time:
```bash
ls -l filename.txt  # Display file modification time
```

#### System Information

9. Checking Disk Usage
```bash
df -h  # Show disk space usage
```

10. Checking Memory Usage
```bash
free -h  # Show available and used RAM
```

#### Getting Help

11. Manual Pages
```bash
man command  # Show manual page for a command
```
Example: `man ls` provides detailed information about the `ls` command.

12. Command Help Option
```bash
command --help  # Show a brief summary of how to use a command
```
Example: `ls --help` lists available options for `ls`.


### Using Visual Studio Code
___
![Example](https://img.shields.io/badge/Example:%20Follow%20along%20with%20VS%20Code%20Setup-indigo?style=for-the-badge)

To establish a remote tunnel, follow the steps below:
  1) Connect to your Koa account via the local terminal using ```ssh``` and follow the prompts for two-factor authentication
 ```bash
 ssh <username>@koa.its.hawaii.edu
 ```
  2) Install and unpack VS Code through the CLI on Koa using the commands below (you only need to do this the first time)
 ```bash
 curl -Lk 'https://code.visualstudio.com/sha/download?build=stable&os=cli-alpine-x64' --output vscode_cli.tar.gz

 tar -xf vscode_cli.tar.gz
 ```
  3) Create a new tmux session
 ```bash
 tmux new -s vscode
 ```
  4) Request compute, or connect to an existing interactive job using ```srun```
       - I often request an interactive job through Open OnDemand then connect to the existing job within the tmux session. Note that existing job IDs can be found in the upper left corner of each interactive job panel or by running ```squeue -u <username>``` in the command line. 
    
     ![image](https://github.com/user-attachments/assets/e62e9ccd-71e9-4f99-85ac-f45402e4b321) ![image](https://github.com/user-attachments/assets/867a4d24-8124-4e2d-bd38-7928d99613a8)


 ```bash
 # Use the following command if you are requesting a new interactive job (Note that certain partitions may have restrictions on the time/amount of compute that can be requested: refer to the Koa docs for more details.)
  srun -p <partition> -c <num of cpus> --mem=<num of GB of ram>G -t <time requested in minutes> --pty /bin/bash
 
 # Use the following command if you are connecting to an existing job
  srun --jobid=<job ID> --pty /bin/bash
 ``` 

  5) Establish the remote tunnel by running the command below from your home directory and following the login prompts using GitHub (example screenshots included below) 
 ```bash
 ./code tunnel 
 ```
 ![image](https://github.com/user-attachments/assets/4453b3d5-186f-4642-9669-56a7a2db3744)
 ![image](https://github.com/user-attachments/assets/6cebd1e3-433c-42de-bff0-d0708b3cb73e)
 ![image](https://github.com/user-attachments/assets/449e6480-607d-4f53-986f-2200db3d0eaf)
 ![image](https://github.com/user-attachments/assets/ee3034b1-7f8f-4f5c-a6ca-b2939450aff2)

  6) Launch VS Code through the provided link (will open in browser), or detach from the tmux session using ```ctrl+b d``` then open VS Code locally and follow the steps below.
     - Click on the profile icon in the lower left corner and enable Remote Tunnel Access (you should only have to do the first two steps once)

     ![image](https://github.com/user-attachments/assets/aad4fb19-17ff-48e3-8fd4-0f94f49a0031)

     - Follow the prompt at the top to enable "for this session" then follow the prompt to sign in with GitHub

     ![image](https://github.com/user-attachments/assets/4b6102af-69f9-4d09-b088-cd251eef6f1c)
     ![image](https://github.com/user-attachments/assets/9c04bafb-f77d-4236-a750-171d83172ac4)

     - Select "Connect to..."
     
     ![image](https://github.com/user-attachments/assets/fbef286a-3e98-4b7d-a3fd-4f3eb404cdbf)

     - Select "Connect to Tunnel..."
     
     ![image](https://github.com/user-attachments/assets/2e43bf68-110f-4657-93d7-25161e01f89c)

     - Select GitHub
     
     ![image](https://github.com/user-attachments/assets/c3a3c6f4-19c0-4f52-9eb4-24aeb93cb2af)

     - Select Koa
       
     ![image](https://github.com/user-attachments/assets/6da46ab0-ce5b-4e12-b117-52f570c360f7)

### Using R in Visual Studio Code
___
While Python is automatically available in VS Code, using R requires some setup. Alternatively, you can use R through RStudio, but if you prefer a unified IDE, the setup below will enable seamless interaction with `.py`, `.ipynb`, `.R`, and `.Rmd` files within a single environment.

1) Open the terminal within VS Code and load the R language. (This will have to be done every time you use R within VS Code.)
```bash
module load lang/R
```

2) Initiate R from the CLI and install `languageserver`

```bash
[<username>@cn-03-13-01 Workshop_1]$ R

R version 4.4.1 (2024-06-14) -- "Race for Your Life"
Copyright (C) 2024 The R Foundation for Statistical Computing
Platform: x86_64-pc-linux-gnu

R is free software and comes with ABSOLUTELY NO WARRANTY.
You are welcome to redistribute it under certain conditions.
Type 'license()' or 'licence()' for distribution details.

R is a collaborative project with many contributors.
Type 'contributors()' for more information and
'citation()' on how to cite R or R packages in publications.

Type 'demo()' for some demos, 'help()' for on-line help, or
'help.start()' for an HTML browser interface to help.
Type 'q()' to quit R.

> install.packages("languageserver")

Warning in install.packages("languageserver") :
  'lib = "/opt/apps/software/lang/R/4.4.1-gfbf-2023b/lib64/R/library"' is not writable
Would you like to use a personal library instead? (yes/No/cancel) y
Would you like to create a personal library
‘/home/<username>/R/x86_64-pc-linux-gnu-library/4.4’
to install packages into? (yes/No/cancel) y
--- Please select a CRAN mirror for use in this session ---
Secure CRAN mirrors 

 1: 0-Cloud [https]
 2: Australia (Canberra) [https]
 3: Australia (Melbourne 1) [https]
 4: Australia (Melbourne 2) [https]
 5: Austria (Wien 1) [https]
 6: Belgium (Brussels) [https]
 7: Brazil (PR) [https]
 8: Brazil (SP 1) [https]
 9: Brazil (SP 2) [https]
10: Bulgaria [https]
11: Canada (MB) [https]
12: Canada (ON 1) [https]
13: Canada (ON 2) [https]
14: Chile (Santiago) [https]
15: China (Beijing 1) [https]
16: China (Beijing 2) [https]
17: China (Beijing 3) [https]
18: China (Hefei) [https]
19: China (Hong Kong) [https]
20: China (Jinan) [https]
21: China (Lanzhou) [https]
22: China (Nanjing) [https]
23: China (Shanghai 2) [https]
24: China (Shenzhen) [https]
25: China (Wuhan) [https]
26: Colombia (Cali) [https]
27: Costa Rica [https]
28: Cyprus [https]
29: Czech Republic [https]
30: Denmark [https]
31: East Asia [https]
32: Ecuador (Cuenca) [https]
33: Finland (Helsinki) [https]
34: France (Lyon 1) [https]
35: France (Lyon 2) [https]
36: France (Paris 1) [https]
37: Germany (Erlangen) [https]
38: Germany (Göttingen) [https]
39: Germany (Leipzig) [https]
40: Germany (Münster) [https]
41: Greece [https]
42: Hungary [https]
43: Iceland [https]
44: India (Bengaluru) [https]
45: India (Bhubaneswar) [https]
46: Indonesia (Banda Aceh) [https]
47: Iran (Mashhad) [https]
48: Italy (Milano) [https]
49: Italy (Padua) [https]
50: Japan (Yonezawa) [https]
51: Korea (Gyeongsan-si) [https]
52: Mexico (Mexico City) [https]
53: Mexico (Texcoco) [https]
54: Morocco [https]
55: Netherlands (Dronten) [https]
56: New Zealand [https]
57: Norway [https]
58: Poland [https]
59: South Africa (Johannesburg) [https]
60: Spain (A Coruña) [https]
61: Spain (Madrid) [https]
62: Sweden (Umeå) [https]
63: Switzerland (Zurich 1) [https]
64: Taiwan (Taipei) [https]
65: Turkey (Denizli) [https]
66: UK (Bristol) [https]
67: UK (London 1) [https]
68: USA (IA) [https]
69: USA (MI) [https]
70: USA (MO) [https]
71: USA (OH) [https]
72: USA (OR) [https]
73: USA (PA 1) [https]
74: USA (TN) [https]
75: USA (UT) [https]
76: United Arab Emirates [https]
77: Uruguay [https]
78: (other mirrors)

Selection: 72
```

3) Install the R extension within VS Code.
![image](https://github.com/user-attachments/assets/096b023d-496e-4176-b2db-939351210422)

4) Within the terminal, activate R and retrieve the path to the executable.
```bash
[<username>@cn-03-13-01 ~]$ R

R version 4.4.1 (2024-06-14) -- "Race for Your Life"
Copyright (C) 2024 The R Foundation for Statistical Computing
Platform: x86_64-pc-linux-gnu

R is free software and comes with ABSOLUTELY NO WARRANTY.
You are welcome to redistribute it under certain conditions.
Type 'license()' or 'licence()' for distribution details.

R is a collaborative project with many contributors.
Type 'contributors()' for more information and
'citation()' on how to cite R or R packages in publications.

Type 'demo()' for some demos, 'help()' for on-line help, or
'help.start()' for an HTML browser interface to help.
Type 'q()' to quit R.

> R.home()
[1] "/opt/apps/software/lang/R/4.4.1-gfbf-2023b/lib64/R"
```

5) Set the appropriate paths to the R executable within the R extension:
  - Select the R extension from the left-side panel.
![image](https://github.com/user-attachments/assets/f81a3b1e-8bee-4942-aaa9-2e56ab90a5cd)

  - Click the cog wheel and select "Settings"
![image](https://github.com/user-attachments/assets/e40f4bfd-aa77-4344-85c1-f1b28699f772)

  - Type "Path" into the search bar then update the path for "Rpath: Linux" and "Rterm: Linux"
![image](https://github.com/user-attachments/assets/b54c4aac-2430-4653-baba-17bdd76b7b51)

You should now be able to edit `.R` and `.Rmd` files in VS Code. Remember if you receive the below message, simply enter `module load lang/R` into the terminal within VS Code. If you encounter any other issues, see [this](https://code.visualstudio.com/docs/languages/r) guide for more details. 
![image](https://github.com/user-attachments/assets/8697d28c-a878-45cc-a74d-da32af532821)


## Coding Best Practices

### __Keeping a Clean Environment__

Environment management is essential for creating isolated, reproducible workspaces for coding. Two of the most popular tools for managing environments are:

- **Conda** (for Python)
- **renv** (for R)

You can use these tools to maintain a clean and reproducible environment for your project, which is especially important on shared systems like Koa. Here's a guide to managing environments on Koa:

---

#### 1. Setting Up a Clean Environment on Koa

![Example](https://img.shields.io/badge/Example:%20Follow%20along%20with%20Conda%20Setup-indigo?style=for-the-badge)

Koa offers a flexible system for loading languages and modules. You can find a list of available languages and modules [here](https://uhawaii.atlassian.net/wiki/spaces/HPC/pages/461307905/Module+List). 

To load a module for a specific language or tool, use the `module load` command in your terminal. For example, to use R and Python, you can load the respective modules:

```bash
# Load R module for renv (R environment management)
module load lang/R
install.packages('renv')

# Load Anaconda and Python modules for managing Python environments
module load lang/Anaconda3
module load lang/Python
```

Once you've loaded the necessary modules, you can begin creating and managing environments in both R and Python.

---

#### 2. Working with Python (Conda)

- **Listing Existing Conda Environments:**

```bash
# This will activate your "base" Conda environment. There is nothing special about this environment-I would suggest keeping this as a clean environment and only using it in the rare instances that you require an existing environment to update other Conda environments. 
source activate
# This will deactivate the base environment 
conda deactivate 
conda env list
```

- **Creating a New Conda Environment:**

You can create a new environment to work in:

```bash
conda create --name ecn_workshop python=3.11.8
```

- **Activating and Deactivating a Conda Environment:**

```bash
# Activate the environment
conda activate ecn_workshop

# Deactivate the environment
conda deactivate
```

- **Installing Packages in Conda:**

You can install packages either from the command line or within a Jupyter notebook or Python script using `pip`.

```bash
# Installing packages using Conda (e.g., numpy)
conda install numpy

# Specifying a specific version of a package
conda install numpy=1.21

# Installing multiple packages at once 
conda install ipykernel pandas polars numpy scipy matplotlib seaborn patsy statsmodels plotnine

# Some packages may require pip (e.g., stargazer)
pip install stargazer
```

To make the conda environment visible within Jupyter Labs and VS Code. 

```bash
python -m ipykernel install --user --name ecn_workshop --display-name "ecn_workshop"
```

To install packages from within a notebook or script, use:

```python
!pip install pandas polars numpy scipy matplotlib seaborn patsy statsmodels stargazer plotnine
```

- **Checking Installed Packages:**

```bash
conda list
```

- **Exporting and Removing Conda Environments:**

You can export your environment configuration to a file and recreate it on another system or share it with others.

```bash
# Export environment to a .yml file
conda env export > environment.yml

# Create an environment from the exported .yml file
conda env create -f environment.yml

# Remove a conda environment
conda env remove --name ecn_workshop
```

#### 3. Working with R (renv)

The `renv` package helps manage R environments by ensuring that package versions are consistent across different systems or projects.

- **Install and Use `renv`**:

First, install the `renv` package in R:

```r
install.packages("renv")
```

- **Initializing a New R Environment**:

To start a new project with `renv`, use:

```r
renv::init()
```

This will create a project-specific environment and install dependencies for your R packages.

- **Installing Packages in R**:

You can install packages in R with:

```r
install.packages("ggplot2")
```

- **Saving the State of the Environment**:

You can save the state of your environment to a lock file with:

```r
renv::snapshot()
```

This will record the exact versions of all packages used in your project, making it easy to reproduce the environment elsewhere.

- **Restoring the Environment**:

To recreate the environment on a different system:

```r
renv::restore()
```

### __Updating the `.bash_profile` with Paths__
___

The `.bash_profile` file is a shell script that runs every time you log in to your terminal session. It’s commonly used to configure environment variables, including setting paths for various tools and software packages. If you install software or tools that you want to access from the terminal, you may need to add their directories to the `PATH` variable in your `.bash_profile`. This ensures that the terminal can find and execute those tools without needing the full path every time.

#### When to Update the `.bash_profile`
You might need to update your `.bash_profile` in the following cases:
- **Installing new software**: If you install software like Python, R, or a specific tool, and the installer doesn’t automatically update the `PATH` for you.
- **Using custom scripts**: If you have custom scripts or binaries that you want to execute easily from any directory.
- **Changing versions of a tool**: If you need to switch between versions of a tool (like Python or Java), adding the path to a specific version will ensure you use the correct one.

#### Example
To add a directory to your `PATH` variable, you can include a line like this in your `.bash_profile`:

```bash
# Set Path
export PATH=$PATH:/path/to/your/tool

# Set a path to a license
export COPT_LICENSE_DIR="/home/ehartley/copt"

# Set a path to a library
export LD_LIBRARY_PATH="/home/ehartley/opt/copt72/lib:$LD_LIBRARY_PATH"

# Set the download path for Llama3
export LLAMA_STACK_CONFIG_DIR="/home/ehartley/koa_scratch/Llama_3"
```

After updating the `.bash_profile`, you’ll need to either restart your terminal session or run the following command to apply the changes:
```bash
source ~/.bash_profile
```

### __Debugging: Best Practices and Strategies__
___

Debugging is an essential skill in programming, helping you identify and fix errors efficiently. Effective debugging requires a structured approach and familiarity with debugging tools available in your development environment.

### General Debugging Practices
- **Read Error Messages Carefully**: Error messages often tell you exactly what went wrong. Start by identifying the error type and the line number where it occurred. Typically, we read error messages from bottom to top to identify the root cause. 
- **Use Print Statements**: Inserting `print()` statements (or `cat()` in R) at key points in your code helps track variable values and execution flow.
- **Break Down the Problem**: If your code is complex, try isolating smaller sections to test them independently.
- **Check for Typos and Syntax Issues**: Sometimes, simple mistakes like missing parentheses or incorrect variable names cause unexpected behavior.
- **Use Version Control**: Committing your code regularly allows you to revert to a working version if something breaks.

---

### The Rubber Duck Debugging Method 🦆  
The *Rubber Duck Debugging* method is a simple yet effective strategy where you explain your code, line by line, to an inanimate object (or a colleague). Often, the act of verbalizing the problem helps you realize mistakes or gaps in logic.

#### How to use it:
1. Take a rubber duck (or any object).
2. Explain each line of your code as if the duck has no prior knowledge.
3. Identify any inconsistencies or logic errors.
4. Fix the issue before the duck even responds! 🦆

---

### Pair Programming for Debugging 👥  
**Pair programming** is another effective debugging approach where two developers work together at the same computer:
- **Driver**: Writes the code.
- **Navigator**: Reviews each line, suggesting improvements and spotting errors.

This technique helps catch bugs early, improves code readability, and encourages best practices. It’s especially useful for tricky issues where a second pair of eyes can spot problems you might overlook.

---

### Debugging in VS Code  
Visual Studio Code provides powerful debugging tools for Python, R, and other languages.

- **Setting Breakpoints**: Click next to a line number to set a breakpoint, allowing you to pause execution and inspect variables.
- **Step Through Code**: Use "Step Over" (F10) and "Step Into" (F11) to walk through your program one line at a time.
- **Variable Inspection**: The "Variables" panel shows live values of all defined variables.
- **Interactive Debug Console**: You can test expressions and modify variables while paused at a breakpoint.

For Python, use the built-in Debugger (`Run → Start Debugging`). For R, the `vscDebugger` package enables debugging inside VS Code.

---

### Debugging Strategies in R  
R provides multiple built-in debugging tools:

- **`browser()`**: Pauses execution at a specific line, allowing interactive debugging.
  ```r
  my_function <- function(x) {
    browser()  # Execution will pause here
    x + 1
  }
  my_function(5)
  ```
- **`traceback()`**: After an error, run `traceback()` to see the sequence of function calls leading to the error.
- **`debug()`**: Use `debug(my_function)` to step through the function interactively.
- **`recover()`**: If an error occurs, `options(error = recover)` allows selecting a call frame to inspect variables.
- **`try()` and `tryCatch()`**: These functions let you handle errors gracefully without stopping execution.

Example:
```r
result <- try(log("text"), silent = TRUE)
if (inherits(result, "try-error")) {
  print("An error occurred, but execution continues.")
}
```

---

### Where to Look for Solutions 🔍  
If you’re stuck on an issue, here are some great resources for finding solutions:

#### 📚 **Package Documentation**  
- Official package documentation often provides function descriptions, usage examples, and explanations of errors.
- In R, use `?function_name` or `help(function_name)` to access docs.
- In Python, use `help(function_name)` or check the package’s website.

#### 💽 **Source Code**  
- If a function isn’t working as expected, look at its source code.
- In R, use:
  ```r
  getAnywhere(function_name)
  ```
  or
  ```r
  print(function_name)
  ```
- In Python, use:
  ```python
  import inspect
  print(inspect.getsource(function_name))
  ```

#### 🏰 **GitHub Repositories (Searchable)**  
- Many open-source packages have their source code on GitHub. You can:
  - Search for function names and error messages.
  - Check the README or Wiki for troubleshooting tips.
  - Look at previous commits to see if a recent change introduced a bug.

#### 🚨 **GitHub Issues**  
- If you encounter a bug, check the package’s **Issues** tab on GitHub.
- You may find that others have reported and discussed the same problem.
- If you can’t find an existing issue, consider **opening a new one** (but be sure to provide a clear explanation and a reproducible example).

#### 💡 **Stack Overflow**  
- A great place to search for answers to common issues.
- Try searching for error messages verbatim—chances are, someone else has encountered the same problem.
- If asking a question, **provide a minimal reproducible example** so others can help you effectively.

---

### Debugging a Single Function from a Package  
If you’re having trouble with a single function in a package, you can **copy its source code** and step through it in a debugger.  

#### Why do this?
- Some package functions are complex and involve hidden steps.
- Debugging within a package isn’t always straightforward.
- Running the function step-by-step in your own script allows you to track variable values and intermediate results.

#### How to do it?
1. Extract the function’s source code:
   - In R, use `print(function_name)` or `getAnywhere(function_name)`.
   - In Python, use `inspect.getsource(function_name)`.
2. Paste the function into a script or notebook.
3. Insert breakpoints (`browser()` in R, `pdb.set_trace()` in Python).
4. Run the function and step through it line by line.

Example in R:
```r
debug(my_function)
my_function(arg1, arg2)
```

Example in Python:
```python
import pdb
def my_function(x):
    pdb.set_trace()  # Execution will pause here
    return x + 1

my_function(5)
```

### __General Coding Advice & Insights__
___

### **Resources**
- [Posit Cheatsheets](https://posit.co/resources/cheatsheets/)
- [CMU R Resources](https://guides.library.cmu.edu/73-265/R_Resources)
- [Python Guides](https://wiki.python.org/moin/BeginnersGuide/Programmers)
- [Python Resources & Exercises](https://github.com/openlists/PythonResources)

### **Writing Code for Humans, Not Just Machines**
Above all else, code should be written for clarity and maintainability. You are writing code for other humans (including your future self), not just for the computer. Think of coding as a structured way to translate your thoughts into logical steps.

### **Core Principles**
#### **1. Test Your Code**
__Never__ push to or publish a repository without verifying that the entire workflow is correct and functioning.
- This, of course, does not apply to personal working repositories or sharing with collaborators to identify errors.

#### **2. Write Clear, Descriptive Variable & Function Names**
For example, use calculate_average() instead of just calc().

#### **3. Keep Functions Focused on One Task**
Each function should do one thing and do it well, making your code modular and easier to test.

#### **4. Comment & Document Code**
Provide context where necessary, but avoid over-commenting obvious code.
- Use docstrings in Python and R for functions to describe their purpose, parameters, and outputs.
- This is a fantastic application of LLMs. 

#### **5. Setting Seeds for Reproducibility:**
When working with random number generation (e.g., in simulations, sampling, or machine learning models), it’s crucial to set a random seed so that the results are reproducible. Without setting the seed, each run might produce different results, which can hinder debugging and comparisons.
- In Python, you can set a seed for various libraries like `random`, `numpy`, `tensorflow`, and `torch`.
```python
import random
import numpy as np

# Set seed for reproducibility
random.seed(42)
np.random.seed(42)
```
- In R, you can use the `set.seed()` function to set the random seed.
```r
# Set seed for reproducibility
set.seed(42)
```

#### **6. Avoid Global Variables**
Global variables can lead to unintended side effects, making debugging difficult. Instead:
- Use local variables within functions and classes.
- Pass data explicitly through function parameters.
- If necessary, encapsulate shared state in well-defined objects or configurations.

#### **7. Never Hard-Code Values**
Hard-coding values makes code brittle and difficult to update. Instead:
- Use named constants at the top of your script or module.
- Store configurations in separate files (e.g., `.json`, `.yaml`, or `.env`).

**Example:**
```python
# Avoid this:
threshold = 0.8  # Magic number

# Do this:
THRESHOLD = 0.8  # Named constant
```

#### **8. Don't Repeat Yourself (DRY Principle)**
If you find yourself copying and pasting similar code, you should refactor it into a function or loop. 
- Reduce redundancy by using functions and modules.
- Generalize patterns instead of making slight variations.

**Example:**
- Bad: Repeating Yourself
```python
# Loading first dataset and fitting model
df1 = pd.read_csv("data1.csv")
X1 = df1[["feature1", "feature2"]]
y1 = df1["target"]
X1 = sm.add_constant(X1)  # Adding a constant for the intercept
model1 = sm.OLS(y1, X1).fit()
predictions1 = model1.predict(X1)

# Loading second dataset and fitting model
df2 = pd.read_csv("data2.csv")
X2 = df2[["feature1", "feature2"]]
y2 = df2["target"]
X2 = sm.add_constant(X2)  # Adding a constant for the intercept
model2 = sm.OLS(y2, X2).fit()
predictions2 = model2.predict(X2)
```
- Better: Operationalizing Your Code

```python
def generate_reg_preds(file_path):
    """Load a dataset, fit a regression model, and return predictions."""
    # Load the data
    df = pd.read_csv(file_path)
    
    # Prepare the features and target
    X = df[["feature1", "feature2"]]
    y = df["target"]
    
    # Add a constant for the intercept
    X = sm.add_constant(X)
    
    # Fit the regression model
    model = sm.OLS(y, X).fit()
    
    # Generate predictions
    predictions = model.predict(X)
    
    return predictions

# Better: Repeating the same operation with slight changes
result1 = generate_reg_preds(file1)
result2 = generate_reg_preds(file2)
result3 = generate_reg_preds(file3)

# Best: Use a loop
files = [file1, file2, file3]
results = [generate_reg_preds(f) for f in files]
```

#### **9. Work Through Logic Sequentially**
When starting a new task, develop logic step by step in an interactive environment (e.g., Jupyter Notebook, RStudio, or a Python script). This helps:
- Validate your approach before encapsulating logic into functions or classes.
- Debug incrementally.

#### **10. Modularize Code into Functions & Classes**
Once you verify the logic, structure your code:
- **Functions**: Encapsulate reusable operations.
- **Classes**: Group related functionality together if state management is needed.
- **Modules**: Split large scripts into separate files for maintainability.

**Example:**
```python
# Start with a function
def process_data(file_path):
    """Reads and processes a data file."""
    data = read_file(file_path)
    cleaned_data = clean_data(data)
    return cleaned_data

# Then organize into a class if state tracking is required
class DataProcessor:
    def __init__(self, file_path):
        self.data = self.read_file(file_path)
    
    def read_file(self, file_path):
        return read_file(file_path)  # Placeholder function

    def clean_data(self):
        self.data = clean_data(self.data)  # Placeholder function
```

#### **11. Realistic Use of AI in Coding**
AI is a powerful tool that can accelerate learning and improve productivity, but it should be used wisely. Consider:
- Using AI to help understand unfamiliar concepts, generate starter code, or suggest improvements.
- Not relying on AI-generated code blindly—always review and test before using it.
- Developing confidence in your coding skills without AI, so you are not dependent on it in critical situations.
- Treating AI as a learning assistant, not a crutch—invest time in understanding the code it generates.

![Example](https://img.shields.io/badge/Example:%20Basic%20Python%20Functions%20&%20Practical%20Guide-indigo?style=for-the-badge)
- Installing & Loading packages
- Exploring pandas
- Efficient data processing 
- Documenting & Debugging Code
  - Copilot in VS Code
- Practical Example: Predicting natural gas demand from weather
  - Computing summary statistics
  - Exporting LaTex tables
  - Fitting regressions
    - Flexible trends vs. fixed effects
  - Exploring documentation
    - Within Python / Package Documentation / GitHub
  - Formatting regression output
  - Plotting Results 
- Use cases outside of research

### __Multiprocessing__ 
___
### Basic Multiprocessing Approaches

Multiprocessing is a powerful technique for leveraging multiple CPUs to run processes in parallel, significantly speeding up computation-heavy tasks. This guide covers basic multiprocessing approaches in Python and R, as well as how high-performance computing (HPC) environments use batch jobs to distribute work across different compute environments.

__Caution: when using multiprocessing on Koa, packages often look for the total resources on the node rather than the resources you have been allocated.__
- This may result in overprovisioning the node and could get you in trouble - take my word on this. A simple approach is to determine the number of processers availble using the following strategies:

![Example](https://img.shields.io/badge/Example:%20Determining%20available%20compute-indigo?style=for-the-badge)
- [how to see available cpus in python](https://stackoverflow.com/questions/1006289/how-to-find-out-the-number-of-cpus-using-python)
- [how to see available cpus in R](https://stackoverflow.com/questions/47318401/r-how-to-check-how-many-cores-cpu-usage-available)

```python
import os

num_process = len(os.sched_getaffinity(0))
```
```r
library(future)

plan(multiprocess)  # Or use other backends
num_cpus <- availableCores()
```

### Python Multiprocessing
___
Python provides several ways to perform multiprocessing, most commonly through the `multiprocessing` module. This module allows the creation of separate processes that can run independently, utilizing multiple CPU cores.

#### Example: Using `multiprocessing` in Python

```python
import os
import multiprocessing

# Function to run in each process
def square(n):
    return n * n

if __name__ == "__main__":
    # Create a pool of worker processes
    with multiprocessing.Pool(processes= len(os.sched_getaffinity(0))) as pool:
        numbers = [1, 2, 3, 4, 5]
        results = pool.map(square, numbers)
    
    print(results)
```

#### Key Concepts:
- **Pool**: A pool of worker processes is created, with the number of processes typically set to the number of available CPUs.
- **`map()`**: The `map()` function is used to apply a function to a list of arguments across the worker processes.
- **Shared Memory**: The `multiprocessing` module also supports shared memory structures for processes to communicate if needed.

### R Multiprocessing
___
R offers several packages for parallel computing, with the most common being `parallel`, which allows parallel execution of code across multiple cores or machines.

#### Example: Using `parallel` in R

```r
library(parallel)
library(future)
plan(multiprocess)

# Function to run in each process
square <- function(n) {
  return(n * n)
}

# Create a cluster of workers
cl <- makeCluster(availableCores()) 
clusterExport(cl, "square")

# Apply function in parallel
numbers <- c(1, 2, 3, 4, 5)
results <- parLapply(cl, numbers, square)

stopCluster(cl)

print(results)
```

#### Key Concepts:
- **`makeCluster()`**: This function creates a cluster of worker processes, using the number of CPU cores available.
- **`parLapply()`**: This function applies the task in parallel across the workers.
- **Cluster Export**: The `clusterExport()` function allows data or functions to be made available to all worker processes in the cluster.

### __Multiprocessing in High-Performance Computing (HPC) Environments__
___

In an HPC environment, the goal is to scale workloads across multiple machines, often with hundreds or even thousands of processors. This is achieved by **batch job scheduling**, which is a common feature of HPC systems.

### How HPC Enables Multiprocessing

#### 1. **Batch Job Scheduling**: 

Batch job schedulers (e.g., SLURM, PBS, or Torque) allow users to submit jobs to a cluster. These schedulers manage job queues, allocate resources (CPUs, memory), and distribute work across multiple nodes in the cluster.

- **Example**: You may write a script that divides a large task into smaller chunks and submits them as separate jobs to the batch scheduler. Each job runs independently on different compute nodes, and the results can later be gathered and combined.

#### 2. **Distributing Work Across Nodes**:

In a typical HPC setup, your workload is distributed across different **compute nodes**, each with its own set of CPU cores and memory. By using batch jobs, tasks can be split into smaller jobs that run in parallel across multiple compute nodes, drastically reducing the overall computation time.

For example, running simulations on a cluster can involve dividing the workload into independent parts and assigning them to different compute nodes. Each node executes its part of the simulation, and the results are gathered afterward for analysis.


#### Example Workflow in HPC

1. **Split Workload**: A large dataset is split into smaller chunks.
2. **Submit Batch Jobs**: Each chunk is submitted as an independent batch job.
3. **Run on Multiple Nodes**: Jobs are run across different compute nodes in parallel.
4. **Collect Results**: After all jobs finish, results are gathered, and post-processing is done.

In this way, the computational efficiency of an HPC system can dramatically reduce processing time, making it invaluable for large-scale problems.

### __Packages to Know About__

### Python

1. **Data Manipulation & Cleaning**  
- **pandas**: Powerful data structures for data analysis, including `DataFrame` for tabular data.
- **polars**:  
- **numpy**: Fundamental package for numerical computations, provides array objects and routines for high-level mathematical functions.  
- **matplotlib / seaborn**: Libraries for data visualization, `seaborn` is built on top of `matplotlib` and provides a high-level interface.  
- **openpyxl / xlrd**: Reading and writing Excel files.  
- **pyjanitor**: Data cleaning functions built on top of `pandas`.  
- **dask**: Parallel computing for large-scale data processing.  

2. **Econometric & Statistical Analysis**  
- **statsmodels**: Comprehensive library for statistical models, including linear regression, time series analysis, and more.  
- **linearmodels**: Estimation of linear panel data models and other econometric models.  
- **scipy**: Scientific computing library, includes statistical functions, optimization, and more.  
- **pyblp**: Python package for solving and estimating discrete choice models, often used in industrial organization.  
- **scikit-learn**: General machine learning library, useful for classification, regression, and other predictive models.   
- **lifelines**: Survival analysis and survival regression models.  
- **pylogit**: A package for estimating logit models, including multinomial logit (MNL) models.  

3. **Time Series Analysis**  
- **statsmodels**: Also useful for time series analysis, with models for ARIMA, SARIMA, and other time series processes.  
- **prophet**: Forecasting tool developed by Facebook that works well for daily and seasonal time series data.  
- **pmdarima**: Auto ARIMA for time series forecasting, an easier interface for ARIMA models.  
- **tsfresh**: Feature extraction for time series data.  
- **forecasting**: Provides machine learning-based time series forecasting methods.  

5. **Visualization**  
- **matplotlib**: The foundational library for data visualization.  
- **seaborn**: High-level data visualization interface built on `matplotlib`, great for statistical graphics.  
- **plotly**: Create interactive plots that can be embedded in websites or used in dashboards.
- **plotnine**: A Python implementation of the Grammar of Graphics (like R's `ggplot2`), allowing for a declarative approach to building plots.
- **altair**: Declarative statistical visualization library.  
- **bokeh**: Interactive visualization for modern web browsers, supports complex visualizations.  
- **holoviews**: High-level package for building complex visualizations quickly.  

6. **Optimization & Computational Economics**  
- **scipy.optimize**: Functions for optimization, including linear and nonlinear solvers.  
- **cvxpy**: Python library for convex optimization problems.  
- **pyomo**: A package for modeling optimization problems in Python.  
- **nlopt**: Nonlinear optimization library, useful for solving complex optimization problems.  
- **geopy**: Useful for geographic data optimization, such as solving the traveling salesman problem.


#### R 

1. Data Manipulation & Cleaning  
- **tidyverse**: A collection of packages for data science, including `ggplot2`, `dplyr`, `tidyr`, `readr`, and more.  
- **data.table**: Fast and efficient data manipulation.  
- **haven**: Import data from Stata, SPSS, and SAS.  
- **readxl / writexl**: Read and write Excel files.  

2. Econometric & Statistical Analysis  
- **fixest**: Fast estimation of fixed-effects models.  
- **plm**: Panel data models.  
- **AER**: Applied econometrics functions.  
- **sandwich**: Robust standard errors.  
- **lmtest**: Hypothesis testing for regression models.  
- **car**: Companion package for regression analysis.
- **ivreg**: Instrumental variable regression.  
- **mlogit**: Multinomial logit models.  
- **mfx**: Compute marginal effects.  
- **survival**: Survival analysis models.  

3. Time Series Analysis  
- **forecast**: Time series forecasting tools.  
- **tseries**: Time series econometrics.  
- **zoo / xts**: Handling time series data.  
- **vars**: Vector autoregressions (VAR models).  
- **dynlm**: Dynamic linear models.  
- **urca**: Unit root and cointegration tests.  
- **fable**: Modern forecasting methods.  

5. Visualization  
- **ggplot2**: Flexible data visualization.  
- **ggthemes**: Additional themes for `ggplot2`.  
- **patchwork**: Arrange multiple `ggplot2` plots.  
- **plotly**: Create interactive visualizations.  

6. Optimization & Computational Economics  
- **nloptr**: Nonlinear optimization.  
- **optimx**: Multiple optimization methods.  
- **DEoptim**: Differential evolution optimization. 


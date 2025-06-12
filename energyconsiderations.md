# Competitive Green Coding




## Our Project
CodeGreen is a web service which allows users to submit solutions to coding problems published on our website and receive a rating for each submission. To determine the rating of a solution, we must consider the energy efficiency of the solution that was submitted. In our case, we create individual docker containers for each submission on the DAS-5 UvA server (https://www.cs.vu.nl/das5/) and execute each submission there. This introduces a few limitations in how we can measure energy consumption. Many tools rely on RAPL which measures the entire CPU usage of the system. Other solutions often require some assumption on the activity of the server, considering it is used by many students and companies we cannot make the assumption that this traffic is consistent. With these constraints in mind we will explore some possible options and argue the optimal solution to our problem.


## Our Choice
Due to all the tools and their limitations that have been discussed below, we have come to the conclusion that the most accurate and fair way to offer feedback to users is in the form of a score that we calculate ourselves. We would do this using `docker stats` which informs us of the CPU Usage, memory usage and I/O of an individual docker container. We can define our own weights for each metric based on their relevance in each problem, normalize them and create our own score that is proportional to energy consumption.




## Considerations
There are a lot of articles that talk about different tools that could be used for sustainable coding, however a lot of these are aimed at corporations that have to hit certain goals specified by the EU. We compiled a list of tools that were often mentioned to limit our search and dive deeper into what would work best for our purposes.








* **Pyrapl:** \
More lightweight than PyJoules, however also less accurate. Doesn't require root access. \
https://github.com/powerapi-ng/pyRAPL
* **PyJoules:** \
Provides fine-grained energy consumption measurements from the CPU level. Does require root access. \
https://github.com/powerapi-ng/pyJoules
* **New Relic:** \
Application performance measuring tool that tracks resource usage. \
https://github.com/newrelic
* **LoadRunner:** \
Loadrunner measures scalability through load testing simulations. \
https://www.opentext.com/products/professional-performance-engineering
* **SonarQube:** \
Static code analysis. While this does not have any direct connection with sustainability it will be quick to point out inefficient code. \
https://github.com/SonarSource/sonarqube
* **CodeCarbon:** \
Calculates the CO2 footprint of executed code. \
https://github.com/mlco2/codecarbon
* **Green Metrics Tool:** \
Estimates the energy usage of a docker container. \
https://github.com/green-coding-solutions/green-metrics-tool






### Pyrapl
Pyrapl is a python library that allows you to measure the energy usages of your machine from within a python program. Specifically it reads the energy usage of the CPU, DRAM and GPU. The main drawback when using Pyrapl is that it reports the energy consumption of the entire machine during the measurement time (by using RAPL), not of a specific program. The documentation therefore recommends eliminating any other running program to get a more accurate result. Unfortunately this isn't achievable in our situation, and therefore we cannot use Pyrapl.




### PyJoules
PyJoules makes use of Intel RAPL, similar to Pyrapl does, and therefore it has the same drawbacks as Pyrapl for our case. One of the similarities Pyjoules shares is that it measures the total energy consumption of the machine instead of limiting it to a specific program. Therefore it is not appropriate for our use-case.




### New Relic
New Relic has been stated to be very powerful for application performance monitoring. However upon further investigation it seems to be a tull to monitor and manage a full stack application, and make sure it keeps running correctly. How much energy the software uses is not the main focus. It is also mainly meant for long-running services as opposed to for example a single C executable.




### Loadrunner
Loadrunner is a very useful performance testing tool for scalable services. Unfortunately scaling in this case means more people connecting. This could be a useful tool to test if our website would function on a larger scale, however for the purposes of rating code in a competitive green coding exercise it is quite useless.






### SonarQube
SonarQube is a static code analysis tool that gets mentioned when talking about sustainable code. Upon looking into what it specifically does it becomes clear that its not exactly what we're looking for, but it might function as a  helpful supplement. SonarQube looks at your code to detect inefficiencies and code with bad practices that make it hard to maintain. This does not necessarily work in our usecase, however it could possibly be used to detect inefficiencies in code and use that to apply a negative impact on the scoring for our platform.








### CodeCarbon
CodeCarbon is a python library that estimates the carbon emissions produced by computing tasks. It does this by tracking the energy consumption of code and converting it into carbon emissions based on the local power grid's carbon intensity. CodeCarbon initially tries to use RAPL, which in our case is not an option. It offers an alternative for these cases though, here CodeCarbon will estimate the energy usage instead of measuring it directly from hardware sensors using TDP-based estimation. This means that the final Carbon Intensity value is also an estimation. The main issue with TDP-based estimation is that it uses the TDP of the CPU together with the % of CPU Utilization, unfortunately CodeCarbon cannot see the CPU utilization of individual docker containers. Which makes it unsuitable in our case.




### Green Metrics Tool
An immediate advantage of Green Metrics Tool is that it is set up as a tool to measure the energy consumption of software, particularly the energy consumption of the software run in a single docker container. Our architecture’s back-end consists of three services, each in its own container. With the code that needs to be tested running on the ‘execution_engine’ service. The execution engine has its own code it needs to run, but with the right user problems this overhead would be a minimal part of the container's executed code. What is an issue with Green Metrics Tool however is the baseline subtraction it used to estimate the energy consumption of the container. This means that when a user goes to submit his code, the accuracy of the resulting score is somewhat dependent on luck. In the competitive environment we aim to create, this simply won’t do.


### Baseline Subtraction
Baseline Subtraction measures the server's idle power for a given window and stores the average that is found. We would then run the user's job and record the total power on the server. Finally we can subtract the total power against the user's job to attempt to estimate the user's used energy. Important is that this approach requires sequential job scheduling. Unfortunately this does not seem like an appropriate solution, considering that we are building a competitive environment that should measure all users fairly. Not only are the results achieved by this solution estimates, due to the traffic on the server they are not relative to each other. Due to the limitations of measuring energy consumption through hardware, we always knew we had to go with a tool that provides an estimation. For our purposes of creating a competitive environment however, this estimation would have to follow some kind of consistency. And due to the volatile nature of the server, baseline subtraction does not provide this consistency.


Moreover we question how noticeable the execution of a single code submission from our service truly is, it is entirely possible that the total output is lesser then the margin of error we should account for.




### Troubles with our search
Our search for suitable energy measurement tools revealed a significant gap between available solutions and our specific needs. Most tools are designed for large-scale corporate use, where services run continuously on dedicated servers. These tools often rely on total system measurements (like RAPL) or assume stable background noise (enabling baseline subtraction).


However, our use case (short-lived, isolated code executions in a shared environment) doesn’t align with these assumptions. Corporate tools prioritize tracking energy use across entire frameworks or services, while we need way smaller, per-submission metrics for a competitive setting.


This disconnect explains why most existing tools fall short for our purposes, pushing us toward a custom scoring system based on Docker’s resource metrics.












# Estimating Greenness of Code
In this document we introduce our requirements for estimating the "greenness" of code, attempt to argue why RAPL is not suitable for this task and introduce our own solution.
## Our Requirements
Our interpretation of the 'Competitive Green Coding' project for Project Software Engineering was to build a platform that allows users to be ranked competitively based on their code solutions as the assignment requires [https://canvas.uva.nl/courses/49524/pages/competitive-green-coding?module_item_id=2416001]. These solutions would run on the shared UvA server, in isolated Docker containers each assigned a single core for the sake of security and fairness. Due to this approach, a few clear requirements for the tool that measures the "greenness" of user-submitted code arise:
* The tool must be able to rate submitted code consistently without any variance.
* The tool must be able to rate only the user-submitted code and no other jobs involved in the process.
* The tool must work without root access on the physical host.

In the next section we will explore the way RAPL and tools who utilize RAPL work and how they fail to meet our requirements.


## How RAPL Works (And Why it Fails for Us)
RAPL is a powerful-hardware-level feature that provides accurate energy consumption data for major system components on modern Intel/AMD CPUs. It exposes its energy counters through Model-Specific Registers (MSRs), low-level CPU interfaces that require privileged access. While Linux provides an abstraction via `/sys/class/powercap`, this sysfs layer ultimately depends on MSR access at the kernel level. Moreover, RAPL's utility highly dependent on measurement context.
The biggest drawback is that it measures physical hardware domains such as the CPU package, not logical software processes.


### Root Access
The default Linux kernel documentation states that:\
"*This file is protected so that it can be read and written only by the user root, or members of the group root.*", referencing `/dev/cpu/*/msr` (https://man7.org/linux/man-pages/man4/msr.4.html).

Within the source code of the Linux kernel we can take a look at the RAPL driver, where `drivers/powercap/intel_rapl_common.c` blocks write permissions through hardware-level BIOS locks within the `rapl_write_pl_data()` function (https://elixir.bootlin.com/linux/v6.15-rc1/source/drivers/powercap/intel_rapl_msr.c).

This results in the root having only read-only access to any RAPL registers. To safely expose RAPL data, the Linux kernel provides a higher level abstraction via `/sys/class/powercap`. This sysfs interface is the intended way for tools to access RAPL data without needing root acess. However, the DAS-5 documentation (https://www.cs.vu.nl/das5/jobs.shtml) mentions the use of users' environments. Normally, these user environments mask specific paths within `/sys` for security or isolation reasons during container setup. We can verify this by running `ll /sys/class/powercap` on the server, we get back:

```
total 0
drwxr-xr-x  2 root root 0 Jun 15 10:58 ./
drwxr-xr-x 68 root root 0 Jun 15 10:58 ../
```

This shows us that all subdirectories within `/sys/class/powercap` are not mounted into the containers/VMs through which students are granted access (We would need an `intel-rapl/` entry). The lack of reading access of these registers stops any tool from reading the information RAPL gathers.

### Lack of per-process measurement
Additionally, RAPL provides no mechanism to attribute energy consumption to a specific PID. While advanced techniques exist to estimate this by correlating RAPL data readings with process scheduling data from the kernel, these are still estimations. For short-lived problems such as those in our project, the overhead of such monitoring system could easily dwarf the energy consumpotion of the actual code being measured.


## Our approach
We suggest estimating power consumption by measuring User CPU time of a user's program using `/usr/bin/time -v [executable]`.
We estimate the consumed power using `energy estimate = user CPU time * power constant`. This approach, while still an estimation, is better suited for our project for the following reasons:

### Isolation and fairness
`user-cpu-time` measures the time the CPU spent executing the program's own code in user-mode. It explicitly excludes time spent on:
- Syscalls
- Time spent waiting for I/O
- Time spent while de-scheduled by the kernel to let other processes run

This provides a pure, isolated measure of the computational work done by the user's algorithm, and is not affected by a noisy environment, and will thus provide a result that is very reprodicuble and fair

### Simplicity and robustness
This method is simple to implement. `/usr/bin/time` is a standard and lightweight Linux utility that requires no special permissions, kernel modules, or direct hardware access, which simplifies security and configuration of the runtime environment.

### Direct correlation with algorithmic efficiency
An algorithm with better time complexity will require fewer CPU cycles and thus results in a lower `user-cpu-time`. Our estimate will therefore rank the more efficient algorithm as "greener". While the absolute value in Joules is an approximation, the relative ranking between submissions will be accurate. 

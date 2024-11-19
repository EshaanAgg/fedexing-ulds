# Problem Statement

As a pre-screening task, you need to solve a simpler variant of the official problem statement. You are given two input files:
- `uld.csv`: Contains the list of ULDs (Unit Load Device) that are available for the flight. Each ULD has a unique identifier, dimensions and weight capacity.
- `packages.csv`: Contains the list of packages that need to be loaded into the ULDs. Each package has a unique identifier, dimensions, weight and score associated with it. 

The packages have been generated such that it is not possible to pack all the packages into the ULDs. Your task is to maximize the total score of the packages that are loaded into the ULDs. 

## Submission Guidelines

- You would need to submit your code that you used to generate the output file, as well as the output file for the provided dataset. 

- The output file should have the following format: 
  - The first line should contain the total score of the packages that are loaded into the ULDs.
  - The next line should contain the number of packages that you are shipping.
  - The subsequent lines should contain the information about the packing of the package. The format for the same is:

    ```
    Package_ID,ULD_ID,x0,y0,z0,x1,y1,z1
    ```

    The convention for the coordinates of the packages is the same as described in the official problem statement. Please note that you need to add the above lines for only the packages that you are shipping, and not all the packages (as described in the official problem statement). We will be using our own evaluation script to evaluate the output file, and if any of the convetions are not followed, the submission will be rejected.

- You do NOT need to consider the spatial and geometric stability of the proposed packing in your solution. However some basic constraints like the package should fit inside the ULD, and each package should either be resting on the ground or be supported on the bottom by some other package should be followed.
- The packages CAN be rotated in any orientation to fit into the ULDs.
- The code can be written in any language. You would need to submit the code and the output file in a ZIP file.
- The output file should be named as `output.csv`.
- You can make use of classical algorithms or heuristics to solve the problem. The output file should be generated within under a minute on a standard laptop.

## Submission Deadline

The deadline for submission is `11:59 AM` on `16 November 2024, Saturday`. The deadline is not flexible and no submissions will be accepted after the deadline. We will be sharing the submission form on the WhatsApp group, where you can submit your solution.
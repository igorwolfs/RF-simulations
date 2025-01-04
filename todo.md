# S-parameter stability gridding optimization
- (Far future) Implement some kind-of function that auto-adds points to the existing base mesh
- (Far Far future) Make the function auto-add points in a loop and make the simulation run again and again, check for s-parameter impedance convergence as a stop-point for simulations.


# Iterative antenna shape modification
- Use bash scripting:
    - Give a range for all antenna-dimension-related variables to the script
    - Make the freecad interpreter change the antenna dimensions through the freecad-sheet
    - Make freecad export the antenna as stl-files
    - Run the openEMS-script until convergence
    - Store the results
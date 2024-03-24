from ambiguity import handle_ambiguity
from planning import create_plan
from executor import execute_plan

# Prompt the user for the initial task
user_provided_task = input("Please enter your task for SALTE: ")
print("") # Add a new line for better readability

# Call the Ambiguity Agent to resolve any ambiguity in the task
task = handle_ambiguity(user_provided_task)

print(f"Final task: {task}\n")

# Call the Planning Agent to create a plan for the task
plan_steps = create_plan(task)

print(f"Plan for the task: {plan_steps}\n")

status = execute_plan(plan_steps, "Delete all temporary files .tmp in the /var/tmp directory.")

print(f"\n---\nExecution status: {status}\n---\n")
print("Execution completed.")
if(status['success']):
    print("Task executed successfully.")
else:
    print("Task execution failed.")
import json
import subprocess
from openai import OpenAI
from system_context import get_operating_system_environment_context

client = OpenAI()

"""
TODO: Instead of calling all of the commands at once, we should send GPT-4 the results of each one, 
going one by one through the plan. That way it can pivot if something goes wrong to accomplish the plan.
"""

def execute_command(command):
    """
    Executes a given command in the Linux command line and prints the output.
    """
    try:
        result = subprocess.run(command, shell=True, check=True, text=True, capture_output=True)
        print(f"Command executed successfully: {command}")
        print(f"Output:\n{result.stdout}")
        return {"command": command, "success": True, "output": result.stdout}
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {command}")
        print(e)
        print(e.output)
        return {"command": command, "success": False, "output": e.output}

def execute_plan(plan_steps, task):
    """
    Executes an array of plan steps
    """
    system_message = """
    # Role
    You are the Executor Agent for SALTE, a Semi-Autonomous Linux Task Executor.

    # Primary Function
    Your primary function is the execution of a series of commands in the Linux command line based on the provided plan steps, with minimal human intervention.
    
    # Objective
    Execute the planned steps using the "execute_commands" function tool.
    
    # Tools
    - **execute_commands**: tool/function to run an array of commands in the Linux command line.
    """

    operating_system_environment_context = get_operating_system_environment_context()
    
    # Format the plan steps into a markdown-formatted string
    steps_markdown = '\n'.join([f"- **PLAN STEP** {step}" for step in enumerate(plan_steps)])

    user_message = f"## Plan Steps\n{steps_markdown}\nPlease begin the execution of the above steps using the 'execute_commands' tool.\n"

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_message},
            {"role": "function", "name": "operating_system_environment_context", "content": operating_system_environment_context},
            {"role": "user", "content": task},
            {"role": "user", "content": user_message}
        ],
        tools=[{"type": "function", "function": {
            "description": "Execute an array of commands in the Linux command line.",
            "name": "execute_commands",
            "parameters": {
                    "type": "object",
                    "properties": {
                        "commands": {
                            "type": "array",
                            "description": "An array of commands to be executed in the Linux command line.",
                            "items": {
                                "type": "string"
                            }
                        }
                    },
                    "required": ["commands"]
                }
        }}],
        stream=False,
    )

    try:
        if(response.choices[0].message.tool_calls is None):
            print("No commands to execute.")
            return {
                "success": False,
                "message": "No commands to execute."
            }
        
        tool_call = response.choices[0].message.tool_calls[0]
        commands = json.loads(tool_call.function.arguments)["commands"]

        print(f"Executing the following commands: {commands}\n")

        execution_results = []
        for command in commands:
            # Execute each command, collecting success or failure
            result = execute_command(command)
            execution_results.append(result)

            # Break after the first failure to stop execution
            if not result['success']:
                break

        # After attempting to execute commands, return the outcome
        return {
            "success": all(result['success'] for result in execution_results),
            "message": "Execution completed with the results provided.",
            "execution_results": execution_results,
            "plan_steps": plan_steps
        }
    except Exception as e:
        print(f"Failed to interpret or execute plan steps: {e}")
        return {
            "success": False,
            "message": "Failed to interpret or execute plan steps.",
            "execution_results": [],
            "plan_steps": plan_steps
        }
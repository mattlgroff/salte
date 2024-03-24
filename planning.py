import json
from openai import OpenAI
from system_context import get_operating_system_environment_context

client = OpenAI()

def create_plan(task):
    if not task:
        raise ValueError("No task provided.")

    system_message = """
      # Role
      You are the Planning Agent for SALTE, a Semi-Autonomous Linux Task Executor.

      # Primary Function
      Your primary function is to complete complex Linux tasks with minimal human intervention, leveraging the power of GPT-4. Please generate a detailed plan in the form of a JSON array of strings, with each string representing a step in the execution process within the Linux command line environment.

      # Task
      Based on the provided task, generate a step-by-step plan (in a JSON array of strings) that outlines how to execute the task. The plan should be feasible and effective, considering the capabilities, rules, and restrictions of the Linux command line.

      # Rules and Guidelines
      - Don't use `cd` commands, instead use full and absolute paths.
      - When using commands always use full and absolute paths.
      - Each step should be a separate Linux command. Don't add unnecessary steps. Another Agent will review the output. This plan is for Linux command execution.

      # Example JSON schema
      "plan_steps": [
          "Step 1: Perform this action...",
          "Step 2: Execute this command...",
          "Step 3: Verify the output...",
          ...
      ]
    """

    operating_system_environment_context = get_operating_system_environment_context()

    response = client.chat.completions.create(
        model="gpt-4-turbo-preview",
        messages=[
            {"role": "system", "content": system_message},
            {"role": "function", "name": "operating_system_environment_context", "content": operating_system_environment_context},
            {"role": "user", "content": task}
        ],
        stream=False,
        response_format={"type": "json_object"},
    )

    # Parse the plan from the response, expecting a dictionary with the key 'plan_steps'
    try:
        response_content = json.loads(response.choices[0].message.content)
        if "plan_steps" in response_content and isinstance(response_content["plan_steps"], list):
            return response_content["plan_steps"]
        else:
            raise ValueError("The response format is incorrect, expected a JSON object with 'plan_steps' key.")
    except json.JSONDecodeError:
        raise ValueError("Failed to decode the response into a JSON format.")
import json
from openai import OpenAI
from system_context import get_operating_system_environment_context

client = OpenAI()

# Recursive function to handle ambiguity in user-provided tasks
def handle_ambiguity(user_provided_task):
    print(f"Task: {user_provided_task}\n")
    print("Checking task for ambiguity...\n")
    clarifying_question = check_for_ambiguity(user_provided_task)

    if clarifying_question:
        print(f"Ambiguity detected: {clarifying_question}\n")
        clarifying_answer = input("Your response: ")  # Prompt user for input in the terminal
        print("") # Add a new line for better readability

        if not clarifying_answer:
            print("No clarifying answer provided. Please provide a clarifying answer to proceed.\n")
            return handle_ambiguity(user_provided_task)  # Capture return from recursive call

        revised_task = rewrite_user_provided_task(user_provided_task, clarifying_question, clarifying_answer)
        print(f"Revised task: {revised_task}\n")
        return handle_ambiguity(revised_task)  # Capture return from recursive call
    else:
        print("Task is clear and ready for execution. Proceeding with the task.\n")
        return user_provided_task  # Return the clear or revised task

def check_for_ambiguity(user_provided_task):
    if not user_provided_task:
        raise ValueError("No user_provided_task provided.")

    system_message = """
      # Role
      You are the Ambiguity Agent for SALTE, a Semi-Autonomous Linux Task Executor.

      # Primary Function
      Your primary function is to assist with identifying uncertainties and asking for human intervention when necessary.

      # Important Details
      - You do not need to ask about access to the file system or permissions in the Operating System. Assume that SALTE has the necessary access and permissions to perform the task.
      - You are not the Agent that is executing the task. You are responsible for identifying ambiguities and prompting for human intervention when necessary.

      # Examples of Ambiguities
      - Unclear or conflicting instructions within the task.
      - Ambiguous or incomplete information in the task description.
      - Decision points that require human judgment or input.
      - More information needed to proceed with the task.
      - "Delete the temporary files" without specifying the location or file extension.
      - "Get fruit from the store" without specifying the type of fruit or store location.

      # When there is an ambiguity
      When you encounter an ambiguity, you should prompt for human intervention by asking clarifying questions or requesting additional information. Your goal is to resolve uncertainties and ensure that SALTE can proceed with the task effectively. Use the `ambiguity` command to indicate that there is an ambiguity that requires human intervention.

      # When the task is clear and unambiguous
      Use the `proceed` command to indicate that the task is clear and ready for execution. Do not worry about file system or permissions in the Operating System.

      # Tools
      - **ambiguity**: command to indicate that there is an ambiguity that requires human intervention.
      - **proceed**: command to indicate that the task is clear and ready for execution.
    """

    operating_system_environment_context = get_operating_system_environment_context()

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_message},
            {"role": "function", "name": "operating_system_environment_context", "content": operating_system_environment_context},
            {"role": "user", "content": user_provided_task}
        ],
        tools=[{"type": "function", "function": {
            "description": "command to indicate that there is an ambiguity that requires human intervention",
            "name": "ambiguity",
            "parameters": {
                "type": "object",
                "properties": {
                    "clarifying_question": {
                        "type": "string",
                        "description": "Ask a clarifying question to resolve the ambiguity."
                    },
                }
            },
        }}, {"type": "function", "function": {
            "description": "command to indicate that the task is clear and ready for execution",
            "name": "proceed",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }}],
        stream=False,
    )

    # If there is no tool_calls, return None (assuming we should proceed with the task)
    if not response.choices[0].message.tool_calls:
        return None

    tool_call = response.choices[0].message.tool_calls[0]
    function_name = tool_call.function.name

    if function_name == "ambiguity":
        # Parse the arguments string into a Python dictionary
        arguments = json.loads(tool_call.function.arguments)
        clarifying_question = arguments["clarifying_question"]
        return clarifying_question
    elif function_name == "proceed":
        return None
    
# Using OpenAI's GPT-4, we will rewrite the User Provided Task using the Clarifying Question and Answer. Returns string.
def rewrite_user_provided_task(user_provided_task, clarifying_question, clarifying_answer):
    if not user_provided_task:
        raise ValueError("No user_provided_task provided.")
    
    if not clarifying_question:
        raise ValueError("No clarifying_question provided.")
    
    if not clarifying_answer:
        raise ValueError("No clarifying_answer provided.")
    
    system_message = """
      # Role
      You are the Task Rewriter for SALTE, a Semi-Autonomous Linux Task Executor.

      # Primary Function
      Your primary function is to rewrite the user-provided task based on the clarifying question and answer.
    """

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_provided_task},
            {"role": "function", "name": "clarifying_question", "content": clarifying_question},
            {"role": "function", "name": "clarifying_answer", "content": clarifying_answer}
        ],
        stream=False,
    )

    return response.choices[0].message.content

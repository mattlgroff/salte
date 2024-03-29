import time
import json
from openai import OpenAI
from system_context import get_operating_system_environment_context

client = OpenAI(
    base_url = 'http://localhost:11434/v1',
    api_key='ollama',
)

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
      When you encounter an ambiguity, you should prompt for human intervention by asking clarifying questions or requesting additional information. Your goal is to resolve uncertainties and ensure that SALTE can proceed with the task effectively. Use the `clarifying_question` command to indicate that there is an ambiguity that requires human intervention.

      # When the task is clear and unambiguous
      Use the `proceed` command to indicate that the task is clear and ready for execution. Do not worry about file system or permissions in the Operating System.

      # Tools
      - **clarifying_question**: command to indicate that there is an ambiguity that requires human intervention.

      ## clarifying_question definition
      {
        "name": "clarifying_question",
        "type": "string",
        "description": "Ask a clarifying question to resolve the ambiguity."
      }

      ## clarifying_question example
      {
        "clarifying_question": "What is the file extension of the temporary files and what folder did you mean?"
      }

      - **proceed**: command to indicate that the task is clear and ready for execution.
      ## proceed definition
      {
        "name": "proceed",
        "type": "boolean",
        "description": "If we should proceed with the task, return 'true'"
      }

      ## proceed example
      {
        "proceed": true
      }

      ## Return Value
      - If there is an ambiguity, return a "clarifying_question" JSON to resolve the ambiguity.
      - If the task is clear and ready for execution, return the "proceed" true JSON to proceed with the task.

      In either case, you must return valid JSON objects as described above.
    """

    operating_system_environment_context = get_operating_system_environment_context()

    start_time = time.time()

    response = client.chat.completions.create(
        model="mixtral",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": f"# For context, this is the Operating System Environment you are working with: \n{operating_system_environment_context}"},
            {"role": "user", "content": user_provided_task}
        ],
        stream=False,
    )

    print(f"Response time from mixtral for 'check_for_ambiguity': {time.time() - start_time}\n")

    # Need to check if this is valid json
    contentToParse = response.choices[0].message.content

    try:
        function = json.loads(contentToParse)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from LLM: ${contentToParse} {e}\n")
        return None

    if function["clarifying_question"]:
        return function["clarifying_question"]
    elif function["proceed"]:
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

      # Return Format
      Return only the newly revised task based on the clarifying question and answer. Nothing before or after the task. Just the revised task.

      For example, if the user-provided task was "Delete all temporary files in the /var/tmp directory." and the clarifying question was "What is the file extension of the temporary files and what folder did you mean?" and the clarifying answer was "The file extension is .tmp and the folder is /var/tmp.", then the revised task would be "Delete all temporary files with the .tmp extension in the /var/tmp directory."
    """

    start_time = time.time()

    response = client.chat.completions.create(
        model="mixtral",
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_provided_task},
            {"role": "user","content": f"# Clarifying Question: \n{clarifying_question}"},
            {"role": "user","content": f"# Clarifying Answer: \n{clarifying_answer}"}
        ],
        stream=False,
    )

    print(f"Response time from mixtral for 'rewrite_user_provided_task': {time.time() - start_time}\n")

    return response.choices[0].message.content

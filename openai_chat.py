from openai import OpenAI
import os
from rich import print

def num_tokens_from_messages(messages, model='gpt-4o'):
  """Returns an estimated number of tokens used by a list of messages.
  Uses character-based estimation (~4 characters per token) since tiktoken dependency was removed."""
  num_tokens = 0
  for message in messages:
      num_tokens += 4  # every message follows <im_start>{role/name}\n{content}<im_end>\n
      for key, value in message.items():
          # Estimate tokens based on character count (~4 characters per token)
          num_tokens += len(str(value)) // 4
          if key == "name":  # if there's a name, the role is omitted
              num_tokens += -1  # role is always required and always 1 token
  num_tokens += 2  # every reply is primed with <im_start>assistant
  return num_tokens
      

class OpenAiManager:
    
    def __init__(self):
        self.chat_history = [] # Stores the entire conversation
        try:
            self.client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])
        except TypeError:
            exit("Ooops! You forgot to set OPENAI_API_KEY in your environment!")

    # Asks a question with no chat history
    def chat(self, prompt=""):
        if not prompt:
            print("Didn't receive input!")
            return

        # Check that the prompt is under the token context limit
        chat_question = [{"role": "user", "content": prompt}]
        if num_tokens_from_messages(chat_question) > 8000:
            print("The length of this chat question is too large for the GPT model")
            return

        print("[yellow]\nAsking ChatGPT a question...")
        completion = self.client.chat.completions.create(
          model="gpt-4o",
          messages=chat_question
        )

        # Process the answer
        openai_answer = completion.choices[0].message.content
        print(f"[green]\n{openai_answer}\n")
        return openai_answer

    # Asks a question that includes the full conversation history
    def chat_with_history(self, prompt=""):
        if not prompt:
            print("Didn't receive input!")
            return

        # Add our prompt into the chat history
        self.chat_history.append({"role": "user", "content": prompt})

        # Check total token limit. Remove old messages as needed
        print(f"[coral]Chat History has a current token length of {num_tokens_from_messages(self.chat_history)}")
        while num_tokens_from_messages(self.chat_history) > 8000:
            self.chat_history.pop(1) # We skip the 1st message since it's the system message
            print(f"Popped a message! New token length is: {num_tokens_from_messages(self.chat_history)}")

        print("[yellow]\nAsking ChatGPT a question...")
        completion = self.client.chat.completions.create(
          model="gpt-4o",
          messages=self.chat_history
        )

        # Add this answer to our chat history
        self.chat_history.append({"role": completion.choices[0].message.role, "content": completion.choices[0].message.content})

        # Process the answer
        openai_answer = completion.choices[0].message.content
        print(f"[green]\n{openai_answer}\n")
        return openai_answer
   

if __name__ == '__main__':
    openai_manager = OpenAiManager()

    # CHAT TEST
    chat_without_history = openai_manager.chat("Hey ChatGPT what is 2 + 2? But tell it to me as Yoda")

    # CHAT WITH HISTORY TEST
    FIRST_SYSTEM_MESSAGE = {"role": "system", "content": "Act like you are Captain Jack Sparrow from the Pirates of Carribean movie series!"}
    FIRST_USER_MESSAGE = {"role": "user", "content": "Ahoy there! Who are you, and what are you doing in these parts? Please give me a 1 sentence background on how you got here."}
    openai_manager.chat_history.append(FIRST_SYSTEM_MESSAGE)
    openai_manager.chat_history.append(FIRST_USER_MESSAGE)

    while True:
        new_prompt = input("\nType out your next question Jack Sparrow, then hit enter: \n\n")
        openai_manager.chat_with_history(new_prompt)
        
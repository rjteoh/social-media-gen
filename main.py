from dotenv import load_dotenv
import sys
import os
import re
import pandas as pd
from openai import OpenAI
from pydantic import create_model
from scripts.reddit_comments import reddit_comment_gen, RedditComment
from scripts.tweets import tweet_gen, Tweet
from scripts.instagram import instagram_gen, insta_pic_gen, InstaPost
from scripts.facebook import Facebook, facebook_gen

# loading .env file
load_dotenv()

# defining default storage folder for pictures (within the output folder)
pic_folder = "pictures"

# name of model to use
model_name = "gpt-4.1"

# checking for OpenAI API key and asking user to manually input it if not found
if not os.getenv("OPENAI_API_KEY"):
    print("""
    OPENAI_API_KEY not found. Please enter your OpenAI API key (you can also set it as an environment variable).
    """)
    os.environ["OPENAI_API_KEY"] = input(">> ").strip()

# checking for defined country and asking user to manually input it if not found
if not os.getenv("COUNTRY"):
    print("""
    Please enter the country of origin for your simulated posts (you can also set it as an environment variable).
    """)
    os.environ["COUNTRY"] = input(">> ").strip()

# passing API key to OpenAI
client = OpenAI()

# checking if 'input.txt' exists in the current directory
if not os.path.exists("user_input.txt"):
    print("[ERROR] input.txt not found in the current directory. Please create it and try again.")
    sys.exit(1)  # Exit the script with an error code

# reading input txt as user prompt
with open("user_input.txt", "r", encoding="utf-8") as file:
    user_prompt = file.read().strip()

# check if file is empty after stripping whitespace
if not user_prompt:
    print("[ERROR] No user input detected. Please add a prompt to input.txt and try again.")
    sys.exit(1)

# inform user if prompt successfully loaded
print("Prompt successfully loaded.")

# initial instructions to user
print("""
Social media generator activated.
Select 1 to generate a Reddit comment thread.
Select 2 to generate a Twitter/X thread.
Select 3 to generate Instagram posts.
Select 4 to generate a Facebook post and comments.
""")

# limiting user choices
valid_choices = {'1', '2', '3', '4'}

# validating user input and adding an error message if they mess up
while True:
    user_choice = input(">> ").strip()
    if user_choice in valid_choices:
        user_choice = int(user_choice)
        break
    else:
        print("Invalid input. Please try again.")

# importing correct system prompt and generating output Pydantic model based on user choice
if user_choice == 1:
    with open("prompts/reddit_prompt.txt", "r", encoding="utf-8") as file:
        system_prompt = file.read()
    GenData = create_model("GenData", Entry=(list[RedditComment])) # dynamically generates output Pydantic model
elif user_choice == 2:
    with open("prompts/twitter_prompt.txt", "r", encoding="utf-8") as file:
        system_prompt = file.read()
    GenData = create_model("GenData", Entry=(list[Tweet]))
elif user_choice == 3:
    with open("prompts/instagram_prompt.txt", "r", encoding="utf-8") as file:
        system_prompt = file.read()
    GenData = create_model("GenData", Entry=(list[InstaPost]))
elif user_choice == 4:
    with open("prompts/facebook_prompt.txt", "r", encoding="utf-8") as file:
        system_prompt = file.read()
    GenData = create_model("GenData", Entry=(list[Facebook]))


# filling in country name from environmental variable
system_prompt = system_prompt.format(country=os.getenv("COUNTRY"))

# creating the LLM result
result = client.responses.parse(
    model = model_name,
    input = [
        {
            "role": "system",
            "content": system_prompt,
        },
        {"role": "user", "content": user_prompt},
    ],
    text_format=GenData
)

# get parsed output in structured form
gen_data = result.output_parsed

# convert to a dataframe
df = pd.DataFrame([e.model_dump() for e in gen_data.Entry])

# FOR INSTAGRAM ONLY, adding an output folder and filepath column to the df
if user_choice == 3:
    df["FilePath"] = df["Username"].apply(
        lambda name: os.path.join(pic_folder, re.sub(r'[^\w-]', '_', name) + ".png")
    )

# get output filename from user
print("""
Enter your preferred output filename (without file extensions).
""")
while True:
    filename = input(">> ").strip()
    # reject empty strings
    if not filename:
        print("Filename cannot be empty.")
        continue
    # reject windows forbidden characters: \ / : * ? " < > |
    if re.search(r'[\\/:*?"<>|]', filename):
        print(r'Filename contains invalid characters: \ / : * ? " < > |')
        continue
    # trim and normalize filename
    filename = re.sub(r'\s+', '_', filename)  # replace spaces with underscores
    break  # break when valid filename accepted

# printing the df for human edits if necessary
df.to_csv("output/" + filename + ".csv", index=False, encoding="utf-8-sig")

# activating generator function
if user_choice == 1:
    reddit_comment_gen(df, "output/" + filename + ".html")
elif user_choice == 2:
    tweet_gen(df, "output/" + filename + ".html")
elif user_choice == 3:
    insta_pic_gen(df, model_name)
    instagram_gen(df, "output/" + filename + ".html")
elif user_choice == 4:
    facebook_gen(df, "output/" + filename + ".html")
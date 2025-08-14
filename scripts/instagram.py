# import packages
import pandas as pd
import os
from openai import OpenAI
from pydantic import BaseModel
import base64
from pathlib import Path
from playwright.sync_api import sync_playwright

# defining a instagram post class for use with structured outputs
class InstaPost(BaseModel):
    Username: str
    ImagePrompt: str
    Caption: str
    Likes: int
    CommentCount: int
    Time: str

def insta_pic_gen(prompt: pd.DataFrame, model_name: str = "gpt-5") -> None:
    """
    Generates a picture from a prompt contained with a DataFrame.
    Expects columns: [ImagePrompt]
    """
    # passing API key to OpenAI
    client = OpenAI()

    # generating images
    for _, row in prompt.iterrows():

        # sends image generation request
        response = client.responses.create(
            model=model_name,
            instructions="Ensure that all generated images are 600px by 600px.",
            input=row["ImagePrompt"],
            tools=[{"type": "image_generation"}]
        )

        # saving image data to a variable
        image_data = [
            output.result
            for output in response.output
            if output.type == "image_generation_call"
        ]

        # checks for image data existing
        if image_data:
            image_base64 = image_data[0]
            # prepend "output" folder to the filename
            output_path = os.path.join("output", row['FilePath'])
            # writes it to a png file based on the filepaths we constructed
            with open(output_path, "wb") as f:
                f.write(base64.b64decode(image_base64))

def instagram_gen(content: pd.DataFrame, output_path: str = "instagram_feed.html") -> None:
    """
    Generates an Instagram-style HTML feed from a DataFrame.
    Expects columns: [Username, ImagePrompt, FilePath, Caption, Likes, CommentCount, Time, FilePath]
    """

    # dynamically generating profile images using the DiceBear API - url defined below
    dicebear_url = "https://api.dicebear.com/9.x/lorelei-neutral/svg?seed="

    # create a new column for ProfileImage using the Username as seed and leveraging on DiceBear's capabilities
    content["ProfileImage"] = content["Username"].apply(lambda name: f"{dicebear_url}{name}")

    # defining the HTML template and styling
    html_template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Instagram Feed</title>
        <style>
            body {{
                font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
                background-color: #fafafa;
                margin: 0;
                padding: 20px;
            }}
            .container {{
                max-width: 600px;
                margin: auto;
            }}
            .insta-post {{
                background-color: white;
                border: 1px solid #dbdbdb;
                border-radius: 3px;
                margin-bottom: 20px;
            }}
            .post-header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 14px;
            }}
            .user-info {{
                display: flex;
                align-items: center;
            }}
            .profile-pic {{
                width: 32px;
                height: 32px;
                border-radius: 50%;
                margin-right: 10px;
                object-fit: cover;
            }}
            .username {{
                font-weight: bold;
            }}
            .timestamp {{
                font-size: 12px;
                color: #8e8e8e;
            }}
            .post-image {{
                width: 100%;
                height: 600px;
                object-fit: cover;
                background-color: #efefef;
            }}
            .post-content {{
                padding: 0 14px 14px 14px;
            }}
            .likes {{
                font-weight: bold;
                margin: 8px 0;
            }}
            .caption {{
                margin: 4px 0;
            }}
            .view-comments {{
                color: #8e8e8e;
                font-size: 14px;
                margin-top: 6px;
            }}
            .time {{
                font-size: 10px;
                color: #8e8e8e;
                margin-top: 10px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            {body}
        </div>
    </body>
    </html>
    """

    # instantiates empty string to build html content
    body_html = ""

    # dynamically generates html from the imported dataframe
    for _, row in content.iterrows():
        post_block = f"""
        <div class="insta-post">
            <div class="post-header">
                <div class="user-info">
                    <img class="profile-pic" src="{row['ProfileImage']}" alt="Profile">
                    <div>
                        <span class="username">{row['Username']}</span>
                        <span style="color: #8e8e8e; padding: 0 4px;">•</span>
                        <span class="timestamp" style="font-size: inherit;">{row['Time']}</span>
                    </div>
                </div>
                <div style="font-weight: bold; font-size: 20px;">⋯</div>
            </div>
            <img class="post-image" src="{row['FilePath']}" alt="Post image">
            <div class="post-content">
                <div class="likes">{row['Likes']:,} likes</div>
                <div class="caption"><span class="username">{row['Username']}</span> {row['Caption']}</div>
                <div class="view-comments">View all {row['CommentCount']:,} comments</div>
            </div>
        </div>
        """
        body_html += post_block

        # adding dynamically generated html to the empty string following the template laid out above
        final_html = html_template.format(body=body_html)

        # writing html file
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(final_html)

    # write html to pdf
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(f"file://{Path(output_path).resolve()}")
        page.pdf(path=Path(output_path).with_suffix(".pdf"), format="A4")
        browser.close()

    # completion message
    print("Instagram post generated.")

# alternative functionality if python file is executed directly
if __name__ == "__main__":
    # prompting user for input
    user_path = input("Manual input activated. Enter path to CSV file: ").strip()
    # constructing a path to default output directory in case user didn't type full path
    default_path = Path(__file__).resolve().parent.parent / "output" / user_path
    # checking if either file exists
    if os.path.isfile(user_path) or os.path.isfile(default_path):
        # picking correct file name to use if it does
        if os.path.isfile(user_path):
            file_path = user_path
        else:
            file_path = default_path
        # running generator
        try:
            df = pd.read_csv(file_path)
            output_path = Path(file_path).with_suffix(".html")
            instagram_gen(df, output_path)
        except Exception as e:
            print(f"Failed to generate comment chain: {e}")
    # print error message if file doesn't exist
    else:
        print("File not found. Please check the path and try again.")
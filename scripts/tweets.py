import os
import pandas as pd
from pathlib import Path
from playwright.sync_api import sync_playwright
from pydantic import BaseModel

# defining a tweet class for use with structured outputs
class Tweet(BaseModel):
    Username: str
    Handle: str
    Time: str
    Content: str
    Replies: str
    Retweets: str
    Likes: str
    Views: str

def tweet_gen (content: pd.DataFrame, output_path: str = "tweets.html") -> None:
    """
    Generates a Twitter-style HTML feed from a DataFrame.
    Expects columns: [Username, Handle, Time, Content, Replies, Retweets, Likes, Views]
    """

    # dynamically generating profile images using the DiceBear API - url defined below
    dicebear_url = "https://api.dicebear.com/9.x/notionists-neutral/svg?seed="

    # create a new column for ProfileImage using the Username as seed and leveraging on DiceBear's capabilities
    content["ProfileImage"] = content["Username"].apply(lambda name: f"{dicebear_url}{name}")

    # defining the HTML template and styling
    html_template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Twitter Thread</title>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background-color: #f5f8fa;
                margin: 0;
                padding: 20px;
            }}
            .container {{
                max-width: 600px;
                margin: auto;
            }}
            .tweet {{
                background-color: white;
                padding: 15px 20px;
                border-bottom: 1px solid #e1e8ed;
                display: flex;
            }}
            .profile-img {{
                width: 48px;
                height: 48px;
                margin-right: 15px;
                border-radius: 50%;
                object-fit: cover;
            }}
            .tweet-body {{
                flex-grow: 1;
            }}
            .tweet-header {{
                font-weight: bold;
            }}
            .tweet-handle {{
                color: #657786;
                font-weight: normal;
                margin-left: 5px;
            }}
            .tweet-time {{
                color: #657786;
                font-size: 12px;
                margin-top: 2px;
            }}
            .tweet-content {{
                margin-top: 8px;
                font-size: 15px;
            }}
            .tweet-footer {{
                margin-top: 10px;
                font-size: 13px;
                color: #657786;
                display: flex;
                gap: 20px;
                flex-wrap: wrap;
            }}
            .tweet-footer span {{
                cursor: default;
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
    # instantiating an empty string to accept html
    tweet_html = ""

    # dynamically generating tweets from content
    for _, row in content.iterrows():
        # creating a fallback image in case prof images fail to load
        profile_img_tag = f"""
        <img class="profile-img" src="{row["ProfileImage"]}" alt="Profile"
             onerror="this.onerror=null;this.src='https://cdn-icons-png.flaticon.com/512/149/149071.png';">
        """
        tweet_html += f"""
        <div class="tweet">
            {profile_img_tag}
            <div class="tweet-body">
                <div class="tweet-header">{row['Username']} <span class="tweet-handle">{row['Handle']}</span></div>
                <div class="tweet-time">{row['Time']}</div>
                <div class="tweet-content">{row['Content']}</div>
                <div class="tweet-footer">
                    <span>{row['Replies']} Replies</span>
                    <span>{row['Retweets']} Retweets</span>
                    <span>{row['Likes']} Likes</span>
                    <span>{row['Views']} Views</span>
                </div>
            </div>
        </div>
        """

    # adding dynamically generated html to template
    final_html = html_template.format(body=tweet_html)

    # writing the final output to file
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(final_html)

    # write html to pdf
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(f"file://{Path(output_path).resolve()}")
        page.pdf(path=Path(output_path).with_suffix(".pdf"), format="A4")
        browser.close()

    # printing completion message
    print(f"Twitter thread generated.")

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
            tweet_gen(df, output_path)
        except Exception as e:
            print(f"Failed to generate comment chain: {e}")
    # print error message if file doesn't exist
    else:
        print("File not found. Please check the path and try again.")
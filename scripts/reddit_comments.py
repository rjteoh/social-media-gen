# import packages
import pandas as pd
import os
from pydantic import BaseModel
from pathlib import Path
from playwright.sync_api import sync_playwright

# defining a reddit comment class for use with structured outputs
class RedditComment(BaseModel):
    Type: str
    Username: str
    Upvotes: str
    Time: str
    Content: str

# defining necessary inputs
def reddit_comment_gen(content: pd.DataFrame, output_path: str = "reddit_comments.html") -> None:
    """
    This is a simple tool that takes a dataframe and generates a reddit style content chain. "Top" type comments
    are generated as top level comments while "comment" type comments are generated as nested replies beneath them in
    the order they are presented in the dataframe.
    Parameters:
        df (pd.DataFrame): DataFrame with columns [Type, Username, Upvotes, Time, Content].
        output_path (str): Path to save the generated HTML file.
    """

    # HTML header and styling
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Reddit Comments</title>
        <style>
            body {{ font-family: Arial, sans-serif; background-color: #dae0e6; padding: 20px; }}
            .container {{ max-width: 800px; margin: auto; }}
            .post-box, .comment-box {{
                background-color: white;
                padding: 15px;
                border-radius: 8px;
                margin-top: 10px;
                border: 1px solid #ccc;
            }}
            .comment-box {{ margin-left: 20px; border-left: 2px solid #ccc; }}
            .username {{ color: #0079d3; font-weight: bold; }}
            .meta {{ color: #7c7c7c; font-size: 12px; }}
            .upvotes {{ color: #ff4500; font-weight: bold; margin-right: 10px; }}
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
        box_class = "post-box" if row["Type"] == "top" else "comment-box"
        html_block = f"""
        <div class="{box_class}">
            <div class="meta">
                <span class="upvotes">⬆ {row['Upvotes']}</span>
                <span class="username">u/{row['Username']}</span> · {row['Time']}
            </div>
            <div class="text">{row['Content']}</div>
        </div>
        """
        body_html += html_block

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
    print("Reddit comment chain generated.")

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
            reddit_comment_gen(df, output_path)
        except Exception as e:
            print(f"Failed to generate comment chain: {e}")
    # print error message if file doesn't exist
    else:
        print("File not found. Please check the path and try again.")
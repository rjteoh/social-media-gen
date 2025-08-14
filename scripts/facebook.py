# import packages
import pandas as pd
import os
from pydantic import BaseModel
from pathlib import Path
from playwright.sync_api import sync_playwright

# defining a facebook post class for use with structured outputs
class Facebook(BaseModel):
    Name: str
    Type: str
    Time: str
    Text: str
    Likes: str

def facebook_gen(content: pd.DataFrame, output_path: str = "facebook.html") -> None:
    """
    Generates a Facebook-style HTML feed from a DataFrame.
    Expects columns: [Name, Type, Time, Text, Likes]
    """
    # dynamically generating profile images using the DiceBear API - url defined below
    dicebear_url = "https://api.dicebear.com/9.x/avataaars-neutral/svg?seed="

    # create a new column for ProfileImage using the Name as seed and leveraging on DiceBear's capabilities
    content["ProfileImage"] = content["Name"].apply(lambda name: f"{dicebear_url}{name}")

    # defining the HTML template and styling
    html_template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8" />
      <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
      <title>Facebook Posts</title>
      <style>
        body {{
          font-family: Arial, sans-serif;
          background: #f0f2f5;
          margin: 0;
          padding: 20px;
        }}
    
        .post-container {{
          background: #fff;
          border-radius: 8px;
          padding: 15px;
          max-width: 600px;
          margin: 20px auto;
          box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
    
        .post-header {{
          display: flex;
          align-items: center;
          justify-content: space-between;
          margin-bottom: 8px;
        }}
    
        .header-left {{
          display: flex;
          align-items: center;
        }}
    
        .post-options {{
          font-size: 1.25em;
          color: #888;
          cursor: pointer;
        }}
    
        .avatar {{
          width: 40px;
          height: 40px;
          border-radius: 50%;
          margin-right: 10px;
        }}
    
        .user-info {{
          display: flex;
          flex-direction: column;
        }}
    
        .user-name {{
          font-weight: bold;
        }}
    
        .timestamp {{
          font-size: 0.85em;
          color: #555;
        }}
    
        .post-text {{
          margin: 6px 0 8px 0;
          font-size: 1em;
        }}
    
        .post-image {{
          width: 100%;
          max-height: 400px;
          object-fit: cover;
          border-radius: 5px;
          margin: 6px 0 8px 0;
        }}
    
        .like-count {{
          font-size: 0.9em;
          color: #65676b;
          margin: 4px 0;
        }}
    
        .reaction-bar {{
          display: flex;
          justify-content: space-around;
          padding: 10px 0;
          border-top: 1px solid #ccc;
          border-bottom: 1px solid #ccc;
          margin: 10px 0;
        }}
    
        .reaction-bar span {{
          cursor: pointer;
          color: #65676b;
          font-size: 0.95em;
        }}
    
        .comments-section {{
          margin-top: 10px;
        }}
    
        .comment {{
          display: flex;
          align-items: flex-start;
          margin-top: 12px;
          gap: 10px
        }}
    
        .comment-avatar {{
          width: 40px;
          height: 40px;
          border-radius: 50%;
          flex-shrink: 0;
        }}
    
        .comment-body {{
          background: #f0f2f5;
          border-radius: 15px;
          padding: 8px 12px;
          display: inline-block;
          max-width: calc(100% - 50px);
          position: relative;
          word-wrap: break-word;
        }}
    
        .comment-author {{
          font-weight: bold;
          margin-bottom: 4px;
        }}
    
        .comment-text {{
          margin-bottom: 6px;
          word-wrap: break-word;
        }}
    
        .comment-meta {{
          font-size: 0.75em;
          color: #777;
        }}
    
        .comment-like {{
          position: absolute;
          bottom: 6px;
          right: 12px;
          font-size: 0.75em;
          color: #65676b;
        }}
    
        .icon {{
          font-family: "Segoe UI Symbol", sans-serif;
          font-weight: normal;
        }}
      </style>
    </head>
    <body>
        <div class="post-container">
            {post}
            <div class="reaction-bar">
                <span class="icon">♡ Like</span>
                <span class="icon">💬 Comment</span>
                <span class="icon">🔗 Share</span>
            </div>
            <div class="comments-section">
                {comments}
            </div>
        </div>
    </body>
    </html>
    """
    # separating the df into post and comments section
    post_content = content[content['Type'] == 'Post'].iloc[0].to_dict() # extracting as a dict for ease of reference
    comments_content = content[content['Type'] == 'Comment']

    # building post content from dataframe
    post_html = f"""
    <div class="post-header">
        <div class ="header-left">
            <img src={post_content['ProfileImage']} alt="Avatar" class="avatar"/>
            <div class="user-info">
                <span class="user-name">{post_content['Name']}</span>
                <span class="timestamp">{post_content['Time']}</span>
            </div>
        </div>
        <div class="post-options">⋯</div>
    </div>
    <div class="post-text">
        {post_content['Text']}
    </div>
        
    <!-- 
    # Uncomment the line below to insert pictures in the main facebook post
    <img src="INSERT URL HERE" alt="Post Image" class="post-image"/> 
    -->
        
    <div class="like-count">♡ {post_content['Likes']} people like this</div>
    """

    # instantiates empty string to store comments section
    comments_html = ""

    # dynamically generates html from the imported dataframe
    for _, row in comments_content.iterrows():
        html_block =f"""
        <div class="comment">
            <img src="{row['ProfileImage']}" alt="Commenter Avatar" class="comment-avatar"/>
            <div class="comment-body">
              <div class="comment-author">{row['Name']}</div>
              <div class="comment-text">{row['Text']}</div>
              <div class="comment-meta">{row['Time']}</div>
              <div class="comment-like">♡ {row['Likes']}</div>
            </div>
        </div>
        """
        comments_html += html_block

    # adding dynamically generated html to the empty string following the template laid out above
    final_html = html_template.format(post=post_html, comments=comments_html)

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
    print("Facebook post generated.")

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
            facebook_gen(df, output_path)
        except Exception as e:
            print(f"Failed to generate comment chain: {e}")
    # print error message if file doesn't exist
    else:
        print("File not found. Please check the path and try again.")
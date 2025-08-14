# Social Media Simulator

This is a simple ChatGPT wrapper that generates **simulated social media content** in the style of several popular platforms. It is designed for exercise planners, Model UN organizers, or anyone engaging in current affairs roleplay.

## 🔧 Supported Formats

The script can generate content in the style of:

- Reddit comments  
- Tweet threads  
- Instagram posts (including AI-generated pictures)
- Facebook posts

## 🗝 Requirements

- An OpenAI API key
- Python 3.8+
- Optional: `.env` file with:
  - `OPENAI_API_KEY`
  - `COUNTRY` (e.g. "Singapore", "generic English-speaking country", etc.)

## 📦 Installation

1. **Clone the repository**
```bash
git clone https://github.com/rjteoh/social-media-gen.git
cd social-media-gen
```

2. **Run the setup script**
- On **macOS/Linux**:
   ```bash
   ./setup.sh
  ```
- On **Windows** (Command Prompt):
   ```bat
   ./setup.bat
  ```
**Note for advanced users:** You can install dependencies manually by installing from `requirements.txt`, then running `python -m playwright install` to download browser binaries used by Playwright.

## 🚀 Quick Start

1. **Write your prompt**  
   Add your input to `user_input.txt`. You can:
   - Specify the topic and number of posts (e.g. *“Write 5 posts about a forest fire.”*)
   - Optionally include metadata (e.g. post timing, likes, views)
   - Copy the prompt below into `user_input.txt` to try it out yourself! (Select the Facebook post option when running `main.py`.)
   ```
   Write a post with 8 comments about the sighting of a magic unicorn in the country's busiest shopping mall.
   The post should have >500 likes and be posted about an hour ago. 
   ```

2. **Run the script**  
   First, activate the virtual environment you created during setup:  
   - **Windows**: `.venv\Scripts\activate`   
   - **macOS/Linux**: `source venv/bin/activate`  

   Then run the script:  
   ```bash
   python main.py
   ```
   If no `.env` is provided, you'll be prompted for:
   - OpenAI API key  
   - Country context

3. **Choose post style**  
   Select from Reddit, Twitter, Instagram, or Facebook.

4. **Review output**  
   Your files will be generated in the `output` folder. You will receive:
   - A `.csv` file (raw content)
   - A `.pdf` file (formatted)
   - A `.html` file (viewable in browser)

## ✏️ Editing Content

You can edit generated posts in two ways:

### Option 1: Manual HTML Editing  
Open the `.html` file in a text editor like Notepad++.

### Option 2: CSV Re-Generation  
1. Edit the `.csv` file directly.  
2. Re-run the appropriate renderer (not `main.py`):
   - `scripts/reddit_comments.py`
   - `scripts/tweets.py`
   - `scripts/instagram.py`
   - `scripts/facebook.py`  
3. You'll be prompted to enter the filepath to the edited CSV.

## 📸 Special Notes 

- Images are saved in the `pictures` folder within the output directory by default.
  - You can change this via the `pic_folder` variable in `main.py`.
  - To insert your own image, manually update the `FilePath` column in the `.csv`.
  - ⚠️ *Image generation can be costly — avoid generating large batches.*
- You can change the model used to generate content by editing the `model_name` variable in `main.py`.

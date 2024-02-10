import os
import re
import subprocess
import urllib.parse
import requests
from markdownify import markdownify as md

def download_scripts(output_folder):
    # Define URLs for showdown.min.js and txt-content.js
    showdown_url = "https://cdnjs.cloudflare.com/ajax/libs/showdown/2.1.0/showdown.min.js"
    txt_content_url = "https://bn-paf-test.birby.de/txt-content.js"

    # Download showdown.min.js
    response_showdown = requests.get(showdown_url)
    with open(os.path.join(output_folder, "showdown.min.js"), "wb") as showdown_file:
        showdown_file.write(response_showdown.content)

    # Download txt-content.js
    response_txt_content = requests.get(txt_content_url)
    with open(os.path.join(output_folder, "txt-content.js"), "wb") as txt_content_file:
        txt_content_file.write(response_txt_content.content)

def extract_title(html_content):
    # Define the regex pattern to match the specified h1 element
    pattern = re.compile(r'<h1 class="entry-title">(.*?)</h1>', re.DOTALL)

    # Find the first match in the HTML content
    match = re.search(pattern, html_content)

    if match:
        # Get the inner text
        inner_text = match.group(1).strip()
        return inner_text

    return None  # Return None if no match is found

def convert_html_to_md(html_content, md_url, md_filename):
    # Define the regex pattern to match the specified div element
    pattern = re.compile(r'<div class="entry-content">(.*?)</div><!-- \.entry-content -->', re.DOTALL)

    # Find the first match in the HTML content
    match = re.search(pattern, html_content)
   
    if match:
        # Get the inner HTML content
        inner_html = match.group(1)

        # Convert inner HTML to Markdown using the 'md' function
        markdown_content = md(inner_html)

        # Replace the entire match with the new div element
        updated_html = re.sub(pattern, f'<div class="md-content" data-url="{md_url}"></div>', html_content)

        # Write the Markdown content to the specified file (_content/A.md)
        with open(md_filename, "w+", encoding="utf-8") as md_file:
            md_file.write(markdown_content)

        return updated_html

    return html_content

def modify_html_files(html_folder):
    for root, dirs, files in os.walk(html_folder):
        for file in files:
            if file.endswith(".html"):
                file_path = os.path.join(root, file)
                print("converting", file_path)
                with open(file_path, "r") as html_file:
                    content = html_file.read()

                title = extract_title(content) or file

                # Add script tags before </body>
                content = content.replace("</body>", "<script src='showdown.min.js'></script><script src='txt-content.js'></script></body>")

                md_name = ''.join(c for c in title if c.isalnum() or c in ".-_ ")
                md_path = os.path.join(root, '_content/', md_name + '.md')
                if not os.path.exists(os.path.dirname(md_path)):
                    os.makedirs(os.path.dirname(md_path))
                content = convert_html_to_md(content, f"_content/{md_name}.md", md_path)

                with open(file_path, "w") as html_file:
                    html_file.write(content)

def main():
    # Check if the script is called with an argument
    import sys
    if len(sys.argv) != 2:
        print("Usage: python script.py <URL>")
        sys.exit(1)

    url = sys.argv[1]
    output_folder = urllib.parse.urlparse(url).netloc

    # Call wget with specified arguments
    print("Downloading...")
    subprocess.run(["wget", "--page-requisites", "--recursive", "--level=5", "--convert-links", "--adjust-extension", "-e", "robots=off", url])

    # Download and modify scripts
    print("downloading scripts...")
    download_scripts(output_folder)

    print("modiying html...")
    modify_html_files(output_folder)

if __name__ == "__main__":
    main()

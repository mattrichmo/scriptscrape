import os
import re

source_directory = "./scripts"
target_directory = "./data"

os.makedirs(target_directory, exist_ok=True)

for filename in os.listdir(source_directory):
    if filename.endswith(".html"):
        with open(os.path.join(source_directory, filename), "rb") as file:
            try:
                html_content = file.read().decode("ISO-8859-1")
            except UnicodeDecodeError as e:
                print(f"Error reading {filename}: {e}")
                continue

        writers_label_pos = html_content.find("<b>Writers</b>")
        genres_label_pos = html_content.find("<b>Genres</b>")
        
        title_start = html_content.rfind("<h1>", 0, writers_label_pos) + len("<h1>")
        title_end = html_content.find("</h1>", title_start)

        if title_start != -1 and title_end != -1:
            movie_title = html_content[title_start:title_end].strip()

            movie_directory = os.path.join(target_directory, movie_title)
            os.makedirs(movie_directory, exist_ok=True)

            writers_start = writers_label_pos + len("<b>Writers</b> :")
            writers_end = html_content.find("<br>", writers_start)
            writers_links = html_content[writers_start:writers_end].split('&nbsp;')

            # Extract the text within <a> tags for writers and join with a comma and space
            writers = ', '.join([re.search(r'>(.*?)</a>', link).group(1) for link in writers_links if re.search(r'>(.*?)</a>', link)])

            genres_start = genres_label_pos + len("<b>Genres</b> :")
            genres_end = html_content.find("<br>", genres_start)
            genres_links = html_content[genres_start:genres_end].split('&nbsp;')

            # Extract the text within <a> tags for genres and join with a comma and space
            genres = ', '.join([re.search(r'>(.*?)</a>', link).group(1) for link in genres_links if re.search(r'>(.*?)</a>', link)])

            content_start = html_content.find("<pre>") + len("<pre>")
            content_end = html_content.find("</pre>")
            
            # If no <pre> tags found, check for <td class="scrtext">
            if content_start == -1 or content_end == -1:
                content_start = html_content.find('<td class="scrtext">') + len('<td class="scrtext">')
                content_end = html_content.find("</td>", content_start)

            if content_start != -1 and content_end != -1:
                content = html_content[content_start:content_end]
                # Remove all HTML comments
                content = re.sub(r"<!--.*?-->", "", content, flags=re.DOTALL)

                content = re.sub(r"<.*?>", "", content)  # Remove remaining HTML tags

                markdown_directory = os.path.join(movie_directory, f"{os.path.splitext(filename)[0]}")
                os.makedirs(markdown_directory, exist_ok=True)

                markdown_filename = os.path.join(markdown_directory, f"{os.path.splitext(filename)[0]}.md")
                with open(markdown_filename, "w", encoding="utf-8") as markdown_file:
                    # Write the YAML front matter
                    markdown_file.write("---\n")
                    markdown_file.write(f"Title: {movie_title}\n")
                    markdown_file.write(f"Writers: {writers}\n")
                    markdown_file.write(f"Genres: {genres}\n")
                    markdown_file.write("---\n\n")

                    # Write the content
                    markdown_file.write(content.strip())

                print(f"Processed: {filename} -> {markdown_filename}")
            else:
                print(f"Warning: No content found in {filename}")
        else:
            print(f"Warning: No movie title found in {filename}")

print("All HTML files processed, and Markdown files created in separate folders.")

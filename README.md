# Sitemapper

The `Sitemapper` script extracts nearly all URLs from a website's sitemap, including those with specific file extensions. It is particularly useful for gaining insights into a website's surface and size.

## Supported File Extensions
The script retains URLs with the following file extensions if they are found:
- `.asp`
- `.aspx`
- `.cgi`
- `.htm`
- `.html`
- `.js`
- `.jsp`
- `.php`
- `.pl`
- `.py`

## How Does It Work?
The script performs a recursive search through the sitemap. If nested sitemaps are found within the primary sitemap, it will also extract URLs from each nested sitemap. The final output is a text file containing all the collected URLs.

This tool was designed to help assess a website's structure and gather a comprehensive list of accessible pages for further analysis.


## Usage
<br>

```
python sitemapper.py
Enter the sitemap URL or domain: https://example.com
```
<br>
Example usage on bug bounty website:
<br>

![image](https://github.com/user-attachments/assets/6594e8eb-7bab-453d-8ff2-976be0f7d702)


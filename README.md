# Sitemapper
Exports almost all URLs from a website's sitemap and also keeps these file extension URLs if found:
<br>

.asp
.aspx
.cgi
.htm
.html
.js
.jsp
.php
.pl
.py

<br>
The search is recursive, so if there are sitemaps within the sitemaps, it will grab all URLs from each sitemap and then export a txt file with everything.
<br>
I used this to get a website's surface/size.
<br>

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


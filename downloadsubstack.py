import requests
from bs4 import BeautifulSoup
import os
import pdfkit

# Replace the path to the wkhtmltopdf executable with the correct path on your system
path_wkhtmltopdf = r'G:\Dev\Python\wkhtmltopdf\bin\wkhtmltopdf.exe'
config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)


# Replace the URL with the URL of the substack archive you want to download
URL = "https://defijangle.substack.com/archive"

# Make a GET request to the URL
#session = requests.session
response = requests.get(URL)

# Check if the request was successful
if response.status_code == 200:
  # Parse the HTML using BeautifulSoup
  soup = BeautifulSoup(response.text, "html.parser")

  # Find all the links on the page
  links = soup.find_all("a")


  #removing comments from the list of links retrieved by soup.findall; we only want posts 

  # Loop through the links
  for link in links:
    # Get the URL of the link
    href = link.get("href")

    # Check if the URL is not None and is a link to a post
    if href is not None and href.startswith("https://defijangle.substack.com/p/"):

      # Remove the "https://" prefix from the URL & / from comments url messing up the execution
      fileName = href.replace("https://", "")
      #this is mainly to clean up the file name and prevent errors in naming convention
      head,sep, tail = fileName.partition('.com/p/')
      tail = tail.replace('/', "")

      # Construct the path to the directory where you want to save the PDF - replace with your directory
      directory = "G:\Dev\Python\webscrapingdownloads"
      file_path = os.path.join(directory, head)

      # Create the directory if it does not exist
      os.makedirs(file_path, exist_ok=True)
      
      # Construct the file path for the new file using the 'tail' variable as the file name
      file_path = os.path.join(file_path, f"{tail}.pdf")

      # Download the post as a PDF (not yet working)
      pdf_response = pdfkit.from_url(href, file_path , configuration=config)


else:
  print("Failed to download page")

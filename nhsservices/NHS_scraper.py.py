import requests
from bs4 import BeautifulSoup
import cloudscraper
import streamlit as st
import pandas as pd

def get_job_listings_url(position, location, miles, page):
    URL = "https://www.jobs.nhs.uk/candidate/search/results?keyword={}&location={}&distance={}&skipPhraseSuggester=true&sort=publicationDateDesc&language=en&page={}"
    return URL.format(position, location, miles, page)

def scrape_job_cards(soup, titles, linker):
    job_card = soup.find_all("li", {"class": "nhsuk-list-panel search-result nhsuk-u-padding-3"})
    for jobs in job_card:
        job_title = jobs.find("h3", {"class": "nhsuk-heading-m nhsuk-u-margin-bottom-2"})
        titles.append(job_title.text.strip())

        pre_links = job_title.find_all("a")
        for link in pre_links:
            linker.append("https://www.jobs.nhs.uk" + link.get("href"))

def scrape_job_details(linker, scraper, direct_links, cos):
    for job_link in linker:
        response2 = scraper.get(job_link)
        soup2 = BeautifulSoup(response2.text, 'html.parser')

        dir_links = soup2.find_all("a", {"class": "nhsuk-button"})
        for dir_link in dir_links:
            direct_links.append("https://www.jobs.nhs.uk" + dir_link.get("href"))

        COS = soup2.find(attrs={'id': 'tier-two-sponsorship'})
        cos.append("Yes" if COS else "No")

def scrape_jobs(position, location, miles, num_pages):
    titles = []
    linker = []
    direct_links = []
    cos = []

    for page in range(1, num_pages + 1):
        url = get_job_listings_url(position, location, miles, page)
        scraper = cloudscraper.create_scraper()
        response = scraper.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        scrape_job_cards(soup, titles, linker)
        scrape_job_details(linker, scraper, direct_links, cos)

    return titles, cos, direct_links

def main():
    st.title("NHS Jobs Scraper App")

    position = st.sidebar.text_input("Enter Position")
    location = st.sidebar.text_input("Enter Location")
    miles = st.sidebar.text_input("Enter Miles")
    num_pages = st.sidebar.number_input("Enter Number of Pages", min_value=1, max_value=10, value=1)

    if st.sidebar.button("Scrape Jobs"):
        st.text("Scraping jobs... Please wait.")
        titles, cos, direct_links = scrape_jobs(position, location, miles, num_pages)

        data = {"Title": titles, "COS": cos, "Direct Link": direct_links}
        

        st.write("## Job Results")
        df = pd.DataFrame.from_dict(data,orient="index")
        df = df.transpose()
        # df = df.sort_values("Closing Date",ascending=False)
        st.table(df)
        
        

if __name__ == "__main__":
    main()
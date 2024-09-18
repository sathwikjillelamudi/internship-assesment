from bs4 import BeautifulSoup
import requests
import json


# Step 1: get access to the main page and scrape state links
response = requests.get('https://www.4icu.org/de/universities/')
data = response.text
soup = BeautifulSoup(data, "html.parser")

# Extract state links and names
state_table = soup.find("table", class_="table")
links = []
names = []
x = "https://www.4icu.org"
for a in state_table.find_all('a'):
    link = a['href']
    full_link = x + link
    links.append(full_link)
    name = a.getText()
    names.append(name)
# print(links)
# print(names)

# List to store universities data
universities_data = []

# Step 2: scrape into each statelink to get university links
for i, link in enumerate(links):
    state_name = names[i]

    # Get each state's page
    response1 = requests.get(link)
    data1 = response1.text
    soup1 = BeautifulSoup(data1, "html.parser")

    # Find universities on that state's page
    university_section = soup1.find("tbody")
    university_links = []

    if university_section:
        for a in university_section.find_all('a'):
            uni_link = a['href']
            full_uni_link = x + uni_link
            university_links.append(full_uni_link)

    # Step 3: Scrape each university page for the details of university
    for uni_link in university_links:
        response_uni = requests.get(uni_link)
        data_uni = response_uni.text
        soup_uni = BeautifulSoup(data_uni, "html.parser")

        # Extract university name
        name_tag = soup_uni.find(name='h1', itemprop='name')
        uni_name = name_tag.getText() if name_tag else None

        # Extract address details
        div_tag = soup_uni.find('div', class_='panel-body', itemprop='address')
        city, state, country = None, None, None
        if div_tag:
            td_tag = div_tag.find('td')
            if td_tag:
                city = td_tag.find('span', itemprop='addressLocality').text if td_tag.find('span',
                                                                                           itemprop='addressLocality') else None
                state = td_tag.find('span', itemprop='addressRegion').text if td_tag.find('span',
                                                                                          itemprop='addressRegion') else state_name
                country = list(td_tag.stripped_strings)[-1] if td_tag else None

        # Extract university logo
        logo_tag = soup_uni.find('img', {'itemprop': 'logo'})
        logo = logo_tag['src'] if logo_tag else None

        # Extract establishment year
        establish_year_span = soup_uni.find('span', {'itemprop': 'foundingDate'})
        establish_year = establish_year_span.text if establish_year_span else None

        # Extract social media links and official website
        contact = {}
        for a in soup_uni.find_all('a'):
            href = a.get('href')
            if href:
                if "facebook.com" in href:
                    contact["facebook"] = href
                elif "twitter.com" in href:
                    contact["twitter"] = href
                elif "youtube.com" in href:
                    contact["youtube"] = href
                elif "instagram.com" in href:
                    contact["instagram"] = href
                elif "linkedin.com" in href:
                    contact["linkedin"] = href

        #  Extract the official website
        a_tag = soup_uni.find('a', itemprop='url')
        if a_tag:
            official_website = a_tag['href']
            contact["officialWebsite"] = official_website  # Add official website to contact links
        else:
            contact["officialWebsite"] = None  # Set to None if not found


        control_div = soup_uni.find('div', class_='col-sm-6 col-md-3')
        if control_div:
            control_type_tag = control_div.find('strong')
            control_type = control_type_tag.text.strip() if control_type_tag else None
        else:
            control_type = "Not specified"


        phone_number = None
        rows = soup_uni.find_all('tr')
        for row in rows:
            th_tag = row.find('th')
            if th_tag and th_tag.find('img') and 'phone' in th_tag.find('img')['src']:
                phone_number = row.find('td').text.strip()
                break
        contact["phone"] = phone_number

        # Create a structured dictionary for each university
        university_info = {
            "name": uni_name,
            "location": {
                "country": country,
                "state": state,
                "city": city
            },
            "logoSrc": logo,
            "type": control_type,
            "establishedYear": establish_year,
            "contact": contact
        }

        # Append to the list
        universities_data.append(university_info)

# Step 4: Export the data to a JSON file
with open('universities__data.json', 'w', encoding='utf-8') as f:
    json.dump(universities_data, f, ensure_ascii=False, indent=4)


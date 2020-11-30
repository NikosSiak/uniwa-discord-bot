from bs4 import BeautifulSoup

from constants import URL


async def fetch_notifications(aiohttp_session):
    with open('data/last_digits.txt', 'r', encoding="utf-8") as f:
        last_digits = [f.readline().strip() for _ in range(5)]

    async with aiohttp_session.get(URL) as r:
        if r.status != 200:
            return []
        page_html = await r.text()

    page_soup = BeautifulSoup(page_html, "html.parser")
    announcements = page_soup.find_all(class_="single_post_row")

    to_send = []
    latest_digits = get_digits_from_link(announcements[0]['data-url'])

    for announcement in announcements:
        title = announcement.find(class_="single_post_title").contents[0].strip()
        link = announcement['data-url']

        digits = get_digits_from_link(link)

        if digits not in last_digits:
            to_send.append([title, link])
        else:
            break

    if latest_digits not in last_digits:
        update_digits(latest_digits, last_digits)

    return to_send


def get_digits_from_link(link):
    digits = ""
    for l in link[::-1]:
        if l.isdigit():
            digits += l
        else:
            break
    digits = digits[::-1]
    return digits


def update_digits(digits: str, old_digits: list):
    # Rotate the list
    old_digits.append(old_digits.pop(0))
    # Replace last digit with new
    old_digits[-1] = digits
    with open('data/last_digits.txt', 'w') as f:
        f.write("\n".join(old_digits))


async def fetch_schedule(programma, aiohttp_session):
    async with aiohttp_session.get(URL) as r:
        if r.status != 200:
            return None, None
        page_html = await r.text()

    page_soup = BeautifulSoup(page_html, "html.parser")
    announcements = page_soup.find_all('div', {'class': 'col-lg-12 col-md-12 col-sm-12 col-xs-12 single_post_row'})
    for announcement in announcements:
        title = announcement.find('div', {'class': 'single_post_title'}).contents[0].strip()
        announcement = str(announcement)
        link = announcement[announcement.find('http'):announcement.find('">')].replace('amp;', '')
        if programma in title.lower():
            return title, link

    return None, None

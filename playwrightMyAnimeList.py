from playwright.sync_api import sync_playwright
from playwright._impl._api_types import TimeoutError as TE
import json
import time

def main():
    anime_list= []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        base_page = "https://myanimelist.net"
        page.goto(f"{base_page}/anime.php")
        page.wait_for_load_state()
        content = page.query_selector(".anime-manga-search")
        tags = content.query_selector_all(".genre-link")
        temp_tag_list = tags[0].query_selector_all('.genre-name-link')
        href = [tag.get_attribute('href') for tag in temp_tag_list]
        anime_dict = {}


        for link in href:
            x=1
            while True:
                try:
                    
                    page.goto(f"{base_page}{link}?page={x}")
                    #page.wait_for_load_state()

                    
                except TE:
                    continue
            
                if page.query_selector('.error404') != None:
                    break
                else:
                    cards = page.query_selector_all('.js-anime-category-producer')
                    for card in cards:
                        title = card.query_selector('.link-title').text_content()
                        subtitle = card.query_selector('.h3_anime_subtitle')
                        if subtitle != None:
                            subtitle = subtitle.text_content()
                        genres = card.query_selector_all('.genre')
                        genre_list = [genre.text_content().strip() for genre in genres]
                        properties = card.query_selector_all('.property')
                        anime_dict = {"title" : title,
                                      "subtitle": subtitle,
                                      "genres": genre_list}
                        for prop in properties:
                            property_name = prop.query_selector('.caption').text_content()
                            if property_name == "Theme" or property_name == "Studio" or property_name == "Demographic":
                                property_name += "s"
                                
                            anime_dict.update({property_name.lower():
                                                    [item.text_content() for item in prop.query_selector_all('.item')]})

                        anime_list.append(anime_dict.copy())

                    x+=1
 
        with open("MyAnimeList.json", "w") as mal:
            json.dump(anime_list, mal)
                     


main()
from playwright.sync_api import sync_playwright
import json

def main():
    '''
    {
        {
            "year": 2006,
            "season": Spring,
            "title": title1
        }
        {
            "year": 2006,
            "season": Spring,
            "title": title2
        }
        ...
        {
            "year": 2008,
            "season": Winter,
            "title": title20
        }
    }
    '''
    seasons=["Spring", "Summer", "Fall", "Winter"]
    years=[y for y in range(2006, 2023)]
    list_of_anime = []
    anime_dict = {}
    i = 0
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        for year in years:
            anime_dict["year"] = year
            for season in seasons:
                anime_dict["season"] = season


                while True:
                    page.goto(f'https://anichart.net/{season}-{str(year)}')
                    page.wait_for_load_state()
                    script_counts = page.eval_on_selector_all("script", "(scripts, min) => scripts.length >= min", 1)
                    if(script_counts):
                        break
                    else:
                        page.close()
                        context = browser.new_context()
                        page = context.new_page()
                
                page.evaluate(
                    """
                    var intervalID = setInterval(function () {
                        var scrollingElement = (document.scrollingElement || document.body);
                        scrollingElement.scrollTop = scrollingElement.scrollHeight;
                    }, 200);

                    """
                )
                prev_height = None
                while True:
                    curr_height = page.evaluate('(window.innerHeight + window.scrollY)')
                    if not prev_height:
                        prev_height = curr_height
                        page.wait_for_timeout(500)
                    elif prev_height == curr_height:
                        page.evaluate('clearInterval(intervalID)')
                        break
                    else:
                        prev_height = curr_height
                        page.wait_for_timeout(500)

                all_cards = page.query_selector_all('.media-card')
                for card in all_cards:
                    overlay = card.query_selector('.overlay')
                    if(overlay!=None):
                        title = overlay.query_selector('.title')
                        anime_dict["title"] = title.text_content()
                        list_of_anime.append(anime_dict.copy())

        with open("AniChart.json", "w") as ac:
            json.dump(list_of_anime, ac)


if __name__ == '__main__':
    main()


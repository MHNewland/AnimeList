# AnimeList

## Description
This application was set up to be able to display a table about Anime scraped from AniChart and MyAnimeList, as well as chart a graph to show how many titles were released by year and season.

## Supported OS
This application is hosted at <a>https://clda2-animelist.streamlit.app</a>.

## Packages needed
No packages are needed as this is hosted on streamlit's website, but these are the packages I used within Python 3.11:
- Streamlit==1.24.1
- SQLAlchemy==2.0.4
- pandas==2.0.3
- playwright==1.33.0
- plotly==5.15.0

# Features
## Creating the data
The data for this application was created by using the playwrite scripts to scrape data off of their respective sites. 
### Anichart
The script playwrightAniChart scrapped the year, season and title from <a>https://anichart.net</a>. Anichart's site is set up where it sorts anime by their year and season and displays them in a dynamic list. By scrollig down, it loads more titles. 

I had the script start at Spring and 2006, then end on Winter on 2023. I waited for the page to load, then checked to make sure the javascript loaded to make sure it would load all of the titles when scrolling. Then I'd have the script keep scrolling down the page until the height didn't change. After getting to the bottom, I scraped the title from each of the cards and added it to a dictionary containing the year and season it was found in.

The format of the json is laid out as follows:
```json
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
        "year": 2023,
        "season": Summer,
        "title": title##
    }
}
```

### MyAnimeList
The script playwrightMyAnimeList.py scraped the title, subtitle, genres, studios, source, themes, and demographics for each anime listed on <a>https://myanimelist.net/anime.php</a>.

The way MyAnimeList is set up is the anime is broken up between genres, themes, demographics, studios, ranking, and seasons.

Because of how the site is set up, I grabbed a list of the genres and looped through them. I then looped through each page for that genre until it hit a 404 error and scraped the previously listed information from each card on each page. If the title existed within the list previously, it would skip over that data.

The format of the json is laid out as follows:
```json
{
    "title": "",
    "subtitle": "",
    "genres": [],
    "studios": [],
    "source": [],
    "themes": [],
    "demographics": []
}
```

## Database creation
In SQLAlchemyORM.py the create_database() function reads through each of the json files and added each value for each title into a database. 

Anichart was easy to add as it only had 3 columns and each had a single value.

MyAnimeList was more difficult due to the number of lists of attributes it had. The process was commented within the code as shown below:
https://github.com/MHNewland/AnimeList/blob/ce74f7cfa46dcc617e9367452b61c871631d176a/SQLAlchemyORM.py#L103-L184

## Clean and merge
In SQLAlchemyORM, the get_full_table() cleans the titles in MyAnimeList before joining the tables together,
due to the differences in how AniChart and MyAnimeLists handle
naming seasons of shows

The titles in MyAnimeList are stripped of saying "season"

If the title ends in 'nd season', 'rd season', or 'th season', and the previous character is a digit, it strips everything after 3 characters before the last instance of the word 'season' so that it grabs everything after the digit. The reason it checks for the character at -10 is to prevent it from breaking titles that end with the word instead of the digit, such as 'second season'.

Also in streamlit.py's get_data() function, it replaces all 'NaN' values with the string 'None' so that 'None' can be used to filter by.

## Visualize the data
Within streamlit.py, after you click the 'Submit' button for the filters, it creates both a chart and a table with the raw data in it below the filters. You can switch between the two views with tabs above the chart or table.

## Best Practices
For each function in  SQLAlchemyORM.py and streamlit.py, I have added documentation as to what the function does as well as what each parameter is. This way, if you hover over the function call, it will show you the information needed rather than having to switch back and forth between the call and the actual function.

## Interpretation of the data
By using the filters and the corresposnding plotly charts, any number of analyses can be made.

Example 1:

![alt text](https://github.com/MHNewland/AnimeList/blob/main/anime-spring.png?raw=true)

![alt text](https://github.com/MHNewland/AnimeList/blob/main/anime-summer.png?raw=true)

![alt text](https://github.com/MHNewland/AnimeList/blob/main/anime-fall.png?raw=true)

![alt text](https://github.com/MHNewland/AnimeList/blob/main/anime-winter.png?raw=true)

Using the images above, we can see that springtime is generally when new titles are released.


Example 2:

![alt text](https://github.com/MHNewland/AnimeList/blob/main/isekai.png?raw=true)

Looking at the image above, we can see that there was a massive spike in the number of isekai anime released. Isekai literally translates to "different world" and it is used to describe a subgenre of light novels, manga, anime, and video games that involve a normal person from Earth being transported to, reborn, or trapped in a parallel universe, usually a fantasy world.

Considering there was a global pandemic that started in 2019 and continued through 2020, plus that anime can typically take about a year to develop, we can draw a possible corelation between the pandemic and the production of the genre.
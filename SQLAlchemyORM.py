from typing import Optional
import sqlalchemy as sa
import sqlalchemy.orm as sao
import json
from copy import deepcopy
import pandas as pd
#AniChart: year, season, title
#MyAnimeList: title, subgenre, genres, studios, source, themes, demographics

class Base(sao.DeclarativeBase):
    pass

#Need to rewrite the AniChart.json/playwrightAniChart.py
'''
AniChart json is formatted as 
[
    {
        "year": int,
        "season": str,
        "title": str
    }
]
'''
class AniChart(Base):
    __tablename__ = "AniChart"

    id: sao.Mapped[int] = sao.mapped_column(primary_key=True)
    year: sao.Mapped[int] =sao.mapped_column(sa.SmallInteger())
    season: sao.Mapped[str] =sao.mapped_column(sa.String(6))
    title: sao.Mapped[str] =sao.mapped_column(sa.String(50), sa.ForeignKey("MyAnimeList.title"))
    #MyAnimeList: sao.Mapped["MyAnimeList"] = sao.relationship(back_populates="title")

    def __repr__(self) -> str:
        return f"AniChart(id={self.id!r}, year={self.year!r}, season={self.season}, title={self.title})"


'''
 MyAnimeList json is formatted as 
[
    {
        "title": "str",
        "subtitle": str/null,
        "genres": list[str]/null,
        "studios": list[str]/null,
        "source": list[str]/null,
        "themes": list[str]/null,
        "demographics": list[str]/null
    }
]
 '''   
class MyAnimeList(Base):
    __tablename__ = "MyAnimeList"

    id: sao.Mapped[int] =sao.mapped_column(primary_key=True)
    title: sao.Mapped[str] =sao.mapped_column(sa.String(50))
    subtitle: sao.Mapped[Optional[str]]
    genres: sao.Mapped[Optional[str]] =sao.mapped_column(sa.String(15))
    studios: sao.Mapped[str] =sao.mapped_column(sa.String(30))
    source: sao.Mapped[str] =sao.mapped_column(sa.String(10))
    themes: sao.Mapped[Optional[str]] = sao.mapped_column(sa.String(15))
    demographics: sao.Mapped[Optional[str]] = sao.mapped_column(sa.String(15))
    #AniChart: sao.Mapped["AniChart"] = sao.relationship(back_populates="title")

    def __repr__(self) -> str:
        returnstr = (
            f"MyAnimeList(id={self.id}, " \
            f"title={self.title}, " \
            f"subtitle={self.subtitle}, " \
            f"genres={self.genres}, " \
            f"studios={self.studios}, " \
            f"source={self.source}, " \
            f"themes={self.themes}, " \
            f"demographics={self.demographics})"
            )
        return returnstr


# def main():
#     #session = create_database()
#     print(read_data())

def create_database():
    try:
        engine = sa.create_engine("sqlite:///database.db", echo=False)
    except Exception as e:
        print(e)
    Base.metadata.create_all(engine)
    with sao.Session(engine) as session:
        anime_items = []
        with open("MyAnimeList.json") as mal:
            for mal_anime in json.load(mal):
                if len(anime_items) > 0:
                    if any(mal_anime["title"] == ai.__getattribute__("title") for ai in anime_items):
                        continue

                mal_obj = MyAnimeList()
                mal_list = [mal_obj]

                for key, value in mal_anime.items():
                    

                    #if value isn't a list, convert it into one to reduce code variance
                    if type(value) != list:
                        value = [value]
                    # if nothing has been set for the initial item's key,
                    # that means it has not been set for any of the items in the list,
                    # add that value to all of the objects in the list.
                    for val in value:
                        if ((mal_list[0].__getattribute__(key)) == None):
                            for obj in mal_list:
                                obj.__setattr__(key,val)
                        # if it has been set, 
                        # make a copy of the object so we don't override the original, 
                        # change the value of the new object to the new value
                        # add it to te list
                        else:
                            temp = deepcopy(obj)
                            temp.__setattr__(key,val)
                            mal_list.append(temp)

                # after going through each key value pair for an anime
                # add all created objects to the items_to_add list
                anime_items.extend(mal_list)

            # add all objects from items_to_add
            session.add_all(anime_items)

        with open("AniChart.json", "r") as ac:
            ac_list = []
            for ac_anime in json.load(ac):
                year, season, title = ac_anime.values()
                ac_list.append(AniChart(year = year, season = season, title = title))
            session.add_all(ac_list)

        # commit to table
        session.commit()    
        return session

def read_data(session = sao.Session(engine:=sa.create_engine("sqlite:///database.db", echo=False)),
              start_year = 2006,
              end_year = 2024,
              seasons = [],
              titles = [],
              genres = [],
              subtitles = [],
              source = [],
              themes = [],
              demographics = []):
    
    joined_tables = sa.select(AniChart.year,
                         AniChart.season,
                         MyAnimeList.title,
                         MyAnimeList.subtitle,
                         MyAnimeList.genres,
                         MyAnimeList.studios,
                         MyAnimeList.source,
                         MyAnimeList.themes,
                         MyAnimeList.demographics
                         ) \
                    .join(AniChart, AniChart.title == MyAnimeList.title)
             

    filtered_table = joined_tables.where(AniChart.year >= start_year) \
                                .where(AniChart.year <= end_year)
    
    if len(seasons) !=0:
        filtered_table = filtered_table.where(AniChart.season.in_(seasons))
    
    if len(titles)!=0:
        filtered_table = filtered_table.where(MyAnimeList.title.in_(titles))

    if len(subtitles) !=0:
        filtered_table = filtered_table.where(MyAnimeList.subtitle.in_(subtitles))
    
    if len(genres) != 0:
        filtered_table = filtered_table.where(MyAnimeList.genres.in_(genres))

    if len(source) != 0:
        filtered_table = filtered_table.where(MyAnimeList.source.in_(source))

    if len(themes) != 0:
        filtered_table = filtered_table.where(MyAnimeList.themes.in_(themes))

    if len(demographics) != 0:
        filtered_table = filtered_table.where(MyAnimeList.demographics.in_(demographics))

    df = pd.DataFrame(session.execute(filtered_table))
    return df


# main()
from typing import Optional
import sqlalchemy as sa
import sqlalchemy.orm as sao
import json
from copy import deepcopy
#AniChart: year, season, title
#MyAnimeList: title, subgenre, genres, studios, source, themes, demographics

class Base(sao.DeclarativeBase):
    pass

#Need to rewrite the AniChart.json/playwrightAniChart.py
'''
AniChart json is formatted as 
year(smallint){
    season(str): [titles(str)]
}
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
 title(str){
    subtitle: subtitle(str, optional)
    genres: [genre(str)]
    Studios: [studio name(str)]
    Source: [source(str)]
    Themes: [theme(str)] (optional)
    Demographics: [demographic(str)]
 }
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
    demographics: sao.Mapped[str] = sao.mapped_column(sa.String(15))
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


def main():
    engine = sa.create_engine("sqlite://", echo=False)
    Base.metadata.create_all(engine)
    with sao.Session(engine) as session:
        anime_items = []
        with open("MyAnimeList.json") as mal:
            for mal_anime in json.load(mal):
                mal_obj = MyAnimeList()
                mal_list = [mal_obj]

                # for each key value pair for the anime
                # if the first item doesn't have a value set for that key
                # add that value for all items in the list
                # if it does have a value
                # create a copy of the object, change the value to the new value and add it to the list of
                for key, value in mal_anime.items():
                    if type(value) != list:
                        value = [value]
                    for val in value:
                        if ((mal_list[0].__getattribute__(key)) == None):
                            for obj in mal_list:
                                obj.__setattr__(key,val)
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

    session = sao.Session(engine)

    ac_stmt = sa.select(AniChart.year, AniChart.title, MyAnimeList.genres). \
                 join(AniChart, AniChart.title == MyAnimeList.title). \
                 distinct(AniChart.title). \
                 where(MyAnimeList.themes == "Isekai")
    
    result = session.execute(ac_stmt).all()

    for i in result:
        print(i)


main()
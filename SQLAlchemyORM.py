from typing import Optional
from typing import List
import sqlalchemy as sa
import sqlalchemy.orm as sao
#AniChart: year, season, title
#MyAnimeList: title, subgenre, genres, studios, source, themes, demographics

class Base(sao.DeclarativeBase):
    pass


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
    title: sao.Mapped[str] =sao.mapped_column(sa.String(50), sa.ForeignKey("AniChart.title"))
    subtitle: sao.Mapped[Optional[str]]
    genres: sao.Mapped[str] =sao.mapped_column(sa.String(15))
    studios: sao.Mapped[str] =sao.mapped_column(sa.String(30))
    source: sao.Mapped[str] =sao.mapped_column(sa.String(10))
    themes: sao.Mapped[Optional[str]]
    demographics: sao.Mapped[List] =sao.mapped_column(sa.String(15))

    def __repr__(self) -> str:
        return f"MyAnimeList( " + \
                    "id={self.id!r}, " + \
                    "title={self.tite!r}, " + \
                    "subtitle={self.subtitle!r}, " + \
                    "genres={self.genres!r})" + \
                    "Studios={self.Studios!r}" + \
                    "Source={self.Source!r}" + \
                    "Themes={self.Themes!r}" + \
                    "Demographics={self.Demographics!r})"

def main():
    engine = sa.create_engine("sqlite://",echo=True)

    Base.metadata.create_all(engine)

    with sao.Session(engine) as session:
        #create objects to represent each item in the tables
        for i in range(10):
            test = AniChart(
                year = i,
                season = "Autumn",
                title = "This is a test"
            )
            session.add(test)
        session.commit()

    session = sao.Session(engine)
    statement = sa.select(AniChart)
    for item in session.scalars(statement):
        print(item)

main()
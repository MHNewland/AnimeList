from typing import Optional
from typing import List
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
    genres: sao.Mapped[Optional[str]] =sao.mapped_column(sa.String(15))
    studios: sao.Mapped[str] =sao.mapped_column(sa.String(30))
    source: sao.Mapped[str] =sao.mapped_column(sa.String(10))
    themes: sao.Mapped[Optional[str]] = sao.mapped_column(sa.String(15))
    demographics: sao.Mapped[str] = sao.mapped_column(sa.String(15))

    def __repr__(self) -> str:
        returnstr = (
            f"MyAnimeList(id={self.id}, " \
            f"title={self.title}, " \
            f"subtitle={self.subtitle}, " \
            f"genres={self.genres}, " \
            f"Studios={self.studios}, " \
            f"Source={self.source}, " \
            f"Themes={self.themes}, " \
            f"Demographics={self.demographics})"
            )
        return returnstr


def iter_dict(dictionary:dict, prev_key="", dict_line=[]):
    #look at each item
    #if the value is a dictionary, call again
    #else, for each value, add "key : value"
    #return the list

    # the way I want it to look like
    # dict1{
    #   sub_dict1: strVal,        
    #   sub_dict2:[strVal1, strVal2]
    # }
    #
    # should add
    # "dict1 : sub_dict1 : strVal"
    # "dict1 : sub_dict2 : strVal1"
    # "dict1 : sub_dict2 : strVal2"
    for key, val in dictionary.items():
        if type(val)==dict:
            iter_dict(val, f"{prev_key}{key} -- ",dict_line)
        else:
            if type(val)==type(None):
                val=[None]
            if type(val)==str:
                val=[val]
            for v in val:
                dict_line.append(f"{prev_key}{key} -- {v}")
    return dict_line


def main():
    engine = sa.create_engine("sqlite://",echo=False)

    Base.metadata.create_all(engine)

    with sao.Session(engine) as session:
        
        with open("./AniChart.json") as acjson:
            ac = json.load(acjson)
            session.add_all(add_all_items(ac, "AniChart"))
        

        with open("./MyAnimeList.json") as maljson:
            mal = json.load(maljson)
            session.add_all(add_all_items(mal, "MyAnimeList"))

        session.commit()

    session = sao.Session(engine)
    statement = sa.select(MyAnimeList).where(MyAnimeList.id<3)
    for line in session.scalars(statement):
        print(f"test: {line}")
    
    statement = sa.select(AniChart).where(AniChart.id<3)
    for line in session.scalars(statement):
        print(f"test: {line}")


def add_all_items(json, class_name):
    items_to_add = []
    prev_title = ""
    class_dict = {
        "MyAnimeList": MyAnimeList,
        "AniChart": AniChart
    }
    obj = object
    for line in iter_dict(json):
        row, col, value = line.split(" -- ")
        col=col.lower()
        #print(f"{row}:{col}:{value}")

        # if the title is the same
        # check if that value exists for that title
        # if it doesn't, 
        #   set the value for every item in the list
        # if the value already exists, 
        #   create another item and set the attribute to the new value
        #   add the new item to the list

        if prev_title =="":
            item=[]
            obj = class_dict[class_name]()
            root_attr = list(class_dict[class_name].__annotations__.keys())[1]
            obj.__setattr__(root_attr, row)
            obj.__setattr__(col,value)
            item.append(obj)
            prev_title=row
        elif row == prev_title:
            if ((item[0].__getattribute__(col)) == None):
                for i in item:
                    i.__setattr__(col,value)
            else:
                temp = deepcopy(i)
                temp.__setattr__(col,value)
                item.append(temp)
        else:
            for x in item:
                items_to_add.append(x)
            item=[]         
            del obj
            obj = class_dict[class_name]()
            obj.__setattr__("title", row)
            obj.__setattr__(col,value)
            item.append(obj)  
            prev_title=row
    return items_to_add


main()
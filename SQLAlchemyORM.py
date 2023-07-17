from typing import Optional
import sqlalchemy as sa
import sqlalchemy.orm as sao
import json
from copy import deepcopy

default_session = sao.Session(engine:=sa.create_engine('sqlite:///database.db', echo=False))

#AniChart: year, season, title
#MyAnimeList: title, subgenre, genres, studios, source, themes, demographics

class Base(sao.DeclarativeBase):
    pass

class AniChart(Base):
    """
    AniChart json is formatted as 
    [
        {
            'year': int,
            'season': str,
            'title': str
        }
    ]
    """    
    __tablename__ = 'AniChart'

    id: sao.Mapped[int] = sao.mapped_column(primary_key=True)
    year: sao.Mapped[int] =sao.mapped_column(sa.SmallInteger())
    season: sao.Mapped[str] =sao.mapped_column(sa.String(6))
    title: sao.Mapped[str] =sao.mapped_column(sa.String(150), sa.ForeignKey('MyAnimeList.title'))

    def __repr__(self) -> str:
        return f'AniChart(id={self.id!r}, year={self.year!r}, season={self.season}, title={self.title})'

   
class MyAnimeList(Base):
    """ 
    MyAnimeList json is formatted as 
    [
        {
            'title': 'str',
            'subtitle': str/null,
            'genres': list[str]/null,
            'studios': list[str]/null,
            'source': list[str]/null,
            'themes': list[str]/null,
            'demographics': list[str]/null
        }
    ]
    """

    __tablename__ = 'MyAnimeList'

    id: sao.Mapped[int] =sao.mapped_column(primary_key=True)
    title: sao.Mapped[str] =sao.mapped_column(sa.String(150))
    subtitle: sao.Mapped[Optional[str]] =sao.mapped_column(sa.String(150))
    genres: sao.Mapped[Optional[str]] =sao.mapped_column(sa.String(15))
    studios: sao.Mapped[str] =sao.mapped_column(sa.String(30))
    source: sao.Mapped[str] =sao.mapped_column(sa.String(10))
    themes: sao.Mapped[Optional[str]] = sao.mapped_column(sa.String(15))
    demographics: sao.Mapped[Optional[str]] = sao.mapped_column(sa.String(15))

    def __repr__(self) -> str:
        returnstr = (
            f'MyAnimeList(id={self.id}, ' \
            f'title={self.title}, ' \
            f'subtitle={self.subtitle}, ' \
            f'genres={self.genres}, ' \
            f'studios={self.studios}, ' \
            f'source={self.source}, ' \
            f'themes={self.themes}, ' \
            f'demographics={self.demographics})'
            )
        return returnstr


def create_database():
    """
    Reads AniChart.json and MyAnimeList.json and creates
    SQLAlchemyORM objects, saving them to a local database.
    """

    try:
        engine = sa.create_engine('sqlite:///database.db', echo=False)
    except Exception as e:
        print(e)
    Base.metadata.create_all(engine)
    with sao.Session(engine) as session:
        anime_items = []
        with open('MyAnimeList.json') as mal:
            for mal_anime in json.load(mal):
                if len(anime_items) > 0:
                    if any(mal_anime['title'] == ai.__getattribute__('title') for ai in anime_items):
                        continue

                mal_obj = MyAnimeList()
                mal_list = [mal_obj]

                for key, value in mal_anime.items():
                    
                    #if value isn't a list, convert it into one to reduce code variance
                    if type(value) != list:
                        value = [value]

                    # figure out how many copies of each row we need to make to update all of
                    # then with the values so that given
                    # {key1: {
                    #   sub_key1: {
                    #       value1,
                    #       value2                           
                    #   }
                    #   sub_key2: {
                    #       value3,
                    #       value4
                    #   }
                    #   sub_key3: {
                    #       value5,
                    #       value6,
                    #       value7
                    #   }
                    # }
                    #
                    # produces
                    #   key1    |   sub_key1    |
                    #---------------------------|
                    #   1       |   value1      | 
                    #   1       |   value2      |
                    #___________________________
                    #
                    #
                    # since there are 2 values in sub_key2, 
                    # get the length of the current list,
                    # create 1 additional copy (num of values - 1)
                    # then for the number of items in each set,
                    # set the value of the new key.
                    # since there are 2 values, it'd set the first 2 values to 'value3'
                    # then the next 2 values to 'value4'
                    #
                    # for v in range(len of values)
                    #   for l in range(len of list)
                    #       mal_list[v*len of list+l] attribute = new value
                    #   
                    # l=1 -> value2
                    # v=0 -> value3
                    # mal_list[0*2+1] -> mal_list[1] -> value2  | value3
                    #    
                    #   key1    |   sub_key1    |   sub_key2    |  
                    #-------------------------------------------|   l,v
                    #   1       |   value1      |   value3      |   0,0 -> 0
                    #   1       |   value2      |   value3      |   1,0 -> 1
                    #   1       |   value1      |   value4      |   0,1 -> 2
                    #   1       |   value2      |   value4      |   1,1 -> 3
                    #___________________________________________
                    #
                    # since there are 3 values in sub_key3, 
                    # get the length of the current list,
                    # create 2 additional copies (num of values - 1)
                    # then for the number of items in each set,
                    # set the value of the new key.
                    # since there are 3 values, it'd set the first 3 values to 'value5'
                    # then the next 3 values to 'value6'
                    # and the next 3 values to 'value7'
                    # 
                    # for v in range(len of values)
                    #   for l in range(len of list)
                    #       mal_list[v*len of list+l] attribute = new value
                    #   
                    # l=2 -> value1  |   value4
                    # v=1 -> value6
                    # mal_list[1*4+2] -> mal_list[6] -> value1  |   value4  |   value6
                    #
                    #
                    #   key1    |   sub_key1    |   sub_key2    |   sub_key3    |
                    #-----------------------------------------------------------|   l,v
                    #   1       |   value1      |   value3      |   value5      |   0,0 -> 0
                    #   1       |   value2      |   value3      |   value5      |   1,0 -> 1
                    #   1       |   value1      |   value4      |   value5      |   2,0 -> 2
                    #   1       |   value2      |   value4      |   value5      |   3,0 -> 3
                    #   1       |   value1      |   value3      |   value6      |   0,1 -> 4
                    #   1       |   value2      |   value3      |   value6      |   1,1 -> 5
                    #   1       |   value1      |   value4      |   value6      |   2,1 -> 6
                    #   1       |   value2      |   value4      |   value6      |   3,1 -> 7
                    #   1       |   value1      |   value3      |   value7      |   0,2 -> 8
                    #   1       |   value2      |   value3      |   value7      |   1,2 -> 9
                    #   1       |   value1      |   value4      |   value7      |   2,2 -> 10
                    #   1       |   value2      |   value4      |   value7      |   3,2 -> 11

                    num_of_values = len(value)
                    num_in_list = len(mal_list)
                    temp_list= []
                    for copies in range(num_of_values-1):
                        temp = deepcopy(mal_list)
                        temp_list.extend(temp)

                    mal_list.extend(temp_list)

                    for v in range(num_of_values):
                      for l in range(num_in_list):
                          mal_list[v*num_in_list+l].__setattr__(key,value[v])


                # after going through each key value pair for an anime
                # add all created objects to the items_to_add list
                anime_items.extend(mal_list)

            # add all objects from items_to_add
            session.add_all(anime_items)

        with open('AniChart.json', 'r') as ac:
            ac_list = []
            for ac_anime in json.load(ac):
                year, season, title = ac_anime.values()
                ac_list.append(AniChart(year = year, season = season, title = title))
            session.add_all(ac_list)

        # commit to table
        session.commit()    
        return session


def get_full_table(session = default_session):
    """
    Creates the select statement to make a joined table between 
    AniChart and MyAnimeList objects.

    If no session was passed, it uses the default session using
    the local database.

    Due to the differences in how AniChart and MyAnimeLists handle
    naming seasons of shows, the titles in MyAnimeList are stripped 
    of saying "season"

    If the title ends in 'nd season', 'rd season', or 'th season', 
    and the previous character is a digit, it strips everything after
    3 characters before the last instance of the word 'season' so 
    that it grabs everything after the digit. The reason it checks 
    for the character at -10 is to prevent it from breaking titles
    that end with the word instead of the digit, such as 'second 
    season'.
    
    Parameters
    ----------
    session : SQLAlchemyORM Session
            The active SQLAlchemyORM Session object
            default: sa.create_engine('sqlite:///database.db', echo=False)

    Returns
    ----------
        SQLAlchemy Select statement:
            Select statment to create or group a table to be manipulated later      
        SQLAlchemyORM Session:
            The active session to preserve data continuity.
    """

    with session:
        for obj in session.scalars(sa.select(MyAnimeList)):
            title = obj.title
        
            if (title[-9:].casefold() == 'nd season' or \
                title[-9:].casefold() == 'rd season' or \
                title[-9:].casefold() == 'th season') and \
                title[-10].isnumeric():
                
                season_index = title.casefold().rfind('season')-3                                   
                obj.title = title[:season_index]

            if title[-9:-1].casefold() == 'season ' and title[-1].isnumeric():
                season_index = title.casefold().rfind('season')
                obj.title = title[:season_index] + title[season_index+6:]
                
               
        #print('making full table')
        joined_tables = sa.select(
                            AniChart.year,
                            AniChart.season,
                            MyAnimeList.title,
                            MyAnimeList.subtitle,
                            MyAnimeList.genres,
                            MyAnimeList.studios,
                            MyAnimeList.source,
                            MyAnimeList.themes,
                            MyAnimeList.demographics
                            ) \
                        .join(target=AniChart, onclause=MyAnimeList.title == AniChart.title)
    #print('returning full table')
    return joined_tables, session


def read_data(session = default_session,
              group_by=[],
              joined_tables=None):
    """
    Groups a given table by the values listed in group_by 
    using the session passed.

    If no session was passed, it uses the default session using
    the local database.

    Creates the joined table if no table is supplied.

    Parameters
    ----------
        session : SQLAlchemyORM Session
            The active SQLAlchemyORM Session object
            default: sa.create_engine('sqlite:///database.db', echo=False)

        group_by : list
            The list of column names as strings to group by.
            If no list is given, it leaves the table alone

        joined_tables : SQLAlchemy Select statement 
            The current SQLAlchemy Select statement for building
            the table wanted.
            If no table was passed, it creates the default table in
            get_full_table()
        
    Returns
    ----------
        SQLAlchemy Select statement:
            Select statment to create or group a table to be manipulated later      
        SQLAlchemyORM Session:
            The active session to preserve data continuity.
    """

    #print('reading data')
    with session:
        if joined_tables == None:
            joined_tables, session = get_full_table(session=session)

        joined_tables = group_table(joined_tables, group_by)
    #print('done reading data')
    return joined_tables, session


def filter_data(session= default_session,
                joined_tables = None,
                start_year = 2006,
                end_year = 2024,
                title = '',
                seasons = [],
                studios = [],
                genres = [],
                source = [],
                themes = [],
                demographics = [],
                group_by = []):
    """
    Creates a SQLAlchemy Select statement with all filters applied using 
    SQLAlchemyORM where functions. All list parameters are treated as an OR.

    Parameters
    ----------
        session : SQLAlchemyORM Session
            The active SQLAlchemyORM Session object
            default: sa.create_engine('sqlite:///database.db', echo=False)

        joined_tables : SQLAlchemy Select statment
            Table that is to be filtered

        start_year : int
            Lower bound for the years the anime released (inclusive) 

        end_year : int
            Upper bound for the years the anime released (inclusive) 
        
        title : str
            String to filter either the title or subtitle with using 'like'
            
        seasons : list[str]
            String relating to time of year the anime released.

        studios : list[str]
            The name of the studio that created the anime.

        genres : list[str]
            The genres of the anime.
            
        source : list[str]
            The source of the anime (e.g. 'Manga').

        themes : list[str]
            The theme of the anime.

        demographics : list[str]
            Who the intended audience for the anime was in Japanese terms.

        group_by : list[str]
            List of columns to group values from.

    Returns
    ----------
        SQLAlchemy Select statement:
            Select statment for a table with the filters applieid in 'where' clauses
            to be manipulated later.
        SQLAlchemyORM Session:
            The active session to preserve data continuity.
    """

    with session:
        #print('filtering data')
        if joined_tables == None:
            joined_tables, session = get_full_table(session= session, group_by=group_by)

        #print('filtering year')
        filtered_table = joined_tables.where(AniChart.year >= start_year) \
                                    .where(AniChart.year <= end_year)
        #print('filtering title')
        if title != '':
            filtered_table = filtered_table.where(sa.or_(
                MyAnimeList.title.like('%'+title+'%'),
                MyAnimeList.subtitle.like('%'+title+'%')
            ))
        #print('filtering seasons')
        if len(seasons) !=0:
            filtered_table = filtered_table.where(AniChart.season.in_(seasons))

        #print('filtering studios')        
        if len(studios) !=0:
            filtered_table = filtered_table.where(MyAnimeList.studios.in_(studios))
        
        #print('filtering genres')                
        if len(genres) != 0:
            if 'None' in genres:
                filtered_table = filtered_table.where(
                    sa.or_(
                        MyAnimeList.genres.in_(genres), 
                        MyAnimeList.genres ==None
                    )
                )
            else:
                filtered_table = filtered_table.where(MyAnimeList.genres.in_(genres))

        #print('filtering sources')        
        if len(source) != 0:
            if 'None' in source:
                filtered_table = filtered_table.where(
                    sa.or_(
                        MyAnimeList.source.in_(source), 
                        MyAnimeList.source ==None
                    )
                )
            else:
                filtered_table = filtered_table.where(MyAnimeList.source.in_(source))

        #print('filtering themes')        
        if len(themes) != 0:
            if 'None' in themes:
                filtered_table = filtered_table.where(
                    sa.or_(
                        MyAnimeList.themes.in_(themes), 
                        MyAnimeList.themes ==None
                    )
                )
            else:
                filtered_table = filtered_table.where(MyAnimeList.themes.in_(themes))

        #print('filtering demographics')        
        if len(demographics) != 0:
            if 'None' in demographics:
                filtered_table = filtered_table.where(
                    sa.or_(
                        MyAnimeList.demographics.in_(demographics), 
                        MyAnimeList.demographics ==None
                    )
                )
            else:
                filtered_table = filtered_table.where(MyAnimeList.demographics.in_(demographics))

    #print('done filtering data')
    return filtered_table, session

def group_table(table, groupby=[]):
    """
    Groups the provided table by the columns specified. 
    If no table is specified, it returns 'None'.
    If no groupby is provided, it returns the table.

    Parameters
    ----------
        table : SQLAlchemy Select statement
            The select statement to add the group_by method to.

        group_by : list[str]
            List of columns to group values from.
        
    Returns
    ----------
        SQLAlchemy Select statement:
            Select statment for a table with the filters applieid in 'where' clauses
            to be manipulated later.
        SQLAlchemyORM Session:
            The active session to preserve data continuity.    
    """
    if table == None:
        return
    
    if groupby==[]:
        return table
    
    return table.group_by(*groupby)

def execute_table(table, session = default_session):
    """
    Executes the select statement in 'table' to create a Result.

    Parameters
    ----------
        table : SQLAlchemy Select statement
            The select statement to add the group_by method to.

        session : SQLAlchemyORM Session
            The active SQLAlchemyORM Session object
            default: sa.create_engine('sqlite:///database.db', echo=False)
        
    Returns
    ----------
        Result[_T@execute]:
            The result of the executed table
        SQLAlchemyORM Session:
            The active session to preserve data continuity.    
    """

    if table != None:
        table = session.execute(table)
    return table, session
    

# def main():
#     session = create_database()
#     # print(pd.DataFrame(read_data()))

# main()
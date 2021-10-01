"""
Project for Week 4 of "Python Data Visualization".
Unify data via common country codes.
Be sure to read the project description page for further information
about the expected behavior of the program.
"""

import csv
import math
import pygal

def read_csv_as_list_dict(file_name, separator, quote):
    """
    Inputs:
      filename  - name of CSV file
      separator - character that separates fields
      quote     - character used to optionally quote fields
    Output:
      Returns a list of dictionaries where each item in the list
      corresponds to a row in the CSV file.  The dictionaries in the
      list map the field names to the field values for that row.
    """
    csv_dict={}
    list_dict=[]
    with open (file_name,"rt",newline='') as csv_file:
        csv_reader = csv.DictReader(csv_file,delimiter=separator,quotechar=quote)

        for row in csv_reader:
            csv_dict = {key: value for key, value in row.items()}

            list_dict.append(csv_dict)

    return list_dict


def build_country_code_converter(codeinfo):
    """
    Inputs:
      codeinfo      - A country code information dictionary
    Output:
      A dictionary whose keys are plot country codes and values
      are world bank country codes, where the code fields in the
      code file are specified in codeinfo.
    """
    dict1={}
    data=read_csv_as_list_dict(codeinfo['codefile'], codeinfo['separator'], codeinfo['quote'])
    First_Code=codeinfo['plot_codes']
    Second_Code=codeinfo['data_codes']

    for idx in range(len(data)):
        dict1[data[idx][First_Code]]=data[idx][Second_Code]

    return dict1



def reconcile_countries_by_code(codeinfo, plot_countries, gdp_countries):
    """
    Inputs:
      codeinfo       - A country code information dictionary
      plot_countries - Dictionary whose keys are plot library country codes
                       and values are the corresponding country name
      gdp_countries  - Dictionary whose keys are country codes used in GDP data
    Output:
      A tuple containing a dictionary and a set.  The dictionary maps
      country codes from plot_countries to country codes from
      gdp_countries.  The set contains the country codes from
      plot_countries that did not have a country with a corresponding
      code in gdp_countries.
      Note that all codes should be compared in a case-insensitive
      way.  However, the returned dictionary and set should include
      the codes with the exact same case as they have in
      plot_countries and gdp_countries.
    """
    Codes=build_country_code_converter(codeinfo)
    Codes_lowercase=dict((k.lower(), v.lower()) for k,v in Codes.items())

    output_dict={}
    output_set=set()
    count=0

    for key_plot in plot_countries.keys():
        if(len(gdp_countries)==0):
            output_set.add(key_plot)
        for key_gdp in gdp_countries.keys():
            try:
                if(Codes_lowercase[key_plot.lower()] ==key_gdp.lower()):
                        output_dict[key_plot]=key_gdp
                else:
                    count+=1
                    if(count==len(gdp_countries)):
                        output_set.add(key_plot)
            except:
                output_set.add(key_plot)
        count=0

    if(len(gdp_countries)==0):
        return {}, output_set
    else:
        return output_dict, output_set



def build_map_dict_by_code(gdpinfo, codeinfo, plot_countries, year):
    """
    Inputs:
      gdpinfo        - A GDP information dictionary
      codeinfo       - A country code information dictionary
      plot_countries - Dictionary mapping plot library country codes to country names
      year           - String year for which to create GDP mapping
    Output:
      A tuple containing a dictionary and two sets.  The dictionary
      maps country codes from plot_countries to the log (base 10) of
      the GDP value for that country in the specified year.  The first
      set contains the country codes from plot_countries that were not
      found in the GDP data file.  The second set contains the country
      codes from plot_countries that were found in the GDP data file, but
      have no GDP data for the specified year.
    """
    list_of_dict=read_csv_as_list_dict(gdpinfo['gdpfile'], gdpinfo['separator'], gdpinfo['quote'])

    gdp_countries={}
    for index in range(len(list_of_dict)):
        gdp_countries[list_of_dict[index][gdpinfo['country_code']]]=''

    reconsiled=reconcile_countries_by_code(codeinfo, plot_countries, gdp_countries)

    dict1={}
    set1=set()
    set2=set()

    for key_plot,value_plot in reconsiled[0].items():
        idx_not_found=0
        for index in range(len(list_of_dict)):
            if(value_plot == list_of_dict[index][gdpinfo['country_code']]):
                try:
                    dict1[key_plot]=math.log(float(list_of_dict[index][year]),10)
                except:
                    set2.add(key_plot)
                    break
    set1=reconsiled[1]
    return dict1,set1,set2


def render_world_map(gdpinfo,codeinfo, plot_countries, year, map_file):
    """
    Inputs:
      gdpinfo        - A GDP information dictionary
      codeinfo       - A country code information dictionary
      plot_countries - Dictionary mapping plot library country codes to country names
      year           - String year of data
      map_file       - String that is the output map file name
    Output:
      Returns None.
    Action:
      Creates a world map plot of the GDP data in gdp_mapping and outputs
      it to a file named by svg_filename.
    """

    data=build_map_dict_by_code(gdpinfo,codeinfo, plot_countries, year)
    worldmap_chart = pygal.maps.world.World()
    worldmap_chart.title = 'GDP by country for '+year+' (log scale), unified by common country NAME'
    worldmap_chart.add('GDP for '+year, data[0])
    worldmap_chart.add('Missing from World Bank Data',data[1])
    worldmap_chart.add('No GDP Data',data[2])
    worldmap_chart.render_to_file(map_file)
    return


def test_render_world_map():
    """
    Test the project code for several years
    """
    gdpinfo = {
        "gdpfile": "isp_gdp.csv",
        "separator": ",",
        "quote": '"',
        "min_year": 1960,
        "max_year": 2015,
        "country_name": "Country Name",
        "country_code": "Country Code"
    }

    codeinfo = {
        "codefile": "isp_country_codes.csv",
        "separator": ",",
        "quote": '"',
        "plot_codes": "ISO3166-1-Alpha-2",
        "data_codes": "ISO3166-1-Alpha-3"
    }

    # Get pygal country code map
    pygal_countries = pygal.maps.world.COUNTRIES

    # 1960
    render_world_map(gdpinfo, codeinfo, pygal_countries, "1960", "isp_gdp_world_code_1960.svg")

    # 1980
    render_world_map(gdpinfo, codeinfo, pygal_countries, "1980", "isp_gdp_world_code_1980.svg")

    # 2000
    render_world_map(gdpinfo, codeinfo, pygal_countries, "2000", "isp_gdp_world_code_2000.svg")

    # 2010
    render_world_map(gdpinfo, codeinfo, pygal_countries, "2010", "isp_gdp_world_code_2010.svg")


#test_render_world_map()
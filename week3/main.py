#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Unify data via common country name. Use pygal library to plot world map data with the GDP of each country.
"""

import csv
import math
import pygal


def read_csv_as_nested_dict(filename, keyfield, separator, quote):
    """
    Inputs:
      filename  - Name of CSV file
      keyfield  - Field to use as key for rows
      separator - Character that separates fields
      quote     - Character used to optionally quote fields
    Output:
      Returns a dictionary of dictionaries where the outer dictionary
      maps the value in the key_field to the corresponding row in the
      CSV file.  The inner dictionaries map the field names to the
      field values for that row.
    """
    table = {}
    with open(filename, newline='') as csvfile:
        csvreader = csv.DictReader(csvfile, delimiter=separator, quotechar=quote)
        for row in csvreader:
            rowid = row[keyfield]
            table[rowid] = row
    return table


def reconcile_countries_by_name(plot_countries, gdp_countries):
    "returns dictionary that has countryId and countryName touples which are not present in the gdp_countries"""
    #initialising
    dic = {}
    lis = []
    #iterating values
    for keys in plot_countries:
        for key in gdp_countries:
            if plot_countries[keys] == key:
                dic[keys] = key
    for keys in plot_countries:
        if keys not in dic.keys():
            lis.append(keys)
    return dic, set(lis)


def build_map_dict_by_name(gdpinfo, plot_countries, year):
    """
    Inputs:
      gdpinfo        - A GDP information dictionary
      plot_countries - Dictionary whose keys are plot library country codes
                       and values are the corresponding country name
      year           - String year to create GDP mapping for
    Output:
      A tuple containing a dictionary and two sets.  The dictionary
      maps country names from plot_countries to the log (base 10) of
      the GDP value for that country in the specified year.  The first
      set contains the country names from plot_countries that were not
      found in the GDP data file.  The second set contains the country
      names from plot_countries that were found in the GDP data file, but
      have no GDP data for the specified year.
    """
    gdp = {}  # for the first element of tuple
    nocountry = set()  # countries not found in GDP data file
    nodata = set()  # counties that did not have any GDP
    filename = gdpinfo['gdpfile']
    keyfield = gdpinfo['country_name']
    separator = gdpinfo['separator']
    quote = gdpinfo['quote']
    stat = read_csv_as_nested_dict(filename, keyfield, separator, quote)

    for code in plot_countries:
        # if country names match
        if plot_countries[code] in stat:
            # the keys of dictionary are strings such as '2005' and values such as '5'
            yrs = stat[plot_countries[code]]
            for key in yrs:
                # checks to go to the right year such as '2005'
                if (key == year) and (yrs[key] != '' or yrs[key] != ""):
                    # map the log10 value of yrs[key] to the gdp dictionary
                    gdp[code] = math.log10(float(yrs[key]))
                # checks to see if country is found but has no value for GDP
                elif (key == year) and (yrs[key] == '' or yrs[key] == ""):
                    nodata.add(code)
        # final option is that the country code was not found in the file
        else:
            nocountry.add(code)
    return (gdp, nocountry, nodata)


def render_world_map(gdpinfo, plot_countries, year, map_file):
    """
    Inputs:
      gdpinfo        - A GDP information dictionary
      plot_countries - Dictionary whose keys are plot library country codes
                       and values are the corresponding country name
      year           - String year to create GDP mapping for
      map_file       - Name of output file to create
    Output:
      Returns None.
    Action:
      Creates a world map plot of the GDP data for the given year and
      writes it to a file named by map_file.
    """
    mapdata = build_map_dict_by_name(gdpinfo, plot_countries, year)
    gdpdict = mapdata[0]  # the GDP dictionary
    notinfile = mapdata[1]  # set of country codes not present in file
    nogdp = mapdata[2]  # set of country's with no gdp value

    worldmap = pygal.maps.world.World()
    worldmap.title = "GDP by country for " + year + " (log scale), " + "unified by common country NAME"
    # shades of counties are different between all three adds or datasets
    worldmap.add("GDP for " + year, gdpdict)
    worldmap.add("Missing from World Bank Data", notinfile)
    worldmap.add("No GDP data", nogdp)
    worldmap.render_to_file(map_file)


def test_render_world_map():
    """
    Test the project code for several years.
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

    # Get pygal country code map
    pygal_countries = pygal.maps.world.COUNTRIES

    # 1960
    render_world_map(gdpinfo, pygal_countries, "1960", "isp_gdp_world_name_1960.svg")

    # 1980
    render_world_map(gdpinfo, pygal_countries, "1980", "isp_gdp_world_name_1980.svg")

    # 2000
    render_world_map(gdpinfo, pygal_countries, "2000", "isp_gdp_world_name_2000.svg")

    # 2010
    render_world_map(gdpinfo, pygal_countries, "2010", "isp_gdp_world_name_2010.svg")


#test_render_world_map()
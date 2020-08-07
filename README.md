# Toronto Apartment Finder

This is a bot that will scrape all listings off Viewit and then using the filters that you have selected will post each listing to slack for you to be able to get a condensed view of all rental options matching your criteria.

# Filters

* Price Range
* Closest Subway Station
* Distance to Closest Subway Station
* Walking Distance to Closest Subway Station
* Commute Time to Work via Subway/Bus/Walking

# Implementation

After the bot has scraped all listings on Viewit, it will reference a sqlite database to remove all duplicates. Then it will apply the filter selection through Viewit pricing, and use the address from Viewit to grab GPS coordinates from Google Maps. It will then use those GPS coordinates and again reference Google Maps API to get various distance filter selections. Once the filtering is complete, it will format all of the new available listings into appropriate Slack messages and push them using Slack's API.

The default Slack message format is a picture of the listing, as well as hyperlinks to the listing, phone number, any emails that are provided, as well as the filter criteria selection displayed. This can be changed in the settings file if needed.

This project was inspired by [Ian Whitesone]("https://github.com/ian-whitestone/toronto-apartment-finder"), please feel free to check him out.


# LibGen Scraper

This tools will scrape all relevant results to your inputted term after fetching term into libgen search engine.

Then cach/save all results into Data Base with full informations.


## Usage/Examples

Just need to run following file to start a new fetching session

```bash
python main.py
```

## Notes

- When you try to execute a certain SQL Query, if your entry data has single or double qoute chars (dependent to your query used chars) you will take SQL Exception ... !

You can easily handle it with just replacing one of this chars (single or double quotes) then write your SQL Query based on other one

[check my replacements in fetchTermInLibGenSearchEngine() func]


## Authors

- [@AmirAM03](https://github.com/AmirAM03)


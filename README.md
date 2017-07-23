# Quality Content Synthesizer #
#### ____Rates search results based on their content, for a given query____ ####
#### Link: <https://unsupervised-spider.herokuapp.com/> #### 
- - - -
## PROBLEM STATEMENT ##
    Create a tool that could scrawl the web on a specific topic and create a synthesis of the content found – the challenge is to
    mitigate the sources depending on their quality. Solution should be show content from various sources and rate those sources 
    based on the quality of content. Also, solution should be able to crawl automatically and learn from the content and the source.

- - - -
## STEPS INVOLVED ##
    1. Input the query from the user.
    2. Convert that text query into a search query url to gather results from various search engines such as Google, Yahoo, Bing and DuckDuckGo.
    3. Scrape the results' webpages using our Custom Parser and store the results in a file.
    4. Visit each link gathered in the above step and get the content of the webpage.
    5. Process each webpage and rank them solely on the basis of the content with the help of our Custom Ranking algorithm.
    6. Render results to the user.

- - - -
## WEB CRAWLING SPIDER ##
    To acquire a set of relevant sites that serve the content related to the keywords entered, the first step is to boot the spider with the keywords and let it gather links from 4 major search engines:
        * Google
        * Bing
        * Yahoo
        * DuckDuckGo

- - - -
## RATING ALGORITHM ##
    The Algorithm would compare all results with each other and return the results containing the most common information.

- - - -
## RESULTS ###

- - - -
## SCALIBILITY ###

- - - -
## TECHNOLOGY STACK ##
#### Python (Language) #####
    * NumPy
    * SciPy
    * BeautifulSoup
    * Requests
    * Tornado
#### HTML5/CSS3 (Web Develeopment) #####
#### JavaScript/JQuery (Web Development) #####
#### Materialize CSS (Web Framework) #####
#### Heroku Server (Deployment Server) #####




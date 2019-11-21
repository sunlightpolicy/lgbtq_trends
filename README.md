# LGBTQ trends
Code and functions for content analysis of federal websites

## Background
These scripts were used in the analysis for Sunlight Foundation's [Identity, Protections, and Data Coverage: How LGBTQ-related language and content has changed under the Trump Administration](https://sunlightfoundation.com/web-integrity-project/), which looks at how the use of LGBTQ-related terms has changed between the Obama and Trump administrations across federal department websites.

## Methodology
We pooled together a set of WIP-identified URLs (1) with a set of URLs coming
from a search of specific terms on the usa.gov search engine (2).
For each URL, these scripts fetch the latest available IAWM "snapshot" for the "pre" inauguration and "post" inauguration period and count the number of times that a
set of terms appear in the "visible text" of the webpage.

To analyze the text from our set of web pages these scripts adapt [EDGI’s
code](https://github.com/ericnost/EDGI) and extend its functionality to
support sentiment analysis that is tailored to the set of analyzed URLs.
To compare websites before and after the 2017 inauguration, we rely
on websites archived on the Internet Archive’s Wayback Machine [IAWM](https://archive.org/web/) website archives.

Read more about the methodology [here](https://sunlightfoundation.com/web-integrity-project/)

## Results
Our analysis of almost 150 federal government webpages on LGBTQ-related topics, all of which were created before President Trump took office and continue to be live on the web, reveals that, under the Trump administration, federal government webpages addressing LGBTQ-related topics use the terms “gender” and “transgender” more and the terms “sex” less. However, there is considerable variation between departments and within departments.

Our analysis of 1,875 HHS.gov webpages on all topics for LGBTQ-related terms, showed that LGBTQ-related terms are used less often under the Trump administration with a 25% reduction in the use of the term “gender” and a 40% reduction in the use of “transgender.”
By contrast, the use of terms like “faith-based and community organizations,” “religious freedom,” and “conscience protection” all increased markedly.

Our examination of key case studies of changed LGBTQ-related content on federal agency websites identifies two key trends: 
1. The removal of access to resources about discrimination protections and prevention, especially for transgender individuals
2. The removal of resources containing LGBTQ community-specific information


**Figure. Absolute Changes by Department, August 2019**
![Image](https://github.com/sunlightpolicy/lgbtq_trends/blob/master/src/images/fig3.png "Changes by department")

Read more about our results [here](https://sunlightfoundation.com/web-integrity-project/)

## Repository structure
This repository's structure is as follows:

```
.
├── README.md                         
├── requirements.txt                 
└── src/                             # Contains all code and outputs
    ├── content_analysis.ipynb       # Analysis and results notebook, generic version available
    ├── data_detail.csv              # Metadata for obtained url set
    ├── images/                      # Contains image .png files with corresponding .csv file
    ├── inputs/                      # Contains input and intermediate files
    │    ├── departments_final.csv            # Department names
    │    ├── final_urls_for_visual_check.csv  # URLs for visual check (intermediate)
    │    ├── hhslinks_final.csv               # Final links for hhs analysis (from wayback machine)    
    │    ├── links_final.csv                  # Final links for content analysis  
    │    ├── usagovsearch_urls.csv            # Queries to get second set of URLs (intermediate)
    │    └── wip_identified.csv               # First set of WIP identified URLs  
    └── scripts/                     # Contains all code for this project
         ├── analysis.py                      # Main analysis functions
         ├── chromedriver                     # Driver for webscraping
         ├── get_content.py                   # Content extraction functions
         ├── internetarchive.py               # EDGI module
         ├── sentiment_analysis.py            # Sentiment analysis functions
         └── utils.py                         # EDGI module
```

## Requirements
- Python 3.x
- For the sentiment analysis you will need to make sure that the `pysentiment`
package is correctly installed:

  `pip install git+https://github.com/hanzhichao2000/pysentiment`

  If the [static folder](https://github.com/hanzhichao2000/pysentiment/tree/master/pysentiment/static) does not download, you will need to download it and then
  copy it to your python packages `pysentiment`folder, which should look like this:

  `cp -R STATIC YOUR_DOWNLOAD_PATH '/usr/local/lib/python3.7/site-packages/pysentiment'`
- To run `selenium` you will need to make sure that your Chrome Browser's version (which you can check on your browser's menu: `Chrome > About Chrome`) matches the provided ChromeDriver version (76.0.3809.126). You can download and substitute the driver with the latest [version](https://sites.google.com/a/chromium.org/chromedriver/downloads).

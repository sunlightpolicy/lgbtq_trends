# LGBTQ trends
Code for content analysis of federal websites

## Background
These scripts perform the analysis for Sunlight Foundation's [REPORT NAME HERE](https://linktoreport), which looks at how the use of LGBTQ-related terms has changed
between the Obama and Trump administrations across federal department websites.

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

Read more about the methodology [here](https://linktoreport)

## Results
We find that, on the aggregate, there has been a modest increase in the use of
LGBTQ-related terms across the analyzed domains, mainly driven by changes in the
HHS domain, and that their relative importance has barely changed. However, at
the department level, we find that out of the eleven departments that we
analyzed, seven saw decreases in the use of LGBTQ-related terms. Some
departments saw some degree of substitution, using more inclusive terms, whereas
others, like HUD, saw decreases across the board.

**Figure 1. Absolute Changes by Department**
![Image](https://github.com/sunlightpolicy/lgbtq_trends/blob/master/images/changes_department.png "Changes by department")

Read more about our results [here](https://linktoreport)

## Requirements
- Python 3.x
- For the sentiment analysis you will need to make sure that the `pysentiment`
package is correctly installed:

  `pip install git+https://github.com/hanzhichao2000/pysentiment`

  If the [static folder](https://github.com/hanzhichao2000/pysentiment/tree/master/pysentiment/static) does not download, you will need to download it and then
  copy it to your python packages location, which should look like this:

  `cp -R STATIC YOUR_DOWNLOAD_PATH '/usr/local/lib/python3.7/site-packages/pysentiment'`

## Repository structure
This repository's structure is as follows:

```
.
├── README.md                         
├── requirements.txt                 
└── src/                             # Contains all code and outputs
    ├── content_analysis.ipynb       # Shows the analysis and results
    ├── images/                      # Contains image .png files
    ├── inputs/                      # Contains input and intermediary files
    ├── outputs/                     # Contains all generated output files
    └── scripts/                     # Contains all code for this project
```

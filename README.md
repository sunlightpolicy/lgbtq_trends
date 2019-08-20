# LGBTQ trends
Code for content analysis of federal websites

## Background
These scripts handle the data used for Sunlight Foundation's [REPORT NAME HERE](https://link to the report),
which looks at how the use of LGBTQ-related terms has changed between the Obama
and Trump administrations, to describe broad trends that might reflect changing
policy stances or attitudes vis a vis the former previous administration’s
policy on LGBTQ rights.

## Introduction
To analyze the text from our set of web pages these scripts adap [EDGI’s
code](https://github.com/ericnost/EDGI) and extend its functionality to
support sentiment analysis that is tailored to the set of analyzed URLs.
To compare websites before and after the 2017 inauguration, we rely
on websites archived on the Internet Archive’s Wayback Machine [IAWM](https://archive.org/web/) website archives.

## Requirements
- Python 3.x
- For the sentiment analysis you will need to make sure that the `pysentiment`
package is correctly installed:
`pip install git+https://github.com/hanzhichao2000/pysentiment`
If the "static" folder does not download, you will need to download it and then
copy it to your python packages location, which should look like this:
`cp -R STATIC FOLDER LOCATION '/usr/local/lib/python3.7/site-packages/pysentiment'`

## Methodology
We pooled together a set of WIP-identified URLs (1) with a set of URLs coming
from a search of specific terms on the usa.gov search engine (2).
For each URL, these scripts fetch the latest available IAWM "snapshot" for the "pre" inauguration and "post" inauguration period.

Read more about the methodology [here](https://link to the report)

## Results
We find that, on the aggregate, there has been a modest increase in the use of
LGBTQ-related terms across the analyzed domains, mainly driven by changes in the
HHS domain, and that their relative importance has barely changed. However, at
the department level, we find that out of the eleven departments that we
analyzed, seven saw decreases in the use of LGBTQ-related terms. Some
departments saw some degree of substitution, using more inclusive terms, whereas
others, like HUD, saw decreases across the board.

![alt text](https://github.com/sunlightpolicy/lgbtq_trends/images/changes_department.png "Changes by department")

Read more about our results [here](https://link to the report)

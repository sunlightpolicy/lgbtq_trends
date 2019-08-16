# LGBTQ trends
Code for content analysis of federal websites

## Background
These scripts handle the data used for Sunlight Foundation's REPORT NAME HERE,
which looks at how the use of LGBTQ-related terms has changed between the Obama
and Trump administrations, to describe broad trends that might reflect changing
policy stances or attitudes vis a vis the former previous administration’s
policy on LGBTQ rights.

## Introduction
To analyze the text from our set of web pages these scripts adapted EDGI’s
code and extend its functionality to support sentiment analysis that is
tailored to the set of analyzed URLs. In order to compare websites before
and after the 2017 inauguration, we relied on websites archived on the Internet
Archive’s website archives.


## Methodology
In order to explore broad trends across federal government domains, we pooled
together a set of WIP-identified URLs (1) with a set of URLs coming from a
search of specific terms on the usa.gov search engine (2). Set (1) comes from
WIP’s web tracking activities, through which we have identified domains and
particular URLs that have had changes to LGBTQ content or that have been
perceived as being susceptible to having them because of the nature of their
content.

Set (2), the usa.gov set of URLs comes from scraping the results of the first
five pages from the search of eight key terms: lgbtq, lgbt, transgender, gay,
lesbian, bisexual, queer, transgender; representing a potential set of up to 800
websites. See functions (X and Y on module XX)

These scripts apply the following rules to the scraped URLs:
1. Only URLs from federal government (.gov) domains were considered. That is,
web pages belonging to state or local governments were systematically excluded.
2. Non HTML formats (pdf, doc, docx, rtf) were also excluded from the analysis
as the program developed for this analysis does not yet support them.
3. Web pages that are likely to be constantly updated because of the nature of their content were excluded to the extent possible (news, blogs).
4. Non-english websites were excluded from the analysis.

Finally, we intersected both sets, which resulted in 282 web pages.

---
title: Listed building outlines
description: The boundary of the area relating to a listed building which is protected because it has special architectural or historic interest
template: consideration
stage: On the platform
datasets:
- listed-building-grade
- listed-building-outline
- listed-building
frequency_of_updates: Fortnightly
legislation:
  text: Planning (Listed Buildings and Conservation Areas) Act 1990
  url: https://www.legislation.gov.uk/ukpga/1990/9/contents
specification:
  text: Listed building outline
  url: https://digital-land.github.io/specification/specification/listed-building/
useful_links:
- text: Design process document
  url: https://docs.google.com/document/d/1BoTm7kmESHZLBNJibuvdVaMsF3odKsKGLXlPnf-8gFY/edit?usp=sharing
- text: Data dependency document
  url: https://docs.google.com/document/d/1SJBxZ_pKY1BL9aTckboKS6u6nqwZJOk4_buY9SKJ3Xg/edit
- text: The listing process (Historic England)
  url: https://historicengland.org.uk/listing/apply-for-listing/listing-process/
tags:
- local land charge
- local plan
github_discussion_number: 44
created: 2024-03-25
updated: 2025-03-24
---
## Backlog

### Who asked for 'Listed building outlines' data?

Open Systems Lab - Planning Software, specifically as constraint in PlanX

### What is the driver for the request?

Specific user requirement

### Which 2024 focus area does the request support?

Modern planning software

## Screen

### What is the 'Listed building outlines' consideration?

A building which is protected because it has special architectural or historic interest.

### Is there legislation that defines 'Listed building outlines'?

Yes

### What is the legislation that defines 'Listed building outlines'?

[Planning (Listed Buildings and Conservation Areas) Act 1990, Chapter 1](https://www.legislation.gov.uk/ukpga/1990/9/part/I/chapter/1 )

### What is the specific part of the legislation that describes how a 'Listed building outlines' gets designated?

There is no legislation covering how a listed building gets designated.
A web page produced by Historic England can be found [here](https://historicengland.org.uk/listing/apply-for-listing/listing-process/) which outlines the process and the different steps in designating a listing.

[Planning (Listed Buildings and Conservation Areas) Act 1990, Section 1](https://www.legislation.gov.uk/ukpga/1990/9/section/1) - 

One part of the designation process is highlighted in this section of legislation, being the need for the SoS to consult with “The Commission” (Historic England) and other people / bodies who have special knowledge or interest in the building.

### What is the specific part of the legislation that requires the publication of 'Listed building outlines'?

[Chapter 1, Section 2](https://www.legislation.gov.uk/ukpga/1990/9/section/2) - “Publication of Lists”  
(4) The Secretary of State shall keep available for public inspection free of charge at reasonable hours and at a convenient place, copies of all lists and amendments of lists, compiled, approved or made by him under section 1.
(5) Every authority with whom copies of any list or amendments are deposited under this section shall similarly keep available copies of so much of any such list or amendment as relates to buildings within their area.
(6) For the purposes of subsection (5) the Commission shall be taken to be an authority whose area is Greater London.

[Chapter 1, Section 1](https://www.legislation.gov.uk/ukpga/1990/9/part/I/chapter/1 ) provides more specificity around the SoS and “the Commission” compiling the list. 
“The Secretary of State shall compile lists of such buildings, or approve, with or without modifications, such lists compiled by the Historic Buildings and Monuments Commission for England (in this Act referred to as “the Commission”)”

### Who, in law, is responsible for the planning consideration or makes decisions about 'Listed building outlines'?

[SoS for DCMS](https://www.legislation.gov.uk/ukpga/1990/9/section/1 ) - “the Secretary of State shall compile lists of such buildings.”

### Which organisations do we think should publish the data?

Historic England

### Is the Listed building outlines a trigger?

Yes

### What needs to be done because Listed building outlines has acted as the trigger?

- Heritage statement 
- Structural survey
- Lighting assessment
- Archaeological assessment
- Listed building consent

### Is the Listed building outlines something to consult during plan making?

Yes

### Provide information about when Listed building outlines is used during plan making

Further research is required to confirm whether listed building data would be consulted in the completion of listed building consent applications.

### Is there any Listed building outlines data already available?

Yes

### What Listed building outlines data is currently available?

- [Historic England](https://opendata-historicengland.hub.arcgis.com/datasets/historicengland::national-heritage-list-for-england-nhle/about?layer=0) (coverage: National; licence: “Subject to the Open Government Licence v3 (OGL), you are granted a worldwide, perpetual, non-exclusive licence to use the Historic England Data.”; fields: List entry number;Name;Grade;Listing date;Amendment date;Capture scale;NHLE link;National Grid Reference;Easting;Northing)
- [Camden London Borough Council](https://ssa.camden.gov.uk/connect/analyst/mobile/#/main?mapcfg=%2FMapProjects%2FCamdenConservation) (coverage: Local; licence: Unknown; fields: Title;Key (Grade);Description;Link (to HE);Geometry)
- [Newcastle City Council](https://newcastlecc.maps.arcgis.com/apps/instant/basic/index.html?appid=6956e23b13874008b18a2598b4ade83a&locale=en-gb) (coverage: Local; licence: “This website and its content is copyright of Newcastle City Council - © Newcastle City Council 2012. All rights reserved.”; fields: Title;Grade;Link (to HE);Geometry)

### Do we think the data should come from a single source?

Listed building point data is nationally available through Historic England. Polygon data was commenced by Historic England for all listings after the 4th April 2011, and as such this dataset will always have gaps.
This remaining data will not come from a single source, it will be down to all LPAs to produce this data individually.

### Will a data standard be required?

Yes

## Research

### Do we understand the lifecycle of a Listed building outlines?

Yes

### Document a stage of the high-level lifecycle of a Listed building outlines

- Preliminary Checks
-  Application to Historic England
- Period of consultation
-  Decision from SoS
- Right to appeal
- Right to appeal
- Delisting Process

### Do we understand how the data is created/produced?

We have not explicitly asked Historic England how they produce their data yet. It is assumed based off of research and our initial conversation with them that they get the relevant point data from applications for listing, but it is yet unclear as to how they get their polygon data. 
When it comes to LPAs producing their Listed Building Polygon data individually, we expect that they will use:
reference values from the Historic England dataset
point data to identify the listed buildings which require polygons
use OS basemap data from Mastermap to complete their polygons as accurately as possible.

### Where will or should the data be used?

Knowing about a listed building will impact the information an applicant will need to provide to gain planning consent.

### What other planning considerations does it interact with?

- Certificate of Immunity
- Building Preservation Notice
- Local plans - Listed buildings are referenced regularly in local plans (also under the guise of 'heritage assets'), so we think that this consideration feeds into the process of creating a local plan.

### From what we have learnt so far are there any risks to making Listed building outlines data available?

Historic England has said that if there is a listing that started before 4th April 2011, that this would not be polygonised. The risk of using Historic England’s data for polygons is that it will forever be incomplete and inconsistent. 

The issue is mainly in the curtilage and data accuracy. If the curtilage is incorrectly mapped and a decision is made based on this incorrect data, that becomes a criminal offence. If a curtilage is mapped beyond initial boundaries under the mindset of “better safe than sorry”, this will create much more work for LPAs as more applications for listed building consent will be “required” based on this data.

To minimise this risk, curtilage would need to be properly defined, and then every listing in England would have to be independently assessed for accurate curtilage decisions before mapping. This is extremely costly and time consuming, in an environment where LPAs already struggle for resources. Historic England have also mentioned that they would struggle for resources to update the register in line with the amendment cases, which would also impact the SoS’ workload in confirming the new listing descriptions.

The main question is:
Is there a way we can work with Historic England and LPAs to reach a mutually agreeable decision?

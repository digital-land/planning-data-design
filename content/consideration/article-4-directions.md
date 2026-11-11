---
title: Article 4 Directions
description: An Article 4 direction is made by the local planning authority to remove all or some of the permitted development rights on a site in order to protect it
template: consideration
stage: On the platform
datasets:
- article-4-direction-area
- article-4-direction-rule
- article-4-direction
frequency_of_updates: Ad hoc
legislation:
  text: Town and Country Planning (General Permitted Development) (England) Order 2015
  url: https://www.legislation.gov.uk/uksi/2015/596/contents/made
specification:
  text: Article 4 Direction
  url: https://digital-land.github.io/specification/specification/article-4-direction/
useful_links:
- text: Design process document
  url: https://docs.google.com/document/d/1HL7GkBJhYvTfUohy9djPQpP8NWgONRS-yrfpkl8ppNo/edit#heading=h.q1fqqglen3fg
tags:
- odp
github_discussion_number: 30
created: 2024-03-25
updated: 2024-07-30
---
## Backlog

### Who asked for 'Article 4 Directions' data?

Open System Labs - required as a planning constraint in PlanX

### What is the driver for the request?

Specific user requirement

### Which 2024 focus area does the request support?

Modern planning software

## Screen

### What is the 'Article 4 Directions' consideration?

An Article 4 direction is made by the local planning authority to remove all or some of the permitted development rights on a site in order to protect it.

### Is there legislation that defines 'Article 4 Directions'?

Yes

### What is the legislation that defines 'Article 4 Directions'?

[The Town and Country Planning (General Permitted Development)(England) Order 2015, Article 4](https://www.legislation.gov.uk/uksi/2015/596/article/4/made) - 

“The Secretary of State or (as the case may be) the local planning authority, may make a direction under this paragraph that the permission granted by article 3 does not apply to—
all or any development of the Part, Class or paragraph in question in an area specified in the direction; or
any particular development, falling within that Part, Class or paragraph, which is specified in the direction,
and the direction must specify that it is made under this paragraph.”

### What is the specific part of the legislation that describes how a 'Article 4 Directions' gets designated?

[The Town and Country Planning (General Permitted Development)(England) Order 2015, Schedule 3, “Procedures for Article 4 directions”](https://www.legislation.gov.uk/uksi/2015/596/schedule/3/made)

### What is the specific part of the legislation that requires the publication of 'Article 4 Directions'?

[The Town and Country Planning (General Permitted Development)(England) Order 2015, Schedule 3, “Procedures for Article 4 directions”, Sub-paragraph 4(c)](https://www.legislation.gov.uk/uksi/2015/596/schedule/3/made) -
“name a place where a copy of the direction, and a copy of a map defining the area to which it relates, or the site to which it relates, as the case may be, may be seen at all reasonable hours” -

### Who, in law, is responsible for the planning consideration or makes decisions about 'Article 4 Directions'?

[Local Planning Authorities](https://www.legislation.gov.uk/uksi/2015/596/article/4/made)

[Secretary of State (DLUHC)](https://www.legislation.gov.uk/uksi/2015/596/article/4/made)

### Which organisations do we think should publish the data?

Local authorities

### Is the Article 4 Directions a trigger?

No

### Is the Article 4 Directions something to consult during plan making?

Yes

### Provide information about when Article 4 Directions is used during plan making

If an applicant applies to do work under a permitted development right which has been removed by an Article 4 Direction, this dataset will consult that process.

### Is there any Article 4 Directions data already available?

Yes

### What Article 4 Directions data is currently available?

- [Great Yarmouth Borough Council](https://www.great-yarmouth.gov.uk/article/8109/Article-4-direction-Great-Yarmouth) (coverage: Local; licence: Unknown; fields: Geometry;Document; Schedule 1;Schedule 2)
- [Medway Council](https://www.medway.gov.uk/downloads/file/2102/article_4_directions) (coverage: Local; licence: Unknown)
- [Cornwall Council](https://map.cornwall.gov.uk/website/ccmap/?zoomlevel=1&xcoord=162690&ycoord=64380&wsName=ccmap&layerName=Article%204%20direction%20orders) (coverage: Local; licence: Unknown; fields: Name;TLC reference;Paper file reference no.;Alternative reference no.;Link to scanned order)

### Do we think the data should come from a single source?

No - all LPAs will hold this data individually.

### Will a data standard be required?

Yes

## Research

### Do we understand the lifecycle of a Article 4 Directions?

Yes

### Document a stage of the high-level lifecycle of a Article 4 Directions

- Notice of designation publicised
- Confirmation of direction
- Cancel a direction OR Make a direction through modifying / cancelling a direction

### Do we understand how the data is created/produced?

We know that an LPA creates and maintains article 4 directions, and the secretary of state typically has the ability to cancel or modify article 4 directions, and must also be notified when an article 4 direction is introduced to give ample time for decision.
Through our examples, we do not know how Cornwall have created and put together their data, but with the remaining examples we can see that their article 4 directions have been published on their websites and scanned documentation and/or map outlines are available.
In order to create this data, we think that LPAs will use the OS basemap as a rough guide to produce the article 4 direction polygons, and UPRNs may be used to complete references if polygons relate to specific boundaries and don’t cross over multiple. Official documentation should be linked to related references.

### Where will or should the data be used?

This data should be used at an early stage of the planning and application process so users are aware of immediate development restrictions.

### What other planning considerations does it interact with?

Permitted Development Rights (Article 3 Directions)
An article 4 direction is the removal of a permitted development right, so these datasets directly interact with one another

[Area of Outstanding Natural Beauty (AONB), Paragraph 38](https://www.gov.uk/guidance/when-is-permission-required) - 
There needs to be a strong justification for the withdrawal of permitted development rights relating to a wide area such as an Area of Outstanding National Beauty, so there may be a link between these 2 datasets -

### From what we have learnt so far are there any risks to making Article 4 Directions data available?

Licencing is currently unclear and needs to be confirmed with local planning authorities as data begins to get made available in line with our specifications. 
It would also appear that data is currently of a low quality.
If UPRNs are used to create this dataset, we will need to ensure that best practice is being used and the usage is in line with GDPR.

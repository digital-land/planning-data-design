---
title: Conservation areas
description: An area of special architectural or historic interest with a character or appearance that must be preserved or enhanced
template: consideration
stage: On the platform
datasets:
- conservation-area
- conservation-area-document
- conservation-area-document-type
frequency_of_updates: Ad hoc
legislation:
  text: Planning (Listed Building and Conservation Areas) Act 1990, Part II
  url: https://www.legislation.gov.uk/ukpga/1990/9/part/II
specification:
  text: Conservation area
  url: https://digital-land.github.io/specification/specification/conservation-area/
useful_links:
- text: Design process document
  url: https://docs.google.com/document/d/1xXmcLRxSzEzLB9Z2H2ztsjh75ZtpSVz0V89R2j-hC1g/edit
- text: Conservation areas process map
  url: https://app.mural.co/t/mhclg2837/m/mhclg2837/1712065213311/0ddf4128ff318850d5965b157fb7ebd91e3c140a?sender=u1cae178c0a712eade24c2472
- text: Historic environment guidance
  url: https://www.gov.uk/guidance/conserving-and-enhancing-the-historic-environment
tags:
- local land charge
- local plan
- odp
github_discussion_number: 33
created: 2024-03-25
updated: 2024-09-04
---
## Backlog

### Who asked for 'Conservation areas' data?

Open Systems Lab - Planning Software, specifically as constraint in PlanX

### What is the driver for the request?

Specific user requirement

### Which 2024 focus area does the request support?

Modern planning software;Faster local plans

## Screen

### What is the 'Conservation areas' consideration?

Conservation areas are areas of special architectural or historic interest with a character or appearance that must be preserved or enhanced.

### Is there legislation that defines 'Conservation areas'?

Yes

### What is the legislation that defines 'Conservation areas'?

[https://www.legislation.gov.uk/ukpga/1990/9/section/69](https://www.legislation.gov.uk/ukpga/1990/9/section/69) which describes:

“Every local planning authority—
shall from time to time determine which parts of their area are areas of special architectural or historic interest the character or appearance of which it is desirable to preserve or enhance, and shall designate those areas as conservation areas.

(2) It shall be the duty of a local planning authority from time to time to review the past exercise of functions under this section and to determine whether any parts or any further parts of their area should be designated as conservation areas; and, if they so determine, they shall designate those parts accordingly.

(3) The Secretary of State may from time to time determine that any part of a local planning authority’s area which is not for the time being designated as a conservation area is an area of special architectural or historic interest the character or appearance of which it is desirable to preserve or enhance; and, if he so determines, he may designate that part as a conservation area.“

### What is the specific part of the legislation that requires the publication of 'Conservation areas'?

[Section 70, Paragraph 8](https://www.legislation.gov.uk/ukpga/1990/9/section/70) which defines:
“Notice of any such designation, variation or cancellation as is mentioned in subsection (5) or (6), with particulars of its effect, shall be published in the London Gazette and in at least one newspaper circulating in the area of the local planning authority, by that authority or, as the case may be, the Secretary of State”. 

[Planning (Listed Buildings and Conservation Areas) Act 1990, Section 71](https://www.legislation.gov.uk/ukpga/1990/9/section/71) which defines:
“It shall be the duty of a local planning authority from time to time to formulate and publish proposals for the preservation and enhancement of any parts of their area which are conservation areas.”

### Who, in law, is responsible for the planning consideration or makes decisions about 'Conservation areas'?

Local Planning Authorities - [Section 69](https://www.legislation.gov.uk/ukpga/1990/9/section/69)

SoS DCMS - [Section 69](https://www.legislation.gov.uk/ukpga/1990/9/section/69)

Historic England (for decisions in Greater London) - [Section 70](https://www.legislation.gov.uk/ukpga/1990/9/section/70)

### Which organisations do we think should publish the data?

Local authorities;Historic England

### Is the Conservation areas a trigger?

Yes

### What needs to be done because Conservation areas has acted as the trigger?

- design and access statement
- heritage statement
- lighting assessment
- tree survey 
- impact assessment on conservation area
- demolition consent
- statement of community involvement
- town centre visual impact assessment
- archaeological assessment
- arboricultural impact assessment
- land and visual impact assessment (LVIA)

### Is the Conservation areas something to consult during plan making?

Yes

### Provide information about when Conservation areas is used during plan making

- Heritage statement
- Lighting assessment
- Arboricultural impact assessment
- Archaeological assessment
- Landscape and visual impact assessment (LVIA)

### Is there any Conservation areas data already available?

Yes

### What Conservation areas data is currently available?

- [Historic England](https://opendata-historicengland.hub.arcgis.com/datasets/historicengland::conservation-areas/explore?location=52.126721%2C-0.634887%2C6.82) (coverage: National (incomplete); licence: OGL3 - https://historicengland.org.uk/terms/website-terms-conditions/open-data-hub/ ; fields: Name;Designation Date;Update Date;Local Planning Authority;Capture Scale;Easting;Northing;UID;Shape_area;Shape_length)
- [Newcastle City Council](https://newcastlecity.maps.arcgis.com/apps/instant/basic/index.html?appid=e0efda2acdec4d3b85550d1a13f522bb) (coverage: Local; licence: This website and its content is copyright of Newcastle City Council - © Newcastle City Council 2012. All rights reserved.; fields: Name;Geometry)

### Do we think the data should come from a single source?

No - the data should be provided by LPAs individually

### Will a data standard be required?

Yes

## Research

### Do we understand the lifecycle of a Conservation areas?

Yes

### Document a stage of the high-level lifecycle of a Conservation areas

- Appraisal
- Surveys, research, consultation, presentation and assessment
- Designation
- Notice of designation
- Management plan drafted
-  Variation
- Cancellation

### Do we understand how the data is created/produced?

We expect that LPAs will use the above process to designate a conservation area, and will be using base mapping (any) to define the boundary of a conservation area and produce the data. It is likely to copy small elements of road, field, hedge, river features and property boundaries to create a contiguous polygon defining the conservation area.

### Where will or should the data be used?

Knowing about the presence of a conservation area is required for any type of planning application and will impact the information an applicant will need to provide.

### What other planning considerations does it interact with?

- Permitted development rights - Some PDRs will typically be removed in a conservation area. 
- Trees – trees within a conservation area are protected regardless of whether there is a tree protection order or not.
- Local plans - Conservation areas are referenced regularly in local plans (also under the guise of 'heritage assets'), so we are confident that they act as input to the creation of a local plan.

### From what we have learnt so far are there any risks to making Conservation areas data available?

The currently available data is not always clearly published under an open licence.

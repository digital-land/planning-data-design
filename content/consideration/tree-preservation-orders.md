---
title: Tree preservation orders
description: The order document that protects a tree or group of trees
template: consideration
stage: Co-design
datasets:
- tree-preservation-order
- tree-preservation-zone-type
- tree-preservation-zone
- tree
frequency_of_updates: Ad hoc
legislation:
  text: The Town and Country Planning (Tree Preservation)(England) Regulations 2012
  url: https://www.legislation.gov.uk/uksi/2012/605/contents/made
specification:
  text: Tree preservation order
  url: https://digital-land.github.io/specification/specification/tree-preservation-order/
useful_links:
- text: Design process document
  url: https://docs.google.com/document/d/1ziDNUExJiUWtMFI3x90T2G-HGtNldUOQrd13u-h6UHY/edit#heading=h.q1fqqglen3fg
- text: Tree preservation order guidance
  url: https://www.gov.uk/guidance/tree-preservation-orders-and-trees-in-conservation-areas
tags:
- local land charge
github_discussion_number: 43
created: 2024-03-25
updated: 2024-10-14
---
## Backlog

### Who asked for 'Tree preservation orders' data?

Open System Labs - required as a planning constraint in PlanX

### What is the driver for the request?

Specific user requirement

### Which 2024 focus area does the request support?

Modern planning software;Faster local plans

## Screen

### What is the 'Tree preservation orders' consideration?

The order document that protects a tree or group of trees.

### Is there legislation that defines 'Tree preservation orders'?

Yes

### What is the legislation that defines 'Tree preservation orders'?

[The Town and Country Planning (Tree Preservation)(England) Regulations 2012, Part 2, Regulation 3](https://www.legislation.gov.uk/uksi/2012/605/regulation/3/made)

### What is the specific part of the legislation that describes how a 'Tree preservation orders' gets designated?

[The Town and Country Planning (Tree Preservation)(England) Regulations 2012, Part 2](https://www.legislation.gov.uk/uksi/2012/605/part/2/made) 

Form of tree preservation order
Provisional effect of order
Procedure after making an order
Objections and representations
Procedure for confirmation of a tree preservation order
Action after confirmation of tree preservation order
Action where tree preservation order not confirmed
Variation of tree preservation orders
Revocation of tree preservation orders
Register

### What is the specific part of the legislation that requires the publication of 'Tree preservation orders'?

[The Town and Country Planning (Tree Preservation)(England) Regulations 2012, Part 2, Regulation 5, Paragraph 3](https://www.legislation.gov.uk/uksi/2012/605/regulation/5/made) 

“A copy of the order shall be made available for inspection, free of charge, at all reasonable hours, at the offices of the authority by whom the order was made;...”

### Who, in law, is responsible for the planning consideration or makes decisions about 'Tree preservation orders'?

Local Planning Authorities

[https://www.legislation.gov.uk/uksi/2012/605/regulation/12/made](https://www.legislation.gov.uk/uksi/2012/605/regulation/12/made)

### Which organisations do we think should publish the data?

Local authorities

### Is the Tree preservation orders a trigger?

Yes

### What needs to be done because Tree preservation orders has acted as the trigger?

* Tree Survey and/or Report
* Arboricultural Impact Assessment
* Tree Protection Plan

### Is the Tree preservation orders something to consult during plan making?

Yes

### Provide information about when Tree preservation orders is used during plan making

Some of the information included in the TPO documentation may be of use to complete the planning requirements as a result of the trigger, ie. coordinates of affected trees, conditions and variations linked to orders, but this needs to be researched further.

### Is there any Tree preservation orders data already available?

Yes

### What Tree preservation orders data is currently available?

- [Cornwall Council](https://map.cornwall.gov.uk/website/ccmap/?zoomlevel=3&xcoord=200241&ycoord=65297&wsName=ccmap&layerName=Tree%20preservation%20order%20points:Tree%20preservation%20order%20areas) (coverage: Local; licence: Unknown; fields: Reference number;Tree reference;Tree Preservation Order name;Status;Date order made;Date of confirmation;Species/situation description;Link to pdf of TPO document)
- [Wiltshire Council](https://wiltscouncil.maps.arcgis.com/apps/webappviewer/index.html?id=74a353612a934bd48fee1f2bc564cdd8) (coverage: Local; licence: Unknown; fields: TPOREF;REFVAL;DESCR)

### Do we think the data should come from a single source?

No - LPAs will have this data individually

### Will a data standard be required?

Yes

## Research

### Do we understand the lifecycle of a Tree preservation orders?

Yes

### Document a stage of the high-level lifecycle of a Tree preservation orders

- Request
- Site Visit
- Order prepared
- Objections
- Order confirmed
- Variation of order
- Revocation of order

### Do we understand how the data is created/produced?

[Making and confirming a tree preservation order - Flowchart](https://assets.publishing.service.gov.uk/media/5c5da17b40f0b676d487d027/TPO_flowchart_1.pdf)

In regards to the creation of data (for those LPAs that already have polygon data), this remains unknown.
For “tree” and “tree-preservation-zone,” we expect that the OS basemap will be used as a guide, but will likely not be traced to produce the data. “Tree-preservation-order” is the dataset pertaining to the official documentation of the TPO itself, and so being owned by the LPA will mean there is no input from a third party in the creation of this part of the dataset.

### Where will or should the data be used?

The presence of tree preservation orders will influence the amount of prospective development and will impact the amount of information and research required to fully complete an application.

### What other planning considerations does it interact with?

- Conservation Areas - There is a link between Trees and Conservation Areas in [the legislation](https://www.legislation.gov.uk/uksi/2012/605/regulation/15/made).
- Local plans - TPOs are occasionally referenced in local plans, so we think that this consideration feeds into the process of creating a local plan.

### From what we have learnt so far are there any risks to making Tree preservation orders data available?

- Licensing - currently, available data is not always clearly published under an open licence
- Digital Immaturity - Local planning authorities (where data is not currently available online) may struggle to find the capacity to create polygon data for tree preservation zones and point data for tree preservation orders

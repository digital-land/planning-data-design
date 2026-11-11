---
title: Uprn
description: Unique Property Reference Number (UPRN) is the unique identifier for every addressable location in the UK
template: consideration
stage: Co-design
frequency_of_updates: Every 6 weeks
useful_links:
- text: National dataset documentation page
  url: https://osdatahub.os.uk/downloads/open/OpenUPRN
github_discussion_number: 72
created: 2024-03-25
updated: 2024-09-05
---
## Backlog

### Who asked for 'Uprn' data?

The Geospatial Commission has published a list of 65 open datasets that they believe are used during the housing and planning process. This includes UPRNs

### What is the driver for the request?

Other

### Which 2024 focus area does the request support?

Modern planning software

## Screen

### What is the 'Uprn' consideration?

OS Open UPRN

UPRNs are the authoritative identifier used to uniquely identify addressable locations in Great Britain. Essential for bringing property and address information together.

### Who, in law, is responsible for the planning consideration or makes decisions about 'Uprn'?

Ordnance Survey

### Which organisations do we think should publish the data?

Ordnance Survey

### Is the Uprn a trigger?

No

### Is there any Uprn data already available?

Yes

### What Uprn data is currently available?

- [OS Open UPRN](https://www.ordnancesurvey.co.uk/products/os-open-uprn) (publisher: Ordnance Survey; coverage: GB; licence: OGL version 3; fields: FID; UPRN; X_Coordinate; Y_Coordinate; Latitude; longitude)

### Do we think the data should come from a single source?

Yes - Ordnance Survey

### Will a data standard be required?

No

## Research

### Do we understand the lifecycle of a Uprn?

Yes

### Document a stage of the high-level lifecycle of a Uprn

- 

### Do we understand how the data is created/produced?

A UPRN is a unique numeric identifier for every addressable location in Great Britain. The UPRN is the
persistent identifier providing consistency across the AddressBase product range.

Each address record has a UPRN, assigned by Local Authorities in England, Wales and Scotland or Ordnance
Survey depending on the type of address. This is the primary key of the AddressBase Core product.
Throughout its lifecycle, information on the address of a property can change. This may be due to a change
of name, change of use, or the eventual demolition of the property. Independent of any changes being made

the UPRN associated to an address is never changed, meaning the unique identifier remains persistent and
reliable.

### Where will or should the data be used?

UPRNs are used in lots of datasets so would be useful to link datasets together

### What other planning considerations does it interact with?

* [Energy performance certificates](https://design.planning.data.gov.uk/planning-consideration/energy-performance-certificates) - each certificate has a uprn for the property
* [Article 4 directions](https://design.planning.data.gov.uk/planning-consideration/article-4-directions) - these can reference specific properties using UPRNs

### Other than the statutory consultees who are the primary users of Uprn? How do we expect them to use Uprn?

N/A

### What are the planning needs for this data?

A specific planning need is unclear

### Who are the types of users who might benefit from having access to Uprn data?

N/A

### What are some potential uses of Uprn data?

Use of UPRN data can reduce any nature of ambiguity in identifying correct properties, whether this be for emergency, logistics or domestic reason.
An example could be for someone selling their home. A user would be able to find out the UPRN of their property through the platform, so that there would never be any confusion over which property is up for sale, potentially in a tight cluster.

### What's the value of adding Uprn data to the platform?

UPRNs are the authoritative identifier used to uniquely identify addressable locations in Great Britain.

This means they are used in lots of different datasets. Using them allows us to link more datasets together and know more about the property or addressable location in question

---
title: Usrn
description: Unique Street Reference Number (USRN) is an 8 digit unique identifier for every street across Great Britain
template: consideration
stage: Co-design
frequency_of_updates: Every 6 weeks
useful_links:
- text: National dataset documentation page
  url: https://osdatahub.os.uk/downloads/open/OpenUSRN
github_discussion_number: 73
created: 2024-03-25
updated: 2025-01-28
---
## Backlog

### Who asked for 'Usrn' data?

The Geospatial Commission has published a list of 65 open datasets that they believe are used during the housing and planning process. This includes USRNs

### What is the driver for the request?

Other

### Which 2024 focus area does the request support?

Modern planning software

## Screen

### What is the 'Usrn' consideration?

OS Open USRN

A Unique Street Reference Number (USRN) is a unique and persistent identifier for every street, road, track, path, cycle track or cycle way in Great Britain.

### Who, in law, is responsible for the planning consideration or makes decisions about 'Usrn'?

Ordnance Survey

### Which organisations do we think should publish the data?

Ordnance Survey

### Is there any Usrn data already available?

Yes

### What Usrn data is currently available?

- [OS Open USRN](https://www.ordnancesurvey.co.uk/products/os-open-usrn#technical) (publisher: Ordnance Survey; coverage: GB; licence: OGL version 3; fields: id; USRN; street_type; geometry)

### Do we think the data should come from a single source?

Ordnance Survey

### Will a data standard be required?

No

## Research

### Do we understand the lifecycle of a Usrn?

Yes

### Document a stage of the high-level lifecycle of a Usrn

- 

### Do we understand how the data is created/produced?

A USRN is a unique and persistent identifier for a street contained in either the National or Scottish Street
Gazetteer. Every street, road, track, path, cycle track or way is assigned a USRN by a Roads Authority, Local
Highway Authority or Highways England.
OS Open USRN will include all live USRNs published within the OS MasterMap Highways Network, including
Type 1, 2, 3 and 4 streets (see Table 1).

Local authorities have a statutory responsibility that means they are the source of information for both
street naming and managing the highways/roads network. 

Each authority is provided a USRN range, that is
centrally allocated and managed by GeoPlace in England and Wales, and Improvement Service in Scotland.

A USRN is assigned to the complete street feature and is made up of junction-to-junction segments. It is mandatory for all USRNs to be assigned a Street Type. All streets must have a Type 1 or a Type 2 USRN
assigned, but a Type 3 or Type 4 USRN can also represent the same sections of carriageway as the Type 1 or
2 are assigned. 

Table 1 provides the definitions for different street types.

### Where will or should the data be used?

N/A

### What other planning considerations does it interact with?

N/A

### Who are the statutory consultees for Usrn?

N/A

### Other than the statutory consultees who are the primary users of Usrn? How do we expect them to use Usrn?

N/A

### What are the planning needs for this data?

Planning need is unclear

### Who are the types of users who might benefit from having access to Usrn data?

According to [Geoplace](https://www.geoplace.co.uk/addresses-streets/location-data/usrn)

* Highways authorities - coordinating works
* Utility companies - coordinating works

### What are some potential uses of Usrn data?

The USRN is key to ensuring works on streets can be planned effectively.

They can facilitate better insights into traffic patterns, infrastructure utilisation, planning, and development, leading to informed decision-making and resource allocation

### What's the value of adding Usrn data to the platform?

The Government Digital Service has mandated that the UPRN and USRN are to be the public sector standard for referencing and sharing property and street information
-- [Geoplace](https://www.geoplace.co.uk/addresses-streets/location-data/usrn)

Therefore we should make these available to service builders so that they can be used as intended.

### From what we have learnt so far are there any risks to making Usrn data available?

N/A

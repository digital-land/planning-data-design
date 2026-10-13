Follow these principles when designing planning data.

## 1. Model the world, not existing data

Design data which represents things in the real-world and how they are related. Don’t just copy existing data sources, formats, and schemas. 

We can collect data in many different ways, and make it available to users in many different forms,
but the core concepts of data on the platform needs to reflect reality.

* [Start with user needs](https://www.gov.uk/guidance/government-design-principles#start-with-user-needs)  
* [Modelling entities and relationships](https://en.wikipedia.org/wiki/Ontology_\(information_science\))

## 2. Use precise definitions, not general terms

The names you use in your model must be simple, easily understood and unambiguous. 
Avoid using product names, abbreviations or acronyms as they are often unclear, ambiguous, or quickly become outdated.

Ensure each term you use has an authoritative definition found in legislation, policy, or other trusted source. 
Where a good definition for a term is hard to find, pick a short, plain English term and test it with users.

* [Be consistent, not uniform](https://www.gov.uk/guidance/government-design-principles#be-consistent-not-uniform)
* [Domain driven design](https://en.wikipedia.org/wiki/Domain-driven_design)
* [Wikipedia:Citation needed](https://en.wikipedia.org/wiki/Wikipedia:Citation_needed)

## 3. Do not repeat yourself

Repeating values, such as the name and other information about the local authority 
against each planning application, increases opportunities for the values to diverge, and for mistakes to creep in.
Duplication makes it harder to reliably update data, and increases the size of the data stored.

Design datasets which only contain one type of entity managed by a single kind of organisation and link between them.

* [Tidy data principles](https://www.gov.uk/government/statistics/personal-and-stakeholder-pensions-statistics/tidy-data-guide)
* [DRY principle](https://en.wikipedia.org/wiki/Don%27t_repeat_yourself)  
* [Database normalisation](https://en.wikipedia.org/wiki/Database_normalization)   

## 4. Only include what is needed

Resist the temptation to add anything and everything related to an entity. 

Instead, discover the core data a user needs to act, or inform a decision, or where it’s a legal requirement, and just include that.

Don’t just add what people say they want, or think could be useful: design the data you know users need. 

Only ask a user to provide information for which they are responsible.
Don't ask them to provide data which can be easily derived, or which is more authoritatively managed elsewhere.
Every field you ask for places a burden on the provider of the data, often leading to a reduction in its quality. 

* [Do less](https://www.gov.uk/guidance/government-design-principles#do-less)
* [Do the hard work to make it simple](https://www.gov.uk/guidance/government-design-principles#do-the-hard-work-to-make-it-simple)


## 5. Link to the sources

The information recorded in your data model may come from multiple places, but every fact recorded should have a single, authoritative source. Linking facts back to where information is available helps users assess its veracity, increasing the trust they can place in the data.

* [Persistent resolvable identifiers](https://www.gov.uk/government/publications/open-standards-for-government/persistent-resolvable-identifiers)
* [Reuse and linkage](https://www.ons.gov.uk/aboutus/transparencyandgovernance/datastrategy/dataprinciples#reuse-and-linkage)  

## 6. Preserve history

The word changes and the data needs to record the changes. There are many use-cases in planning which depend on understanding this change, to monitor the impact of policies, or to challenge a decision made in the past. Deleting old facts erodes trust users can place in the data and reduces its use.

There are some exceptions to this principle. You should expect to quickly remove data added by mistake, especially where it contains sensitive or personal information. Mistakes in authoritative information should be preserved, but erroneous recordings, especially outliers which cause issues with statistical analysis can be removed.


* [Digital continuity](https://www.nationalarchives.gov.uk/information-management/manage-information/policy-process/digital-continuity/what-is-digital-continuity/)
* [No link left behind](https://gds.blog.gov.uk/2012/10/11/no-link-left-behind/)
* [Cool URIs don't change](https://www.w3.org/Provider/Style/URI)

## 7. Seek and give feedback, early and often

Openness should be the default across all design decisions. Wherever possible, share draft specifications, concept models, and documentation publicly to invite early feedback from planning authorities, software vendors, and downstream data users.

Quickly responding to, and acting on feedback is essential to increasing the trust users can place in the platform.
Conversely, you should provide good feedback to others, in a way they value, and can easily act upon.

*  [Make things open: it makes things better](https://www.gov.uk/guidance/government-design-principles#make-things-open-it-makes-things-better)

## 8. Expect change, and don't make breaking changes

Data standards need to evolve as legislation changes, and new users and needs emerge. 

Users of the platform should enable forwards compatibility by ignoring any unexpected fields added in a later version of a specification, or added as an extension to support a local use-case.

Conversely, your specifications must maintain backward compatibility whenever possible. 
This means not removing existing fields, or changing the meaning of values users depend upon.

Where a breaking change is unavoidable, it should be clearly communicated in advance, for example by marking a field as being deprecated before later removing it.


* <a href="https://en.wikipedia.org/wiki/Open%E2%80%93closed_principle">Open-Closed principle</a>.

## 9. Some data is better than no data

Start small with the simplest of needs, with the clearest needs for data, which can be quickly met using data collected from the smallest number of sources.
Then work to improve data quality, coverage, and cover more use-cases over time through feedback loops.

This iterative approach gives the most immediate value to users, allowing you to test and prove a specification before committing to it as a standard.

* [Iterate, then iterate again](https://www.gov.uk/guidance/government-design-principles#iterate-then-iterate-again)

## 10. Show the benefits

Data is a public good that increases in value the more people use it. To sustain the platform and justify the effort required to publish and maintain data, we need to show that value clearly.

Standard web analytics do not show real-world use. Popularity is not the same as impact:
* a user might download a dataset once and serve it downstream to millions of people
* an automated script or AI agent might make hundreds of API calls without creating any public value

Measuring benefit requires getting closer to users to understand what decisions, services, and policies the data makes possible. 
When designing a dataset, work with users to develop quantitative metrics and build case studies that demonstrate tangible outcomes, not vanity traffic.

* [Value of Public Sector Data Estimate](https://www.gov.uk/government/publications/value-of-public-sector-data-estimate/value-of-public-sector-data-estimate)
* [Design with data](https://www.gov.uk/guidance/government-design-principles#design-with-data)

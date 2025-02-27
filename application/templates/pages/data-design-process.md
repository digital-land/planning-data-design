We have created a data design process to determine what data is needed to support planning in the UK and should be made available on [planning.data.gov.uk](https://planning.data.gov.uk).

The output of the process is a technical specification that data providers can use to provide high-quality planning data.

Once we have created, tested and verified the technical specification we will hand it over to a data management team, who will work with data providers to get the data onto [planning.data.gov.uk](https://planning.data.gov.uk).

<div class="govuk-inset-text">
Find out <a href="{{ url_for('main.page', page='how-to-contribute-to-the-data-design-process') }}" class="govuk-link">how you can contribute to the data design process</a>
</div>

## About the design process

This process needs to explore different aspects of the planning system, determine what is underpinned by legislation and what data is needed to support how it is used in planning.

We've created a repeatable and modular data design process to produce better and more consistent results. This approach makes the process more transparent and makes it easier for interested parties to contribute.

Our process is split into several stages. We want to make it easy to see where a planning consideration is in our process and what we need to do to make progress. It is worth noting that the process is not always linear. A planning consideration might move back a stage if we need to do more work on it.

Each planning consideration we take through the process gives us more information about our process. Measuring what worked, what didn't work and what needs tweaking helps us make each step more efficient.

<details class="govuk-details">
  <summary class="govuk-details__summary">
    <span class="govuk-details__summary-text">
      What is a planning consideration?
    </span>
  </summary>
  <div class="govuk-details__text">
    <p>A planning consideration is something specific to an area that may impact the outcome of a planning decision.</p>
    <p>For example, a national planning policy impacts what can be built across the whole of England, and a conservation area restricts what can be developed in that area.</p>
  </div>
</details>

## Stages of the design process

There are 8 stages in total.

### 1. Backlog

This stage helps us to understand the planning data landscape.

#### What happens

Someone tells us about a subject area (we call these planning considerations) that plays a part in planning decision-making. This can be during an application or plan-making process. They are expressing an opinion that data for this consideration should be more readily available.

We then add it to the backlog and indicate where we think it fits with our programme objectives.

Once it's on the backlog, this means we're committed to looking at this consideration.

[See planning considerations in the Backlog stage]({{ url_for('planning_consideration.considerations', stage='Backlog')}}).

### 2. Screen

This stage helps us to verify that a consideration plays an important role in planning decision-making.

#### What happens

We answer set questions in the screening stage to help us to understand the legal underpinnings of the consideration, where it is used and needed in the planning system and what, if any, data already exists.

At this stage, it is usually possible to tell if we can use an existing national dataset or whether a new technical specification will be needed.

[See planning considerations in the Screen stage]({{ url_for('planning_consideration.considerations', stage='Screen')}}).

### 3. Research

This stage is intended to help us to understand the planning need for a consideration.

#### What happens

We answer set questions in the research stage to help us understand the planning and data needs.

We capture how and where the considerations are used, the size and scope of any potential data yield, assumed user needs, use cases for the data, and an expectation of who might be able to provide the required data.

During this stage, we will capture any existing open data we find. Analysis of this data will help us to design a feasible and value data model in the co-design stage.

[See planning considerations in the Research stage]({{ url_for('planning_consideration.considerations', stage='Research')}}).

### 4. Co-design

This stage is focused on designing the smallest data model that will satisfy the highest number of needs.

#### What happens

In the co-design stage we develop a draft data model.

Our approach is to start small and build up from there. At this initial stage, we will design a data model that captures only the essential data required to meet the most pressing and clear needs. We anticipate that these data models will grow and evolve as new needs emerge. Each dataset will be designed with a minimal set of fields to start.

The data model will be co-designed with our users: people needing the data, people providing the data and stakeholders.

[See planning considerations in the Co-design stage]({{ url_for('planning_consideration.considerations', stage='Co-design')}}).

### 5. Test and iterate

This stage helps us to build confidence in the data model, proving it is both feasible and will add value.

#### What happens

We take the draft data model and create a detailed specification and any supporting materials.

Next, we test the data model and these materials in a controlled environment with potential data providers.

This testing helps us ensure that the data will work in practice, is feasible to produce and provides value.

If no existing data is available for a specific planning consideration, we may decide to create some sample data. This sample data, based on real instances of the planning consideration, allows us to test the data model and create an example data explorer to demonstrate how the data can be used.

We expect to iterate the data model during this stage.

[See planning considerations in the Test and iterate stage]({{ url_for('planning_consideration.considerations', stage='Test and iterate')}}).

### 6. Go / no-go

This stage allows us to check we have followed the process and completed the expected steps.

#### What happens

We will summarise what we've learnt during the data design process and check off any associated risks.

This stage gives us the chance to consider the potential costs, and any legal challenges and to prepare supporting guidance we think will help data providers to provide quality data.

This is a governance step for [planning.data.gov.uk](https://www.planning.data.gov.uk/)

[See planning considerations in the Ready for go/no-go stage]({{ url_for('planning_consideration.considerations', stage='Ready for go/no-go')}}).

### 7. Prepare for platform

This stage is focused on preparing for the productionisation of the dataset(s) for the planning consideration.

#### What happens

We will ensure we have provided all the required information needed by the data management team for them to be able to start collecting and publishing production-quality data that you can trust.

We wouldn't expect to make many changes to the data model at this point.

We'll articulate what to expect from an authoritative dataset — for example, who we expect to publish, what we expect them to publish, and how often.

[See planning considerations in the Prepare for platform stage]({{ url_for('planning_consideration.considerations', stage='Prepared for platform')}}).

### 8. On the platform

At this stage, we will handover to the data management team. They will work with data providers, collect the data they publish and make authoritative datasets available on [planning.data.gov.uk](https://www.planning.data.gov.uk/).

#### What happens

The focus will shift from designing the data to collecting the data. The data management team will lead this work.

Some, less authoritative, data, created in earlier stages, will be on the platform for data consumers to use. Over time more data for the dataset(s) will be collected, increasing the quality and authority of the available data.

Feedback from providers and consumers will be collected and fed back to the data design team for future iterations of the data model.

[See planning considerations in the On the platform stage]({{ url_for('planning_consideration.considerations', stage='On the platform')}}).

---

## Collaborate and co-design

The data design process is a collaborative and open process. We want all interested parties to be involved in the design of the data they need, produce and use.

There are different ways to contribute depending on what stage in the process a planning consideration is at. Find out [how you can contribute]({{ url_for('main.page', page='how-to-contribute-to-the-data-design-process') }}).

We will set up working groups for various planning considerations. They will be open to everyone that's interested in working on the subject.

If you have an existing dataset you think should be on the platform, there is a [process for you to work with us]({{ url_for('main.page', page='how-to-get-existing-datasets-on-to-planning-data-gov-uk') }}) on that too.

---

## Help improve our process

To help improve our process, you can:

* take part in the ['Data design process' discussion on GitHub](https://github.com/digital-land/data-standards-backlog/discussions/60), ask questions and share your thoughts

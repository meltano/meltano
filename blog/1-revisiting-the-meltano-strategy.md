# Revisiting the Meltano strategy: a return to our roots

This is part 1 of a 2 part series. If you've been following the Meltano project for a while or would like to have some historical context, start here. If you're new to the Meltano project and mostly interested in what's next, start with part 2.

---

The Meltano project was [founded 2 years ago](https://about.gitlab.com/blog/2018/08/01/hey-data-teams-we-are-working-on-a-tool-just-for-you/), as an internal team at GitLab to build tooling for GitLab's Data team. The goal was to build an open source end-to-end tool for data teams that would allow data engineers, data analytics engineers, data analysts, data scientists, and business end users to collaborate within the context of one standardized Meltano project, tying together all of the open source tools needed to extract, load, transform, orchestrate, model, and analyze the data. (Also, DevOps practices, versioning etc.) The glue between different open source tools, coming together as single tool to go all the way from data to dashboard.

For a while, the team was making great process working closely with the Data team, until unfortunately (for Meltano, though fortunately for GitLab), the Data teams needs were growing at a pace that the Meltano team couldn't keep up with, and the Data team decided to switch to a more traditional stack so that their results wouldn't be affected by the dependence on a tool in its infancy.

That didn't deter the Meltano team, who continued to work to realize the end-to-end vision. Because the different users involved in the different stages on the journey from extraction to analysis have different needs and skills, and since we envisioned Meltano bringing value to both teams with engineers on staff, and those without (https://about.gitlab.com/blog/2018/10/08/meltano-functional-group-update-post/), the decision was made to develop the CLI and the UI in parallel, so that Meltano could serve both technical and non-technical users.

Since every next stage depends on the result of the one that came beforehand (we're talking about data pipelines after all), our prioritization process had a cyclical nature, where we'd start with the first stage (extraction and loading), iterate on that one for a bit up to the point that it would unlock further improvements to the next stage, after which we'd move on to the next stage, and so on on. Once the end of the journey was reached (analysis), we'd once again focus on the first stage and the cycle would continue.

V1 marked the completion of one such cycle and the realization of end-to-end vision: you could set up a project with existing extractor, loader, transform, and model plugins, spin up the UI, enter your connection details, and go from data to dashboard in minutes. Pretty awesome! (https://meltano.com/blog/2019/10/07/meltano-graduates-to-version-1-0/)

Despite our aspirations, though, we had not yet managed to attract an open source community to build this thing with us, and while there had been a lot of interest in the project from the beginning, no data teams were jumping at the chance to replace their existing stack with Meltano yet. While we had certainly proven the concept, we had not yet gotten it to a place where the value it could bring was significant or obvious enough that new or existing data teams would actually consider it an alternative to more traditional stacks.

To address that, we decided to focus on the user who ultimately gets the most value out of any data pipeline: they end user who consumes the reports, finds the insights and uses them improve their business. Specifically, we picked a persona for whom the no-coding-needed end-to-end batteries-included aspect of Meltano would be significant selling point: non-technical startup founders who may not have a data stack at all yet, but use a bunch of common tools that they would like to create reports and dashboards over. (https://meltano.com/blog/2019/11/11/clarifying-the-target-persona-for-meltano/)

So in November, we decided to go all-in on turning Meltano into an analytics tool with built-in support for the most popular data sources used at early startups, that could be connected with a click, after which the user would be taken to straight to a set of default dashboards and reports.

Since this user could not be expected to be comfortable installing Python packages or setting up Docker containers themselves, we decided to make installation as easy as clicking a button, by offering hosted Meltano instances: https://meltano.com/blog/2019/11/26/were-going-saas-let-us-set-you-up-with-free-hosted-dashboards/

These users could also not be expected to write extractors, transforms, or models, so we took on this burden ourselves, as we tried to prove that Meltano could bring significant value by showing that _assuming the plugins exist_, it's really powerful to have one application manage that take care of everything from extraction to analysis, so that end user can forget about the details and just go straight from data to dashboard.

This was also a great opportunity to dogfood the experience of data engineer and data analytics engineer who would write Meltano plugins (Singer taps, dbt transformations and m5o models), as we were wearing their shoes for a while and running into all of the challenges involved. By working directly with end-users of Meltano Analyze, we were also able to iterative heavily on the UI to cater it better to people not already intimately familiar with data pipeline concepts, by wrapping the Extract, Load, and Transform concepts up into "Connections", and by introducing a new "dashboard" plugin type so that we could build default reports and dashboards that would be installed automatically along with a data source's extractor, transformations, and models.

About 6 months into this, in March 2020, we found ourselves in a much better place with Analyze, and were about to embark on a new effort to not just ship transforms, models and default dashboards and reports for individual data sources, but for combinations of data sources as well, since this is where the more interesting insights are often hidden. Meltano already supported this in principle, meaning that more technical users setting up Meltano and building plugins themselves could figure it out, but the challenge would be in allowing these connections to be made through the UI, and offering our non-technical end user out of the box support for all reasonable combinations of data sources that they had connected. (https://gitlab.com/meltano/meltano/-/issues/518)

Since the value of hosted Meltano was as much a function of the actual functionality the Meltano application offered, as it was of the extent of our out of the box data source support, improving the experience and increasing the value Meltano could bring to non-technical end users would come down to us taking on the significant burden of developing and maintaining all of these plugins ourselves.

It became clear that while this 6 month experiment had certainly proven the concept that "Meltano can actually bring value to non-technical people as a one-click data to dashboard platform", it had also showed us that in order for real world teams to be able to use this tool, implementing data source support ourselves as a means of showing the world how valuable this tool could be was not going to scale, because we could never start to rival the set of connectors supported by a tool like Fivetran, for example, if we were going to be writing all of the plugins ourselves.

We had built a pretty cool and useful tool specifically aimed at startup founders looking to analyze their sales funnel performance, but if our overarching goal was still to build an end-to-end toolset for any data team and any use case, we weren't going to get there this way.

So what's next, then? If the non-technical user experience of Meltano will only ever be as good as the quality of its plugins, we need to get more people involved in building plugins, so back to open source, self-hosting, and catering to technical users it is!

But wasn't that exactly what we did for about a year and a half while we were working towards V1, and before we decided to pivot to the startup founder persona?

What we had been doing then had worked in some ways (we had built an actual end-to-end data tool!), but not in others (we hadn't attracted a community of users who would also contribute to Meltano and build plugins), so we can't just go back and assume things to be better without specifically addressing that problem.

To figure out what that means and where to go from here, I've spent much of the last few weeks diving deep into and having many calls with people about Meltano's history (what was the original vision, what resonated with users, what got people to contribute, what got them to lose interest), the state of the industry (alternatives in the end-to-end, data integration, and data analytics spaces), and Meltano's place in it.

While the end-to-end vision certainly inspired and excited many, we've seen that that ultimately wasn't enough to build an open source community of active contributors to both plugins and Meltano itself, and I have a couple of thoughts as to why that may be.

(WRITE SOMETHING A BIT MORE COHERENT HERE, based on the bullet points below)

- Since the value of Meltano comes out of the end-to-end use case, a team would need to adopt it in one go instead of piecemeal, so an individual is unlikely to be motivated to contribute since they can't see this bringing value to themselves until it gets officially adopted by their team
- For the end-to-end vision of Meltano to work, there needs to be a large set of supported data sources, with extractors, transforms, and models. How do we get there? By selling people on the whole vision and hoping they'll contribute all at once? Not reasonable, we're talking about different people within teams.
- When a project intends to do "everything" for "everyone", the reward is far way
- What we've been doing before is work a little on one step, then go to the next, etc.
  I don't think that works as a way to build an open source community, because you're basically changing personas and "resetting" the current set of community members every time you move on the next stage. This means the only people who stick around are those who are motivated by the entire vision, with very delayed reward.
  For it to be a community, it's got to feel like we're in this together, and not like the main contributor is going to "forget about us" for 5 our of every 6 months. Start here, and build it until it has reached a point where it's actually good enough and being maintained by the community, and we can naturally start focusing on the next step.
- End-to-end vision was biting off too much at once, open source project has to start small and focused, not big and ambitious.

As a comparison: If GitLab had been announced as the open source project that was one day going to support the entire DevOps cycle, before a single line of code had been written, everyone coming in would have been confused by all the different things being worked on, disappointed by the state of all of it, not feel like the tool is for _them_ because it targets everyone, and discouraged from contributing because the road to value still seems so long: the distance between the now and the vision was too big. GitLab’s “open source Git web interface” was much easier to “get”, get excited by, give a try, feel that initial delight, and start contributing to.

So if we can't start with end-to-end, where do we start?

Since the plugins that will make Meltano's end-to-end vision come true for any given data source will have to be written roughly in order by people with different roles and skillsets, the only place to start is at the very beginning, with the first plugin.

No one will build a report on a design that was never modeled for a table that was never transformed for data that was never loaded or extracted, so if we want this end-to-end story to work _eventually_, we have to start with data engineers writing extractors, so that _later_ data analytics engineers can write transforms and models, so that _after that_ data analysts and business end users can use the model to create reports and dashboards.

The assumption (or hope?) is that if we build an open source community around data integration, and get people to collaborate on extractors and loaders, people will be increasingly motivated to also write transformations because dbt is supported out of the box. Once Meltano ships with extractors and transformations for various data sources out of the box, people would also be motivated to write models, because Analyze comes out of the box, and once a bunch of those are done, we're ready for the non-technical end-user who we won't need to contribute at all, because all of the plugins have been written already.

This means that the end-to-end vision is still alive, but for the foreseeable future, we cannot afford to be distracted and will go all-in on Meltano as an open source self-hosted data integration pipeline platform, with the goal being to "build a production-ready self-hosted open source alternative to existing proprietary hosted ELT/data pipeline/data integration solutions with a great library of extractors", without which an open source end-to-end data tool can never exist.

In the "Go all-in on Meltano as an open source self-hosted data integration pipeline platform" epic (https://gitlab.com/groups/meltano/-/epics/77, I've also laid out my step-by-step thought process from assumption "Meltano's end-to-end vision depends on teams coming to see it as an alternative to Fivetran and Looker (and similar tools)" to these two final conclusion:

- We will go all-in on building a great self-hosted open source ELT tool and will treat the end-to-end vision just like the early GitLab contributors would have treated the "entire DevOps cycle" vision
- From GitLab's perspective, Meltano's success will be measured based on contributions first and usage next, until real-world production usage has increased to a point where it's clear that Meltano ELT can truly compete in the market with hosted proprietary tools, at which point GitLab will attempt to build a business around and supporting the existing open source community and product. This point is expected to be multiple years away from today.

That means Meltano is now an open source self-hosted data integration platform, yay!

And everything that's old is new again, since this is pretty much exactly what Taylor Murphy suggested in https://gitlab.com/meltano/meltano/-/issues/94#note_103950871, not too long after the project was originally founded in 2018:

> From my perspective, given what Meltano can be, the real opportunities for building a community around Meltano are initially around Extractors and Loaders and eventually Meltano Analyze. dbt already has quite a community and working well with them would be a quick way to get more people excited.

To learn why we are just as excited about the opportunity to build an open source data integration platform as we are about the end-to-end vision a few more years down the line, check out part 2:

**Why we are building an open source data integration platform**
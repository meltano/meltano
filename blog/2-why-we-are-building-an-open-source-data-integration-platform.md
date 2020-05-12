# Why we are building an open source platform for ELT pipelines

This is part 2 of a 2-part series to announce and provide context on the new direction of [Meltano](https://meltano.com).

If you're new to Meltano or are mostly interested in what's coming, feel free to start here and skip part 1.

If you've been following Meltano for a while or would like to have some historical context, start with part 1: [Revisiting the Meltano strategy: a return to our roots](#).

## Introduction

If you've read [part 1 of the series](#), you know that Meltano is now focused on building an **open source platform for data integration and transformation (ELT) pipelines**, and that we're very excited about it.

But why are we even building this?

Isn't data integration (getting data from sources, like SaaS tools, to destinations, like data warehouses) a solved problem by now, with modern off-the-shelf tools having taken the industry by storm over the past few years, making it so that many (smaller) companies and data teams don't even need data engineers on staff anymore?

Off-the-shelf ELT tools are not _that_ expensive, especially compared to other tools in the data stack, like Looker, and not having to worry about keeping your pipelines up and running or writing and maintaining data source connectors (extractors) is obviously extremely valuable to a business.

On top of that, writing and maintaining extractors can be tedious, thankless work, so why would anyone want to do this themselves instead of just paying a vendor to handle this burden instead?

Who would ever want to use a self-hosted ELT platform? And why would anyone think building this is a good use of time or money, _especially_ if it's going to be free and open source?

---

In [part 1](#), I explained why we have concluded that in order to eventually realize our end-to-end vision for Meltano (a single tool for the entire data lifecycle, from data source to dashboard), we have to go all-in on positioning Meltano as an open source self-hosted platform for running data integration and transformation (ELT) pipelines, and will turn Meltano into a true open source alternative to existing proprietary hosted solutions like [Alooma](https://www.alooma.com/), [Blendo](https://www.blendo.co/), [Hevo](https://hevodata.com/), [Matillion](https://www.matillion.com/products/etl-software/), [Pentaho](https://www.hitachivantara.com/en-us/products/data-management-analytics/pentaho-platform.html), and [Xplenty](https://www.xplenty.com/), in terms of ease of use, reliability, and quantity and quality of supported data sources.

However, the points and questions raised above are totally valid, and were in fact raised by actual data engineers I've talked to over the past few weeks. While Meltano (and [GitLab](https://about.gitlab.com), which sponsors its development) have a need for the existence of such a tool, it's a separate matter entirely whether there are any data engineers or data teams out there who share that need.

Would any data team actually consider joining the community, contributing to Meltano and its extractors and loaders, and eventually migrating to the open source tool, away from whatever proprietary solution they use today?

## The problem: pay to play

The idea is that every data team in the world needs a data integration tool, because one way or another you have to get your data from your various sources into your data warehouse so that it can be analyzed. And since every company would be better off if they were analyzing their data and learning from their ups and downs, every company in the world needs a data integration tool whether they already realize it or not.

Since there is currently no true open source alternative to the popular proprietary tools, the data space has effectively become "pay to play". There are many great open source analytics and business intelligence tools out there ([Superset](https://superset.incubator.apache.org/), [Metabase](https://www.metabase.com/), and [Redash](https://redash.io/) come to mind, and let's not forget that Meltano comes with built-in analytics functionality as well), but all assume that your data will somehow have already found its way into a data warehouse.

If for any reason at all you cannot use one of the hosted platforms, you are essentially out of luck and will not get to compete on a level playing field with those companies that can afford to integrate their data and start learning from it. Even if you have everything else going for you, you are massively disadvantaged from day one.

Perhaps, you do not think of these off-the-shelf tools as particularly expensive, you're fine with your sensitive data flowing through a US company's servers, and you would happily pay for professional services if you ever need to extract data from a source that isn't supported already. 

However, many around the world will find prices US companies charge prohibitively expensive relative to their local income, may prefer (or be legally required) to have their data not leave their country or their servers, or may find that the locally grown SaaS services they use are often not supported by the existing US-centric vendors.

And to be clear, US companies are not immune to these issues, even if they may be somewhat less affected by the financial argument. Think of HIPAA compliance, for example, which many (most? all?) hosted tools don't offer unless you sign up for one of their more expensive plans.

**If you do not feel the pain of the current situation or see the need for change, recognize that your experience may not be representative.**

### Data integration as a commodity

This perspective leads me to an argument with an ideological angle, that is particularly compelling to me because of the many parallels I see with the early days of [GitLab](https://about.gitlab.com/): the open source project that was [founded in Ukraine back in 2011](https://about.gitlab.com/company/history/) with the goal of building a self-hosted alternative to the likes of [GitHub](https://github.com/) and [Bitbucket](https://bitbucket.org/), that a few years later became an open core product maintained primarily by the newly founded company that shares its name. To this day, GitLab comes in open source and proprietary flavors, and the functionality included in the Community Edition continues to be sufficient for hundreds of thousands of organizations around the world, that would otherwise have needed to opt for a paid, proprietary alternative. As GitLab is sponsoring the development of Meltano, these parallels are not a coincidence.

Since an ELT platform is a tool every data engineer and every company needs if they want to have the best chance of survival and success, I would argue that it should be a commodity and should be available at a reasonable cost to everyone who wants or needs it. Anything less than that hurts a significant number of companies in their ability to reach their true potential and serve their users and customers as well as they would want to, thereby stifling innovation and competition, and we all end up paying the price because we have to deal with companies and products that are less optimized and improved than they could be.

The obvious question: if this is apparently such a problem, why haven't tons of competitors popped up already to serve these local markets or inject some competition into the US market? Orchestrating reliable data pipelines _is_ a solved problem, even in the open source space, where great tools like [Airflow](https://airflow.apache.org/) and [Luigi](https://github.com/spotify/luigi) exist and are running in production at thousands of organizations. That's not to say they're as easy to configure and get started with as the hosted platforms we're talking about, but the technology is there, assuming you have an extractor and loader to plug in.

And I think that assumption is at the core of the issue, and at the core of the economic moat that the existing vendors have created around themselves, that makes it hard for new parties to enter the market and compete: the impressive amount of data sources they support out of the box, and their massive (in-house or outsourced) teams that have spent and continue to spend thousands of hours developing and maintaining these extractors and loaders.

If you've read [part 1](#) of this 2-part series, you'll remember that we ran into this ourselves when we offered a hosted version of Meltano's data connection and analytics interface to non-technical end-users. They could go straight from connecting their data source to viewing a dashboard, but only if we had written the extractor, loader, transformations, and models for that data source beforehand, and if we would continue to maintain these forever. We realized that this wasn't going to scale, and so would most companies that would decide to just write and maintain their own extractors instead of paying someone else to do it: it's a lot of work, and **it never ends**.

## The solution: open source

Ultimately, though, the size of the economic moat that exists around these vendors can be measured in terms of developer hours, and there's no secret sauce or intellectual property that separates the current major players from anyone else out there who has their own hours to bring to the table.

By yourself, as a single company or data engineer, implementing and maintaining extractors for all of the data sources you need to integrate is not feasible, which is why most don't.

Together, though, that changes. With a big enough group of people capable of programming and motivated to collaborate on the development and maintenance of extractors and loaders, it's just a matter of time (and continued investment of time by a subset of the community) before every proprietary extractor or loader has an open source equivalent. The maintenance burden of keeping up with API and schema changes is not insignificant, but if open source communities can manage to maintain language-specific API client libraries for most SaaS APIs out there, there's no reason to think we'd have a harder time maintaining these extractors.

Assuming there is no secret sauce or key intellectual property involved, **a sufficiently large and motivated group of people capable of programming can effectively will any new tool into existence**: that is the power of open source.

The more common the data source, the more people will want it, the faster it'll be implemented, the more heavily it'll be tested, and the more actively it'll be maintained. It doesn't need to take long before the segment of the market that only uses these common data sources will be able to swap out their current data integration solution for this open source alternative. It's not an all-or-nothing matter either: data teams can move their data pipelines over on a pipeline-by-pipeline basis, as extractors become available and reach the required level of quality.

Of course, a self-hosted platform for running data integration pipelines wouldn't just need to support a ton of extractors and loaders. You would also want to be confident that you can run it in production and get the same reliability and monitoring capabilities you get with the hosted vendors. Fortunately, this is where we can leverage an existing open source tool like Airflow or Luigi, that this hypothetical self-hosted platform could be built around.

### Everyone wins

Even if you're not personally interested in ever using a self-hosted data integration platform, you may benefit from us building one anyway.

Open source is the most promising strategy available today to increase competition in the data integration and data pipeline space. Even if the specific tool we're building doesn't actually become the Next Big Thing, the market will benefit from that increased competition.

Developers of new SaaS tools and data warehouse technology would also benefit from an open source standard for extractors and loaders. Rather than wait (or pay) for data integration vendors to eventually implement support for their tool once it reaches a high enough profile or once its users start begging (or paying) the vendor loudly enough, new tools could hit the ground running by writing their own integrations. Today, many companies wouldn't consider switching to a new SaaS tool that isn't supported by their data integration vendor at all, putting these tools at a significant competitive disadvantage against their more mature and well-connected competitors.

The only ones who have something to lose here are the current reigning champions. For everyone else it's a win-win, whether you actually contribute to or use Meltano, or not. If you don't believe me, just look at the DevOps space and the impact that GitLab has had on the industry and the strategy and offering of the previously dominant players, GitHub and Bitbucket.

If an industry has effectively become "pay to play" because every software engineer in that industry needs to use one of a handful of paid tools in order to get anything done at all, there is a massive opportunity for an open source alternative "for the people, by the people" to level the playing field, and disrupt the established players from the bottom on up.

Of course, GitLab is not just interested in sponsoring the development of such an open source project out of the goodness of its heart. The hope is that eventually, a business opportunity will arise out of this project and its community and ecosystem, because even if a truly competitive free and open source self-hosted option is available, there will always be companies that would still prefer a hosted version with great support and enterprise features, who won't mind paying for it.

But for everyone else, **there will always be a Community Edition, and data integration will forever be a commodity rather than pay to play**.

## The Singer specification

Of course, we are not the first to be intrigued by the concept of open source data integration. Most significantly, [Stitch](https://www.stitchdata.com/) has developed the [Singer specification](https://www.singer.io/), which they describe as follows:

> Singer describes how data extraction scripts—called “taps” —and data loading scripts—called “targets”— should communicate, allowing them to be used in any combination to move data from any source to any destination. Send data between databases, web APIs, files, queues, and just about anything else you can think of.

There's a [Getting Started guide](https://github.com/singer-io/getting-started/) on how to develop and run taps and targets (extractors and loaders), many dozens of them have already been written for wide range of data sources, warehouses and file formats, a good amount of them are actively maintained and being used in production by various organizations, and the [Singer community on Slack](https://singer-slackin.herokuapp.com/) has over 2,100 members, with new people joining every day.

Once you've written (or installed) a tap and target, you can pipe them together on the command line (`tap | target`) and see your data flow from source to destination, which you can imagine is quite satisfying.

Once you've hit that milestone, though, the next step is not quite so obvious. How do I actually build a data pipeline out of this that I can run in production? Is there a recommended deployment or orchestration story? How do I manage my pipeline configuration and state? How do I keep track of the metrics some taps output, and how do I monitor the whole setup so that it doesn't fall flat on its face while I'm not looking?

Unfortunately, the Singer specification and website don't touch on this. A number of tools have come out of the Singer community that make it easier to run taps and targets together ([PipelineWise](https://transferwise.github.io/pipelinewise/), [singer-runner](https://github.com/datamill-co/singer-runner), [tapdance](https://github.com/aaronsteers/tapdance), and [knots](https://github.com/singer-io/knots), to list a few), and some of these are successfully being used in production, but getting to that point still requires one to figure out and implement a deployment and orchestration strategy, and those who have managed to do so effectively have all needed to reinvent the wheel.

This means that while open source extractors and loaders do exist, as does a community dedicated to building and maintaining them, what's missing is the open source tooling and documentation around actually deploying and using them in production.

### The missing ingredients

If this tooling did exist and if Singer-based data integration pipelines were truly easy to deploy onto any server or cloud, the Singer ecosystem immediately becomes a lot more interesting. Anyone would be able to spin up their own [Alooma](https://www.alooma.com/)/[Blendo](https://www.blendo.co/)/[Hevo](https://hevodata.com/)/[Matillion](https://www.matillion.com/products/etl-software/)/[Pentaho](https://www.hitachivantara.com/en-us/products/data-management-analytics/pentaho-platform.html)/[Xplenty](https://www.xplenty.com/)-alternative, self-hosted and ready to go with a wide range of supported data sources and warehouses. Existing taps and targets would get more usage, more feedback, and more contributions, even if many prospective users may still end up opting for one of the proprietary alternatives in the end.

Many people who come across the Singer ecosystem today end up giving up because they can't see a clear path towards actually using these tools in production, even if taps and targets already exist for all of the sources and destinations they're interested in. You have to be particularly determined to see it through and not just opt for one of the hosted alternatives, so the majority of people developing taps and targets and running them in production today are those for whom _not_ self-hosting was never really an option. Any amount of better tooling and documentation will cause people to take the Singer ecosystem more seriously as an open source data integration solution, and convince a couple more people to give it a try, who would have long given up today.

Developing taps and targets is also not as easy as it could be. The Getting Started guide and [singer-tools](https://github.com/singer-io/singer-tools) toolset are a great start, and implementing a basic tap is pretty straightforward, but building one you would actually be comfortable running in production is still a daunting task. The existing taps can serve as examples, but they are not implemented consistently and don't all implement the full range of Singer features. The [singer-python](https://github.com/singer-io/singer-python) library contains utility functions for some of the most common tasks, but taps end up reimplementing a lot of the same boilerplate behavior anyway. Moreover, a testing framework or recommended strategy does not exist, meaning that users may not find out that a small inconspicuous change broke their extractor or loader until they see their entire data pipeline fail.

All in all, the Singer ecosystem has a ton of potential but suffers from a high barrier to entry, that negatively affects the experience of those who want to use using existing taps and targets, as well as those potentially interested in developing new ones.

Over the past few weeks, I've spent many hours talking to various members of the Singer community who _have_ been able to get their Singer-based pipelines running in production, and the observations above are informed by their perspectives and experience. Unanimously, they agreed that the Singer ecosystem is not currently living up to its potential, that change is needed, and that better tooling and documentation around deployment and development would go a long way.

## Where Meltano fits in

As I'm sure you've pieced together by now, [Meltano](https://meltano.com/) intends to be that tooling and bring that change.

Our goal is to **make the power of data integration available to all** by turning Meltano into a **true open source alternative to existing proprietary hosted ELT solutions**, in terms of ease of use, reliability, and quantity and quality of supported data sources.

Luckily, we're not starting from zero: Meltano already speaks the Singer language and [uses taps and targets for its extractors and loaders](https://meltano.com/#integration). Its support goes beyond simply piping two commands together, as it also manages [configuration](https://meltano.com/docs/command-line-interface.html#config), [entity selection](https://meltano.com/docs/command-line-interface.html#select) and [extractor state](https://github.com/singer-io/getting-started/blob/master/docs/CONFIG_AND_STATE.md#state-file) for you. It also makes it super easy to [set up pipeline schedules](https://meltano.com/#orchestration) that can be run on top of a supported orchestrator like [Airflow](https://airflow.apache.org/).

Additionally, Meltano supports [dbt](https://www.getdbt.com/)-based [transformation as part of every ELT pipeline](https://meltano.com/#transformation), and has [basic point-and-click analytics functionality](https://meltano.com/docs/analysis.html) built in, enabling you to go from data to dashboard using a single tool, that you can [run locally or host on any cloud](https://meltano.com/docs/installation.html).

For the foreseeable future, though, our focus will primarily be on [data integration](https://meltano.com/#integration), not transformation or analysis.

While we've come a long way already, there's still plenty of work to be done on the fronts of ease of use, reliability, and quantity and quality of supported data sources, and we can't afford to get distracted.

### Let's get to work!

If any of the above has resonated with you, or perhaps even inspired you, we'd love your help in realizing this vision for Meltano, the Singer ecosystem, and the data integration space in general. We literally won't be able to do it without you.

Before anything else, you'll want to see what Meltano can already do today by following the [examples on the homepage](https://meltano.com/). They can be copy-pasted right onto your command line, and in a matter of minutes will take you all the way through [installation](https://meltano.com/#installation), [integration](https://meltano.com/#integration), [transformation](https://meltano.com/#transformation), and [orchestration](https://meltano.com/#orchestration) with the [`tap-gitlab` extractor](https://meltano.com/plugins/extractors/gitlab.html) and [`target-jsonl`](https://meltano.com/plugins/loaders/jsonl.html) and [`target-postgres`](https://meltano.com/plugins/loaders/postgres.html) loaders.

Once you've got that working, you'll probably want to try Meltano with a different, more realistic data source and destination combination, which will require you to add a new [extractor](https://meltano.com/plugins/extractors/) ([Singer tap](https://www.singer.io/#taps)) and/or [loader](https://meltano.com/plugins/loaders/) ([Singer target](https://www.singer.io/#targets)) to your Meltano project. To learn how to do this, the homepage once again [has got you covered](https://meltano.com/#meltano-add).

And that's about as far as you'll be able to get right now, with Meltano's existing tooling and documentation. Running a Meltano pipeline locally (with or without Airflow) is one thing, but actually deploying one to production is another. As we've identified, this is one of the places where the Singer ecosystem and documentation currently fall short, and for the moment, Meltano is no different.

For this reason, the first people we would love to get involved with the Meltano project are **those who are already part of the Singer community**, and in particular **those who have already managed to get Singer-based ELT pipelines running in production**. We want to make it so that all future Singer community members and Meltano users will be able to accomplish what they did, and no one knows better what that will take (and how close or far off Meltano currently is) than they do.

If you're one of those people, or simply anyone with similarly relevant feedback, ideas, or experience, please:
- [give Meltano a try](https://meltano.com/) (with your existing taps and targets?),
- [join us on Slack](https://join.slack.com/t/meltano/shared_invite/zt-cz7s15aq-HXREGBo8Vnu4hEw1pydoRw) to receive (and provide) community support,
- [follow us on Twitter](https://twitter.com/meltanodata) to stay up to date on new releases and other developments,
- [file new issues on GitLab](https://gitlab.com/meltano/meltano/-/issues/new) for any ideas you have or bugs you run into,
- [participate in existing issues](https://gitlab.com/meltano/meltano/-/issues) that may benefit from your perspective,
- [check out the Python codebase](https://gitlab.com/meltano/meltano) if you're curious, and last but not least:
- **consider [contributing to Meltano](https://meltano.com/#contributing), its documentation, and its [extractors](https://meltano.com/plugins/extractors/) and [loaders](https://meltano.com/plugins/loaders/)**, so that your and everyone else's suggestions and dreams may come true.

I can't wait to see what we'll be able to accomplish together.

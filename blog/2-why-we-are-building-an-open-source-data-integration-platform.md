# Why we are building an open source data integration platform

This is part 2 of a 2 part series. If you're new to the Meltano project and mostly interested in what's next, feel free to start here and skip part 1. If you've been following the Meltano project for a while or would like to have some historical context, start with [part 1](#).

---

If you've read part of 1 the series, you know that Meltano is now an open source self-hosted data integration platform, yay!

But why are we even building this? Isn't data integration (getting data from sources like SaaS tools to destinations like data warehouses) a solved problem by now, with modern off-the-shelf tools like Fivetran having taken the data space by storm over the last few years and making it so that many (smaller) data teams don't even need a data engineer anymore?

Data integration tools are not _that_ expensive, especially compared to other tools in the data stack like Looker, and not having to worry about keeping your pipelines up and running or writing and maintaining data source connectors (extractors) is obviously extremely valuable.

On top of that, writing and maintaining extractors can be tedious, thankless work, so why would anyone want to do this themselves instead of just paying a vendor like Fivetran to handle this burden instead?

Why would anyone even want to use a self-hosted data integration platform, and why would anyone think building this is a good use of time or money, _especially_ if it's going to be open source?

---

In part 1, I explained why we have concluded that in order to eventually realize our end-to-end vision for Meltano (a single tool for the entire data analytics lifecycle, from data to dashboard), our goal for the foreseeable future has to be to "build a production-ready self-hosted open source alternative to existing proprietary hosted ELT/data pipeline/data integration solutions with a great library of extractors".

However, the points and questions raised above are totally valid, and were in fact raised by actual data engineers I've been talking to over the past few weeks. Meltano (and GitLab) may have a need for the existence of such an open source data integration platform, but it's a seperate matter entirely whether there are any data engineers or data teams out there who share that need and would actually consider joining the community, contributing, and eventually using the tool instead of whatever proprietary hosted tool they use today.

---

The argument that gets me the most excited personally is ideological in part, and I see many parallels with the early days of GitLab, the open source project that was founded in 2011 and a few years later became an open core product maintained primarily by the company that shares its name. (https://about.gitlab.com/company/history/)

The idea is that every data team in the world needs a data integration tool, because one way or another you have to get the data from the various sources into the data warehouse so that it can be analyzed. And since every company would be better off if they were analyzing their data and learning from their ups and their downs, every company in the world needs a data integration tool whether they already realize it or not.

Since there is currently no true open source alternative to the proprietary hosted tools, the data space has effectively become "pay to play". There are many great open source analytics and BI tools out there (Superset, Metabase and Redash come to mind, and of course Meltano comes with built-in analytics as well), but all assume that your data will somehow have already found its way into a data warehouse.

If for any reason at all you cannot use one of the hosted platforms, you are essentially out of luck and will not get to compete on a level playing field with those companies that can afford to integrate their data and start learning from it, even if you have everything else going for you. You are massively disadvantaged from day one.

While these tools may not be expensive to you, you're fine with your sensitive data flowing through a US company's servers, and you might not mind paying for professional services if you ever need to extract data from a source that isn't supported already, many around the world will find prices US companies charge prohibitively expensive relative to their local income, may prefer for their data not to leave their country, and will find that the locally grown SaaS services they use are often not supported by the existing vendors.

And it's not just non-US companies I'm talking about: think of HIPAA compliance, which many (most? all?) hosted tools don't offer unless you go for one of their more expensive plans.

So if you do not feel the pain of the current situation or see the need for change, realize that your experience may not be representative.

Since this is a tool every data engineer and every company needs if they want to have the best chance of survival and success, I would argue that it should be a commodity and should be available at a reasonable cost to everyone who wants or needs it. Anything less than that limits a massive number of companies from reaching their true potential, thereby stifling innovation and competition, and we all end up paying the price because we have to deal with companies and products that are less great than they could be.

So if this is apparently such a problem, why haven't tons of competitors popped up already to serve these local markets or inject some competition into the US market? Setting up and running reliable data pipelines _is_ a solved problem, even in the open source space, where great tools like Airflow and Luigi exist and are running in production at thousands of organizations. That's not to say they're as easy to configure and get started with as the hosted options we're talking about, but the technology is there, assuming you have an extractor and loader to plug in.

And I think that assumption is at the core of the issue, and at the core of the economic moat that the existing vendors have created around themselves that makes it hard for any newcomer to come in and compete: the impressive amount of data sources they support out of the box, and the massive (in-house or outsouced) teams that have spent and continue to spend thousands of hours developing and maintaining these extractors and loaders.

If you've read part 1 of this 2-part blog post series, you'll remember that we ran into this ourselves when we offered a hosted end-to-end data-to-dashboard platform to non-technical end-users, and we realized that in order for real world data teams to be able to use this tool, implementing data source support ourselves was not going to scale. The same goes for any individual company that would decide to just write and maintain their own extractors: it's a lot of work, and it never ends.

We are lucky, though, because the size of that moat is ultimately just measured in terms of man hours, and there's no secret sauce or IP that separates the current players from anyone else out there who has man hours to bring to the table.

By yourself, as a single company or data engineer, implementing and maintaining extractors for all of the data sources you need to integrate is not feasible, which is why most don't, and why there aren't dozens of small ELT startups out there.

Together, though, that changes. With a big enough group of people capable of programming and motivated to collaborate on the development and maintenance of extractors and loaders, it's just a matter of time (and continued investment of time by a subset of the community) before every proprietary extractor or loader has an open source equivalent. A sufficiently large and motivated group of people capable of programming can effecively will any new tool into existence: that's the power of open source.

The more common the data source, the more people will want it, the faster it'll be implemented, the more heavily it'll be tested, and the more actively it'll be maintained, meaning that it doesn't need to take long before the segment of the market that only uses these common data sources will be able to swap out their data integration tool for this open source alternative. It's not an all-or-nothing thing either: data teams can move their data pipelines over on a pipeline by pipeline basis, as extractors become available and reach the required level of quality.

Of course, a self-hosted data integration platform wouldn't just need to support a ton of extractors and loaders, you would also actually want to be confident that you can run it in production and get the same reliability you get with the hosted vendors. Fortunately, this is where existing tools like Airflow come in.

---

Even if you're not personally interested in ever using a self-hosted data integration platform, you may benefit from us building one anyway.

The way I see it, open source is the most promising strategy available today to increase competition in the data integration space. And even if this specific tool doesn't actually become the Next Big Thing, the market will benefit from that increased competition.

Developers of new SaaS tools and data warehouse technology would also benefit from an open source standard for extractors and loaders, since they could hit the ground running by writing their own integrations, instead of having to wait (or pay) for data integration vendors to eventually implement that support, once the tool becomes high profile enough or users start begging the vendor loud enough. Today, many companies wouldn't consider switching to a new SaaS tool that isn't supported by their data integration vendor at all, putting these tools at a significant competitive disadvantage against their more mature and well-supported competitors.

The only ones who have something to lose here are the current reigning champions. For everyone else it's a win-win, whether you actually contribute to or use Meltano or not.

If you don't believe me, just look at the DevOps space and the impact that GitLab has had on the industry and the strategy and offering of the previously dominant players, GitHub and Bitbucket. If an industry has effectively become "pay to play" because every software engineer in that industry needs to use one of a handful of paid tools in order to be productive, there is a massive opportunity for an open source alternative "for the people, by the people" to level the playing field, and disrupt the established players from the bottom.

It works out for GitLab (the company) that _eventually_, a business opportunity may arise out of such an open source project, community, and ecosystem, because there will always be people who do want a hosted version with great support and enterprise features and don't mind paying for it. 

But for everyone else, there will always be a Community Edition, and data integration will therefore always be a commodity.

---

Of course, we are not the first to be intrigued by the concept of open source data integration. Most significantly, Stitch Data has developed the Singer specification, which they describe as follows:

> Singer describes how data extraction scripts—called “taps” —and data loading scripts—called “targets”— should communicate, allowing them to be used in any combination to move data from any source to any destination. Send data between databases, web APIs, files, queues, and just about anything else you can think of.

There's a Getting Started guide (https://github.com/singer-io/getting-started/) on how to develop and run taps and targets, many dozens of them have already been written for wide range of data sources and warehouses, a good amount of them are actively maintained and being used in production by various organizations, and the community on Slack has over 2,000 members, with new people signing up every day.

Once you've written (or installed) a tap and target, you can pipe them together on the command line (`tap | target`) and see your data flow from source to destination, which you can imagine is quite satisfying.

Once you've hit that milestone, though, the next step is not quite so obvious. How do I actually build a data pipeline out of this that I can run in production? Is there a recommended deployment or orchestration story? How do I manage my configuration and state? How do I keep track of the metrics some taps output, and how do I monitor the whole setup so it doesn't fall flat on its face?

Unfortunately, the Singer specification and website don't touch on this. A number of tools have come out of the Singer community that make it easier to run taps and targets together (PipelineWise, singer-runner, and knots, to list a few), and some of these are successfully being used in production, but getting to that point still requires one to figure out and implement a deployment and orchestration strategy, and those who have managed to do so have effectively all needed to reinvent the wheel.

This means that while open source extractors and loaders do exist, as does a community dedicated to building and maintaining them, what's missing is the open source tooling and documentation around actually deploying and using them in production.

If this tooling did exist and was truly easy to deploy onto any server or cloud, the Singer ecosystem immediately becomes a lot more interesting and the community more active, because anyone would be able to spin up their Fivetran alternative, with a wide range of supported data sources and warehouses. Existing taps and targets would get more usage, more feedback, and more contributions, even if many prospective users may still end up opting for one of the hosted alternatives in the end.

Many people who come across the Singer ecosystem today end up giving up because they can't see a clear path towards actually using these tools in production, even if taps and targets already exist for all of the sources and destinations they're interested in. You have to be particularly determined to see it through and not just opt for one of the hosted alternatives, so the majority of people running Singer-based data pipelines in production and developing taps and targets today are those for whom _not_ self-hosting was really not an option. Any amount of better tooling and documentation will cause people to take the Singer ecosystem more seriously as an open source data integration solution, and convince a couple more people to give it a try, who would have long given up today.

Developing taps and targets is also not as easy as it could be. The Getting Started guide is a great start, and implementing a basic tap is pretty straightforward, but building one you would actually be comfortable running in production is still a daunting task. The existing taps can serve as examples, but they are not implemented consistently, and don't all implement the full range of Singer features. The singer-python library contains utility functions for some of the most common tasks, but taps end up reimplementing a lot of the same boilerplate behavior anyway. A testing framework also does not exist, meaning that users may not find out that a small inconspicuous change broke their extractor or loader until they see their entire data pipeline fail.

All in all, the Singer ecosystem has a ton of potential but suffers from a high barrier to entry, keeping out entirely or turning away quickly many if not most of those who want to use existing taps and targets, as well as those who want to develop new ones.

Over the last few weeks, I've spent many hours talking to various prominent members of the Singer community, who have been able to get it working in production, and the observations above are informed by their perspectives and experience. Unanimously, they agreed that the Singer ecosystem is not currently living up to its potential, that change is needed, and that better tooling and documentation would go a long way.

---

As I'm sure you've figured out by now, Meltano intends to be that tooling and bring that change.

Meltano already speaks the Singer language and uses taps and targets for its extractors and loaders. It goes beyond simply piping two scripts together, and manages configuration, entity selection and state for you. It also allows you to set up schedules that can be run on top of a supported orchestrator, like Airflow or GitLab CI.

Additionally, it supports dbt transformations as part of every ELT pipeline, and has basic analytics built in so that you can go from data to dashboard using a single tool, that you can run locally or host anywhere you like.

For the foreseeable future, though, our focus will be on data integration, not transformation or analysis. There's still plenty of work to be done here to realize our dream of turning Meltano into that production-ready self-hosted open source alternative to existing proprietary hosted ELT/data pipeline/data integration solutions, and we can't afford to get distracted.

Let's get to work!

(Some call to action)

- Link to epic, milestone
- Link to getting started guide
- 

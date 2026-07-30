<div align="center">

<img src="./ascii.svg" width="460" alt="PedroZia"/>

<img src="./stats.svg" width="620" alt="Contributions in the last year"/>
<img src="./runs.svg" width="620" alt="Workflow status"/>

[linkedin](https://br.linkedin.com/in/pedrozia) &nbsp;·&nbsp;
[instagram](https://www.instagram.com/pedropaulozia) &nbsp;·&nbsp;
[website](#) &nbsp;·&nbsp;
[email](mailto:pedropaulozia@gmail.com)

</div>

<img src="./hd-about.svg" width="620" alt="about"/>

> Backends that hold up, pipelines that don't need babysitting — CI, scheduled<br>
> automation, and embedded when something has to talk to the real world.

I build backends in Java / Quarkus, ship them through pipelines I maintain, and<br>
reach for C on microcontrollers when the problem leaves the server. This profile<br>
is a scheduled automation in itself — every graphic here is drawn by a workflow<br>
from live data, not embedded from a third-party service.

<img src="./hd-stack.svg" width="620" alt="stack"/>

**Backend**&nbsp;&nbsp;&nbsp; <samp>java &nbsp; quarkus &nbsp; hibernate &nbsp; rest apis &nbsp; python</samp><br>
**Frontend**&nbsp; <samp>javascript &nbsp; html &nbsp; css &nbsp; primefaces</samp><br>
**Database**&nbsp; <samp>postgresql &nbsp; sqlite &nbsp; sql</samp><br>
**DevOps**&nbsp;&nbsp;&nbsp;&nbsp;<samp>docker &nbsp; git &nbsp; github actions &nbsp; gitlab ci &nbsp; linux &nbsp; wildfly</samp><br>
**Embedded**&nbsp; <samp>arduino &nbsp; esp32 &nbsp; avr &nbsp; automation</samp><br>
**Exploring** <samp>ai &nbsp; machine learning &nbsp; computer vision</samp>

<img src="./hd-projects.svg" width="620" alt="projects"/>

**[contribution-snapshot](https://github.com/PedroZia/contribution-snapshot)** &nbsp;·&nbsp; <samp>github actions, yaml</samp><br>
Reusable composite action — draws an SVG contribution sparkline from the<br>
GraphQL API. Drop it into any workflow, no third-party services.

**[your-project](#)** &nbsp;·&nbsp; <samp>stack, here</samp><br>
Short description of what this project does.

**[another-project](#)** &nbsp;·&nbsp; <samp>stack, here</samp><br>
Short description of what this project does.

<img src="./hd-stats.svg" width="620" alt="stats"/>

<div align="center">

<img src="./streak.svg" width="620" alt="Current and longest streak"/>

<img src="./langs.svg" width="620" alt="Top languages by bytes and by repo"/>

<img src="./year.svg" width="620" alt="The last year, one character per day"/>

<img src="./recent-activity.svg" width="620" alt="Recent public activity"/>

</div>

<img src="./hd-about-this-page.svg" width="620" alt="how it runs"/>

Every graphic here is generated, not embedded from anyone else's server.<br>
`ascii.svg` is a photo pushed through a character ramp by<br>
[`scripts/make_portrait.py`](scripts/make_portrait.py); the stat graphics and<br>
these section headings are drawn by two scheduled actions —<br>
[`refresh stats`](.github/workflows/stats.yml) at 05:17 UTC and<br>
[`refresh activity`](.github/workflows/activity.yml) at 05:41 UTC — once a day,<br>
committing only what changed. The `runs.svg` badge at the top tells you whether<br>
they actually ran — drawn from the Actions API, not a third-party badge service.

They animate with SMIL inside the SVG, because GitHub strips scripts from<br>
READMEs — and since nothing loads from a third party, nothing here can<br>
rate-limit or go dark. The headings are SVGs for the same reason: GitHub also<br>
strips CSS, so an image is the only way to put this page's own typeface on them.

The typeface is [JetBrains Mono](scripts/fonts), subset to just the characters<br>
each graphic draws and inlined as base64. That isn't only for looks: the<br>
portrait's grid assumes an advance width of exactly 0.600 em, and a viewer whose<br>
default monospace is narrower would otherwise see it squeezed.

Three APIs feed this page — GraphQL for contributions, Events for recent<br>
activity, Actions for workflow status — all called from the runner with zero<br>
external services in the critical path. Language totals cover public<br>
repositories only. `year.svg` uses the portrait's character ramp: `:` `+` `#` `@`,<br>
quiet to loud.

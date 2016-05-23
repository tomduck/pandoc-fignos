---
figure-name: FIG
fignos-plus-name: FIG.
fignos-star-name: FIGURE
...

Figures @fig:1, {@fig:2}a and {@fig:2}b, and  {@fig:3}: 

![Some data.](img/plot1.png){#fig:1}

![More data.](img/plot2.png){#fig:2}

![Even more data. Reference to +@fig:1.][ref-link]

[ref-link]: img/plot3.png {#fig:3}

*@fig:1, {+@fig:2}a and fig. !@fig:3.

Figures {@fig:1}-{@fig:3}, and figs. {@fig:1}-{@fig:2}-{@fig:3}.

References in lists:

 1. *@fig:1, {+@fig:2}a and fig. !@fig:3.
 2. Figures {@fig:1}-{@fig:3}, and figs. 
    {@fig:1}-{@fig:2}-{@fig:3}.

A [regular link](http://example.com/), an [*italicized link*](http://example.com/) and an email.address@mailinator.com.


****


\newpage


Corner cases
------------

*Issue: Attributed images are supported by pandoc >= 1.16.  Using the attribute `width="50px"` with earlier versions has no effect.*

****

Figure:

![Unnumbered and unattributed.](img/plot3.png)

****

Figure:

![Unnumbered with empty attributes.](img/plot3.png){}

****

Figure:

![Unnumbered and attributed (small).](img/plot3.png){#baz width="50px"}

****


\newpage


Figure @fig:c1:

*Issue: references ending in colons do not convert for pandoc 1.15*

![Numbered and attributed (small).](img/plot3.png){#fig:c1 width="50px"}

****

Figure {@fig:c2}:

![Numbered and link-attributed (small).][link-c2]

[link-c2]: img/plot3.png {#fig:c2 width="50px"}

****

Figure {@fig:c3}:

![Numbered and attributed (small) with breaking space after markdown.](img/plot3.png){#fig:c3 width="50px"} 

****

Image (non-breaking space after markdown), unattributed:

![Caption should not show.](img/plot3.png)\ 

****

Image (non-breaking space after markdown), attributed (small):

![Caption should not show.](img/plot3.png){#fig: width="50px"}\ 

****


\newpage


Inline image with attributes (small)
![Caption should not show.](img/plot3.png){#fig: width="50px"}
and another without
![Caption should not show.](img/plot3.png)

****

Here is a series of unreferenceable figures:

![Unreferenceable 1.](img/plot1.png){#fig: width="50px"}

![Unreferenceable 2.](img/plot1.png){#fig: width="50px"}

![Unreferenceable 3.](img/plot1.png){#fig: width="50px"}


****


\newpage


Figures @fig:tag1 and @fig:tag2 are tagged tables:

![Tagged 1.](img/plot1.png){#fig:tag1 width="50px" tag=B.1}

![Tagged 2.](img/plot1.png){#fig:tag2 width="50px" tag="$\mathrm{B.3'}$"}

Check that the number for Fig. @fig:tag3 follows from those earlier.

![Numbered.](img/plot1.png){#fig:tag3 width="50px"}

****


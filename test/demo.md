---
figure-name: FIG
...

Figures @fig:plot1, {@fig:plot2}a and {@fig:plot2}b, and  {@fig:plot3}:

![Plot 1.](img/plot1.png){#fig:plot1}

![Plot 2.](img/plot2.png){#fig:plot2}

![Plot 3.][ref-link]

[ref-link]: img/plot3.png {#fig:plot3}

*@fig:plot1 and {+@fig:plot2}a.

Figures {@fig:plot1}-{@fig:plot3}, and Figs {@fig:plot1}-{@fig:plot2}-{@fig:plot3}.

References in lists:

 1. Figure @fig:plot1 and Fig. {@fig:plot2}a.
 2. Figures {@fig:plot1}-{@fig:plot3}, and Figs. 
    {@fig:plot1}-{@fig:plot2}-{@fig:plot3}.

A [regular link](http://example.com/), an [*italicized link*](http://example.com/) and an email.address@mailinator.com.


\newpage

****

Corner cases
------------

Note: Attributed images are supported by pandoc >= 1.16.  Using the attribute `width="50px"` with earlier versions has no effect.

****

Figure:

![Unnumbered and unattributed.](img/plot3.png)

*[Issue #15](https://github.com/tomduck/pandoc-fignos/issues/15): pdf output has numbers.*

****

Figure:

![Unnumbered and attributed (small).](img/plot3.png){#baz width="50px"}

*[Issue #15](https://github.com/tomduck/pandoc-fignos/issues/15): pdf output has numbers.*

***

\newpage

Figure {@fig:c1}:

![Numbered and attributed (small).](img/plot3.png){#fig:c1 width="50px"}

****

Figure {@fig:c2}:

![Numbered and link-attributed (small).][link-c2]

[link-c2]: img/plot3.png {#fig:c2 width="50px"}

****

Figure {@fig:c3}:

![Numbered and attributed (small) with breaking space after markdown.](img/plot3.png){#fig:c3 width="50px"} 

****

\newpage

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

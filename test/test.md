---
figure-name: FIG
fignos-plus-name: FIG.
fignos-star-name: FIGURE
header-includes: 
  - \usepackage{caption}
...

Figures @fig:1, {@fig:2}a and {@fig:2}b, and {@fig:3}: 

![Number one.](img/fig-1.png){#fig:1 width=1in}

![Number two.](img/fig-2.png){#fig:2 width=1in}

![Number three. Reference to +@fig:1.][ref-link]

[ref-link]: img/fig-3.png {#fig:3 width=1in}

*@fig:1, {+@fig:2}a and fig. !@fig:3.

Figures {@fig:1}-{@fig:3}, and figs. {@fig:1}-{@fig:2}-{@fig:3}.

References in lists:

 1. \*@fig:1, {+@fig:2}a *and* fig. !@fig:3.
 2. Figures {@fig:1}-{@fig:3}, and figs. 
    {@fig:1}-{@fig:2}-{@fig:3}.

A [regular link](http://example.com/), an [*italicized link*](http://example.com/) and an email.address@mailinator.com.



\newpage

More Tests
----------

**Issues:**

  * Attributed images are supported by pandoc >= 1.16.  Using
    attributes like `width="50px"` with earlier versions has 
    no effect. (won't fix)

  * References ending in colons do not convert for pandoc 1.15.
    (won't fix; use curly-braces workaround)


### Unnumbered figures ###

![Unnumbered and unattributed.](img/fig-1.png)

![Unnumbered with empty attributes.](img/fig-1.png){}

![Unnumbered and attributed (small).](img/fig-1.png){#baz width="50px"}


\newpage

### Attributed Figures ###

Figure @fig:c1:

![Numbered and attributed (small).](img/fig-1.png){#fig:c1 width="50px"}

Figure {@fig:c2}:

![Numbered and link-attributed (small).][link-c2]

[link-c2]: img/fig-1.png {#fig:c2 width="50px"}

Figure {@fig:c3}:

![Numbered and attributed (small) with breaking space after markdown.](img/fig-1.png){#fig:c3 width="50px"} 


\newpage

### Images ###

Image (non-breaking space after markdown), unattributed:

![Caption should not show.](img/fig-1.png)\ 

Image (non-breaking space after markdown), attributed (small):

![Caption should not show.](img/fig-1.png){#fig: width="50px"}\ 

Inline image with attributes (small)
![Caption should not show.](img/fig-1.png){#fig: width="50px"}
and another without
![Caption should not show.](img/fig-1.png)


\newpage 

### Unreferenceable Figures ###

![Unreferenceable 1.](img/fig-1.png){#fig: width="50px"}

![Unreferenceable 2.](img/fig-1.png){#fig: width="50px"}

![Unreferenceable 3.](img/fig-1.png){#fig: width="50px"}


\newpage

### Tagged Figures ###

Figures @fig:tag1 and @fig:tag2 are tagged figures:

![Tagged 1.](img/fig-1.png){#fig:tag1 width="50px" tag=B.1}

![Tagged 2.](img/fig-1.png){#fig:tag2 width="50px" tag="$\text{B.3}'$"}

Check that the number for Fig. @fig:tag3 follows from those earlier.

![Numbered.](img/fig-1.png){#fig:tag3 width="50px"}


---
cleveref: True
xnos-number-sections: True
title: Test Document
header-includes:
  - \numberwithin{figure}{section}
  - \numberwithin{equation}{section}
  - \numberwithin{table}{section}
...

Title 1
=======

Blah blah @fig:1, @eq:1.

![Caption.](fig.png){#fig:1 width=5%}

$$ y = f(x) $${#eq:1}

![Caption.](fig.png){#fig:1.1 width=5%}

$$ y = f(x) $${#eq:1.1}

X Y
- -
T F

Table: Foo. {#tbl:1}


Subtitle 1 {-}
----------

Blah @fig:2, @eq:2.

![Caption.](fig.png){#fig:2 width=5%}

![Caption.](fig.png){#fig:2.1 width=5%}

$$ y = f(x) $${#eq:2}

$$ y = f(x) $${#eq:2.1}


Title 2
=======

Blah blah blah @fig:2, @eq:3.

$$ y = f(x) $${#eq:3}

![Caption.](fig.png){#fig:3 width=5%}


Subtitle 2
----------

Blah @fig:4, @eq:4.


Subtitle 3
----------

$$ y = f(x) $${#eq:4}

![Caption.](fig.png){#fig:4 width=5%}

![Caption.](fig.png){#fig:4.1 tag="B.3" width=5%}

![Caption.](fig.png){#fig:4.2 width=5%}

$$ y = f(x) $${#eq:4.1 tag "A.3"}

$$ y = f(x) $${#eq:4.2}



Title 3
=======

![Caption.](fig.png){#fig:5 width=5%}

$$ y = f(x) $${#eq:5}

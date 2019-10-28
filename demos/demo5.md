---
title: Pandoc-fignos Subfigures Demo
geometry:
  - top=1in
  - bottom=1in
fignos-cleveref: True
fignos-plus-name: Fig.
fignos-star-name: Figure
...

Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.

::: {#fig:1 .subfigures}

![a) The number one.](img/fig-1.png){width=1in}

![b) The number two.](img/fig-2.png){width=1in}

*@fig:1{nolink=True}: Two numbers.
:::

References to @fig:1, {@fig:1}a, and {@fig:1}b.

![The number three.](img/fig-3.png){#fig: width=1in}

Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.

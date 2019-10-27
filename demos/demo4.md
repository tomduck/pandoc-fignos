---
title: Pandoc-fignos Subfigures Demo
geometry:
  - top=1in
  - bottom=1in
fignos-cleveref: True
fignos-plus-name: Fig.
header-includes: \usepackage{subcaption}
...

Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.

\begin{figure}
  \centering
  \begin{subfigure}[b]{0.3\textwidth}
    \centering
    \includegraphics[width=\textwidth]{img/fig-1.png}
    \caption{The number one.}
  \end{subfigure}
  \begin{subfigure}[b]{0.3\textwidth}
    \centering
    \includegraphics[width=\textwidth]{img/fig-2.png}
    \caption{The number two.}
  \end{subfigure}
  \caption{Two numbers.}
  \label{fig:1}
\end{figure}

References to @fig:1, {@fig:1}a, and {@fig:1}b.

![The number three.](img/fig-3.png){#fig: width=1in}

Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.

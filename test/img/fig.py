#! /usr/bin/env python3

from matplotlib import pyplot

def makefig(n, x):
    fig = pyplot.figure(figsize=(1, 1))
    ax=fig.add_axes((0,0,1,1))
    ax.set_axis_off()
    ax.text(0.5, 0.43, str(n), size=65, color='k', ha='center', va='center',
                transform=ax.transAxes)
    ax.plot([0.01, 0.01, 0.99, 0.99, 0.01],
            [0.01, 0.99, 0.99, 0.01, 0.01], 'k-')
    pyplot.savefig('fig-%s.png' % (str(n),), dpi=300)

makefig(1, 0.4)
makefig(2, 0.48)
makefig(3, 0.5)

pyplot.show()

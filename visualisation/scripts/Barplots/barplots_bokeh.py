#!/usr/bin/env python
# coding: utf8

from bokeh.io import show, output_file
from bokeh.io import export_png

from bokeh.models import ColumnDataSource, FactorRange
from bokeh.models import LinearAxis, Range1d
from bokeh.models import Legend

from bokeh.palettes import Spectral6
from bokeh.plotting import figure
from bokeh.transform import factor_cmap

import pandas as pd
import argparse
from math import pi
import logging
logging.basicConfig()

def makeValues(df, start, list_sp):
    """ store values of a line in a dictionary containing counts, frequencies and pvalues for each species
    (keys=lines index). Read on every two lines

    Args:
        - df : a pandas dataFrame
        - start (int) : which lines to store (0: counts, 1:frequencies, 3: pvalues)
        - list_sp (list of str) : the species names

    Return:
        - dic (dict)
    """
    dic = {}
    for i in range(start, len(df), 3):
        dic[list_sp[i/3]] = list(df.iloc[i])
    return dic


def makeLegend(what, r):
    """ Build the legend of the barplot

    Args:
        - what (tuple of str): ex ('counts', 'Frequencies', 'pvalues')
        - r (tuple of [bokeh objects])

    Return:
        - legend (bokeh 'Legend' object)
    """
    items = []
    for i in range(len(what)):
        items.append((what[i], r[i]))
    legend = Legend(items=items, location=(0,0), orientation='horizontal')
    return legend

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="Input csv file")
    parser.add_argument("represent", choices=("counts", "frequencies", "both"), help="choose what to plot")
    # Compatible only with represent = both
    parser.add_argument("-s", "--separated", action="store_true", help="choose to plot frequencies and counts on the same graph or not")

    args = parser.parse_args()

    df = pd.read_csv(args.file, sep=",", index_col=0)   

    # 1 - species (do not sort !)    
    list_sp = [str.split(sps, "_")[0] for sps in list(df.index.values)[0::3]]

    # 2 - codons/aa/aatypes names
    xaxis = list(df)
    if len(xaxis) == 4:
        end_title = "amino-acids-types"
        width = 500
    if len(xaxis) == 20:
        end_title = "amino-acids"
        width = 650
    if len(xaxis) == 61:
        end_title = "codons"
        width = 900

    # 3 - store values
    dic_yaxis_counts = makeValues(df, 0, list_sp)
    dic_yaxis_freqs = makeValues(df, 1, list_sp)
    dic_yaxis_pvalues = makeValues(df, 2, list_sp)

    # For ordering xaxis according to amino-acids types
    x_range = {'codons' : ['ttt','ttc','tgg','tat','tac','gat','gac','gaa','gag','cat',
                            'cac','aaa','aag','cgt','cgc','cga','cgg','aga','agg','tgt',
                            'tgc','aat','aac','cct','cca','ccg','ccc','caa','cag','tct',
                            'tcc','tca','tcg','agt','agc','act','acc','aca','acg','gct',
                            'gcc','gca','gcg','ggt','ggc','gga','ggg','att','atc','ata',
                            'tta','ttg','ctt','ctc','cta','ctg','atg','gtt','gtc','gta','gtg'],
                'amino-acids' : ['F','W','Y','D','E','H','K','R','C','N','P','Q','S','T','A','G','I','L','M','V'],
                'amino-acids-types' : ['aromatics','charged','polar','unpolar']}
    
    # 4 - plots. One plot per species

    # separated barplots for counts and freqs
    if args.separated :
        for species in list_sp:
            if args.represent in ['counts', 'both']:
                title = 'counts on {} {}'.format(species, end_title)

                p = figure(x_range=x_range[end_title], plot_width=width, plot_height=350, toolbar_location=None, title=title)
                if end_title == 'codons':
                    p.xaxis.major_label_orientation = pi / 3

                source = ColumnDataSource(data=dict(what=xaxis, counts=dic_yaxis_counts[species]))
                r1 = p.vbar(x='what', top='counts', width=0.9, source=source, line_color='white', fill_color=Spectral6[0]) # barplot
               
                # second y-axis and dot plot for pvalues
                p.extra_y_ranges = {'pvalues': Range1d(start=0, end=1)}
                p.add_layout(LinearAxis(y_range_name='pvalues'), 'right')
                r2 = p.circle(xaxis, dic_yaxis_pvalues[species], y_range_name='pvalues', color='black', line_width=2)
                
                legend = makeLegend(('counts', 'pvalues'), ([r1], [r2]))
                p.add_layout(legend, 'below')

                export_png(p, filename='{}.png'.format(title.replace(" ","_")))

            if args.represent in ['frequencies', 'both']:
                title = 'Frequencies on {} {}'.format(species, end_title)

                p = figure(x_range=x_range[end_title], y_range=(0,1), plot_width=width, plot_height=350, toolbar_location=None, title=title)
                if end_title == 'codons':
                    p.xaxis.major_label_orientation = pi / 3

                source = ColumnDataSource(data=dict(what=xaxis, freqs=dic_yaxis_freqs[species]))
                # plot frequencies and pvalues (barplot, dotplot)
                r1 = p.vbar(x='what', top='freqs', width=0.9, source=source, line_color='white', fill_color=Spectral6[5])
                r2 = p.circle(xaxis, dic_yaxis_pvalues[species], y_range_name='pvalues', color='black', line_width=2)
                p.y_range.start = 0
               
                legend = makeLegend(('Frequencies', 'pvalues'), ([r1], [r2]))
                p.add_layout(legend, 'below')

                export_png(p, filename='{}.png'.format(title.replace(" ","_")))

    # counts and frequencies on the same graph
    if not args.separated:
        for species in list_sp:
            title = 'Counts and Frequencies on {} {}'.format(species, end_title)

            p = figure(x_range=x_range[end_title], plot_width=width, plot_height=350, toolbar_location=None, title=title)
            if end_title == 'codons':
                p.xaxis.major_label_orientation = pi / 3

            p.extra_y_ranges = {'pvalues': Range1d(start=0, end=1)}
            p.add_layout(LinearAxis(y_range_name='pvalues'), 'right')

            source = ColumnDataSource(data=dict(what=xaxis, counts=dic_yaxis_counts[species]))
            r1 = p.vbar(x='what', top='counts', width=0.9, source=source, line_color='white', fill_color=Spectral6[0])
            source = ColumnDataSource(data=dict(what=xaxis, freqs=dic_yaxis_freqs[species]))
            r2 = p.vbar(x='what', top='freqs', width=0.9, source=source, y_range_name='pvalues', line_color='white', fill_color=Spectral6[5])
            r3 = p.circle(xaxis, dic_yaxis_pvalues[species], y_range_name='pvalues', color='black', line_width=2)

            legend = makeLegend(('counts', 'Frequencies', 'pvalues'), ([r1], [r2], [r3]))
            p.add_layout(legend, 'below')

            export_png(p, filename='{}.png'.format(title.replace(" ","_")))

if __name__ == "__main__":
    main()

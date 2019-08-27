'''
Main analysis script
'''
from matplotlib.colors import ListedColormap
from IPython.display import display_html
import matplotlib.ticker as ticker
import matplotlib.pyplot as plt
from scipy import stats
import seaborn as sns
import pandas as pd
import numpy as np
import matplotlib
import pickle
import math
import re

# setting sunlight foundation colors for graphs
sns.set(font='Arial', style="whitegrid")
sunlight = ["#d9b80d", "#ce4500", "#2e565a", "#323235", "#fafaf5"]
color_codes_wanted = ['yellow', 'red', 'blue', 'black', 'cream']
c = lambda x: sunlight[color_codes_wanted.index(x)]
sns.set_palette(sunlight)

def fetch_additional_data(txt_name, multi_word_terms, one_word_terms):
    '''
    Gets additional data from the objects stored in the pickle file. Useful for
    sentiment analysis, sanity checks and further data analysis. The ouputs from
    this function are used in the get_final_df function.

    Inputs:
        - txt_name (str): name of pickle file
        - multi_word_terms (lst): list of multi word terms
        - one_word_terms (lst): list of one word terms

    Outputs:
        - df_pre (pandas dataframe): dataframe containing all of the information
            collected in the pickle file for the pre period
        - df_post (pandas dataframe): dataframe containing all of the information
            collected in the pickle file for the post period
        - col_names (list): list of term names in more readable and presentable
            format
    '''
    with open (txt_name, 'rb') as fp:
        snapshots = pickle.load(fp)
    multi_word_terms = [' '.join(map(str, multi_word_terms[i])) for i in range(len(multi_word_terms))]
    #print('snapshots len', len(snapshots))
    col_names = one_word_terms + multi_word_terms
    #print(len(snapshots))

    ids = [snapshot.id for snapshot in snapshots]
    #print(len(ids), len(set(ids)))
    ttal_post = [snapshot.post['word_count'] for snapshot in snapshots]
    ttal_pre = [snapshot.pre['word_count'] for snapshot in snapshots]
    status = [snapshot.status for snapshot in snapshots]
    dates_post = [snapshot.post['date'] for snapshot in snapshots]
    dates_pre = [snapshot.pre['date'] for snapshot in snapshots]
    text_post = [snapshot.post['text'] for snapshot in snapshots]
    text_pre = [snapshot.pre['text'] for snapshot in snapshots]
    url_pre = [snapshot.pre['url'] for snapshot in snapshots]
    url_post = [snapshot.post['url'] for snapshot in snapshots]
    results_pre = [snapshot.pre['results'] for snapshot in snapshots]
    results_post = [snapshot.post['results'] for snapshot in snapshots]
    #print(len(ids), len(ttal_post), len(url_pre))
    df_pre = pd.DataFrame({'id': ids,
                                      'ttal': ttal_pre,
                                      'dates': dates_pre,
                                      'text': text_pre,
                                      'url': url_pre,
                                      'results': results_pre})
    df_post = pd.DataFrame({'id': ids,
                                      'ttal': ttal_post,
                                      'dates': dates_post,
                                      'text': text_post,
                                      'url': url_post,
                                      'results': results_post})

    return df_pre, df_post, col_names

def clean_matrix(csv_name, col_names):
    '''
    Cleans results matrix.

    Inputs:
        - csv_name (str): name of the csv file containing the raw matrix
        - col_names (lst): list of terms

    Output: a pandas dataframe that only contains counts for websites from which
        the content was succesfully extracted
    '''
    df = pd.read_csv(csv_name, names=col_names, header=None)
    df['id'] = df.index + 1 #constructs consecutive id
    df_clean = df.dropna()

    return df_clean

def get_final_df(department_file, multi_word_terms, one_word_terms, output_file):
    '''
    Constructs the final dataframe that is used in further analysis.

    Inputs:
        - department_file (str): path to file with department names and ids
        - multi_word_terms (lst): multiword list of terms
        - one_word_terms (lst): list of one word terms
        - output_file (str): path for output file

    Outputs:
        - df_pre (df): a pandas pre dataframe with all the collected data
        - df_post (df): a pandas post dataframe with all the collected data
        - col_names (lst): list of names with proper format
    '''
    pickle_file = 'outputs/snapshots_{}.txt'.format(output_file)
    df_pre_additional, df_post_additional, col_names = fetch_additional_data(
                                                       pickle_file,
                                                       multi_word_terms,
                                                       one_word_terms)
    #print(len(df_pre_additional), len(df_post_additional))
    df_pre_clean = clean_matrix('outputs/{}_pre.csv'.format(output_file), col_names)
    df_post_clean = clean_matrix('outputs/{}_post.csv'.format(output_file), col_names)
    #print(len(df_pre_clean), len(df_post_clean))
    # merge additional data to matrix
    df_pre = df_pre_clean.merge(df_pre_additional, how='left',
                                       left_on='id', right_on='id')
    df_post = df_post_clean.merge(df_post_additional, how='left',
                                        left_on='id', right_on='id')
    #print(len(df_pre), len(df_post))
    # merge department data
    if department_file:
        df_departments = pd.read_csv(department_file)
        df_pre = df_pre.merge(df_departments, how='left', left_on='id', right_on='id')
        df_post = df_post.merge(df_departments, how='left', left_on='id', right_on='id')

    return df_pre, df_post, col_names

def get_changes(df_pre, df_post, id_col, term_cols, ttal_col, department_name=None, pctg=True):
    '''
    Gets changes in total values or as the change in the prevalence (term /
    total words) of all terms
    '''
    if department_name:
        print(department_name)
        df_pre = df_pre[df_pre.department == department_name]
        df_post = df_post[df_post.department == department_name]

    if pctg:
        pd.set_option('display.float_format', lambda y: '%.2f' % y)
        # total number of words across all urls
        ttal_pre = df_pre[ttal_col].sum(axis=0)
        ttal_post = df_post[ttal_col].sum(axis=0)
        # total number of times word as percentage of all words (per term)
        pct_pre = (df_pre[term_cols].sum(axis=0) / ttal_pre)
        pct_post = (df_post[term_cols].sum(axis=0) / ttal_post)

        grand_ttal_pre = df_pre[term_cols].sum().sum() / ttal_pre
        grand_ttal_post = df_post[term_cols].sum().sum() / ttal_post
        delta = ((grand_ttal_post / grand_ttal_pre) - 1) * 100
        print("The relative number of terms changed {} %, from {} to {}".format(
            '%.2f'%(delta), '%.3f'%(grand_ttal_pre), '%.3f'%(grand_ttal_post)))
        #test_significance(df_pre[term_cols], df_post[term_cols], column, significance, normality)
        # percentage change
        changes = ((pct_post / pct_pre) - 1) * 100
        # drop nas
        changes_df = changes.sort_values().reset_index().rename(columns={'index': 'term', 0: 'change'}).dropna()
        changes_df = changes_df[changes_df.change != 0]

        return changes_df, pct_pre * 100, pct_post * 100
    else:
        # slice data with term columns and take post - pre difference
        changes = df_post[term_cols] - df_pre[term_cols]
        # sum totals by column
        changes_df = changes.sum(axis=0).sort_values().reset_index().rename(columns={'index': 'term', 0: 'change'})
        # filter out zeros
        changes_df = changes_df[changes_df.change != 0]
        grand_ttal_pre = df_pre[term_cols].sum().sum()
        grand_ttal_post = df_post[term_cols].sum().sum()
        delta = ((grand_ttal_post / grand_ttal_pre) - 1) * 100
        print("The absolute number of terms changed {} %, from {} to {}".format(
            '%.2f'%(delta), '%.0f'%(grand_ttal_pre), '%.0f'%(grand_ttal_post)))

        return changes_df

def plot_bars(df, x_col, y_col):
    '''
    Bar plot function
    '''
    sns_plot = sns.catplot(x=x_col, y=y_col, data=df,
                kind='bar', legend=False,
                height=5, aspect=6/5,
                color=c('yellow'))
                #palette=sns.light_palette(c('blue'), n_colors=50)
    sns_plot.set_xticklabels(rotation=90, fontsize=9)
    sns_plot.ax.set(xlabel='Term', ylabel='Change')

def plot_changes_dept(df_pre_merged, df_post_merged, col_names, department_list):
    '''
    Plot changes by department
    '''
    n_cols = 2
    n_rows = math.ceil(len(department_list) / n_cols)
    print('number of rows', n_rows)
    if n_rows == 2:
        fig, axs = plt.subplots(n_rows, n_cols, figsize=(7.5, 7.5))
    elif n_rows == 3:
        fig, axs = plt.subplots(n_rows, n_cols, figsize=(7.5, 9.5))

    for i, department_name in enumerate(department_list):
        df = get_changes(df_pre_merged, df_post_merged, 'id',
             col_names, 'ttal', department_name, pctg=False)
        df.to_csv('images/fig5_{}.csv'.format(re.sub(r"[^a-zA-Z0-9]+", '', department_name)))
        plt.subplot(n_rows, n_cols, i + 1)
        plt.xlabel("Terms", fontsize=9, fontfamily='Arial')
        plt.ylabel("Change", fontsize=9, fontfamily='Arial')
        plt.title(department_name, fontsize=10, fontfamily='Arial')
        plt.grid(which='major', axis='x')
        plt.xticks(rotation='vertical', fontsize=8, fontfamily='Arial')
        plt.yticks(fontsize=8, fontfamily='Arial')
        plt.gca().spines['right'].set_color('none')
        plt.gca().spines['top'].set_color('none')
        plt.bar(df['term'], df['change'], color="#d9b80d")
    if len(department_list) % 2 != 0:
        plt.delaxes(axs[n_cols - 1, n_rows - 1])
    plt.tight_layout()
    plt.show()

    #plt.savefig(save_name)
    '''
    for department_name in department_list:
        try:
            #rel_changes = a.get_changes(df_pre_merged, df_post_merged, 'id', col_names, 'ttal', department_name, pctg=True)
            abs_changes = get_changes(df_pre_merged, df_post_merged, 'id', col_names, 'ttal', department_name, pctg=False)
            plot_bars(abs_changes, 'term', 'change', department_name)
        except:
            pass
    '''

def plot_dpt_changes(df_pre, df_post, cols, control_terms, exclude=None):
    '''
    Plots discontinuous lollipop graph
    Reference: https://python-graph-gallery.com/184-lollipop-plot-with-2-groups/
    '''
    # handle data
    col_names = cols[:]
    for c_term in control_terms:
        col_names.remove(c_term)
    df_dpt_pre = df_pre.groupby(['department']).sum(axis=0)[col_names] # sum columns by department
    df_dpt_pre = df_dpt_pre.sum(axis=1).reset_index() # sum totals
    df_dpt_pre.columns = ['department', 'counts']
    # dpt_ttal_pre = df_dpt_pre.sum()
    df_dpt_post = df_post.groupby(['department']).sum(axis=0)[col_names] # sum columns by department
    df_dpt_post = df_dpt_post.sum(axis=1).reset_index() # sum totals
    df_dpt_post.columns = ['department', 'counts']

    df = pd.DataFrame({'department': df_dpt_pre.department,
                   'pre': df_dpt_pre.counts,
                   'post': df_dpt_post.counts})

    df['change'] = ((df.post / df.pre) - 1) * 100

    if exclude:
        df = df[df.department != exclude]
    ordered_df = df.sort_values(by='pre')
    # now plot it
    # left part of the plot
    my_range = range(1, len(df.index) + 1)
    f, (ax, ax2) = plt.subplots(1, 2, sharey=True, gridspec_kw={'width_ratios': [3, 1]})
    ax.hlines(y=my_range, xmin=ordered_df['pre'], xmax=ordered_df['post'], alpha=0.4)
    ax.scatter(ordered_df['pre'], my_range, color="#2e565a", label='pre', s=80)
    ax.scatter(ordered_df['post'], my_range, color="#d9b80d", label='post', s=80)
    for i, label in enumerate(ordered_df.change[:-1]):
        x = ordered_df.post.iloc[i]
        y = my_range[i]
        label = str(round(label, 2)) + ' %'
        ax.text(x, y + 0.3, label, fontsize=9)
    # right part of the plot
    ax2.hlines(y=my_range, xmin=ordered_df['pre'], xmax=ordered_df['post'], alpha=0.4)
    ax2.scatter(ordered_df['pre'], my_range, color="#2e565a", label='pre', s=80)
    ax2.scatter(ordered_df['post'], my_range, color="#d9b80d", label='post', s=80)
    for i, label in enumerate(ordered_df.change):
        # last data point
        if i == len(ordered_df.change) - 1:
            x = ordered_df.post.iloc[i]
            y = my_range[i]
            label = str(round(label, 2)) + ' %'
            ax2.text(x, y + 0.3, label, fontsize=9)

    ax.set_xlim(0, 1000)
    ax2.set_xlim(5400, 5800)

    d = .015 # how big to make the diagonal lines in axes coordinates
    # arguments to pass plot, just so we don't keep repeating them
    kwargs = dict(transform=ax.transAxes, color='grey', clip_on=False)
    ax.plot((1-(d/3), 1+(d/3)), (-d, +d), **kwargs)
    ax.plot((1-(d/3), 1+(d/3)),(1-d, 1+d), **kwargs)
    kwargs.update(transform=ax2.transAxes)  # switch to the bottom axes
    ax2.plot((-d, +d), (1-d, 1+d), **kwargs)
    ax2.plot((-d, +d), (-d, +d), **kwargs)

    ax2.xaxis.set_major_locator(ticker.MultipleLocator(200))
    ax.xaxis.set_major_locator(ticker.MultipleLocator(200))
    # make x label not visible at a certain position
    plt.setp(ax.get_xticklabels()[6], visible=False)
    plt.setp(ax2.get_xticklabels()[0], visible=False)
    plt.subplots_adjust(wspace=0.03) #space between plots
    #changing to arial and
    for tick in ax.yaxis.get_major_ticks():
        tick.label.set_fontfamily('Arial')
        tick.label.set_fontsize(9)
    for tick in ax.xaxis.get_major_ticks():
        tick.label.set_fontfamily('Arial')
        tick.label.set_fontsize(9)
    for tick in ax2.xaxis.get_major_ticks():
        tick.label.set_fontfamily('Arial')
        tick.label.set_fontsize(9)

    plt.legend(loc='lower right', fontsize=9)
    plt.yticks(my_range, ordered_df['department'])
    f.text(0.5, 0.04, 'Total term count', ha='center', va='center', fontsize=11)
    f.set_size_inches(6, 5)
    #plt.savefig(save_name)
    return ordered_df #.sort_values(by='change').set_index('department').rename_axis(None)

def plot_boxplot(df_pre, df_post):
    '''
    Plot boxplot
    '''
    df_boxplot = df_pre
    df_boxplot['time'] = 'pre'
    df_post['time'] = 'post'
    df_boxplot = df_boxplot.append(df_post, ignore_index=True)
    f, ax = plt.subplots()
    sns.boxplot(x="department", y="subjectivity", hue="time",
                  data=df_boxplot, ax=ax)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=90, fontsize=9)
    ax.set(xlabel='Department', ylabel='Subjectivity')
    f.set_size_inches(6, 5)

    return df_boxplot

def plot_normal(df_pre, df_post, column):
    '''
    Plot distribution
    Reference: https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.shapiro.html
    '''
    df_pre = df_pre[[column, 'id']]
    df_post = df_post[[column, 'id']]
    df = df_pre.merge(df_post, how='left', left_on='id', right_on='id')
    #print(df.columns)
    pre = column + '_x'
    post = column + '_y'
    df['change'] = df[pre] - df[post]
    df.dropna(inplace=True)
    p_value = stats.shapiro(df['change'])[1]
    f, ax = plt.subplots()
    f.set_size_inches(6, 5)
    sns.kdeplot(df.change, shade=True, color=c('blue'), ax=ax)
    ax.set(xlabel='Score', ylabel='Density')
    normality = True
    if p_value <= (5 / 100):
        print('With a p-value of {}, we reject the null hypothesis that the data was drawn from a normal distribution'.format(p_value))
        normality = False
    else:
        print('With a p-value of {}, there is evidence that the data is normally distributed'.format(
              p_value))

    #f.savefig(save_name)

    return normality

def test_significance(df_pre, df_post, column, significance, normality):
    '''
    Tests for the signficance in the change of a variable pre and post
    If the p-value is lower than the chosen signficance (1, 5, 10)
    Wilcoxon signed-rank Test
    Reference: https://docs.scipy.org/doc/scipy-0.14.0/reference/generated/scipy.stats.wilcoxon.html
    '''
    if normality:
        statistic, p_value = stats.ttes_rel(df_pre[column], df_post[column])
    else:
        statistic, p_value = stats.wilcoxon(df_pre[column], df_post[column])
    #print('The p-value is: ', p_value)
    if p_value <= (significance / 100):
        print('The change in {} is statistically significant at the {} %'.format(
              column, significance))
    else:
        print('The change in {} is not statistically significant at the {} %'.format(
              column, significance))


def display_side_by_side(*args):
    '''
    Display two pandas dataframes side by side
    Attribution: https://stackoverflow.com/questions/38783027/jupyter-notebook-display-two-pandas-tables-side-by-side
    '''
    html_str=''
    for df in args:
        html_str+=df.to_html()
    display_html(html_str.replace('table','table style="display:inline"'),raw=True)

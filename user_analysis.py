#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
used to analyze user activity
"""
from __future__ import division
import collections
import json
import sys
import pandas as pd
from scipy.ndimage.filters import gaussian_filter
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import FuncFormatter
import os
from matplotlib import rcParams
rcParams['font.family']  =  'Times New Roman'
rcParams['font.sans-serif']  =  ['Tahoma']
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from scipy import stats
import operator
from scipy.ndimage.filters import gaussian_filter1d, median_filter, uniform_filter1d
from urllib.parse import urlparse
from pathlib import Path
p_dropbox = Path(__file__).resolve().parents[3]
sys.path.append(os.path.join(p_dropbox, 'hf_codes'))
import sensing_tools


# loading shenzhen device IDs, key: ID, value: [busline, platenumber]
sz_busline_plate = json.load(open('../dev_busline_plate_dict'))

# sz_devID = []
# with open('../sz_devID') as f:
#     for line in f:
#         sz_devID = line.split(",")
# print ("Number of devices in Shenzhen: %d." %(len(sz_devID)))

devID_city_dict = json.load(open('../devID_city_dict'))


def time_2_sec(time_str):
    """
    :param time_str: 2017-03-06T11:28:26.000Z
    :return: seconds of data
    """

    times = time_str.split('T')[1].split('.')[0].split(':')
    return (3600*int(times[0])+60*int(times[1])+int(times[2]))


def user_temporal_dist(day_number):
    """
    show temporal distribution of users, 5 minute slot
    data source: con_discon
    :return:
    """

    data_path = "/home/hadoop/Downloads/bus_wifi/huashi/con_discon/2017-03-0"+str(day_number)+".gz/"

    user_total = []
    files = [];user_time = collections.defaultdict(list)
    for j in os.listdir(data_path):
        if j.startswith('part'):
            files.append(open(data_path+j))
    for file in files:
        for line in file:
            attrs = line.split('`')
            if attrs[0] in sz_busline_plate:
                try:
                    user_time[int(time_2_sec(attrs[3])/300)].append(attrs[1])
                    user_total.append(attrs[1])
                except:
                    continue

    user_num = collections.defaultdict(int)
    for k,v in user_time.items():
        user_num[k] = len(set(v))

    time_series = [0]*288
    for k1,v1 in user_num.items():
        time_series[k1] = v1

    time_series_percent = []
    for item in time_series:
        max_ = max(time_series)
        time_series_percent.append(100*item/max_)

    print ("Total number of users a day in Shenzhen: %d" %len(set(user_total)))

    # # used to show single day temporal pattern
    # with PdfPages('sz_user_num_temp_'+str(day_number)+'.pdf') as pdf:
    #     font_size = '33'
    #     fig  =  plt.figure()
    #     ax = fig.add_subplot(111)
    #     ax.plot(np.arange(288), uniform_filter1d(time_series_percent,5), '-', color = '#0066cc', linewidth = 3)
    #     # ax.annotate('(0.27 hour, 80% buses)', xy = (982, 80), xytext = (1800, 60),\
    #     # arrowprops = dict(facecolor = 'black', shrink = 0.1),\
    #     # size = font_size)
    #     plt.subplots_adjust(top = 0.95, right = 0.9, left = 0.22, bottom = 0.23)
    #     plt.xticks(np.arange(0,289,step = 48),[0,4,8,12,16,20,24],size = font_size)
    #     plt.yticks(np.arange(0,101,step = 20),[0,20,40,60,80,100],size = font_size) #
    #     # plt.legend(['Network A','Network B'],fontsize = 25, loc = 'lower right')
    #     plt.xlabel('Time of Day (h)', fontsize = font_size)
    #     plt.ylabel('% of Users',fontsize = font_size)
    #     plt.grid()
    #     plt.xlim(0,288)
    #     plt.ylim(0,100)
    #     plt.show()
    #     pdf.savefig(fig)
    return time_series_percent


def user_temporal_dist_week():
    """
    draw a week long temporal pattern
    :return:
    """

    time_series_percent_all = []
    for i in [6,7,1,2,3,4,5]:
        time_series_percent_all + =  user_temporal_dist(i)


def user_http_analysis():
    """
    cdf of user request
    """

    data_path = '/home/hadoop/Downloads/bus_wifi_data/huashi_2month/userHttp/2017-03-06.gz/'
    files = [];user_recs_http = collections.defaultdict(int)
    tmp = collections.defaultdict(list)
    for j in os.listdir(data_path):
        if j.startswith('part'):
            files.append(open(data_path+j))
    for file in files:
        for line in file:
            attrs = line.split('`')
            if attrs[0] == []:
                continue
            # quick way
            if (attrs[0]) in sz_busline_plate:
                tmp[attrs[2]].append(attrs[6]) # 6: url
    for userid, con in tmp.items():
        user_recs_http[userid] = len(list(set(con)))
    # with PdfPages('sz_user_http_num_cdf.pdf') as pdf:
    #     font_size = '33'
    #     fig  =  plt.figure()
    #     ax = fig.add_subplot(111)
    #     ax.plot(new_x_vals, new_y_vals, '-', color = '#0066cc', linewidth = 3)
    #     ax.annotate('(1 record,\n 55% users)', xy = (1, 55.45), xytext = (15, 40),\
    #     arrowprops = dict(facecolor = 'black', shrink = 0.1),\
    #     size = font_size)
    #     plt.subplots_adjust(top = 0.95, right = 0.9, left = 0.22, bottom = 0.23)
    #     plt.xticks(np.arange(0,51,step = 10),[0,10,20,30,40,50],size = font_size) #
    #     plt.yticks(np.arange(0,101,step = 20),[0,20,40,60,80,100],size = font_size) #
    #     # plt.legend(['Network A','Network B'],fontsize = 25, loc = 'lower right')
    #     plt.xlabel('# of HTTP Requests', fontsize = font_size)
    #     plt.ylabel('% of Users',fontsize = font_size)
    #     plt.grid()
    #     plt.xlim(0,50)
    #     plt.ylim(0,100)
    #     # plt.show()
    #     pdf.savefig(fig)

    return user_recs_http


def user_portal_analysis():
    """
    cdf of user request of portal
    :return: # of buses
    """

    data_path = '/home/hadoop/Downloads/bus_wifi_data/huashi_2month/userPortal_V1.4/2017-03-06.gz/'
    files = [];user_recs_portal = collections.defaultdict(int)
    tmp = collections.defaultdict(list)
    for j in os.listdir(data_path):
        if j.startswith('part'):
            files.append(open(data_path+j))
    for file in files:
        for line in file:
            attrs = line.split('`')
            if (attrs[0]) in sz_busline_plate:
                tmp[attrs[2]].append(attrs[5]) # 2: userID, 5: content
    for userid, con in tmp.items():
        user_recs_portal[userid] = len(list(set(con)))
    # with PdfPages('sz_user_portal_num_cdf.pdf') as pdf:
    #     font_size = '33'
    #     fig  =  plt.figure()
    #     ax = fig.add_subplot(111)
    #     ax.plot(new_x_vals, new_y_vals, '-', color = '#0066cc', linewidth = 3)
    #     ax.annotate('(1 record,\n 58% users)', xy = (1, 58), xytext = (30, 30),\
    #     arrowprops = dict(facecolor = 'black', shrink = 0.1),\
    #     size = font_size)
    #     plt.subplots_adjust(top = 0.95, right = 0.9, left = 0.22, bottom = 0.23)
    #     plt.xticks(np.arange(0,101,step = 20),[0,20,40,60,80,100],size = font_size) #
    #     plt.yticks(np.arange(0,101,step = 20),[0,20,40,60,80,100],size = font_size) #
    #     # plt.legend(['Network A','Network B'],fontsize = 25, loc = 'lower right')
    #     plt.xlabel('# of Portal Visits', fontsize = font_size)
    #     plt.ylabel('% of Users',fontsize = font_size)
    #     plt.grid()
    #     plt.xlim(0,100)
    #     plt.ylim(0,100)
    #     plt.show()
    #     pdf.savefig(fig)

    return user_recs_portal


def http_portal_one_draw(user_recs_http, user_recs_portal): #
    """
    draw http visit and portal visit in one figure
    """
    # user_one = collections.defaultdict(int)
    # for user, num in user_recs_http.items():
    #     if user in user_recs_portal:
    #         user_one[user] = num+user_recs_portal[user]
    # json.dump(user_one, open("user_content_cdf","w"))

    user_one = json.load(open("user_content_cdf"))
    xvals, yvals = sensing_tools.cdf_draw(user_one.values())
    for i in range(len(xvals)):
        print (xvals[i], yvals[i])
    with PdfPages('sz_content_num_cdf.pdf') as pdf:
        font_size = '33'
        fig  =  plt.figure()
        ax = fig.add_subplot(111)
        ax.plot(xvals, yvals, '-', color = 'k', linewidth = 4)
        ax.annotate('(13 visits,\n 50% users)', xy = (1, 58), xytext = (15, 65),\
        arrowprops = dict(facecolor = 'black', shrink = 0.1, width = 2),\
        size = 30)
        # ax.annotate('(1 HTTP,\n 55% users)', xy = (1, 55.45), xytext = (15, 5),\
        # arrowprops = dict(facecolor = 'black', shrink = 0.1, width = 2),\
        # size = 30)
        plt.subplots_adjust(top = 0.95, right = 0.9, left = 0.22, bottom = 0.23)
        plt.xticks(np.arange(0,121,step = 30),[0,30,60,90,120],size = font_size) #
        plt.yticks(np.arange(0,101,step = 20),[0,20,40,60,80,100],size = font_size) #

        plt.xlabel('# of Visits', fontsize = font_size)
        plt.ylabel('% of Users',fontsize = font_size)
        # plt.grid()
        plt.xlim(0,120)
        plt.ylim(0,100)
        plt.show()
        pdf.savefig(fig)


def user_register_type_stat():
    """
    showing distribution of users' device types, registration way during a day
    data source: antelop
    :return: a bar chart
    """

    data_path = '/home/hadoop/Downloads/bus_wifi/huashi/antelop/'
    files = [];user_dev = collections.defaultdict(int)
    user_reg = collections.defaultdict(int)
    for date_ in ['2017-03-01.gz/','2017-03-02.gz/','2017-03-03.gz/',\
                  '2017-03-04.gz/','2017-03-05.gz/','2017-03-06.gz/','2017-03-07.gz/']:
        for j in os.listdir(data_path+date_):
            if j.startswith('part'):
                files.append(open(data_path+date_+j))
    for file in files:
        for line in file:
            attrs = line.split('`')
            if len(attrs[2]) == 0 or len(attrs[1]) == 0:
                continue
            # if unicode(attrs[3]) in sz_busline_plate:
            user_dev[attrs[2]]+ = 1 # key: device type, val: count
            user_reg[attrs[1]]+ = 1 # k: account type, val: count

    for k,v in user_dev.items():
        print ("device type:", k)
        print ("count num:", v)
    for k1,v1 in user_reg.items():
        print ("account type:", k1)
        print ("count num:", v1)

	
def user_online_time_cdf():
    """
    show cdf of user total online time
    :return:
    """

    data_path = '/home/hadoop/Downloads/bus_wifi/huashi/con_discon/2017-03-06.gz/'
    files = [];session_num = collections.defaultdict(list)
    for j in os.listdir(data_path):
        if j.startswith('part'):
            files.append(open(data_path+j))
    for file in files:
        for line in file:
            attrs = line.split('`')
            if attrs[0] == []:
                continue
            # quick way
            if (attrs[0]) in sz_busline_plate:
                if attrs[4] == 'Missing': # con time: 0
                    session_num[attrs[1]].append([time_2_sec(attrs[3]),0]) #k: userID, v: con_time
                elif attrs[3] == 'Missing': #discon time: 1
                    session_num[attrs[1]].append([time_2_sec(attrs[4]),1])

    session_time = collections.defaultdict(list); multiple_session = 0;single_session = 0
    for k,v in session_num.items(): #k: userID, v: timestamps
        if len(v) == 2:
            session_time[k].append(abs(v[0][0]-v[1][0]))
            single_session+ = 1
        elif len(v)>2:
            con_time = [];discon_time = []
            for item in v:
                if item[1] == 0:
                    con_time.append(item[0])
                elif item[1] == 1:
                    discon_time.append(item[0])
            if len(con_time)! = 0 and len(discon_time)! = 0 \
                    and len(con_time) == len(discon_time):
                multiple_session+ = 1
                con_time.sort(); discon_time.sort()
                for i in range(len(con_time)):
                    session_time[k].append(abs(discon_time[i]-con_time[i]))

    print (multiple_session, single_session)

    # count number of user for each session length
    all_len = []
    url_num = collections.defaultdict(int)
    for k,v in session_time.items():# k: userID, v: session length
        all_len.append(sum(v))
        url_num[sum(v)]+ = 1 # k: online time length, v: user number

    print ('mean online time', np.mean(all_len))

    user_num = sum(url_num.values())

    x_vals = []; y_vals = []; sum_temp = 0
    user_url_num_sorted = sorted(url_num.items(), key = operator.itemgetter(0))
    for item in user_url_num_sorted:
        x_vals.append(item[0])
        sum_temp+ = item[1]
        y_vals.append(100*sum_temp/user_num)

    # for i in range(len(y_vals)):
    #     if y_vals[i]> = 79 and y_vals[i]< = 81:
    #         print x_vals[i]

    new_x_vals = [];new_y_vals = []
    for i in range(len(x_vals)):
        if x_vals[i]< = 50*60:
            new_x_vals.append(x_vals[i])
            new_y_vals.append(y_vals[i])
    # new_x_vals = [0]+new_x_vals
    # new_y_vals = [0]+new_y_vals
    print (new_x_vals)
    print (new_y_vals)

    with PdfPages('sz_online_len_cdf.pdf') as pdf:
        font_size = '33'
        fig  =  plt.figure()
        ax = fig.add_subplot(111)
        ax.plot(new_x_vals, gaussian_filter(new_y_vals,3), '-', color = '#0066cc', linewidth = 3)
        ax.annotate('(13 min,\n 80% users)', xy = (780, 80), xytext = (1800, 40),
        arrowprops = dict(facecolor = 'black', shrink = 0.1),
        size = font_size)
        plt.subplots_adjust(top = 0.95, right = 0.9, left = 0.22, bottom = 0.23)
        plt.xticks(np.arange(0,6001,step = 1200),[0,20,40,60,80,100],size = font_size) #np.arange(0,101,step = 20),[0,20,40,60,80,100],
        plt.yticks(size = font_size) #np.arange(0,101,step = 20),[0,20,40,60,80,100],
        # plt.legend(['Network A','Network B'],fontsize = 25, loc = 'lower right')
        plt.xlabel('Total Session (min)', fontsize = font_size)
        plt.ylabel('% of Users',fontsize = font_size)
        plt.grid()
        plt.xlim(0,6001)
        plt.ylim(0,100)
        plt.show()
        pdf.savefig(fig)

	
def  user_traffic_unbalance():
    """
    show the unbalanced data usage, every 1% users,
     we calculate total traffic for this 1% users
    :return:
    """

    data_path = "/home/hadoop/Downloads/bus_wifi/huashi/userFlow/2017-03-0"+str(6)+".gz/"

    files = [];user_upflow = collections.defaultdict(list);user_downflow = collections.defaultdict(list)
    for j in os.listdir(data_path):
        if j.startswith('part'):
            files.append(open(data_path+j))
    for file in files:
        for line in file:
            attrs = line.split('`')
            if attrs[2] in sz_busline_plate:
                user_upflow[attrs[1]].append(int(attrs[-3])) # diff values
                user_downflow[attrs[1]].append(int(attrs[-2]))

    user_upflow_ave = collections.defaultdict(int);user_downflow_ave = collections.defaultdict(int)
    for k,v in user_upflow.items():
        user_upflow_ave[k] = int(max(v))
    for k,v in user_downflow.items():
        user_downflow_ave[k] = int(max(v))

    user_all_flow = []
    for k,v in user_upflow.items():
        user_all_flow.append(user_upflow_ave[k]+user_downflow_ave[k])

    # sorted_user_flow = sorted(user_all_flow.items(), key = operator.itemgetter(1))
    user_all_flow.sort()

    new_traffic_percent = []
    delta = int(0.05*len(user_all_flow))
    for i in range(0,len(user_all_flow),delta):
        new_traffic_percent.append(100*sum(user_all_flow[i:i+delta])/sum(user_all_flow))
    print (new_traffic_percent[:len(new_traffic_percent)-2]\
                +[new_traffic_percent[-1]]+[new_traffic_percent[-2]])

    with PdfPages('sz_user_traffic_unbalance.pdf') as pdf:
        font_size = '33'
        fig  =  plt.figure()
        ax = fig.add_subplot(111)
        ax.plot(np.arange(0, len(new_traffic_percent)), new_traffic_percent[:len(new_traffic_percent)-2]\
                +[new_traffic_percent[-1]]+[new_traffic_percent[-2]],
                '-', color = '#0066cc', marker = '^', markersize = 10, \
                markevery = 1, linewidth = 3)
        # ax.bar(np.arange(0, len(new_traffic_percent)), uniform_filter1d(new_traffic_percent,1), color = '#0066cc')
        # print max(bus_traffic_all)
        # ax.annotate('(1200 bus,\n '+str(int(new_traffic_percent[1200]/(1024*1024)))+' GB)',
        #             xy = (1200, new_traffic_percent[1200]), xytext = (400, 600*1024*1024),
        #             arrowprops = dict(facecolor = 'black', shrink = 0.1),
        #             size = font_size)
        plt.subplots_adjust(top = 0.95, right = 0.9, left = 0.22, bottom = 0.23)
        plt.xticks(np.arange(0,21,step = 4),[0,20,40,60,80,100],size = font_size) #np.arange(0,11,step = 2),[0,20,40,60,80,100],
        plt.yticks(size = font_size) #np.arange(0,1500*1024*1024+1,step = 300*1024*1024),[0,3,6,9,12,15],
        # plt.legend(['Network A','Network B'],fontsize = 25, loc = 'lower right')
        plt.xlabel('% of Users', fontsize = font_size)
        plt.ylabel('% of Traffic',fontsize = font_size)
        plt.grid()
        plt.xlim(0,20)
        plt.ylim(0,100)
        plt.show()
        pdf.savefig(fig)


def http_url_analysis():
    """
    analyze how users visit HTTP url
    :return:
    """

    data_path = "/home/hadoop/Downloads/bus_wifi_data/huashi_2month/userHttp/2017-03-0"+str(6)+".gz/"
    ct = collections.defaultdict(int)
    files = [];user_domain = collections.defaultdict(list); all_domain = []
    for j in os.listdir(data_path):
        if j.startswith('part'):
            files.append(open(data_path+j))
    for file in files:
        for line in file:
            attrs = line.split('`')
            if attrs[0] in sz_busline_plate:
                # result = '{uri.scheme}://{uri.netloc}/'.format(uri = urlparse(attrs[6]))
                # print result
                # if result not in all_domain:
                all_domain.append(attrs[6])
                user_domain[attrs[2]].append(attrs[6]) # url domain
                ct[attrs[2]]+ = 1
    user_domain_num = collections.defaultdict(int)
    for k,v in user_domain.items():
        user_domain_num[k] = len(set(v))
    print (max(list(ct.values())))

    user_num = len(user_domain_num.keys())
    print ('Number of users:', user_num)
    print ('Number of url domains:', len(all_domain))

    domain_num = dict(collections.Counter(all_domain))
    domain_num_sort = sorted(domain_num.items(), key = operator.itemgetter(1), reverse = True)

    new_x_vals, new_y_vals = sensing_tools.cdf_draw(list(user_domain_num.values()))

    # dev_flow_cdf = collections.defaultdict(int)
    # for k1,v1 in user_domain_num.items():
    #     dev_flow_cdf[v1]+ = 1
    #
    # x_vals = []; y_vals = []; sum_temp = 0
    # user_url_num_sorted = sorted(dev_flow_cdf.items(), key = operator.itemgetter(0))
    # for item in user_url_num_sorted:
    #     x_vals.append(item[0])
    #     sum_temp+ = item[1]
    #     y_vals.append(100*sum_temp/user_num)
    #
    # new_x_vals = [];new_y_vals = []
    # for i in range(len(x_vals)):
    #     if x_vals[i]< = 21:
    #         new_x_vals.append(x_vals[i])
    #         new_y_vals.append(y_vals[i])
    # new_x_vals = [0]+new_x_vals
    # new_y_vals = [0]+new_y_vals
    print (new_x_vals[0], new_y_vals[0])

    # with PdfPages('sz_user_http_cdf.pdf') as pdf:
    #     font_size = '36'
    #     fig  =  plt.figure(figsize = (9,6))
    #     ax = fig.add_subplot(111)
    #     ax.plot(new_x_vals, uniform_filter1d(new_y_vals,1), '-', color = 'k', linewidth = 4)
    #     ax.annotate('(1 HTTP,\n 55% users)', xy = (1, 55), xytext = (5, 23),
    #     arrowprops = dict(facecolor = 'black', shrink = 0.1, width = 2),
    #     size = font_size)
    #     # plt.subplots_adjust(top = 0.95, right = 0.9, left = 0.22, bottom = 0.23)
    #     plt.subplots_adjust(top = 0.95, right = 0.95, left = 0.16, bottom = 0.19)
    #     plt.xticks(np.arange(0,21,step = 4),[0,4,8,12,16,20],size = font_size) #
    #     plt.yticks(size = font_size) #np.arange(0,101,step = 20),[0,20,40,60,80,100],
    #     # plt.legend(['Network A','Network B'],fontsize = 25, loc = 'lower right')
    #     plt.xlabel('# of HTTP', fontsize = font_size)
    #     plt.ylabel('% of Users',fontsize = font_size)
    #     # plt.grid()
    #     plt.xlim(0,20)
    #     plt.ylim(0,100)
    #     plt.show()
    #     pdf.savefig(fig)

    with PdfPages('sz_user_http_cdf.pdf') as pdf:
        font_size = '46'
        fig  =  plt.figure(figsize = (9,6))
        ax = fig.add_subplot(111)
        ax.plot(new_x_vals, uniform_filter1d(new_y_vals,1), '-', color = 'k', linewidth = 4)
        ax.annotate('(1 HTTP,\n 55% users)', xy = (1, 55), xytext = (5, 23),
        arrowprops = dict(facecolor = 'black', shrink = 0.1, width = 2),
        size = font_size)
        # plt.subplots_adjust(top = 0.95, right = 0.9, left = 0.22, bottom = 0.23)
        plt.subplots_adjust(top = 0.95, right = 0.95, left = 0.19, bottom = 0.20)
        plt.xticks(np.arange(0,21,step = 4),[0,4,8,12,16,20],size = font_size) #
        plt.yticks(size = font_size) #np.arange(0,101,step = 20),[0,20,40,60,80,100],
        # plt.legend(['Network A','Network B'],fontsize = 25, loc = 'lower right')
        plt.xlabel('# of HTTP', fontsize = font_size)
        plt.ylabel('% of Users',fontsize = font_size)
        # plt.grid()
        plt.xlim(0,20)
        plt.ylim(0,100)
        plt.show()
        pdf.savefig(fig)

	
def portal_analysis():
    """
    analyze how users visit portal
    :return:
    """

    data_path = "/home/hadoop/Downloads/bus_wifi/huashi/userPortal_V1.4/2017-03-0"+str(6)+".gz/"

    files = [];user_domain = collections.defaultdict(list); all_domain = []
    for j in os.listdir(data_path):
        if j.startswith('part'):
            files.append(open(data_path+j))
    for file in files:
        for line in file:
            attrs = line.split('`')
            if attrs[0] in sz_busline_plate:
                # if attrs[5] not in all_domain:
                all_domain.append(attrs[5])
                user_domain[attrs[2]].append(attrs[5]) # portal title
    user_domain_num = collections.defaultdict(int)
    for k,v in user_domain.items():
        user_domain_num[k] = len(set(v))
    # print user_domain_num

    user_num = len(user_domain_num.keys())
    print ('Number of users:', user_num)
    print ('Number of portal domains:', len(all_domain))
    print ("Number of portal users:", len(user_domain.keys()))

    domain_num = dict(collections.Counter(all_domain))
    domain_num_sort = sorted(domain_num.items(), key = operator.itemgetter(1), reverse = True)
    for item in domain_num_sort:
        pass
        # print item[0], item[1]

        # try:
        #     u  =  item[0].strip().decode('utf-8')
        #     # print u
        # except UnicodeDecodeError as e:
        #     u  =  item[0].strip().decode('utf-8', 'ignore')


    dev_flow_cdf = collections.defaultdict(int)
    for k1,v1 in user_domain_num.items():
        dev_flow_cdf[v1]+ = 1

    x_vals = []; y_vals = []; sum_temp = 0
    user_url_num_sorted = sorted(dev_flow_cdf.items(), key = operator.itemgetter(0))
    for item in user_url_num_sorted:
        x_vals.append(item[0])
        sum_temp+ = item[1]
        y_vals.append(100*sum_temp/user_num)

    for i in range(len(y_vals)):
        if y_vals[i]> = 78 and y_vals[i]< = 82:
            print (x_vals[i])

    new_x_vals = [];new_y_vals = []
    for i in range(len(x_vals)):
        if x_vals[i]< = 120:
            new_x_vals.append(x_vals[i])
            new_y_vals.append(y_vals[i])
    new_x_vals = [0]+new_x_vals
    new_y_vals = [0]+new_y_vals

    print (new_y_vals[1])

    with PdfPages('sz_user_portal_domain_cdf.pdf') as pdf:
        font_size = '33'
        fig  =  plt.figure()
        ax = fig.add_subplot(111)
        ax.plot(new_x_vals, uniform_filter1d(new_y_vals,3), '-', color = '#0066cc', linewidth = 3)
        ax.annotate('(16 titles,\n 80% users)', xy = (16, 80), xytext = (30, 40),
        arrowprops = dict(facecolor = 'black', shrink = 0.1),
        size = font_size)
        plt.subplots_adjust(top = 0.95, right = 0.9, left = 0.22, bottom = 0.23)
        plt.xticks(np.arange(0,121,step = 30),[0,30,60,90,120],size = font_size) # np.arange(0,21,step = 4),[0,4,8,12,16,20],
        plt.yticks(size = font_size) # np.arange(0,101,step = 20),[0,20,40,60,80,100],
        # plt.legend(['Network A','Network B'],fontsize = 25, loc = 'lower right')
        plt.xlabel('# of Portal Titles', fontsize = font_size)
        plt.ylabel('% of Users',fontsize = font_size)
        plt.grid()
        plt.xlim(0,120)
        plt.ylim(0,100)
        # plt.show()
        pdf.savefig(fig)

	
def user_traffic_dist():
    """
    analyze user traffic distribution CDF
    :return:
    """

    data_path = "/home/hadoop/Downloads/bus_wifi/huashi/userFlow/2017-03-0"+str(6)+".gz/"

    files = [];user_upflow = collections.defaultdict(int);user_downflow = collections.defaultdict(int)
    user_upflow_tmp = collections.defaultdict(int);user_downflow_tmp = collections.defaultdict(int)
    for j in os.listdir(data_path):
        if j.startswith('part'):
            files.append(open(data_path+j))
    for file in files:
        for line in file:
            attrs = line.split('`')
            if attrs[2] in sz_busline_plate:
                try:
                    user_upflow_tmp[attrs[1]]+ = int(attrs[-3]) # diff values
                    user_downflow_tmp[attrs[1]]+ = int(attrs[-2])
                except:
                    continue
    for k_,v_ in user_upflow_tmp.items():
        if v_! = 0:
            user_upflow[k_] = v_
    for k3,v3 in user_downflow_tmp.items():
        if v3! = 0:
            user_downflow[k3] = v3

    bus_num = len(user_downflow.keys())
    print ('Number of users:', bus_num)

    bus_traffic_up_all = user_upflow.values()
    bus_traffic_up_all.sort()
    # cdf preparation
    dev_flow_cdf = collections.defaultdict(int)
    for k1,v1 in user_upflow.items():
        dev_flow_cdf[v1]+ = 1
    x_vals = []; y_vals = []; sum_temp = 0
    user_url_num_sorted = sorted(dev_flow_cdf.items(), key = operator.itemgetter(0))
    for item in user_url_num_sorted:
        x_vals.append(item[0])
        sum_temp+ = item[1]
        y_vals.append(100*sum_temp/len(user_upflow.keys()))

    # for i in range(len(y_vals)):
    #     if y_vals[i]> = 79.8 and y_vals[i]< = 80.2:
    #         print x_vals[i]

    new_x_vals = [];new_y_vals = []
    for i in range(len(x_vals)):
        if x_vals[i]< = 10*1024*1024:
            new_x_vals.append(x_vals[i])
            new_y_vals.append(y_vals[i])
    new_x_vals = [0]+new_x_vals
    new_y_vals = [0]+new_y_vals
    print (new_x_vals)
    print (new_y_vals)

    #down
    bus_traffic_down_all = user_downflow.values()
    bus_traffic_down_all.sort()
    # cdf preparation
    dev_flow_down_cdf = collections.defaultdict(int)
    for k1,v1 in user_downflow.items():
        dev_flow_down_cdf[v1]+ = 1
    x_vals_down = []; y_vals_down = []; sum_temp = 0
    user_url_num_sorted = sorted(dev_flow_down_cdf.items(), key = operator.itemgetter(0))
    for item in user_url_num_sorted:
        x_vals_down.append(item[0])
        sum_temp+ = item[1]
        y_vals_down.append(100*sum_temp/len(user_downflow.keys()))

    # for i in range(len(y_vals)):
    #    if y_vals[i]> = 79.8 and y_vals[i]< = 80.2:
    #         print x_vals[i]
    print (max(x_vals_down))
    new_x_vals_d = [];new_y_vals_d = []
    for i in range(len(x_vals_down)):
        if x_vals_down[i]< = 10*1024*1024: # MB
            new_x_vals_d.append(x_vals_down[i])
            new_y_vals_d.append(y_vals_down[i])
    new_x_vals_d = [0]+new_x_vals_d
    new_y_vals_d = [0]+new_y_vals_d
    print (new_x_vals_d)
    print (new_y_vals_d)

    with PdfPages('sz_user_traffic_cdf.pdf') as pdf:
        font_size = '33'
        fig  =  plt.figure()
        ax = fig.add_subplot(111)
        # ax.plot(new_x_vals, uniform_filter1d(new_y_vals,1),
        #         '-', color = '#0066cc', marker = '^', markersize = 10, \
        #         markevery = 1, linewidth = 3)
        ax.plot(new_x_vals, new_y_vals, '-', color = '#0066cc', linewidth = 3)
        ax.plot(new_x_vals_d, new_y_vals_d, '-.', color = '#000000', linewidth = 3)
        # print max(bus_traffic_all)
        ax.annotate('(28 KB,\n 61% users)', xy = (1053, 61.08), xytext = (2*1024*1024, 50),
        arrowprops = dict(facecolor = 'black', shrink = 0.1),
        size = font_size)
        plt.subplots_adjust(top = 0.95, right = 0.9, left = 0.22, bottom = 0.23)
        plt.xticks(np.arange(0,10*1024*1024+1,step = 2*1024*1024),[0,2,4,6,8,10],size = font_size) #np.arange(0,11,step = 2),[0,20,40,60,80,100],
        plt.yticks(size = font_size) #np.arange(0,1500*1024*1024+1,step = 300*1024*1024),[0,3,6,9,12,15],
        plt.legend(['Upload','Download'],fontsize = 25, loc = 'lower right',frameon = False)
        plt.xlabel('# of Traffic (MB)', fontsize = font_size)
        plt.ylabel('% of Users',fontsize = font_size)
        plt.grid()
        # plt.xlim(-2,10*1024*1024)
        plt.ylim(0,100)
        plt.show()
        pdf.savefig(fig)

	
def user_no_traffic_count():
    # calculate percentage of users without upload/ download data
    date = []
    for i in range(1,10):
        date.append('0'+str(i))
    for i in range(10,21):
        date.append(str(i))
    up_rate = [];down_rate = []
    for item in date:
        user_upflow_tmp = collections.defaultdict(int);user_downflow_tmp = collections.defaultdict(int)
        data_path = "/home/hadoop/Downloads/bus_wifi/huashi_2month/userFlow/2017-02-"+item+".gz"
        # /home/hadoop/Downloads/bus_wifi/huashi_2month/userFlow/2017-02-07.gz
        files = []
        try:
            for k in os.listdir(data_path):
                if k.startswith("part"):
                    files = open(data_path+'/'+k)
            for line in files:
                try:
                    attrs = line.split("`")
                    if attrs[1] == '10:f6:81:bf:a1:41':
                        print (line)
                    user_upflow_tmp[attrs[1]]+ = int(attrs[7]) # up diff values
                    user_downflow_tmp[attrs[1]]+ = int(attrs[8])
                except:
                    pass
            up_null = 0;down_null = 0
            for k,v in user_upflow_tmp.items():
                if v == 0:
                    # print k
                    up_null+ = 1
            for k1,v1 in user_downflow_tmp.items():
                if v1 == 0:
                    down_null+ = 1
            up_rate.append(100*up_null/len(user_upflow_tmp.keys()))
            down_rate.append(100*down_null/len(user_downflow_tmp.keys()))
        except:
            pass
    print ("up null rate of users", np.mean(up_rate))
    print ("down null rate of users", np.mean(down_rate))



def user_repetition_store():
    """
    TODO: calculate user repetition along two month period
    data source: con_discon
    :return: a list of repetition rate
    """

    user_id = collections.defaultdict(list)#k: date, y:
    files = [];data_path = "/home/hadoop/Downloads/bus_wifi_data/huashi_2month/devFlow"
    try:
        for j in os.listdir(data_path):
            if j.startswith("2017-"):
                for k in os.listdir(data_path+"/"+j):
                    if k.startswith("part"):
                        files.append(os.path.join(data_path,j,k))
    except OSError:
        pass
    for i in files:
        print (i)
        for line in open(i):
            try:
                attrs = line.split("`")
                if attrs[2] in sz_devID: # devID
                    # raw: "2017-04-07T08:12:33.000Z"; data: 407
                    date = int(attrs[4].split("T")[0][-2:])+100*int(attrs[4].split("T")[0][-5:-3])
                    if attrs[1] not in user_id[int(date)]: # userID
                        user_id[int(date)].append(attrs[1])
            except:
                pass

    # save all the userID
    with open("TwoMonth_daily_userID_dict","w") as f:
        json.dump(user_id,f)

    # user_id_sorted = sorted(user_id.items(), key = operator.itemgetter(0))
    # user_id_pre = user_id_sorted[0][1] #list of userID
    # rep_rate = []; new_user = []
    # for i in range(0,len(user_id_sorted)-1):
    #     # track new user number
    #     new_user.append(len(list(set(user_id_sorted[i+1][1])-set(user_id_pre))))
    #     # track rep rate
    #     new_temp = len(list(set(user_id_pre)-(set(user_id_sorted[i+1][1])-set(user_id_pre))))
    #     rep_rate.append(100*new_temp/len(user_id_pre))
    #     # accumulate the base user ID
    #     user_id_pre = user_id_sorted[i][1]+list(set(user_id_sorted[i+1][1])-set(user_id_sorted[i][1]))
    # print "New users per day:"
    # print new_user
    # print "Repetition rate:"
    # print rep_rate


def user_rep_read():
    """
    directly read from lists
    :return:
    """

    user_id = collections.defaultdict(list)
    with open("TwoMonth_daily_userID_dict") as f:
        temp = json.load(f) # k: day, v: list of user ID
    for k,v in temp.items():
        user_id[int(k)] = v

    user_id_sorted = sorted(user_id.items(), key = operator.itemgetter(0))
    user_id_pre = user_id_sorted[0][1] #list of userID
    rep_rate = []; new_user = []
    for i in range(0,len(user_id_sorted)-1):
        # track new user number (appearing next day while not in the previous days)
        diff_ = list(set(user_id_sorted[i+1][1])-set(user_id_pre))
        new_user.append(len(diff_))
        # # track rep rate (appeared once in previous days)
        # new_temp1 = len(list(set(user_id_sorted[i+1][1]) & set(user_id_pre)))
        # rep_rate.append(100*new_temp1/len(user_id_pre))
        # track rep rate (appeared once in previous day)
        new_temp1 = len(list(set(user_id_sorted[i+1][1]) & set(user_id_sorted[i][1])))
        rep_rate.append(100*new_temp1/len(user_id_sorted[i][1]))
        # accumulate the base user ID, union of today and previous day
        user_id_pre = list(set(user_id_sorted[i+1][1]) | set(user_id_pre))
        print (len(set(user_id_pre)))
    user_num = [];date_ = []
    for item in user_id_sorted:
        date_.append(item[0])
        user_num.append(len(item[1]))
    print ("Date:")
    print (date_)
    print ("Number of users per day:")
    print (user_num)
    print ("Number of new users per day:")
    print (new_user)
    print ("Repetition rate:")
    print (rep_rate)

	
def one_month_pattern_draw():
    """
    draw the pattern of two month
    """

    date = [202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224, 225, 226, 227, 228, 301, 302, 303, 304, 305, 306, 307, 308, 309, 310, 311, 312, 313, 314, 315, 316, 317, 318, 319, 320, 321, 322, 324, 325, 326, 327, 328, 329, 330, 331]
    user_num_day = [49108, 63394, 70683, 77304, 87842, 91295, 91648, 91728, 96726, 98145, 99784, 107804, 112425, 110813, 111857, 116481, 114704, 114118, 118008, 112122, 114054, 109676, 110538, 103637, 114374, 117788, 116882, 113629, 112433, 116024, 116218, 118438, 113539, 109808, 112126, 107816, 113384, 110461, 117243, 113970, 106108, 110283, 112282, 116473, 111114, 95049, 114228, 112132, 78550, 4564, 4377, 4576, 4509, 4164, 4113, 4231, 3766]
    new_user_day = [51779, 49994, 50628, 52357, 48370, 43955, 40097, 40170, 42084, 41900, 40218, 39730, 36485, 34690, 34946, 36643, 37598, 32090, 28132, 27393, 25105, 24395, 25127, 30102, 24741, 24154, 22497, 21207, 21970, 24989, 27176, 19731, 18506, 18784, 17077, 18718, 20476, 23956, 18030, 15976, 16426, 16845, 17923, 19366, 17336, 17011, 16232, 10609, 1063, 1133, 1366, 1031, 931, 905, 903, 808]
    rep_rate = [23.65195080231327, 24.0227781809004, 23.326683926828235, 24.41658905101935, 27.76348443796817, 27.71564707815324, 27.97224162011173, 28.643380429094716, 24.171370675929946, 23.907483824952877, 24.082017157059248, 29.70483470001113, 29.373360017789636, 30.01633382364885, 30.38701198852106, 25.787038229410804, 24.338296833589062, 24.143430484235616, 29.210731475832148, 30.429353739676422, 29.682431129114278, 29.92176957584157, 24.84846840000724, 25.740806854694753, 24.56939514225261, 30.476788807009203, 29.548604575554833, 30.272201638666186, 30.56664858182206, 26.486761359718678, 25.354936412603898, 23.296577112075518, 29.977364605994417, 30.55970421098645, 29.717460713839788, 31.074237589968092, 25.796408664361813, 25.765654846506912, 23.729348447242053, 29.121698692638414, 31.080597127455047, 31.051930034547482, 30.743128907572007, 25.614520103371596, 21.801933149738108, 24.657808077938746, 29.98914451798158, 22.984518246352515, 0.939528962444303, 10.23225241016652, 9.984007310943568, 8.850524475524475, 11.754269239299179, 12.463976945244957, 13.274981765134939, 11.604821555187899]

    date2 = date[0:28]
    user_num_day2 = user_num_day[0:28]
    new_user_day2 = new_user_day[0:28]
    rep_rate2 = rep_rate[0:28]

    with PdfPages('user_mon_pattern.pdf') as pdf:
        font_size = '30'
        fig  =  plt.figure(figsize = (11,4))
        ax1 = fig.add_subplot(111)
        ax1.tick_params(axis = 'both', which = 'major', labelsize = font_size)
        ax1.plot(np.arange(28), user_num_day2, '-', color = '#0066cc', linewidth = 3)
        ax1.plot(np.arange(28), new_user_day2, '-', marker = '^', markersize = 10, color = '#ef4836', linewidth = 3)
        ax1.set_ylabel('# of Users', size = font_size)
        ax1.set_yticks(np.arange(0,120001,step = 30000)) #,[0,3,6,9,12],size = font_size
        ax1.set_xlabel('Day of Month', fontsize = font_size)

        ax2  =  ax1.twinx()
        ax2.tick_params(axis = 'both', which = 'major', labelsize = font_size)
        ax2.plot(np.arange(28), rep_rate2, '-.', color = '#000000', linewidth = 3)
        ax2.set_ylabel('Repetition Rate', size = font_size)
        ax2.set_yticks(np.arange(0,110,step = 20)) #,[0,20,40,60,80,100]
        # ax1.tick_params('y')

        plt.subplots_adjust(top = 0.75, right = 0.87, left = 0.18, bottom = 0.26)
        plt.xticks(np.arange(0,29,step = 4),
                   [0,4,8,12,16,20,24,28], size = font_size)
        # plt.yticks(np.arange(20,31,step = 2),[20,22,24,26,28,30],size = font_size) #
        ax1.legend(['# of Users','# of New Users'],\
        	fontsize = 28, ncol = 2, loc = [-0.25,1.1], frameon = False)
        ax2.legend(['Rep Rate'],\
        	fontsize = 28, ncol = 1, loc = [0.75,1.1],frameon = False)

        plt.xlim(0,28)
        # plt.ylim(0,100)
        plt.show()
        pdf.savefig(fig)

	
def  user_data_avail():
    """
    calculate how many days a user uses bus WiFi
    user percentage to denote the time
    """
    # #%% ---- prepare data for ploting
    # data_path = "/home/hadoop/Downloads/bus_wifi_data/huashi_2month/userHttp/" # userPortal_V1.4
    #
    # files = [];user_days = collections.defaultdict(list)
    # user_day = collections.defaultdict(list)
    # for j in os.listdir(data_path):
    #     for k in os.listdir(data_path+j):
    #         if k.startswith('part'):
    #             files.append(open(data_path+j+'/'+k))
    # for file in files:
    #     print (file)
    #     for line in file:
    #         attrs = line.split('`')
    #         if attrs[0] in sz_busline_plate:
    #             try:
    #                 user_days[attrs[2]].append(attrs[3].split('T')[0]) #
    #             except:
    #                 continue
    # for k,v in user_days.items():
    #     user_day[k] = len(set(v)) # number of days with data
    #
    # with open("user_http_avail_days_dict",'w') as f:
    #     json.dump(user_day, f)

    # #%% ---- plot
    # with open("user_wifi_avail_days_dict") as f:
    #     temp_dict = json.load(f) # k: days, v: # of users
    http = json.load(open("user_http_avail_days_dict"))
    portal = json.load(open("user_portal_avail_days_dict"))
    xvals1, yvals1 = sensing_tools.cdf_draw(list(http.values()))
    xvals2, yvals2 = sensing_tools.cdf_draw(list(portal.values()))
    # print (xvals1[0], yvals1[6])
    print (xvals2[0], yvals2[0])
    # one axis thing
    # with PdfPages('user_wifi_avail.pdf') as pdf:
    #     font_size = '36'
    #     fig  =  plt.figure(figsize = (9,6))
    #     ax = fig.add_subplot(111)
    #     # ax.plot(xvals1, yvals1, '--', color = 'k', linewidth = 3)
    #     ax.plot(xvals2, yvals2, '-', color = 'k', linewidth = 4) # #0066cc
    #     ax.annotate('(1 day,\n 71% users)', xy = (1, 71.49), xytext = (20, 63),
    #     arrowprops = dict(facecolor = 'black', shrink = 0.1, width = 2),
    #     size = font_size)
    #     ax.annotate('(7 days,\n 96% users)', xy = (6, 96), xytext = (20, 82),
    #     arrowprops = dict(facecolor = 'black', shrink = 0.1, width = 2),
    #     size = font_size)
    #     # plt.subplots_adjust(top = 0.95, right = 0.9, left = 0.22, bottom = 0.23)
    #     plt.subplots_adjust(top = 0.95, right = 0.95, left = 0.16, bottom = 0.19)
    #     plt.xticks(np.arange(0,61,step = 10),[0,10,20,30,40,50,60],fontsize = font_size) # np.arange(0,21,step = 4),[0,4,8,12,16,20],
    #     plt.yticks( np.arange(60,101,step = 10),[60,70,80,90,100],size = font_size) #
    #     plt.xlabel('# of Days',fontsize = font_size)
    #     plt.ylabel('% of Users',fontsize = font_size)
    #     # plt.legend(["HTTP", "Portal"], loc = [0.45, -0.01] , \
    #     #    ncol = 1, columnspacing = 0.1, labelspacing = 0.3,\
    #     #    handletextpad = 0.1, fontsize = 30, frameon = False)
    #     plt.xlim(0,60)
    #     plt.ylim(60,100)
    #     plt.show()
    #     pdf.savefig(fig)

    with PdfPages('user_wifi_avail.pdf') as pdf:
        font_size = '46'
        fig  =  plt.figure(figsize = (9,6))
        ax = fig.add_subplot(111)
        # ax.plot(xvals1, yvals1, '--', color = 'k', linewidth = 3)
        ax.plot(xvals2, yvals2, '-', color = 'k', linewidth = 4) # #0066cc
        ax.annotate('(1 day,\n 71% users)', xy = (1, 71.49), xytext = (20, 63),
        arrowprops = dict(facecolor = 'black', shrink = 0.1, width = 2),
        size = font_size)
        ax.annotate('(7 days,\n 96% users)', xy = (6, 96), xytext = (20, 82),
        arrowprops = dict(facecolor = 'black', shrink = 0.1, width = 2),
        size = font_size)
        # plt.subplots_adjust(top = 0.95, right = 0.9, left = 0.22, bottom = 0.23)
        plt.subplots_adjust(top = 0.95, right = 0.95, left = 0.19, bottom = 0.21)
        plt.xticks(np.arange(0,61,step = 10),[0,10,20,30,40,50,60],fontsize = font_size) # np.arange(0,21,step = 4),[0,4,8,12,16,20],
        plt.yticks( np.arange(60,101,step = 10),[60,70,80,90,100],size = font_size) #
        plt.xlabel('# of Days',fontsize = font_size)
        plt.ylabel('% of Users',fontsize = font_size)
        # plt.legend(["HTTP", "Portal"], loc = [0.45, -0.01] , \
        #    ncol = 1, columnspacing = 0.1, labelspacing = 0.3,\
        #    handletextpad = 0.1, fontsize = 30, frameon = False)
        plt.xlim(0,60)
        plt.ylim(60,100)
        plt.show()
        pdf.savefig(fig)


    # # # %% ---- plot xvals2, yvals2: usage distribution
    # data_path = "/home/hadoop/Downloads/bus_wifi_data/huashi_2month/userFlow/" # userPortal_V1.4
    # files = [];user_usage = collections.defaultdict(list)
    # for j in os.listdir(data_path):
    #     for k in os.listdir(data_path+j):
    #         if k.startswith('part'):
    #             files.append(open(data_path+j+'/'+k))
    # for file in files:
    #     print (file)
    #     for line in file:
    #         attrs = line.split('`')
    #         if attrs[0] in sz_busline_plate:
    #             try:
    #                 user_usage[attrs[1]]+ = int(attrs[-1]) #k: userID, v:data
    #                 user_usage[attrs[1]]+ = int(attrs[-2])
    #             except:
    #                 continue
    # all_usage = list(user_usage.items())
    # json.dump(all_usage, open("user_usage_dist", "w"))

    # yvals0 = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.002335166781812002, 0.008152238306470086, 0.019401095754099724, 0.03755289337200771, 0.0713898041633558, 0.13867640909504242, 0.29685818235528183, 8.747718461923876, 90.67791574824805]
    # xvals0 = np.arange(0,105,5)
    #
    # with PdfPages('user_wifi_usage_dist.pdf') as pdf:
    #     font_size = '33'
    #     fig  =  plt.figure()
    #     ax = fig.add_subplot(111)
    #     ax.plot(xvals0, yvals0, '-', color = '#0066cc',\
    #               marker = '*', markersize = 12, markevery = 1, linewidth = 3)
    #     # ax.annotate('(7 days,\n 98% users)', xy = (6, 98), xytext = (20, 88),
    #     # arrowprops = dict(facecolor = 'black', shrink = 0.1, width = 2),
    #     # size = 30)
    #     # ax.annotate('(7 days,\n 96% users)', xy = (6, 96), xytext = (20, 75),
    #     # arrowprops = dict(facecolor = 'black', shrink = 0.1, width = 2),
    #     # size = 30)
    #     plt.subplots_adjust(top = 0.95, right = 0.9, left = 0.22, bottom = 0.23)
    #     plt.xticks(np.arange(0,101,step = 20),[0,20,40,60,80,100],fontsize = font_size) # np.arange(0,21,step = 4),[0,4,8,12,16,20],
    #     plt.yticks( np.arange(0,101,step = 20),[0,20,40,60,80,100],size = font_size) #
    #     plt.xlabel('% of Users',fontsize = font_size)
    #     plt.ylabel('% of Traffic',fontsize = font_size)
    #     # plt.legend(["HTTP", "Portal"], loc = [0.45, -0.01] , \
    #     #    ncol = 1, columnspacing = 0.1, labelspacing = 0.3,\
    #     #    handletextpad = 0.1, fontsize = 30, frameon = False)
    #     plt.xlim(0,100)
    #     plt.ylim(0,100)
    #     plt.show()
    #     pdf.savefig(fig)

    # #%% ---- wasted: two axis thing
    # with PdfPages('user_wifi_avail.pdf') as pdf:
    #     font_size = '33'
    #     fig  =  plt.figure()
    #     ax1 = fig.add_subplot(111)
    #     ax1.tick_params(axis = 'both', which = 'major', labelsize = font_size)
    #     ax1.plot([100*x/60 for x in xvals], uniform_filter1d(yvals, 1), \
    #              '-', color = '#0066cc', linewidth = 3)
    #     ax1.annotate('(10 days,\n 93% users)', xy = (16.67, 93.55), xytext = (30, 40),
    #     arrowprops = dict(facecolor = 'black', shrink = 0.1, width = 2),
    #     size = font_size)
    #     ax1.set_xlabel('%  of Days/% of Users', fontsize = font_size)
    #     ax1.set_ylabel('% of Users', fontsize = font_size)
    #     ax1.set_yticks(np.arange(0,101,step = 20)) #,[0,3,6,9,12],size = font_size
    #     ax2  =  ax1.twinx()
    #     ax2.tick_params(axis = 'both', which = 'major', labelsize = font_size)
    #     ax2.plot(xvals2, yvals2,'-', color = '#0066cc',\
    #              marker = '*', markersize = 12, markevery = 1,linewidth = 3) #
    #     ax2.set_ylabel('Repetition Rate', fontsize = font_size)
    #     ax2.set_yticks(np.arange(0,110,step = 20)) #,[0,20,40,60,80,100]
    #     plt.subplots_adjust(top = 0.95, right = 0.8, left = 0.21, bottom = 0.23)
    #     plt.xticks(np.arange(0,101,step = 20),[0,20,40,60,80,100],fontsize = font_size) # np.arange(0,21,step = 4),[0,4,8,12,16,20],
    #     plt.yticks(size = font_size) # np.arange(0,101,step = 20),[0,20,40,60,80,100],
    #     plt.ylabel('% of Traffic',fontsize = font_size)
    #     plt.xlim(0,100)
    #     plt.ylim(0,100)
    #     plt.show()
    #     pdf.savefig(fig)

	
def user_busline_similar():
    """ 
    analyze users of the same busline, see if they have anything in common (http/portal)
    """

    date = []
    for i in range(1,10):
        date.append('0'+str(i))
    for i in range(10,21):
        date.append(str(i))
    up_rate = [];down_rate = []
    for item in date:
        user_upflow_tmp = collections.defaultdict(int);user_downflow_tmp = collections.defaultdict(int)
        data_path = "/home/hadoop/Downloads/bus_wifi/huashi_2month/userFlow/2017-02-"+item+".gz"
        # /home/hadoop/Downloads/bus_wifi/huashi_2month/userFlow/2017-02-07.gz
        files = []
        try:
            for k in os.listdir(data_path):
                if k.startswith("part"):
                    files = open(data_path+'/'+k)
            for line in files:
                try:
                    attrs = line.split("`")
                    if attrs[1] == '10:f6:81:bf:a1:41':
                        print (line)
                    user_upflow_tmp[attrs[1]]+ = int(attrs[7]) # up diff values
                    user_downflow_tmp[attrs[1]]+ = int(attrs[8])
                except:
                    pass
            up_null = 0;down_null = 0
            for k,v in user_upflow_tmp.items():
                if v == 0:
                    # print k
                    up_null+ = 1
            for k1,v1 in user_downflow_tmp.items():
                if v1 == 0:
                    down_null+ = 1
            up_rate.append(100*up_null/len(user_upflow_tmp.keys()))
            down_rate.append(100*down_null/len(user_downflow_tmp.keys()))
        except:
            pass


def user_internet_portal_days():
    """
    cdf of users use internet/portal
    """

    # k: # of days, v: # of users
    temp_dict = json.load(open("user_wifi_avail_days_dict"))
    interval_cdf = collections.defaultdict(int)
    for k,v in temp_dict.items():
        interval_cdf[int(k)] = v
    sorted_dict = sorted(interval_cdf.items(), key = operator.itemgetter(0))
    sum_ = sum([x[1] for x in sorted_dict])
    xvals = [];yvals = [];y_temp = 0
    for item in sorted_dict:
        xvals.append(int(item[0]))
        y_temp+ = item[1]
        yvals.append(100*y_temp/sum_)
    # xvals = [1]+xvals
    # yvals = [0]+yvals
    # xvals, yvals = sensing_tools.cdf_draw()

    # k: userid, v: # of days
    portal_dict = json.load(open("user_portal_avail_days_dict"))
    xvals_portal, yvals_portal = sensing_tools.cdf_draw(list(portal_dict.values()))

    with PdfPages('user_wifi_portal_avail.pdf') as pdf:
        font_size = '33'
        fig  =  plt.figure()
        ax1 = fig.add_subplot(111)

        # ax1.tick_params(axis = 'both', which = 'major', labelsize = font_size)
        ax1.plot([100*x/60 for x in xvals], uniform_filter1d(yvals, 1), '-', color = '#0066cc', linewidth = 3)
        ax1.annotate('(7 days,\n 80% users)', xy = (7, 80), xytext = (15, 60),
        arrowprops = dict(facecolor = 'black', shrink = 0.1),
        size = font_size)

        ax1.plot([100*x/60 for x in xvals_portal], uniform_filter1d(yvals_portal, 1), '--', color = 'k', linewidth = 3)
        ax1.annotate('(3 days,\n 80% users)', xy = (3, 80), xytext = (5, 35),
        arrowprops = dict(facecolor = 'black', shrink = 0.1),
        size = font_size)
        ax1.set_xlabel('# of Days', fontsize = font_size)
        ax1.set_ylabel('% of Users', fontsize = font_size)
        # ax1.set_yticks(np.arange(0,101,step = 20)) #,[0,3,6,9,12],size = font_size

        plt.subplots_adjust(top = 0.95, right = 0.9, left = 0.21, bottom = 0.23)
        plt.xticks(np.arange(0,41,step = 10),[0,10,20,30,40],fontsize = font_size) # np.arange(0,21,step = 4),[0,4,8,12,16,20],
        plt.yticks(size = font_size) # np.arange(0,101,step = 20),[0,20,40,60,80,100],
        plt.legend(['HTTP','Portal'],fontsize = font_size, loc = [0.23, -0.05], frameon = False)
        # plt.xlabel('# of days', fontsize = font_size)
        plt.grid()
        plt.xlim(0,40)
        plt.ylim(0,100)
        plt.show()
        pdf.savefig(fig)

	
def user_count():
    """
    all users in China
    """
    files = []; users = []
    data_path = "/home/hadoop/Downloads/bus_wifi_data/huashi_2month/userFlow/2017-03-01.gz/"
    for file in os.listdir(data_path):
        if file.startswith("part"):
            files.append(os.path.join(data_path,file))
    for f in files:
        for line in open(f):
            users.append(line.split("`")[1])
    print ("Number of users: ",len(list(set(users))))


def user_count_city():
    """
    TODO: active user per day in all the cities
    # print city, list of number of active devices for each day
    """

    files = []
    data_path = "/home/hadoop/Downloads/bus_wifi_data/huashi_2month/con_discon"
    for i in os.listdir(data_path):
        if i.startswith("2017-"):
            for j in os.listdir(os.path.join(data_path, i)):
                if j.startswith("part"):
                    files.append(os.path.join(data_path, i, j))
    date_devID = collections.defaultdict(list)
    un_devID = []
    for file in files:
        print (file)
        with open(file) as f:
            for line in f:
                attrs = line.split('`')
                try: # adjust the index by different data sources
                    # print (devID_city_dict[attrs[0]][0])
                    if devID_city_dict[attrs[0]][0] in ['深圳', '无锡', '南京', '长沙']:
                        # 1: userID, 2: devID, 4: date-time
                        date_devID[devID_city_dict[attrs[0]][0]].append(attrs[1])
                except Exception as e:
                    un_devID.append(attrs[0])
    for city, userid in date_devID.items():
        print (f"{city}: accumulative user number: {len(list(set(userid)))}")


def user_device_cdf():
    # TODO: number of devices connects by the user
    # #%% process
    # user_date = collections.defaultdict(list)
    # days = ['0'+str(v) for v in range(1,10)]+[str(x) for x in range(10,22)]
    # # days = ['01']
    # for day in days:
    #     dev_flow_path = '/home/hadoop/Downloads/bus_wifi_data/huashi_2month/userFlow/2017-03-'+day+'.gz/'
    #     files = []; user_dev = collections.defaultdict(list)
    #     for j in os.listdir(dev_flow_path):
    #         if j.startswith('part'):
    #             files.append(os.path.join(dev_flow_path,j))
    #     for file in files:
    #         print (file)
    #         for line in open(file):
    #             attrs = line.split('`')
    #             if attrs[2] in sz_busline_plate: # see if it is a sz device
    #                 try:
    #                     # user_dev[attrs[1]].append(attrs[0]) #k: userID, v: devID, con_discon
    #                     user_dev[attrs[1]].append(attrs[2]) #k: userID, v: devID, userFlow
    #                 except:
    #                     continue
    #     # print (user_dev)
    #     for k, v in user_dev.items():
    #         tmp = [day, len(v)]
    #         user_date[k].append(tmp)
    # res = []
    # for userid, list_ in user_date.items():
    #     res.append(int(sum([x[1] for x in list_])/len(list_)))
    # # # # multi days
    # # res = []
    # # for userid, list_ in user_dev.items():
    # #     res.append(len(list(set(list_))))
    # json.dump(res, open("user_dev_dist_multi","w"))

    # #%% draw
    # all_ = json.load(open("user_dev_dist_multi"))
    # xvals, yvals = sensing_tools.cdf_draw(all_)
    # one_ = json.load(open("user_dev_dist"))
    # xvals1, yvals1 = sensing_tools.cdf_draw(one_)
    # for i in range(len(xvals)):
    #     print (xvals[i], yvals[i])
    # with PdfPages('user_dev_cdf.pdf') as pdf:
    #     font_size = 36; fontw = "normal"
    #     fig  =  plt.figure(figsize = (9,6)) #
    #     ax = fig.add_subplot(111)
    #     # plt.subplots_adjust(top = 0.95, right = 0.9, left = 0.21, bottom = 0.23)
    #     plt.subplots_adjust(top = 0.95, right = 0.95, left = 0.16, bottom = 0.19)
    #     ax.plot(xvals1, yvals1,'k', linestyle = '--',linewidth = 4)
    #     ax.plot(xvals, yvals,'#0066cc',linewidth = 4)
    #
    #     ax.annotate('1 device,\n 66% users', xy = (1, 66), xytext = (25, 75),
    #                 arrowprops = dict(facecolor = 'black', shrink = 0.1, width = 2), size = font_size)
    #
    #     ax.annotate('2 devices,\n 15% users', xy = (2, 14.83), xytext = (25, 5),
    #         arrowprops = dict(facecolor = 'black', shrink = 0.1, width = 2), size = font_size)
    #
    #     plt.xticks(np.arange(0,81,step = 20),[0,20,40,60,80],size = font_size)#
    #     plt.yticks(np.arange(0,101,step = 20),[0,20,40,60,80,100],size = font_size) # np.arange(0,5,step = 1),[0,1,2,3,4],
    #     plt.xlabel(r'# of Devices', fontsize = font_size)
    #     plt.ylabel('% of Users',fontsize = font_size)
    #     plt.legend(["Daily", "60-Day"], loc  =  "center right", \
	# 			   ncol = 1, columnspacing = 0.1, labelspacing = 0.3,\
    #                handletextpad = 0.1, fontsize = font_size, frameon = False)
    #     plt.xlim([0,80])
    #     plt.ylim([0,100])
    #     # plt.grid()
    #     plt.show()
    #     pdf.savefig(fig)

    # #%% draw2
    # all_ = json.load(open("user_dev_dist_multi"))
    # xvals, yvals = sensing_tools.cdf_draw(all_)
    # one_ = json.load(open("user_dev_dist"))
    # xvals1, yvals1 = sensing_tools.cdf_draw(one_)
    # for i in range(len(xvals)):
    #     print (xvals[i], yvals[i])
    # with PdfPages('user_dev_cdf.pdf') as pdf:
    #     font_size = 46; fontw = "normal"
    #     fig  =  plt.figure(figsize = (9,6)) #
    #     ax = fig.add_subplot(111)
    #     # plt.subplots_adjust(top = 0.95, right = 0.9, left = 0.21, bottom = 0.23)
    #     plt.subplots_adjust(top = 0.95, right = 0.95, left = 0.19, bottom = 0.20)
    #     ax.plot(xvals1, yvals1,'k', linestyle = '--',linewidth = 4)
    #     ax.plot(xvals, yvals,'#0066cc',linewidth = 4)

    #     ax.annotate('1 device,\n 66% users', xy = (1, 66), xytext = (25, 70),
    #                 arrowprops = dict(facecolor = 'black', shrink = 0.1, width = 2), size = font_size)

    #     ax.annotate('2 devices,\n 15% users', xy = (2, 14.83), xytext = (25, 5),
    #         arrowprops = dict(facecolor = 'black', shrink = 0.1, width = 2), size = font_size)

    #     plt.xticks(np.arange(0,81,step = 20),[0,20,40,60,80],size = font_size)#
    #     plt.yticks(np.arange(0,101,step = 20),[0,20,40,60,80,100],size = font_size) # np.arange(0,5,step = 1),[0,1,2,3,4],
    #     plt.xlabel(r'# of Devices', fontsize = font_size)
    #     plt.ylabel('% of Users',fontsize = font_size)
    #     plt.legend(["Daily", "60-Day"], loc  =  "center right", \
				#    ncol = 1, columnspacing = 0.1, labelspacing = 0.3,\
    #                handletextpad = 0.1, fontsize = font_size, frameon = False)
    #     plt.xlim([0,80])
    #     plt.ylim([0,100])
    #     # plt.grid()
    #     plt.show()
    #     pdf.savefig(fig)


    #%% larger version
    all_ = json.load(open("user_dev_dist_multi"))
    xvals, yvals = sensing_tools.cdf_draw(all_)
    one_ = json.load(open("user_dev_dist"))
    xvals1, yvals1 = sensing_tools.cdf_draw(one_)
    for i in range(len(xvals)):
        print (xvals[i], yvals[i])
    with PdfPages('user_dev_cdf1.pdf') as pdf:
        font_size = 36; fontw = "normal"
        fig  =  plt.figure(figsize = (9,6)) #
        ax = fig.add_subplot(111)
        # plt.subplots_adjust(top = 0.95, right = 0.9, left = 0.21, bottom = 0.23)
        plt.subplots_adjust(top  =  0.85, right  =  0.95, left  =  0.16, bottom  =  0.19)
        ax.plot(xvals1, yvals1,'k', linestyle = '--',linewidth = 4)
        ax.plot(xvals, yvals,'#0066cc',linewidth = 4)

        ax.annotate('1 device,\n 66% users', xy = (1, 66), xytext = (25, 70),
                    arrowprops = dict(facecolor = 'black', shrink = 0.1, width = 2), size = font_size)

        ax.annotate('2 devices,\n 15% users', xy = (2, 14.83), xytext = (25, 5),
            arrowprops = dict(facecolor = 'black', shrink = 0.1, width = 2), size = font_size)

        plt.xticks(np.arange(0,81,step = 20),[0,20,40,60,80],size = font_size)#
        plt.yticks(np.arange(0,101,step = 20),[0,20,40,60,80,100],size = font_size) # np.arange(0,5,step = 1),[0,1,2,3,4],
        plt.xlabel(r'# of Devices', fontsize = font_size)
        plt.ylabel('% of Users',fontsize = font_size)
        plt.legend(["Daily", "60-Day"], loc  =  "center right", \
                   ncol = 1, columnspacing = 0.1, labelspacing = 0.3,\
                   handletextpad = 0.1, fontsize = font_size, frameon = False)
        plt.xlim([0,80])
        plt.ylim([0,100])
        # plt.grid()
        plt.show()
        pdf.savefig(fig)

	
def device_user_cdf():
    # TODO: number of users connect by the device
    # #%% process
    # user_date = collections.defaultdict(list)
    # user_dev = collections.defaultdict(list)
    # days = ['0'+str(v) for v in range(1,10)]+[str(x) for x in range(10,22)]
    # # days = ['01']
    # # day = '06'
    # for day in days:
    #     dev_flow_path = '/home/hadoop/Downloads/bus_wifi_data/huashi_2month/userFlow/2017-03-'+day+'.gz/'
    #     files = []
    #     for j in os.listdir(dev_flow_path):
    #         if j.startswith('part'):
    #             files.append(os.path.join(dev_flow_path,j))
    #     for file in files:
    #         print (file)
    #         for line in open(file):
    #             attrs = line.split('`')
    #             if attrs[2] in sz_busline_plate: # see if it is a sz device
    #                 try:
    #                     user_dev[attrs[2]].append(attrs[1]) #k: devID, v: userID
    #                 except:
    #                     continue
    # res = []
    # for userid, list_ in user_dev.items():
    #     res.append(len(list(set(list_))))
    # json.dump(res, open("dev_user_dist_multi","w"))

    #%% draw
    all_ = json.load(open("dev_user_dist_multi"))
    xvals, yvals = sensing_tools.cdf_draw(all_)
    one_ = json.load(open("dev_user_dist"))
    xvals1, yvals1 = sensing_tools.cdf_draw(one_)
    for i in range(len(xvals)):
        print (xvals[i], yvals[i])
    with PdfPages('dev_user_cdf.pdf') as pdf:
        font_size = 33; fontw = "normal"
        fig  =  plt.figure() # figsize = (9,6)
        ax = fig.add_subplot(111)
        plt.subplots_adjust(top = 0.95, right = 0.9, left = 0.21, bottom = 0.23)
        ax.plot(xvals1, yvals1,'k', linestyle = '--',linewidth = 4)
        ax.plot(xvals, yvals,'#0066cc',linewidth = 4)

        ax.annotate('254 users,\n 20% devices', xy = (254, 20.0), xytext = (1200, 5),
                    arrowprops = dict(facecolor = 'black', shrink = 0.1, width = 2), size = 30)

        ax.annotate('3907 users,\n 80% devices', xy = (3907, 80), xytext = (4800, 55),
                    arrowprops = dict(facecolor = 'black', shrink = 0.1, width = 2), size = 30)

        plt.xticks(np.arange(0,10001,step = 2000),[0,2,4,6,8,10],size = font_size)#
        plt.yticks(np.arange(0,101,step = 20),[0,20,40,60,80,100],size = font_size)
        plt.xlabel(r'# of Users (10$^3$)', fontsize = font_size)
        plt.ylabel('% of Devices',fontsize = font_size)
        plt.legend(["Daily", "60-Day"], loc = [0.47, 0.17] , \
				   ncol = 1, columnspacing = 0.1, labelspacing = 0.3,\
                   handletextpad = 0.1, fontsize = 30, frameon = False)
        plt.xlim([0,10000])
        plt.ylim([0,100])
        # plt.grid()
        plt.show()
        pdf.savefig(fig)

	
def rep_cal(time_list):
    # TODO: calculate repetition on daily and days
    date_ct = collections.defaultdict(list)
    for item in time_list:
        date_ct[item.split('T')[0]].append(time_2_sec(item))
    all_rep_daily = []
    for date_, secs in date_ct.items():
        secs.sort()
        rep = 0
        for i in range(len(secs)-1):
            if secs[i+1]-secs[i]>1800: # 20 minutes
                rep+ = 1
        all_rep_daily.append(rep)
    daily_rep = np.mean(all_rep_daily) # average daily rep
    days_rep =  sum(all_rep_daily) # sum of all rep
    # print ("daily_rep: {}, days_rep: {}".format(daily_rep, days_rep))
    return daily_rep, days_rep


def dev_repetition_cdf():
    # TODO: # of re-visit from the same user for each device
    # #%% ---- prepare data for ploting
    # data_path = "/home/hadoop/Downloads/bus_wifi_data/huashi_2month/userHttp/" # userPortal_V1.4
    # files = [];dev_days = collections.defaultdict(list)
    # for j in os.listdir(data_path):
    #     for k in os.listdir(data_path+j):
    #         if k.startswith('part'):
    #             files.append(os.path.join(data_path,j,k))
    # for file in files:
    #     print (file)
    #     for line in open(file):
    #         attrs = line.split('`')
    #         if attrs[0] in sz_busline_plate:
    #             try: # devID, v: [timing, userID]
    #                 dev_days[attrs[0]].append([attrs[3], attrs[2]])
    #             except:
    #                 continue
    # dev_rep_days = collections.defaultdict(list)
    # dev_rep_daily = collections.defaultdict(list)
    # for dev, time_list in dev_days.items():
    #     user_time = collections.defaultdict(list)
    #     for item in time_list: # [timing, userID]
    #         user_time[item[1]].append(item[0])
    #     for user, timing in user_time.items():
    #         daily_rep, days_rep = rep_cal(timing)
    #         if daily_rep*days_rep! = 0:
    #             dev_rep_daily[dev].append(daily_rep)
    #             dev_rep_days[dev].append(days_rep)
    # reps_daily = []; reps_days = []
    # for dev, daily_reps in dev_rep_daily.items():
    #     reps_daily.append(int(np.max(daily_reps)))
    # for dev, days_reps in dev_rep_days.items():
    #     reps_days.append(int(np.max(days_reps)))
    # res = collections.defaultdict(list)
    # res['daily'] = reps_daily; res['days'] = reps_days
    # json.dump(res, open("daily_days_reps", "w"))

    #%% ploting
    res = json.load(open("daily_days_reps"))
    reps_daily = res["daily"]; reps_days = res["days"]
    xvals, yvals = sensing_tools.cdf_draw(reps_daily)
    xvals1, yvals1 = sensing_tools.cdf_draw(reps_days)
    print (xvals1[0], yvals1[0])
    print (max(xvals))
    print (yvals[min(range(len(yvals)), key = lambda i: abs(xvals[i]-1))])
    print (xvals1[min(range(len(yvals1)), key = lambda i: abs(yvals1[i]-80))])

    # with PdfPages('dev_user_repetition_cdf.pdf') as pdf:
    #     font_size = 36; fontw = "normal"
    #     fig  =  plt.figure(figsize = (9,6)) #
    #     ax = fig.add_subplot(111)
    #     # plt.subplots_adjust(top = 0.95, right = 0.9, left = 0.21, bottom = 0.23)
    #     plt.subplots_adjust(top = 0.95, right = 0.95, left = 0.16, bottom = 0.19)
    #     ax.plot(xvals, yvals,'#0066cc',linewidth = 4)
    #     ax.plot(xvals1, yvals1,'k', linestyle = '--',linewidth = 4)
    #
    #
    #     ax.annotate('1 revisiting,\n 60% devices', xy = (1, 60.66), xytext = (9, 33),
    #                 arrowprops = dict(facecolor = 'black', shrink = 0.1, width = 2), size = font_size)
    #
    #     ax.annotate('4 revisitings,\n 72% devices', xy = (1, 71.55), xytext = (18, 68),
    #                 arrowprops = dict(facecolor = 'black', shrink = 0.1, width = 2), size = font_size)
    #
    #     plt.xticks(np.arange(0,61,step = 10),[0,10,20,30,40,50,60],size = font_size)# np.arange(0,10001,step = 2000),[0,2,4,6,8,10],
    #     plt.yticks(np.arange(0,101,step = 20),[0,20,40,60,80,100],size = font_size)
    #     plt.xlabel(r'# of Revisiting', fontsize = font_size)
    #     plt.ylabel('% of Devices',fontsize = font_size)
    #     plt.legend(["Daily", "60-Day"], loc  =  "lower right", \
	# 			   ncol = 1, columnspacing = 0.1, labelspacing = 0.3,\
    #                handletextpad = 0.1, fontsize = font_size, frameon = False)
    #     # loc = [0.47, -0.02]
    #     plt.xlim([0,60])
    #     plt.ylim([0,100])
    #     # plt.grid()
    #     plt.show()
    #     pdf.savefig(fig)

    with PdfPages('dev_user_repetition_cdf.pdf') as pdf:
        font_size = 46; fontw = "normal"
        fig  =  plt.figure(figsize = (9,6)) #
        ax = fig.add_subplot(111)
        # plt.subplots_adjust(top = 0.95, right = 0.9, left = 0.21, bottom = 0.23)
        plt.subplots_adjust(top = 0.95, right = 0.95, left = 0.19, bottom = 0.22)
        ax.plot(xvals, yvals,'#0066cc',linewidth = 4)
        ax.plot(xvals1, yvals1,'k', linestyle = '--',linewidth = 4)


        ax.annotate('1 revisiting,\n 60% devices', xy = (1, 60.66), xytext = (9, 33),
                    arrowprops = dict(facecolor = 'black', shrink = 0.1, width = 2), size = font_size)

        ax.annotate('4 revisitings,\n 72% devices', xy = (1, 71.55), xytext = (18, 68),
                    arrowprops = dict(facecolor = 'black', shrink = 0.1, width = 2), size = font_size)

        plt.xticks(np.arange(0,61,step = 10),[0,10,20,30,40,50,60],size = font_size)# np.arange(0,10001,step = 2000),[0,2,4,6,8,10],
        plt.yticks(np.arange(0,101,step = 20),[0,20,40,60,80,100],size = font_size)
        plt.xlabel(r'# of Revisiting', fontsize = font_size)
        plt.ylabel('% of Devices',fontsize = font_size)
        plt.legend(["Daily", "60-Day"], loc  =  [0.47, -0.02], \
				   ncol = 1, columnspacing = 0.1, labelspacing = 0.3,\
                   handletextpad = 0.1, fontsize = font_size, frameon = False)
        # loc = [0.47, -0.02]
        plt.xlim([0,60])
        plt.ylim([0,100])
        # plt.grid()
        plt.show()
        pdf.savefig(fig)


def user_dev_busline_helper(dev_list):
    """ 
    TODO: determine the number of bus lines connected
    """
    tmp = list(set(dev_list))
    buslines = []
    for dev in dev_list:
        buslines.appennd(sz_busline_plate[dev][0])
    return len(tmp)/len(list(set(buslines)))


def user_dev_busline():
    """ 
    TODO: cdf of how user connects to buses or bus lines
    """
    #%% ---- prepare data for ploting
    data_path = "/home/hadoop/Downloads/bus_wifi_data/huashi_2month/con_discon/" # userPortal_V1.4
    files = [];dev_days = collections.defaultdict(list)
    for j in os.listdir(data_path):
        for k in os.listdir(data_path+j):
            if k.startswith('part'):
                files.append(os.path.join(data_path,j,k))
    for file in files:
        print (file)
        for line in open(file):
            attrs = line.split('`')
            if attrs[0] in sz_busline_plate:
                try: # userID, v: [timing, devID]
                    dev_days[attrs[1]].append(attrs[0])
                except:
                    continue
    for user, dev_list in dev_days.items():
        pass

    res['daily'] = reps_daily; res['days'] = reps_days
    json.dump(res, open("daily_days_reps", "w"))

    with PdfPages('dev_user_bus_busline_cdf.pdf') as pdf:
        font_size = 33; fontw = "normal"
        fig  =  plt.figure() # figsize = (9,6)
        ax = fig.add_subplot(111)
        plt.subplots_adjust(top = 0.95, right = 0.9, left = 0.21, bottom = 0.23)
        ax.plot(xvals, yvals,'#0066cc',linewidth = 4)
        ax.plot(xvals1, yvals1,'k', linestyle = '--',linewidth = 4)


        ax.annotate('1 revisit,\n 63% devices', xy = (1, 63.13), xytext = (20, 35),
                    arrowprops = dict(facecolor = 'black', shrink = 0.1, width = 2), size = 30)

        ax.annotate('1 revisits,\n 72% devices', xy = (1, 72), xytext = (40, 70),
                    arrowprops = dict(facecolor = 'black', shrink = 0.1, width = 2), size = 30)

        plt.xticks(np.arange(0,61,step = 10),[0,10,20,30,40,50,60],size = font_size)# np.arange(0,10001,step = 2000),[0,2,4,6,8,10],
        plt.yticks(np.arange(0,101,step = 20),[0,20,40,60,80,100],size = font_size)
        plt.xlabel(r'# of Revisiting', fontsize = font_size)
        plt.ylabel('% of Devices',fontsize = font_size)
        plt.legend(["Daily", "60-Day"], loc = [0.47, -0.02] , \
				   ncol = 1, columnspacing = 0.1, labelspacing = 0.3,\
                   handletextpad = 0.1, fontsize = 30, frameon = False)
        plt.xlim([0,60])
        plt.ylim([0,100])
        # plt.grid()
        plt.show()
        pdf.savefig(fig)


def user_connection():
    """
    TODO: users connected to the WiFi repeatedly in two month
    """
    data_path = "/home/hadoop/Downloads/bus_wifi_data/huashi_2month/con_discon/" # userPortal_V1.4
    files = []; user_times  =  collections.defaultdict(int)
    for j in os.listdir(data_path):
        for k in os.listdir(data_path+j):
            if k.startswith('part'):
                files.append(os.path.join(data_path,j,k))
    for file in files:
        print (file)
        for line in open(file):
            attrs  =  line.split('`')
            if attrs[0] in sz_busline_plate:
                # try: # userID, v: [timing, devID]
                user_times[attrs[1]] + =  1

    all_users  =  len(set(user_times.keys()))
    user_onetime  =  0
    for user, ct in user_times.items():
        if ct  ==  1:
            user_onetime + =  1
    # Total user num: 1461090, one time user percentage: 3.676638673866771
    print (f"Total user num: {all_users}, one time user percentage: {100*user_onetime/all_users}")


def user_url_portal_access():
    """
    TODO: url and portal access ct
    """
    data_path = '/home/hadoop/Downloads/bus_wifi_data/huashi_2month/userHttp/'
    files = []; user_times  =  collections.defaultdict(int)
    for j in os.listdir(data_path):
        for k in os.listdir(data_path+j):
            if k.startswith('part'):
                files.append(os.path.join(data_path,j,k))
    for file in files:
        print (file)
        for line in open(file):
            attrs  =  line.split('`')
            if attrs[0] in sz_busline_plate:
                user_times[attrs[2]] + =  1 #

    data_path = '/home/hadoop/Downloads/bus_wifi_data/huashi_2month/userPortal_V1.4/'
    files = []
    for j in os.listdir(data_path):
        for k in os.listdir(data_path+j):
            if k.startswith('part'):
                files.append(os.path.join(data_path,j,k))
    for file in files:
        print (file)
        for line in open(file):
            attrs  =  line.split('`')
            if attrs[0] in sz_busline_plate:
                user_times[attrs[2]] + =  1 #

    user_onetime  =  0
    for user, ct in user_times.items():
        if ct  ==  1:
            user_onetime + =  1
    all_users  =  len(set(user_times.keys()))
    # Total user num: 186629, one time user percentage: 33.91648671964164
    print (f"Total user num: {all_users}, one time user percentage: {100*user_onetime/all_users}")


if __name__  ==  "__main__":
    # # -------------------------
    # # one day temporal dist
    # user_temporal_dist(6)
    # user_temporal_dist_week()

    # # -------------------------
    # # usage http/portal analysis
    # user_recs_http  =  user_http_analysis()
    # user_recs_portal  =  user_portal_analysis()
    # http_portal_one_draw(user_recs_http, user_recs_portal) #

    # # -------------------------
    # # user information
    # user_register_type_stat()
    # user_online_time_cdf()
    # user_traffic_unbalance()
    # user_traffic_dist()
    # http_url_analysis()
    # portal_analysis()
    # user_no_traffic_count()

    # # -------------------------
    # # overall user number changing pattern
    # user_repetition_store()
    # user_rep_read()
    # one_month_pattern_draw()
    # user_data_avail()

    # # -------------------------
    # # user usage pattern
    # user_busline_similar()
    # user_data_avail()
    # user_count()
    # user_count_city()

    # user_internet_portal_days()

    # # -------------------------
    # # user device connection
    # user_device_cdf()
    # device_user_cdf()
    dev_repetition_cdf()
    # user_dev_busline()
    # user_url_portal_access()
    # user_connection()


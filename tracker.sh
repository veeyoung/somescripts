#!/usr/bin/env bash
#
# https://github.com/P3TERX/aria2.conf
# File name：tracker.sh
#
# Copyright (c) 2018-2021 P3TERX <https://p3terx.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# BT tracker is provided by the following project.
# https://github.com/XIU2/TrackersListCollection
#

RED_FONT_PREFIX="\033[31m"
GREEN_FONT_PREFIX="\033[32m"
YELLOW_FONT_PREFIX="\033[1;33m"
LIGHT_PURPLE_FONT_PREFIX="\033[1;35m"
FONT_COLOR_SUFFIX="\033[0m"
INFO="[${GREEN_FONT_PREFIX}INFO${FONT_COLOR_SUFFIX}]"
ERROR="[${RED_FONT_PREFIX}ERROR${FONT_COLOR_SUFFIX}]"
QBITTORRENT_CONF="${HOME}/.config/qBittorrent/qBittorrent.conf"
DOWNLOADER="curl -fsSL --connect-timeout 3 --max-time 3 --retry 2"
NL=$'\n'

DATE_TIME() {
    date +"%m/%d %H:%M:%S"
}

GET_TRACKERS() {
    
    if [[ -z "${CUSTOM_TRACKER_URL}" ]]; then
        echo && echo -e "$(DATE_TIME) ${INFO} Get BT trackers..."
        TRACKER=$(
            ${DOWNLOADER} https://cf.trackerslist.com/all.txt ||
                ${DOWNLOADER} https://gitea.com/XIU2/TrackersListCollection/raw/branch/master/all.txt ||
                ${DOWNLOADER} https://gcore.jsdelivr.net/gh/XIU2/TrackersListCollection/all.txt
        )
    else
        echo && echo -e "$(DATE_TIME) ${INFO} Get BT trackers from url(s):${CUSTOM_TRACKER_URL} ..."
        URLS=$(echo ${CUSTOM_TRACKER_URL} | tr "," "$NL")
        for URL in $URLS; do
            TRACKER+="$(${DOWNLOADER} ${URL} | tr "," "\n")$NL"
        done
        TRACKER="$(echo "$TRACKER" | awk NF | sort -u | sed 'H;1h;$!d;x;y/\n/,/' )"
    fi

    [[ -z "${TRACKER}" ]] && {
        echo
        echo -e "$(DATE_TIME) ${ERROR} Unable to get trackers, network failure or invalid links." && exit 1
    }
}

ECHO_TRACKERS() {
    echo -e "
--------------------[BitTorrent Trackers]--------------------
${TRACKER}
--------------------[BitTorrent Trackers]--------------------
"
}

ADD_TRACKERS() {
    echo -e "$(DATE_TIME) ${INFO} Adding BT trackers to qBittorrent configuration file ${LIGHT_PURPLE_FONT_PREFIX}${QBITTORRENT_CONF}${FONT_COLOR_SUFFIX} ..." && echo
    if [ ! -f ${QBITTORRENT_CONF} ]; then
        echo -e "$(DATE_TIME) ${ERROR} '${QBITTORRENT_CONF}' does not exist."
        exit 1
    else
        if [ -z "$(grep 'Session\\AddTrackersEnabled=' ${QBITTORRENT_CONF})" ]; then
            sed -i '/^\[BitTorrent\]/a\Session\\AddTrackersEnabled=true' ${QBITTORRENT_CONF}
        fi
        if [ -z "$(grep 'Session\\AdditionalTrackers=' ${QBITTORRENT_CONF})" ]; then
            sed -i '/^Session\\AddTrackersEnabled=/a\Session\\AdditionalTrackers=' ${QBITTORRENT_CONF}
        fi
        CLEANED_TRACKER=$(echo "${TRACKER}" | sed ':a;N;$!ba;s/\n\n/\\\\n/g')
        sed -i "s@^\(Session\\\AdditionalTrackers=\).*@\1${CLEANED_TRACKER}@" ${QBITTORRENT_CONF} && echo -e "$(DATE_TIME) ${INFO} BT trackers successfully added to qBittorrent configuration file !"
    fi
}

[ $(command -v curl) ] || {
    echo -e "$(DATE_TIME) ${ERROR} curl is not installed."
    exit 1
}

if [ "$1" = "cat" ]; then
    GET_TRACKERS
    ECHO_TRACKERS
else
    GET_TRACKERS
    ECHO_TRACKERS
    ADD_TRACKERS
fi

exit 0

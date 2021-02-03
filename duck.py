# Copyright (C) 2020 taylor.fish <contact@taylor.fish>
# with assistance from nc Krantz-Fire (https://pineco.net/)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

# This program was based off of code from duck.vbs, a file distributed
# with NO5 IRC <https://fioresoft.net/download3.php> and licensed under
# version 3 of the GNU General Public License as published by the
# Free Software Foundation.
#
# NO5 IRC is covered by the following attribution and copyright notice
# (from https://github.com/fioresoft/no5irc/blob/main/READ.txt):
#
#   NO5 IRC was made by Fernando Fiore.
#   All rights to https://Fioresoft.net

from collections import defaultdict
import json
import random
import time
import weechat

MAX_DELAY = 10000

points_dict = defaultdict(int)
start = None
shot = True
orig_buffer = None

weechat.register(
    "shoottheduckquack",
    "taylor.fish",
    "0.1",
    "GPL3",
    "shoot the duck QUACK!",
    "",
    "",
)

weechat.hook_command(
    "shoottheduckquack",
    "shoot the duck QUACK!",
    "",
    "",
    "",
    "run",
    "",
)

weechat.hook_signal("*,irc_in2_privmsg", "on_msg", "")
weechat.hook_signal("*,irc_out1_privmsg", "on_msg", "")


def run(data, buffer, args):
    global orig_buffer
    orig_buffer = buffer
    weechat.hook_timer(
        random.randrange(MAX_DELAY),
        0,
        1,
        "on_timer",
        "",
    )
    return weechat.WEECHAT_RC_OK


def on_timer(data, remaining_calls):
    global shot, start
    shot = False
    start = time.time()
    weechat.command(orig_buffer, "shoot the duck QUACK!")
    return weechat.WEECHAT_RC_OK


def on_msg(data, signal, signal_data):
    global shot, orig_buffer
    server = signal.split(",")[0]
    msg = weechat.info_get_hashtable(
        "irc_message_parse",
        {"message": signal_data},
    )
    buffer = weechat.info_get("irc_buffer", "%s,%s" % (server, msg["channel"]))
    if not (buffer == orig_buffer and not shot and "bang" in msg["text"]):
        return weechat.WEECHAT_RC_OK
    shot = True
    nickname = msg["nick"] or weechat.info_get("irc_nick", server)
    timer_data = [orig_buffer, nickname, int(round(time.time() - start))]
    orig_buffer = None
    weechat.hook_timer(
        1,
        0,
        1,
        "send_result",
        json.dumps(timer_data),
    )
    return weechat.WEECHAT_RC_OK


def send_result(data, remaining_calls):
    buffer, nickname, duration = json.loads(data)
    weechat.command(
        buffer,
        "congrats {} you shot the duck in {} seconds".format(
            nickname,
            duration,
        ),
    )
    points_dict[nickname] += 1
    weechat.command(
        buffer,
        "{} has {} point(s)".format(nickname, points_dict[nickname]),
    )
    return weechat.WEECHAT_RC_OK

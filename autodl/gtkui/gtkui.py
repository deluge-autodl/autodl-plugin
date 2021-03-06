#
# gtkui.py
#
# Copyright (C) 2016 DirectorX <DirectorX@users.noreply.github.com>
# Copyright (C) 2016 DjLegolas <DjLegolas@users.noreply.github.com>
#
# Basic plugin template created by:
# Copyright (C) 2008 Martijn Voncken <mvoncken@gmail.com>
# Copyright (C) 2007-2009 Andrew Resch <andrewresch@gmail.com>
# Copyright (C) 2009 Damien Churchill <damoxc@gmail.com>
#
# Deluge is free software.
#
# You may redistribute it and/or modify it under the terms of the
# GNU General Public License, as published by the Free Software
# Foundation; either version 3 of the License, or (at your option)
# any later version.
#
# deluge is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with deluge.    If not, write to:
# 	The Free Software Foundation, Inc.,
# 	51 Franklin Street, Fifth Floor
# 	Boston, MA  02110-1301, USA.
#
#    In addition, as a special exception, the copyright holders give
#    permission to link the code of portions of this program with the OpenSSL
#    library.
#    You must obey the GNU General Public License in all respects for all of
#    the code used other than OpenSSL. If you modify file(s) with this
#    exception, you may extend this exception to your version of the file(s),
#    but you are not obligated to do so. If you do not wish to do so, delete
#    this exception statement from your version. If you delete this exception
#    statement from all source files in the program, then also delete it here.
#

import gtk

from deluge.log import LOG as log
from deluge.ui.client import client
from deluge.plugins.pluginbase import GtkPluginBase
import deluge.component as component
import deluge.common

from autodl.common import get_resource

class GtkUI(GtkPluginBase):
    def enable(self):
        self._create_ui()
        component.get("Preferences").add_page("AutoDL", self.glade.get_widget("vbox1"))

    def disable(self):
        component.get("Preferences").remove_page("AutoDL")
        component.get("PluginManager").deregister_hook("on_apply_prefs", self.on_apply_prefs)
        component.get("PluginManager").deregister_hook("on_show_prefs", self.on_show_prefs)

    def on_apply_prefs(self):
        log.debug("applying prefs for AutoDL")

    def on_show_prefs(self):
        log.debug("showing prefs for AutoDL")

    def _create_ui(self):
        self.glade = gtk.glade.XML(get_resource("main.glade"))
        client.autodl.get_trackers_data().addCallback(self.on_trackers_receive)
        client.autodl.get_irc_servers_data().addCallback(self.on_irc_servers_receive)
        # client.autodl.get_filters_data().addCallback(self.on_filters_receive)

    def on_trackers_receive(self, trackers_info):
        if len(trackers_info) > 0:
            trackers_notebook = self.glade.get_widget('trackers_notebook')
            if trackers_notebook is not None:
                # remove the example page
                trackers_notebook.remove_page(0)
                for tracker_info in trackers_info:
                    label = gtk.glade.XML(get_resource('trackers.glade'), 'tracker_label_')\
                        .get_widget('tracker_label_')
                    label.set_name(label.get_name() + tracker_info['longName'])
                    label.set_label(tracker_info['longName'])
                    table = gtk.glade.XML(get_resource('trackers.glade'), 'tracker_table_')\
                        .get_widget('tracker_table_')
                    table.set_name(table.get_name() + tracker_info['longName'])
                    table.resize(len(tracker_info['settings']) + 2, 2)
                    table.set_border_width(5)
                    for i in range(0, len(tracker_info['settings']) + 2):
                        table.set_row_spacing(i, 10)
                    for i in range(0, 2):
                        table.set_col_spacing(i, 3)
                    trow = 1
                    brow = 2
                    for setting in tracker_info['settings']:
                        if setting['type'] == 'textbox' or setting['type'] == 'integer':
                            tracker_config_lines = tracker_info['data']['lines']
                            label_ = gtk.Label(setting['text'])
                            label_.set_justify(gtk.JUSTIFY_LEFT)
                            label_.set_alignment(0, 0.5)
                            entry = gtk.Entry()
                            entry.set_name(setting['name'])
                            entry.set_tooltip_text(setting['tooltiptext'])
                            if len(tracker_config_lines) is not 0:
                                entry.set_text(tracker_config_lines[setting['name']]['value']
                                               if tracker_config_lines[setting['name']]['value'] is not None
                                               or tracker_config_lines[setting['name']]['value'] != ''
                                               else tracker_config_lines[setting['name']]['defaultValue'])
                            table.attach(label_, 0, 1, trow, brow, gtk.FILL, gtk.SHRINK)
                            table.attach(entry, 1, 2, trow, brow, gtk.FILL | gtk.EXPAND, gtk.SHRINK)
                            trow += 1
                            brow += 1
                    for child in table.get_children():
                        if child.get_name() == 'tracker_notes_content_label':
                            description = ''
                            for setting in tracker_info['settings']:
                                if setting['type'] == 'description':
                                    description += setting['text']
                            child.set_label(description)
                            child.set_use_markup(True)
                        elif child.get_name() == 'entry1' or child.get_name() == 'option1_label':
                            table.remove(child)
                        elif child.get_name() == 'delay_label' or child.get_name() == 'tracker_pull_delay_spinbutton':
                            table.remove(child)
                            if child.get_name() == 'delay_label':
                                table.attach(child, 0, 1, trow + 1, brow + 2, gtk.FILL, gtk.SHRINK)
                            else:
                                table.attach(child, 1, 2, trow + 1, brow + 2, gtk.FILL | gtk.EXPAND, gtk.SHRINK)
                        elif child.get_name() == 'tracker_force_http_download':
                            table.remove(child)
                            child.set_relief(gtk.RELIEF_NORMAL)
                            child.set_border_width(4)
                            table.attach(child, 1, 2, trow + 2, brow + 3, gtk.FILL, gtk.FILL)
                    trackers_notebook.append_page(table, label)
                trackers_notebook.show_all()

    def on_irc_servers_receive(self, irc_servers):
        pass

    def on_filters_receive(self, filters):
        pass

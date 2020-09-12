"""
Version of the gui that plots graphs in html window, should allow for more customisation
WIP - Functional but still buggy
"""

import matplotlib.pyplot as plt
import matplotlib.dates
import mpld3
import wx
import wx.html2
import winreg
import sys
import os

from api_interface import Player

# To stop un needed downloads, store player data locally
loadedPlayers = {}

class MyFrame(wx.Frame):
    """Window for the program"""

    def __init__(self):
        super().__init__(parent=None, title='ETF2L Stat Tracker')
        panel = wx.Panel(self)
        my_sizer = wx.BoxSizer(wx.VERTICAL)
        self.text_ctrl = wx.TextCtrl(panel)
        my_sizer.Add(self.text_ctrl, 0, wx.ALL | wx.EXPAND, 5)

        # Use html window for displaying graphs
        self.browser = wx.html2.WebView.New(panel)

        my_btn = wx.Button(panel, label='Plot Player Progress')
        my_btn.Bind(wx.EVT_BUTTON, self.plot_progress_pressed)

        my_sizer.Add(my_btn, 0, wx.ALL | wx.CENTER, 5)
        my_sizer.Add(self.browser, 1, wx.ALL | wx.EXPAND, 5)

        panel.SetSizer(my_sizer)

        #fig, ax = plt.subplots()
        #labels = ['point {0}'.format(i + 1) for i in range(N)]
        #tooltip = mpld3.plugins.PointLabelTooltip(scatter, labels=labels)
        #mpld3.plugins.connect(fig, tooltip)


        # self.browser.LoadURL(html_filepath)

        self.Show()

    def plot_progress_pressed(self, event):
        idAsString = self.text_ctrl.GetValue()
        idAsInt = int(idAsString)
        html_filepath = "C:/Users/Alex/Documents/GitHub/tf2-stats/src/current_graph.html"

        if not idAsInt:
            print("Please enter ETF2L id")
        else:
            figure = make_progress_graph(idAsInt)
            mpld3.save_html(figure, html_filepath)
            html_string = mpld3.fig_to_html(figure)
            self.browser.SetPage(html_string, "")

def make_progress_graph(player_id):
    '''Split this into load_player() and plot_progress() later'''

    figure = plt.Figure()
    ax = figure.add_subplot(111)

    if player_id not in loadedPlayers.keys():
        status = "Downloading Player Data for ID: " + str(player_id)
        print(status)
        player = Player(player_id)
        loadedPlayers[player_id] = player

    else:
        status = "Player Info For " + loadedPlayers[player_id].playerName + " (" + str(
            player_id) + ") Already Downloaded"
        print(status)
        player = loadedPlayers[player_id]

    # Get the data from player object
    progressData = player.plot_div_progress(False)

    # Plot the graph
    ax.clear()

    ax.set_facecolor('#EEEEEE')
    ax.grid(color='white', linestyle='solid')

    # Matches won
    ax.scatter(progressData['time'][(progressData['impact'] > 0) & (progressData['result'] == "v")],
                    progressData['div'][(progressData['impact'] > 0) & (progressData['result'] == "v")],
                    s=progressData['impact'][(progressData['impact'] > 0) & (progressData['result'] == "v")]
                    , alpha=0.6, marker='o', c="Green")

    # Matches Lost
    ax.scatter(progressData['time'][(progressData['impact'] > 0) & (progressData['result'] == "l")],
                    progressData['div'][(progressData['impact'] > 0) & (progressData['result'] == "l")],
                    s=progressData['impact'][(progressData['impact'] > 0) & (progressData['result'] == "l")]
                    , alpha=0.6, marker='o', c="Red")

    # Matches drawn
    ax.scatter(progressData['time'][(progressData['impact'] > 0) & (progressData['result'] == "d")],
                    progressData['div'][(progressData['impact'] > 0) & (progressData['result'] == "d")],
                    s=progressData['impact'][(progressData['impact'] > 0) & (progressData['result'] == "d")]
                    , alpha=0.6, marker='o', c="Blue")

    # Matches merced
    ax.scatter(progressData['time'][(progressData['impact'] > 0) & (progressData['result'] == "merc")],
                    progressData['div'][(progressData['impact'] > 0) & (progressData['result'] == "merc")],
                    s=progressData['impact'][(progressData['impact'] > 0) & (progressData['result'] == "merc")]
                    , alpha=0.6, marker='o', c="Brown")

    # Black cross for matches with no logs found
    ax.scatter(progressData['time'][progressData['impact'] == 0],
                    progressData['div'][progressData['impact'] == 0], s=50, alpha=0.8, marker='x', c="Black")

    # Formatting
    ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%d-%m-%y'))
    ax.set_title(player.playerName + " ETF2L Division Progress")
    ax.set_xlabel("Match Date")
    ax.set_ylabel("Tier")
    ax.set_ylim([6.2, -0.2])

    return figure




if __name__ == '__main__':

    # See https://github.com/wxWidgets/Phoenix/issues/1256 for discussion of reg edits
    def set_reg(name, reg_path, value):
        try:
            winreg.CreateKey(winreg.HKEY_CURRENT_USER, reg_path)
            registry_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_WRITE)
            winreg.SetValueEx(registry_key, name, 0, winreg.REG_DWORD, value)
            winreg.CloseKey(registry_key)
            return True
        except WindowsError:
            return False


    def get_reg(name, reg_path):
        try:
            registry_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_READ)
            value, regtype = winreg.QueryValueEx(registry_key, name)
            winreg.CloseKey(registry_key)
            return value
        except WindowsError:
            return None


    if wx.Platform == '__WXMSW__':
        reg_path = r"Software\Microsoft\Internet Explorer\Main\FeatureControl\FEATURE_BROWSER_EMULATION"
        set_reg(os.path.basename(sys.executable), reg_path, 11001)

    app = wx.App()
    frame = MyFrame()
    frame.Fit()
    frame.SetMinSize((700,650))

    app.MainLoop()
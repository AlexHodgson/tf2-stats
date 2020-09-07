import wx
import matplotlib

matplotlib.use('WXAgg')

from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wx import NavigationToolbar2Wx
from matplotlib.figure import Figure

from api_interface import Player

loadedPlayers = {}


class MyFrame(wx.Frame):
    """Window for the program"""

    def __init__(self):
        super().__init__(parent=None, title='ETF2L Stat Tracker')
        panel = wx.Panel(self)
        my_sizer = wx.BoxSizer(wx.VERTICAL)
        self.text_ctrl = wx.TextCtrl(panel)
        my_sizer.Add(self.text_ctrl, 0, wx.ALL | wx.EXPAND, 5)

        self.plotCanvas = CanvasPanel(panel)

        my_btn = wx.Button(panel, label='Plot Player Progress')
        my_btn.Bind(wx.EVT_BUTTON, self.on_press)

        my_sizer.Add(my_btn, 0, wx.ALL | wx.CENTER, 5)
        my_sizer.Add(self.plotCanvas, 1, wx.ALL | wx.EXPAND, 5)
        panel.SetSizer(my_sizer)
        self.Show()

    def on_press(self, event):
        idAsString = self.text_ctrl.GetValue()
        idAsInt = int(idAsString)
        if not idAsInt:
            print("Please enter ETF2L id")
        else:
            self.plotCanvas.plot_progress(idAsInt)


class CanvasPanel(wx.Panel):
    '''Class for the drawing of matplotlib plots'''

    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.figure = Figure()
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvas(self, -1, self.figure)

        # Navigation toolbar
        self.chart_toolbar = NavigationToolbar2Wx(self.canvas)
        self.tw, self.th = self.chart_toolbar.GetSizeTuple()
        self.fw, self.fh = self.canvas.GetSizeTuple()
        self.chart_toolbar.SetSize(wx.Size(self.fw, self.th))
        self.chart_toolbar.Realize()

        # Place on window
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.canvas, 1, wx.ALL | wx.EXPAND, 5)
        self.sizer.Add(self.chart_toolbar, 1, wx.ALL | wx.EXPAND, 5)
        self.SetSizer(self.sizer)
        self.Fit()

    def plot_progress(self, playerID):
        '''Split this into load_player() and plot_progress() later'''

        if playerID not in loadedPlayers.keys():
            status = "Downloading Player Data for ID: " + str(playerID)
            print(status)
            player = Player(playerID)
            loadedPlayers[playerID] = player

        else:
            status = "Player Info For " + loadedPlayers[playerID].playerName + " (" + str(
                playerID) + ") Already Downloaded"
            print(status)
            player = loadedPlayers[playerID]

        # Get the data from player object
        progressData = player.plot_div_progress(False)

        # Plot the graph
        self.ax.clear()
        self.ax.scatter(progressData['time'][progressData['impact'] > 0],
                        progressData['div'][progressData['impact'] > 0],
                        s=progressData['impact'][progressData['impact'] > 0], alpha=0.6, marker='o', c="Blue")
        self.ax.scatter(progressData['time'][progressData['impact'] == 0],
                        progressData['div'][progressData['impact'] == 0], s=50, alpha=0.6, marker='x', c="Red")
        self.ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%Y-%m-%d'))
        self.ax.set_title(player.playerName + " ETF2L Division Progress")
        self.ax.set_xlabel("Match Date")
        self.ax.set_ylabel("Tier")
        self.ax.set_ylim([6.2, -0.2])

        self.canvas.draw()


if __name__ == '__main__':
    app = wx.App()
    frame = MyFrame()
    frame.Fit()
    app.MainLoop()

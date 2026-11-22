import os
import wx
import pcbnew

SIZE = pcbnew.FromMM(0.4)
LAYER = pcbnew.Cmts_User


class TextAnchorsPlugin(pcbnew.ActionPlugin):
    def defaults(self):
        self.name = "Toggle Text Anchors"
        self.category = "Modify PCB"
        self.description = "Show or hide real-time anchor crosses for all visible PCB texts"
        self.show_toolbar_button = True
        self.icon_file_name = os.path.join(os.path.dirname(__file__), "icon.png")
        self._timer = None
        self._last_positions = None
        self._active = False

    def Run(self):
        if self._active:
            self._stop()
        else:
            self._start()

    def _start(self):
        self._active = True
        self._last_positions = None
        self._update_crosses()
        self._timer = wx.Timer()
        self._timer.Bind(wx.EVT_TIMER, self._on_timer)
        self._timer.Start(500)

    def _stop(self):
        self._active = False
        if self._timer is not None:
            self._timer.Stop()
            self._timer = None
        board = pcbnew.GetBoard()
        if board:
            self._clear_crosses(board)
            pcbnew.Refresh()

    def _on_timer(self, event):
        if not self._active:
            return
        try:
            self._update_crosses()
        except Exception:
            pass

    def _clear_crosses(self, board):
        for item in list(board.GetDrawings()):
            if item.GetLayer() == LAYER and isinstance(item, pcbnew.PCB_SHAPE):
                board.Remove(item)

    def _get_text_positions(self, board):
        positions = []

        for item in board.GetDrawings():
            if isinstance(item, pcbnew.PCB_TEXT) and item.IsVisible():
                pos = item.GetPosition()
                positions.append((pos.x, pos.y))

        for fp in board.GetFootprints():
            for item in fp.GraphicalItems():
                if isinstance(item, (pcbnew.PCB_TEXT, pcbnew.PCB_FIELD)) and item.IsVisible():
                    pos = item.GetPosition()
                    positions.append((pos.x, pos.y))
            for field in (fp.Reference(), fp.Value()):
                if field.IsVisible():
                    pos = field.GetPosition()
                    positions.append((pos.x, pos.y))

        return sorted(positions)

    def _update_crosses(self):
        board = pcbnew.GetBoard()
        if not board:
            return
        current_positions = self._get_text_positions(board)
        if current_positions == self._last_positions:
            return

        self._clear_crosses(board)
        for x, y in current_positions:
            for dx, dy in [(-SIZE, 0), (0, -SIZE)]:
                seg = pcbnew.PCB_SHAPE(board)
                seg.SetShape(pcbnew.SHAPE_T_SEGMENT)
                seg.SetLayer(LAYER)
                seg.SetWidth(pcbnew.FromMM(0.05))
                seg.SetStart(pcbnew.VECTOR2I(x + dx, y + dy))
                seg.SetEnd(pcbnew.VECTOR2I(x - dx, y - dy))
                board.Add(seg)

        self._last_positions = current_positions
        pcbnew.Refresh()

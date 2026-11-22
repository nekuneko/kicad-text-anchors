import os
import wx
import pcbnew

SIZE = pcbnew.FromMM(0.4)
LAYER = pcbnew.Cmts_User
CROSS_WIDTH = pcbnew.FromMM(0.05)


class TextAnchorsPlugin(pcbnew.ActionPlugin):
    def defaults(self):
        self.name = "Toggle Text Anchors"
        self.category = "Modify PCB"
        self.description = "Show or hide real-time anchor crosses for texts on visible layers"
        self.show_toolbar_button = True
        self.icon_file_name = os.path.join(os.path.dirname(__file__), "icon.png")
        self._timer = None
        self._last_positions = None
        self._pending_positions = None
        self._active = False

    def Run(self):
        if self._active:
            self._stop()
        else:
            self._start()

    def _start(self):
        board = pcbnew.GetBoard()
        if not board:
            return

        # Make User.Comments visible if it is currently hidden
        visible_layers = board.GetVisibleLayers()
        if not visible_layers.Contains(LAYER):
            visible_layers.AddLayer(LAYER)
            board.SetVisibleLayers(visible_layers)
            pcbnew.UpdateUserInterface()

        self._active = True
        self._last_positions = None
        self._pending_positions = None
        self._update_crosses(force=True)
        self._timer = wx.Timer()
        self._timer.Bind(wx.EVT_TIMER, self._on_timer)
        self._timer.Start(300)

    def _stop(self):
        self._active = False
        if self._timer is not None:
            self._timer.Stop()
            self._timer = None

        board = pcbnew.GetBoard()
        if board:
            self._clear_crosses(board)
            pcbnew.Refresh()

        self._last_positions = None
        self._pending_positions = None

    def _on_timer(self, event):
        if not self._active:
            return
        try:
            self._update_crosses(force=False)
        except Exception:
            pass

    def _clear_crosses(self, board):
        expected_len = SIZE * 2
        for item in list(board.GetDrawings()):
            if (
                isinstance(item, pcbnew.PCB_SHAPE)
                and item.GetLayer() == LAYER
                and item.GetShape() == pcbnew.SHAPE_T_SEGMENT
            ):
                start = item.GetStart()
                end = item.GetEnd()
                dx = abs(end.x - start.x)
                dy = abs(end.y - start.y)
                if (dx == expected_len and dy == 0) or (dy == expected_len and dx == 0):
                    board.Remove(item)

    def _is_item_shown(self, item, visible_layers):
        return item.IsVisible() and visible_layers.Contains(item.GetLayer())

    def _get_text_positions(self, board):
        positions = []
        visible_layers = board.GetVisibleLayers()

        for item in board.GetDrawings():
            if isinstance(item, pcbnew.PCB_TEXT) and self._is_item_shown(item, visible_layers):
                pos = item.GetPosition()
                positions.append((pos.x, pos.y))

        for fp in board.GetFootprints():
            for item in fp.GraphicalItems():
                if isinstance(item, (pcbnew.PCB_TEXT, pcbnew.PCB_FIELD)) and self._is_item_shown(item, visible_layers):
                    pos = item.GetPosition()
                    positions.append((pos.x, pos.y))
            for field in (fp.Reference(), fp.Value()):
                if self._is_item_shown(field, visible_layers):
                    pos = field.GetPosition()
                    positions.append((pos.x, pos.y))

        return sorted(positions)

    def _update_crosses(self, force=False):
        board = pcbnew.GetBoard()
        if not board:
            return
        current_positions = self._get_text_positions(board)

        if not force:
            # Wait for movement to settle across two ticks before redrawing
            if current_positions != self._pending_positions:
                self._pending_positions = current_positions
                return
            if current_positions == self._last_positions:
                return

        self._clear_crosses(board)
        for x, y in current_positions:
            for dx, dy in [(-SIZE, 0), (0, -SIZE)]:
                seg = pcbnew.PCB_SHAPE(board)
                seg.SetShape(pcbnew.SHAPE_T_SEGMENT)
                seg.SetLayer(LAYER)
                seg.SetWidth(CROSS_WIDTH)
                seg.SetStart(pcbnew.VECTOR2I(x + dx, y + dy))
                seg.SetEnd(pcbnew.VECTOR2I(x - dx, y - dy))
                board.Add(seg)

        self._last_positions = current_positions
        self._pending_positions = current_positions
        pcbnew.Refresh()

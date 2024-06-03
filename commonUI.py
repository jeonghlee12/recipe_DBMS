from PyQt5.QtWidgets import QTabBar, QStyle, QStylePainter, QStyleOptionTab, QWidget, QTabWidget, QTableView, QVBoxLayout
from PyQt5.QtCore import QSize, QRect, QPoint
from PyQt5.QtGui import QPaintEvent
from PyQt5.QtSql import QSqlQueryModel

class recipeSearch(QWidget):
    def __init__(self, parent = None):
        super().__init__(parent)
        
        self.model = QSqlQueryModel()
        self.model.setQuery("SELECT * FROM Recipe.users;")

        self.view = QTableView()
        self.view.setModel(self.model)
        self.view.resizeColumnsToContents()

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.view)
        self.setLayout(self.layout)




class VTabBar(QTabBar):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        return

    def tabSizeHint(self, index:int) -> QSize:
        s = super().tabSizeHint(index)
        s.transpose()
        return s

    def paintEvent(self, event:QPaintEvent) -> None:
        painter:QStylePainter = QStylePainter(self)
        opt:QStyleOptionTab = QStyleOptionTab()
        for i in range(self.count()):
            self.initStyleOption(opt, i)
            painter.drawControl(QStyle.CE_TabBarTabShape, opt)
            painter.save()

            s:QSize = opt.rect.size()
            s.transpose()
            r:QRect = QRect(QPoint(), s)
            r.moveCenter(opt.rect.center())
            opt.rect = r

            c:QPoint = self.tabRect(i).center()
            painter.translate(c)
            painter.rotate(90)
            painter.translate(-c)
            painter.drawControl(QStyle.CE_TabBarTabLabel, opt)
            painter.restore()
        return

class VTabWidget(QTabWidget):
    def __init__(self, parent:QWidget=None) -> None:
        super().__init__(parent)
        self.setTabBar(VTabBar())
        self.setTabPosition(QTabWidget.West)
        return


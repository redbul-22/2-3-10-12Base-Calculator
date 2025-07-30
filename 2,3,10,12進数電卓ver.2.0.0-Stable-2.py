import sys
from functools import partial
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPalette, QColor
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QMessageBox, QStyleFactory, QSizePolicy
)


class BaseCalculator(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Base-Cl Calculator")
        self.setFixedSize(360, 740)  # 高さを少し増加

        self.reset_state()
        self.current_theme = "dark"    # dark / light
        self.current_lang = "EN"       # EN / JP
        self.current_base = 2          # 2, 3, 10, 12

        self._init_ui()
        self.apply_theme()
        self.apply_language()

    def reset_state(self, keep_result=False):
        if keep_result:
            # preserve the result as operand1, clear everything else
            self.operand1 = self.last_result
        else:
            self.operand1 = ""
        self.operand2 = ""
        self.operator = None
        self.editing_second = False

    def _init_ui(self):
        vbox = QVBoxLayout(self)
        vbox.setContentsMargins(12, 12, 12, 12)
        vbox.setSpacing(8)

        # header: theme & lang toggles
        header = QHBoxLayout()
        header.setSpacing(12)
        self.btn_theme = QPushButton("🌙")
        self.btn_lang = QPushButton("EN")
        for btn in (self.btn_theme, self.btn_lang):
            btn.setFont(QFont("Helvetica Neue", 16))
            btn.setFixedSize(48, 48)
        self.btn_theme.clicked.connect(self.toggle_theme)
        self.btn_lang.clicked.connect(self.toggle_language)
        header.addWidget(self.btn_theme)
        header.addWidget(self.btn_lang)
        header.addStretch()
        vbox.addLayout(header)

        # base-switcher buttons
        self.base_buttons = {}
        base_layout = QHBoxLayout()
        base_layout.setSpacing(8)
        for b in (2, 3, 10, 12):
            btn = QPushButton(str(b))
            btn.setFont(QFont("Helvetica Neue", 14))
            btn.setFixedSize(60, 48)
            btn.clicked.connect(partial(self.set_base, b))
            self.base_buttons[b] = btn
            base_layout.addWidget(btn)
        base_layout.addStretch()
        vbox.addLayout(base_layout)

        # display
        self.display = QLabel("0")
        self.display.setFont(QFont("Helvetica Neue", 40, QFont.Bold))
        self.display.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.display.setFixedHeight(100)
        self.display.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        vbox.addWidget(self.display)

        # 10進数変換表示バー
        self.decimal_bar = QLabel("")
        self.decimal_bar.setFont(QFont("Helvetica Neue", 16))
        self.decimal_bar.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.decimal_bar.setFixedHeight(40)
        self.decimal_bar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        vbox.addWidget(self.decimal_bar)

        # buttons grid: logic, operators, digits, clear/back/equal
        grid = QGridLayout()
        grid.setSpacing(8)  # 横間の隙間
        grid.setVerticalSpacing(12)  # 縦間の隙間を適度に増加（8→12）
        
        keys = [
            ("and",      "AND"),  ("or",       "OR"),
            ("xor",      "XOR"),  ("back",     "⌫"),
            ("add",      "+"),    ("subtract", "-"),
            ("multiply", "×"),    ("divide",   "÷"),
            ("7",        "7"),    ("8",        "8"),
            ("9",        "9"),    ("clear",    "C"),
            ("4",        "4"),    ("5",        "5"),
            ("6",        "6"),    ("equal",    "="),
            ("1",        "1"),    ("2",        "2"),
            ("3",        "3"),    ("A",        "A"),
            ("0",        "0"),    ("B",        "B"),
        ]
        self.buttons = {}
        for idx, (key, _) in enumerate(keys):
            btn = QPushButton()
            btn.setFont(QFont("Helvetica Neue", 24))
            btn.setFixedSize(72, 72)
            btn.clicked.connect(partial(self.on_button, key))
            # classify button types for styling
            if key.isdigit() or key in ("A", "B"):
                btn.setProperty("type", "digit")
            elif key in ("clear", "back"):
                btn.setProperty("type", "func")
            else:
                btn.setProperty("type", "op")
            
            # 配置を調整：6行4列のレイアウト
            if idx < 16:  # 最初の4行（16個）
                r, c = divmod(idx, 4)
            else:  # 最後の行
                if idx == 16:  # "1"
                    r, c = 4, 0  # 左端
                elif idx == 17:  # "2" 
                    r, c = 4, 1  # 中央左
                elif idx == 18:  # "3"
                    r, c = 4, 2  # 中央右
                elif idx == 19:  # "A"
                    r, c = 4, 3  # 右端
                elif idx == 20:  # "0"
                    r, c = 5, 0  # 新しい行の左端
                elif idx == 21:  # "B"
                    r, c = 5, 1  # 新しい行の中央左
            
            grid.addWidget(btn, r, c)
            self.buttons[key] = btn

        vbox.addLayout(grid)

        # state for chaining calculation
        self.last_result = ""

    # theme
    def toggle_theme(self):
        self.current_theme = "light" if self.current_theme == "dark" else "dark"
        self.apply_theme()

    def apply_theme(self):
        QApplication.setStyle(QStyleFactory.create("Fusion"))
        pal = QPalette()

        if self.current_theme == "dark":
            bg_color = "#121212"
            text_color = "white"
            digit_bg = "#2D2D2D"
            func_bg = "#374955"
            eq_bg = "#004C69"
            clr_bg = "#484264"
            decimal_bg = "#1A1A1A"
            decimal_text = "#B0B0B0"
            disabled_bg = "#1A1A1A"
            self.btn_theme.setText("☀")
        else:
            bg_color = "#FFFFFF"
            text_color = "black"
            digit_bg = "#E0E0E0"
            func_bg = "#D2E5F4"
            eq_bg = "#C2E8FF"
            clr_bg = "#E5DEFF"
            decimal_bg = "#F5F5F5"
            decimal_text = "#666666"
            disabled_bg = "#F0F0F0"
            self.btn_theme.setText("🌙")

        pal.setColor(QPalette.Window, QColor(bg_color))
        pal.setColor(QPalette.WindowText, QColor(text_color))
        pal.setColor(QPalette.Base, QColor(bg_color))
        pal.setColor(QPalette.Text, QColor(text_color))
        QApplication.setPalette(pal)

        # display styling
        disp_bg = "#1F1F1F" if self.current_theme == "dark" else "#FFFFFF"
        self.display.setStyleSheet(f"""
            QLabel {{
                background: {disp_bg};
                color: {text_color};
                border-radius: 12px;
                padding-right: 16px;
            }}
        """)

        # decimal bar styling
        self.decimal_bar.setStyleSheet(f"""
            QLabel {{
                background: {decimal_bg};
                color: {decimal_text};
                border-radius: 8px;
                padding-right: 16px;
                padding-left: 16px;
                border: 1px solid {decimal_text}40;
            }}
        """)

        # grid buttons styling
        for key, btn in self.buttons.items():
            # ボタンが現在の基数で有効かどうかチェック
            is_enabled = self.is_button_enabled(key)
            
            if key == "equal":
                bg = eq_bg
            elif key == "clear":
                bg = clr_bg
            elif not is_enabled:
                bg = disabled_bg
            elif btn.property("type") == "digit":
                bg = digit_bg
            else:
                bg = func_bg

            btn.setEnabled(is_enabled)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {bg};
                    color: {text_color if is_enabled else decimal_text};
                    border-radius: 36px;
                }}
                QPushButton:pressed {{
                    background-color: {bg}CC;
                }}
            """)

        # base-switcher buttons styling
        for b, btn in self.base_buttons.items():
            # highlight current base with eq_bg
            bg = eq_bg if b == self.current_base else func_bg
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {bg};
                    color: {text_color};
                    border-radius: 12px;
                }}
                QPushButton:pressed {{
                    background-color: {bg}CC;
                }}
            """)

    def is_button_enabled(self, key):
        """現在の基数でボタンが有効かどうかを判定"""
        if key.isdigit():
            return int(key) < self.current_base
        elif key == "A":
            return self.current_base > 10
        elif key == "B":
            return self.current_base > 11
        else:
            return True

    # language
    def toggle_language(self):
        self.current_lang = "JP" if self.current_lang == "EN" else "EN"
        self.apply_language()

    def apply_language(self):
        self.btn_lang.setText(self.current_lang)
        labels = {
            "EN": {
                "and": "AND", "or": "OR",   "xor": "XOR",   "clear": "C",
                "add": "+",   "subtract": "-", "multiply": "×", "divide": "÷",
                "0": "0",     "1": "1",      "2": "2",       "3": "3",
                "4": "4",     "5": "5",      "6": "6",       "7": "7",
                "8": "8",     "9": "9",      "A": "A",       "B": "B",
                "equal": "=", "back": "⌫",
            },
            "JP": {
                "and": "AND", "or": "OR",   "xor": "XOR",   "clear": "C",
                "add": "＋",   "subtract": "－", "multiply": "×", "divide": "÷",
                "0": "0",     "1": "1",      "2": "2",       "3": "3",
                "4": "4",     "5": "5",      "6": "6",       "7": "7",
                "8": "8",     "9": "9",      "A": "A",       "B": "B",
                "equal": "＝", "back": "⌫",
            },
        }
        for k, btn in self.buttons.items():
            btn.setText(labels[self.current_lang][k])

    # base switching
    def set_base(self, base):
        if self.current_base == base:
            return
        self.current_base = base
        self.reset_state()
        self.update_display()
        self.apply_theme()
        self.last_result = ""

    def update_decimal_bar(self, value_str=""):
        """10進数変換バーを更新"""
        if not value_str:
            self.decimal_bar.setText("")
            return
        
        try:
            # 負の数に対応
            if value_str.startswith("-"):
                decimal_value = -int(value_str[1:], self.current_base)
            else:
                decimal_value = int(value_str, self.current_base)
            
            if self.current_base == 10:
                # 既に10進数の場合は他の基数での表現を表示
                base_labels = {2: "BIN", 3: "BASE3", 12: "BASE12"}
                other_bases = [b for b in [2, 3, 12] if b != 10]
                conversions = []
                for base in other_bases:
                    sign = "-" if decimal_value < 0 else ""
                    converted = self.to_base(abs(decimal_value), base)
                    conversions.append(f"{base_labels[base]}: {sign}{converted}")
                
                text = " | ".join(conversions)
            else:
                # 他の基数の場合は10進数を表示
                text = f"DEC: {decimal_value}"
            
            self.decimal_bar.setText(text)
            
        except ValueError:
            self.decimal_bar.setText("")

    def is_valid_digit(self, key):
        """現在の基数で有効な桁かどうかを判定"""
        if key.isdigit():
            return int(key) < self.current_base
        elif key == "A":
            return self.current_base > 10
        elif key == "B":
            return self.current_base > 11
        return False

    # input / calc
    def on_button(self, key):
        # clear
        if key == "clear":
            self.reset_state()
            self.display.setText("0")
            self.decimal_bar.setText("")
            self.last_result = ""
            return

        # backspace
        if key == "back":
            tgt = "operand2" if self.editing_second else "operand1"
            s = getattr(self, tgt)[:-1]
            setattr(self, tgt, s)
            self.update_display()
            return

        # calculate
        if key == "equal":
            self.calculate()
            return

        # operator
        if key in ("add", "subtract", "multiply", "divide",
                   "and", "or", "xor"):
            if not self.operand1:
                # if previous calculation result is available, use that
                if self.last_result:
                    self.operand1 = self.last_result
                else:
                    return
            # chaining: if result just shown, allow new operator for continued input
            if not self.editing_second and self.operator is None and self.last_result:
                self.operand1 = self.last_result
            self.operator = key
            self.editing_second = True
            self.operand2 = ""
            self.update_display()
            return

        # digit (including A and B)
        if key.isdigit() or key in ("A", "B"):
            # 現在の基数で有効な桁かチェック
            if not self.is_valid_digit(key):
                return
            
            # chaining: if previous result just shown and inputting digit,
            # start new calculation
            if self.last_result and not self.editing_second and not self.operator and not self.operand1:
                self.reset_state()
                self.display.setText("0")
                self.decimal_bar.setText("")
            if not self.editing_second:
                self.operand1 += key
            else:
                self.operand2 += key
            self.update_display()

    def update_display(self):
        if not self.operator:
            txt = self.operand1 or "0"
            # 数値入力中は10進数変換を表示
            if self.operand1:
                self.update_decimal_bar(self.operand1)
            else:
                self.decimal_bar.setText("")
        else:
            sym = self.op_symbol()
            txt = f"{self.operand1} {sym} {self.operand2 or ''}"
            # 演算子入力中は第二オペランドの10進数変換を表示
            if self.operand2:
                self.update_decimal_bar(self.operand2)
            else:
                self.decimal_bar.setText("")
        self.display.setText(txt)

    def op_symbol(self):
        return {
            "add": "+", "subtract": "-", "multiply": "×",
            "divide": "÷", "and": "AND", "or": "OR", "xor": "XOR"
        }[self.operator]

    def to_base(self, num: int, base: int) -> str:
        """Convert non-negative integer to string in given base."""
        if num == 0:
            return "0"
        digits = []
        while num > 0:
            d = num % base
            if d < 10:
                digits.append(str(d))
            else:
                # for base > 10, use A, B...
                digits.append(chr(ord("A") + d - 10))
            num //= base
        return "".join(reversed(digits))

    def calculate(self):
        if not (self.operand1 and self.operator and self.operand2):
            return
        try:
            x = int(self.operand1, self.current_base)
            y = int(self.operand2, self.current_base)

            if self.operator == "add":
                r = x + y
            elif self.operator == "subtract":
                r = x - y
            elif self.operator == "multiply":
                r = x * y
            elif self.operator == "divide":
                if y == 0:
                    raise ZeroDivisionError
                r = x // y
            elif self.operator == "and":
                r = x & y
            elif self.operator == "or":
                r = x | y
            elif self.operator == "xor":
                r = x ^ y

            sign = "-" if r < 0 else ""
            res = self.to_base(abs(r), self.current_base)
            result_str = sign + res
            self.display.setText(result_str)
            
            # 計算結果の10進数変換を表示
            self.update_decimal_bar(result_str)
            
            self.last_result = result_str
            self.reset_state(keep_result=True)

        except ZeroDivisionError:
            msg = {
                "EN": "Cannot divide by zero.",
                "JP": "ゼロで割ることはできません。"
            }[self.current_lang]
            QMessageBox.critical(self, "Error", msg, QMessageBox.Close)
            self.last_result = ""
            self.reset_state()
            self.decimal_bar.setText("")

        except ValueError:
            msg = {
                "EN": "Invalid input.",
                "JP": "無効な入力です。"
            }[self.current_lang]
            QMessageBox.critical(self, "Error", msg, QMessageBox.Close)
            self.last_result = ""
            self.reset_state()
            self.decimal_bar.setText("")

    def keyPressEvent(self, event):
        # Optional: allow keyboard input for quick testing
        keymap = {
            Qt.Key_0: "0", Qt.Key_1: "1", Qt.Key_2: "2", Qt.Key_3: "3",
            Qt.Key_4: "4", Qt.Key_5: "5", Qt.Key_6: "6", Qt.Key_7: "7",
            Qt.Key_8: "8", Qt.Key_9: "9", Qt.Key_A: "A", Qt.Key_B: "B",
            Qt.Key_Plus: "add", Qt.Key_Minus: "subtract",
            Qt.Key_Asterisk: "multiply", Qt.Key_Slash: "divide",
            Qt.Key_Equal: "equal", Qt.Key_Return: "equal", Qt.Key_Enter: "equal",
            Qt.Key_Backspace: "back", Qt.Key_Delete: "clear",
        }
        if event.key() in keymap:
            self.on_button(keymap[event.key()])
        else:
            super().keyPressEvent(event)


def main():
    app = QApplication(sys.argv)
    app.setFont(QFont("Helvetica Neue", 14))
    win = BaseCalculator()
    win.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
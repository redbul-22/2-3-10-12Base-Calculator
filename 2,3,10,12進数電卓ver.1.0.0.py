import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup

kivy.require('2.0.0')


class BaseCalculatorApp(App):
    def build(self):
        # 対応する基数マップ
        self.base_map = {
            2: 2,
            3: 3,
            4: 10,
            5: 12
        }
        self.mode_text = {
            2: "Binary (base 2)",
            3: "Ternary (base 3)",
            4: "Decimal (base 10)",
            5: "Duodecimal (base 12)"
        }

        # モード一覧とインデックス
        self.modes = [2, 3, 4, 5]
        self.mode_index = 0
        self.mode = self.modes[self.mode_index]  # 初期モード: 2進数

        # レイアウト準備
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # 入力欄
        self.entry1 = TextInput(
            hint_text=self.mode_text[self.mode],
            multiline=False, font_size=24
        )
        self.entry2 = TextInput(
            hint_text=self.mode_text[self.mode],
            multiline=False, font_size=24
        )

        # モード表示
        self.mode_label = Label(
            text=f"Mode: {self.mode_text[self.mode]}",
            font_size=20, size_hint=(1, 0.2)
        )

        # 結果表示
        self.result_label = Label(
            text="Result: ",
            font_size=28, size_hint=(1, 0.4)
        )

        # モード切替ボタン
        mode_btn = Button(text="Change Mode", size_hint=(None, 0.4), width=150)
        mode_btn.bind(on_press=self.toggle_mode)

        # クリアボタン
        clear_btn = Button(text="Clear", size_hint=(None, 0.4), width=150)
        clear_btn.bind(on_press=self.clear_fields)

        # モード／クリアボタンを横並びに配置
        btn_layout = BoxLayout(size_hint=(1, 0.4), spacing=10)
        btn_layout.add_widget(mode_btn)
        btn_layout.add_widget(clear_btn)

        # 演算ボタン群
        ops_layout = BoxLayout(size_hint=(1, 0.6), spacing=5)
        buttons = [
            ('+', 'add'),
            ('−', 'subtract'),
            ('×', 'multiply'),
            ('÷', 'divide'),
            ('AND', 'and'),
            ('OR', 'or'),
            ('XOR', 'xor')
        ]
        for label, op in buttons:
            btn = Button(text=label, font_size=20)
            btn.bind(on_press=lambda inst, o=op: self.calculate(o))
            ops_layout.add_widget(btn)

        # ウィジェット配置
        self.layout.add_widget(self.entry1)
        self.layout.add_widget(self.entry2)
        self.layout.add_widget(self.mode_label)
        self.layout.add_widget(btn_layout)
        self.layout.add_widget(ops_layout)
        self.layout.add_widget(self.result_label)

        return self.layout

    def toggle_mode(self, *args):
        # 2→3→4→5→2 の循環
        self.mode_index = (self.mode_index + 1) % len(self.modes)
        self.mode = self.modes[self.mode_index]

        base_name = self.mode_text[self.mode]
        self.mode_label.text = f"Mode: {base_name}"
        self.entry1.hint_text = base_name
        self.entry2.hint_text = base_name
        self.result_label.text = "Result: "

    def clear_fields(self, *args):
        """入力欄と結果表示をクリア"""
        self.entry1.text = ""
        self.entry2.text = ""
        self.result_label.text = "Result: "

    def validate_input(self, s):
        """各モードの許可文字チェック"""
        s = s.strip().upper()
        if not s:
            return False

        allowed_chars = {
            2: '01',
            3: '012',
            4: '0123456789',
            5: '0123456789AB'
        }
        return all(c in allowed_chars[self.mode] for c in s)

    def convert_to_decimal(self, s):
        """モードに応じて10進数に変換"""
        if not self.validate_input(s):
            raise ValueError("Invalid input for current mode.")

        base = self.base_map[self.mode]
        return int(s.strip().upper(), base)

    def convert_from_decimal(self, n):
        """10進数をモードの基数文字列に変換"""
        sign = '-' if n < 0 else ''
        n = abs(n)
        base = self.base_map[self.mode]

        if base == 2:
            return sign + bin(n)[2:]
        if base == 3:
            if n == 0:
                return '0'
            digits = []
            while n:
                digits.append(str(n % 3))
                n //= 3
            return sign + ''.join(reversed(digits))
        if base == 10:
            return sign + str(n)
        # base == 12
        if n == 0:
            return '0'
        digits = []
        while n:
            r = n % 12
            if r < 10:
                digits.append(str(r))
            else:
                digits.append(chr(ord('A') + r - 10))
            n //= 12
        return sign + ''.join(reversed(digits))

    def calculate(self, operation):
        try:
            a = self.convert_to_decimal(self.entry1.text)
            b = self.convert_to_decimal(self.entry2.text)

            if operation == 'add':
                res = a + b
            elif operation == 'subtract':
                res = a - b
            elif operation == 'multiply':
                res = a * b
            elif operation == 'divide':
                if b == 0:
                    raise ZeroDivisionError("Division by zero.")
                res = a // b
            elif operation == 'and':
                res = a & b
            elif operation == 'or':
                res = a | b
            elif operation == 'xor':
                res = a ^ b
            else:
                raise ValueError("Unknown operation.")

            out = self.convert_from_decimal(res)
            self.result_label.text = f"Result: {out}"

        except ZeroDivisionError as e:
            self.show_error(str(e))
        except ValueError as e:
            self.show_error(str(e))

    def show_error(self, msg):
        popup = Popup(
            title='Error',
            content=Label(text=msg),
            size_hint=(0.6, 0.4)
        )
        popup.open()


if __name__ == '__main__':
    BaseCalculatorApp().run()
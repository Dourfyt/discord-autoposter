from PyQt5 import QtWidgets, QtCore
from form import Ui_MainWindow
from sender import send
from slash_sender import slash_send
import sys
import json
import os

class Worker(QtCore.QThread):
    logsbeep = QtCore.pyqtSignal(str)

    def __init__(self, token, channels, delay, image):
        super(Worker, self).__init__()
        self.token = token
        self.channels = channels
        self.delay = delay
        self.image = image
        self._running = True  # Просто флаг без QEvent

    @property
    def running(self):
        return self._running

    @running.setter
    def running(self, value):
        self._running = value

    def run(self):
        while self.running:
            tokens = self.token.split()
            for token in tokens:
                if not self.running:
                    break
                for channel_id, message in self.channels.items():
                    if not self.running:
                        break
                    try:
                        send(self, token, channel_id, message, self.delay, self.image)
                        self.msleep(int(self.delay) * 1000)
                    except Exception as e:
                        self.logsbeep.emit(f"Ошибка: {str(e)}")
                        break

    def stop(self):
        self.running = False
        self.wait()

class SlashWorker(QtCore.QThread):
    logsbeep = QtCore.pyqtSignal(str)

    def __init__(self, token, guild_id, application_id, version_id, command_id, command, delay, channels, image):
        super(SlashWorker, self).__init__()
        self.token = token
        self.guild_id = guild_id
        self.application_id = application_id
        self.version_id = version_id
        self.command_id = command_id
        self.command = command
        self.delay = delay
        self.channels = channels
        self.image = image
        self._running = True

    @property
    def running(self):
        return self._running

    @running.setter
    def running(self, value):
        self._running = value

    def run(self):
        while self.running:
            tokens = self.token.split()
            for token in tokens:
                if not self.running:
                    break
                for channel_id, message in self.channels.items():
                    if not self.running:
                        break
                    try:
                        slash_send(self, token, self.guild_id, self.application_id,
                                 self.version_id, self.command_id, self.command,
                                 self.delay, self.channels, self.image)
                        self.msleep(int(self.delay) * 1000)
                    except Exception as e:
                        self.logsbeep.emit(f"Ошибка: {str(e)}")
                        break

    def stop(self):
        self.running = False
        self.wait()

class formwindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(formwindow, self).__init__()
        self.mainui = Ui_MainWindow()
        self.mainui.setupUi(self)
        self.mainui.start_Button.installEventFilter(self)
        self.mainui.start_Button.clicked.connect(self.start_sending)
        self.mainui.add_channel_button.clicked.connect(self.add_channel)
        self.mainui.remove_channel_button.clicked.connect(self.remove_channel)
        self.mainui.edit_channel_button.clicked.connect(self.edit_channel)
        self.mainui.stop_all_button.clicked.connect(self.stop_all_posters)
        self.workers = []
        self.load_data()

    def eventFilter(self, source, event):
        if event.type() == QtCore.QEvent.MouseButtonPress and source is self.mainui.start_Button:
            self.mainui.start_Button.setStyleSheet("""background: #23272A;
                                                    border-radius: 15px;
                                                    font-family: Sitara;
                                                    font-style: normal;
                                                    font-weight: normal;
                                                    font-size: 36px;
                                                    line-height: 58px;
                                                    text-align: center;
                                                    color: #FFFFFF;""")
            return False
        if event.type() == QtCore.QEvent.MouseButtonRelease and source is self.mainui.start_Button:
            self.mainui.start_Button.setStyleSheet("""background: #7289DA;
                                                    border-radius: 15px;
                                                    font-family: Sitara;
                                                    font-style: normal;
                                                    font-weight: normal;
                                                    font-size: 36px;
                                                    line-height: 58px;
                                                    text-align: center;
                                                    color: #FFFFFF;""")
            return False
        if event.type() == QtCore.QEvent.MouseButtonPress and source is self.mainui.slash_Button:
            self.mainui.slash_Button.setStyleSheet("""background-image: url(img/slash_active.png);
                                                    border: 0;""")
            return False
        if event.type() == QtCore.QEvent.MouseButtonRelease and source is self.mainui.slash_Button:
            self.mainui.slash_Button.setStyleSheet("""background-image: url(img/slash.png);
                                                    border: 0;""")
            return False
        if event.type() == QtCore.QEvent.MouseButtonPress and source is self.mainui.start_slash_Button:
            self.mainui.start_slash_Button.setStyleSheet("""background: #23272A;
                                                            border-radius: 15px;
                                                            font-family: Sitara;
                                                            font-style: normal;
                                                            font-weight: normal;
                                                            font-size: 36px;
                                                            line-height: 58px;
                                                            text-align: center;
                                                            color: #FFFFFF;""")
            return False
        if event.type() == QtCore.QEvent.MouseButtonRelease and source is self.mainui.start_slash_Button:
            self.mainui.start_slash_Button.setStyleSheet("""background: #7289DA;
                                                            border-radius: 15px;
                                                            font-family: Sitara;
                                                            font-style: normal;
                                                            font-weight: normal;
                                                            font-size: 36px;
                                                            line-height: 58px;
                                                            text-align: center;
                                                            color: #FFFFFF;""")
            return False
        if event.type() == QtCore.QEvent.MouseButtonPress and source is self.mainui.stop_all_button:
            self.mainui.stop_all_button.setStyleSheet("""
                background: #CC0000;
                border-radius: 15px;
                font-family: Sitara;
                font-style: normal;
                font-weight: normal;
                font-size: 18px;
                line-height: 29px;
                text-align: center;
                color: #FFFFFF;
            """)
            return False
        if event.type() == QtCore.QEvent.MouseButtonRelease and source is self.mainui.stop_all_button:
            self.mainui.stop_all_button.setStyleSheet("""
                background: #FF0000;
                border-radius: 15px;
                font-family: Sitara;
                font-style: normal;
                font-weight: normal;
                font-size: 18px;
                line-height: 29px;
                text-align: center;
                color: #FFFFFF;
            """)
            return False
        return super(formwindow, self).eventFilter(source, event)

    def load_data(self):
        if not os.path.exists('data.json'):
            with open('data.json', 'w') as outfile:
                json.dump({}, outfile)
        try:
            with open('data.json') as json_file:
                data = json.load(json_file)
                self.mainui.token.setPlainText(data.get('token', ''))
                self.mainui.delay.setText(data.get('delay', ''))
                self.mainui.image.setText(data.get('image', ''))
                channels = data.get('channels', {})
                for channel_id, message in channels.items():
                    item = QtWidgets.QListWidgetItem(f"{channel_id}: {message}")
                    item.setData(QtCore.Qt.UserRole, {'channel_id': channel_id, 'message': message})
                    self.mainui.channels_list.addItem(item)
        except Exception as e:
            print(e)
            pass

    def save_data(self, token, delay, image, channels):
        data = {
            'token': token,
            'delay': delay,
            'image': image,
            'channels': channels
        }
        with open('data.json', 'w') as outfile:
            json.dump(data, outfile)

    def add_channel(self):
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("Add Channel")
        dialog.setFixedSize(600, 250)
        dialog.setStyleSheet("""background: #424549;""")

        layout = QtWidgets.QVBoxLayout(dialog)

        channel_id_label = QtWidgets.QLabel("Channel ID:")
        channel_id_label.setStyleSheet("""font-family: Sitara;
                                        font-style: normal;
                                        font-weight: normal;
                                        font-size: 18px;
                                        line-height: 29px;
                                        color: #FFFFFF;""")
        channel_id_input = QtWidgets.QLineEdit()
        channel_id_input.setStyleSheet("""background: #C4C4C4;
                                        border-radius: 10px;
                                        font-family: Sitara;
                                        font-style: normal;
                                        font-weight: normal;
                                        font-size: 18px;
                                        line-height: 29px;
                                        color: #000000;""")
        channel_id_input.setPlaceholderText("Enter channel id")

        message_label = QtWidgets.QLabel("Message:")
        message_label.setStyleSheet("""font-family: Sitara;
                                        font-style: normal;
                                        font-weight: normal;
                                        font-size: 18px;
                                        line-height: 29px;
                                        color: #FFFFFF;""")
        message_input = QtWidgets.QTextEdit()
        message_input.setStyleSheet("""background: #C4C4C4;
                                        border-radius: 10px;
                                        font-family: Sitara;
                                        font-style: normal;
                                        font-weight: normal;
                                        font-size: 18px;
                                        line-height: 29px;
                                        color: #000000;""")
        message_input.setPlaceholderText("Enter message")

        add_button = QtWidgets.QPushButton("Add")
        add_button.setStyleSheet("""background: #7289DA;
                                    border-radius: 15px;
                                    font-family: Sitara;
                                    font-style: normal;
                                    font-weight: normal;
                                    font-size: 18px;
                                    line-height: 29px;
                                    text-align: center;
                                    color: #FFFFFF;""")
        add_button.clicked.connect(lambda: self.add_channel_to_list(channel_id_input.text(), message_input.toPlainText(), dialog))

        layout.addWidget(channel_id_label)
        layout.addWidget(channel_id_input)
        layout.addWidget(message_label)
        layout.addWidget(message_input)
        layout.addWidget(add_button)

        dialog.exec_()

    def add_channel_to_list(self, channel_id, message, dialog):
        if channel_id and message:
            item = QtWidgets.QListWidgetItem(f"{channel_id}: {message}")
            item.setData(QtCore.Qt.UserRole, {'channel_id': channel_id, 'message': message})
            self.mainui.channels_list.addItem(item)
            dialog.accept()
        else:
            QtWidgets.QMessageBox.warning(self, "Warning", "Channel ID and Message must be filled.")

    def edit_channel(self):
        selected_item = self.mainui.channels_list.currentItem()
        if selected_item:
            data = selected_item.data(QtCore.Qt.UserRole)
            dialog = QtWidgets.QDialog(self)
            dialog.setWindowTitle("Edit Channel")
            dialog.setFixedSize(600, 250)
            dialog.setStyleSheet("""background: #424549;""")

            layout = QtWidgets.QVBoxLayout(dialog)

            channel_id_label = QtWidgets.QLabel("Channel ID:")
            channel_id_label.setStyleSheet("""font-family: Sitara;
                                            font-style: normal;
                                            font-weight: normal;
                                            font-size: 18px;
                                            line-height: 29px;
                                            color: #FFFFFF;""")
            channel_id_input = QtWidgets.QLineEdit()
            channel_id_input.setStyleSheet("""background: #C4C4C4;
                                            border-radius: 10px;
                                            font-family: Sitara;
                                            font-style: normal;
                                            font-weight: normal;
                                            font-size: 18px;
                                            line-height: 29px;
                                            color: #000000;""")
            channel_id_input.setPlaceholderText("Enter channel id")
            channel_id_input.setText(data['channel_id'])

            message_label = QtWidgets.QLabel("Message:")
            message_label.setStyleSheet("""font-family: Sitara;
                                            font-style: normal;
                                            font-weight: normal;
                                            font-size: 18px;
                                            line-height: 29px;
                                            color: #FFFFFF;""")
            message_input = QtWidgets.QTextEdit()
            message_input.setStyleSheet("""background: #C4C4C4;
                                            border-radius: 10px;
                                            font-family: Sitara;
                                            font-style: normal;
                                            font-weight: normal;
                                            font-size: 18px;
                                            line-height: 29px;
                                            color: #000000;""")
            message_input.setPlaceholderText("Enter message")
            message_input.setPlainText(data['message'])

            edit_button = QtWidgets.QPushButton("Edit")
            edit_button.setStyleSheet("""background: #7289DA;
                                        border-radius: 15px;
                                        font-family: Sitara;
                                        font-style: normal;
                                        font-weight: normal;
                                        font-size: 18px;
                                        line-height: 29px;
                                        text-align: center;
                                        color: #FFFFFF;""")
            edit_button.clicked.connect(lambda: self.edit_channel_in_list(channel_id_input.text(), message_input.toPlainText(), dialog, selected_item))

            layout.addWidget(channel_id_label)
            layout.addWidget(channel_id_input)
            layout.addWidget(message_label)
            layout.addWidget(message_input)
            layout.addWidget(edit_button)

            dialog.exec_()
        else:
            QtWidgets.QMessageBox.warning(self, "Warning", "Select a channel to edit.")

    def edit_channel_in_list(self, channel_id, message, dialog, selected_item):
        if channel_id and message:
            selected_item.setText(f"{channel_id}: {message}")
            selected_item.setData(QtCore.Qt.UserRole, {'channel_id': channel_id, 'message': message})
            dialog.accept()
        else:
            QtWidgets.QMessageBox.warning(self, "Warning", "Channel ID and Message must be filled.")

    def remove_channel(self):
        selected_items = self.mainui.channels_list.selectedItems()
        for item in selected_items:
            self.mainui.channels_list.takeItem(self.mainui.channels_list.row(item))

    def start_sending(self):
        def red_color(element):
            element.setStyleSheet("""background: #C4C4C4;
                                    border: 2px solid #BC2E3F;
                                    border-radius: 10px;
                                    font-family: Sitara;
                                    font-style: normal;
                                    font-weight: normal;
                                    font-size: 18px;
                                    line-height: 29px;
                                    color: #000000;""")

        def logs_update(value: str):
            self.mainui.logs_text.append(value)

        token = self.mainui.token.toPlainText()
        delay = self.mainui.delay.text()
        image = self.mainui.image.text()
        channels = {}
        for i in range(self.mainui.channels_list.count()):
            item = self.mainui.channels_list.item(i)
            data = item.data(QtCore.Qt.UserRole)
            channels[data['channel_id']] = data['message']

        if token == '':
            red_color(self.mainui.token)
        elif not channels:
            red_color(self.mainui.channels_list)
        elif delay == '':
            red_color(self.mainui.delay)
        else:
            self.save_data(token, delay, image, channels)
            self.mainui.logs_text.append('Program started! Don\'t close!')
            self.worker = Worker(token, channels, delay, image)
            self.worker.logsbeep.connect(logs_update)
            self.worker.start()
            self.workers.append(self.worker)

    def start_slash_sending(self):
        def red_color(element):
            element.setStyleSheet("""background: #C4C4C4;
                                    border: 2px solid #BC2E3F;
                                    border-radius: 10px;
                                    font-family: Sitara;
                                    font-style: normal;
                                    font-weight: normal;
                                    font-size: 18px;
                                    line-height: 29px;
                                    color: #000000;""")

        def logs_update(value: str):
            self.mainui.logs_text.append(value)

        token = self.mainui.token.toPlainText()
        guild_id = self.mainui.guild_id.text()
        application_id = self.mainui.application_id.text()
        version_id = self.mainui.version_id.text()
        command_id = self.mainui.command_id.text()
        command = self.mainui.command.text()
        delay = self.mainui.delay.text()
        image = self.mainui.image.text()
        channels = {}
        for i in range(self.mainui.channels_list.count()):
            item = self.mainui.channels_list.item(i)
            data = item.data(QtCore.Qt.UserRole)
            channels[data['channel_id']] = data['message']

        if token == '':
            red_color(self.mainui.token)
        elif not channels:
            red_color(self.mainui.channels_list)
        elif guild_id == '':
            red_color(self.mainui.guild_id)
        elif application_id == '':
            red_color(self.mainui.application_id)
        elif version_id == '':
            red_color(self.mainui.version_id)
        elif command_id == '':
            red_color(self.mainui.command_id)
        elif command == '':
            red_color(self.mainui.command)
        elif delay == '':
            red_color(self.mainui.delay)
        else:
            self.save_data(token, delay, image, channels)
            self.mainui.logs_text.append('Program started! Don\'t close!')
            self.worker = SlashWorker(token, guild_id, application_id, version_id, command_id, command, delay, channels, image)
            self.worker.logsbeep.connect(logs_update)
            self.worker.start()
            self.workers.append(self.worker)

    def show_slash(self):
        if self.mainui.slash_Button.text() == '':
            self.mainui.message.setHidden(True)
            self.mainui.message_text.setHidden(True)
            self.mainui.image.setHidden(True)
            self.mainui.image_text.setHidden(True)
            self.mainui.start_Button.setHidden(True)
            self.mainui.delay_text.setGeometry(QtCore.QRect(675, 629, 220, 35))
            self.mainui.delay.setGeometry(QtCore.QRect(780, 637, 45, 22))
            self.mainui.guild_id_text.setHidden(False)
            self.mainui.guild_id.setHidden(False)
            self.mainui.application_id_text.setHidden(False)
            self.mainui.application_id.setHidden(False)
            self.mainui.version_id_text.setHidden(False)
            self.mainui.version_id.setHidden(False)
            self.mainui.command_id.setHidden(False)
            self.mainui.command_id_text.setHidden(False)
            self.mainui.command_text.setHidden(False)
            self.mainui.command.setHidden(False)
            self.mainui.start_slash_Button.setHidden(False)
            self.mainui.slash_Button.setText(' ')
        else:
            self.mainui.message.setHidden(False)
            self.mainui.message_text.setHidden(False)
            self.mainui.image.setHidden(False)
            self.mainui.image_text.setHidden(False)
            self.mainui.start_Button.setHidden(False)
            self.mainui.delay_text.setGeometry(QtCore.QRect(675, 440, 220, 35))
            self.mainui.delay.setGeometry(QtCore.QRect(780, 448, 45, 22))
            self.mainui.guild_id_text.setHidden(True)
            self.mainui.guild_id.setHidden(True)
            self.mainui.application_id_text.setHidden(True)
            self.mainui.application_id.setHidden(True)
            self.mainui.version_id_text.setHidden(True)
            self.mainui.version_id.setHidden(True)
            self.mainui.command_id.setHidden(True)
            self.mainui.command_id_text.setHidden(True)
            self.mainui.command_text.setHidden(True)
            self.mainui.command.setHidden(True)
            self.mainui.start_slash_Button.setHidden(True)
            self.mainui.slash_Button.setText('')

    def stop_all_posters(self):
        # Эффект нажатия кнопки
        self.mainui.stop_all_button.setStyleSheet("""
            background: #CC0000;
            border-radius: 15px;
            font-family: Sitara;
            font-style: normal;
            font-weight: normal;
            font-size: 18px;
            line-height: 29px;
            text-align: center;
            color: #FFFFFF;
        """)

        # Сообщение о начале остановки
        self.mainui.logs_text.append('Начата остановка всех постеров...')

        # Даем время для обновления интерфейса
        QtCore.QCoreApplication.processEvents()

        # Останавливаем все потоки
        for worker in self.workers:
            worker.stop()

        # Ждем завершения всех потоков
        for worker in self.workers:
            worker.wait()

        self.workers.clear()

        # Возвращаем обычный стиль кнопки
        self.mainui.stop_all_button.setStyleSheet("""
            background: #FF0000;
            border-radius: 15px;
            font-family: Sitara;
            font-style: normal;
            font-weight: normal;
            font-size: 18px;
            line-height: 29px;
            text-align: center;
            color: #FFFFFF;
        """)

        # Сообщение о завершении остановки
        self.mainui.logs_text.append('Все постеры успешно остановлены.')

        # Прокручиваем лог вниз
        self.mainui.logs_text.verticalScrollBar().setValue(
            self.mainui.logs_text.verticalScrollBar().maximum()
        )

def main():
    app = QtWidgets.QApplication(sys.argv)
    mainwindow = formwindow()
    mainwindow.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
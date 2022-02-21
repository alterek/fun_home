import PySimpleGUI as sg
from mysql.connector import connect, Error
from main import win


my_str = 'D:/1.BMP'
image = open(my_str, 'rb')
card = image.read()
layout = [[sg.Text('Логин', size=(6, 1)),
           sg.InputText(size=(30, 1), key='login', default_text='root')],
          [sg.Text('Пароль', size=(6, 1)),
           sg.InputText(size=(30, 1), password_char='*', key='pass', default_text='admin')],
          [sg.Button('Войти'), sg.Button('Выход')]
          ]

window = sg.Window('Авторизация', layout)

while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED or event == 'Выход':
        break
    elif event == 'Войти':
        try:
            con = connect(
                host='localhost',
                user=values['login'],
                password=values['pass'],
                db='fun_home'
            )
        except Error as e:
            sg.popup_error(e)
            continue

        cur = con.cursor()

        cur.execute("select super_priv, select_priv from mysql.user WHERE user = '" + values['login'] + "'")
        for x in cur.fetchall():
            admin = x[0]
            reader = x[1]
            if admin == 'N' and reader == 'N':
                sg.popup_error('У этого пользователя нет прав для доступа')
                break
            elif admin == 'Y':
                win(con, cur, True)
            else:
                win(con, cur)

        con.commit()
        cur.close()
        con.close()


window.close()

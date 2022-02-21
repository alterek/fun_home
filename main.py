import PySimpleGUI as sg
import redis
import subprocess
import sys
import psutil
import pymongo
from mysql.connector import Error
import ch_row as cr

client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["fun_home"]

global con, cur, tables, columns, vals, users, view_columns, view_vals, collection, certs, prev_certs


def kill(proc_pid):
    process = psutil.Process(proc_pid)
    for pr in process.children(recursive=True):
        pr.kill()
    process.kill()


def refresh_cert():
    global collection, certs, prev_certs
    collection = db["death_cert"]
    certs = []
    prev_certs = []
    for el in collection.find():
        certs.append(el)
        prev_certs.append([el.get('_id'), el.get('ФИО'), el.get('Дата смерти')])


def refresh_select():
    global view_columns, view_vals
    view_columns = []
    view_vals = []
    view = ['Первый', 'Второй', 'Третий', 'Четвертый', 'Пятый',
            'Шестой', 'Седьмой', 'Восьмой', 'Девятый', 'Десятый']

    for v in view:
        temp = []
        cur.execute("select * from fun_home." + v)
        for x in cur.fetchall():
            temp.append(x)
        view_vals.append(temp)

        temp = []
        cur.execute("show columns from fun_home." + v)
        for x in cur.fetchall():
            temp.append(x[0])
        view_columns.append(temp)


def refresh_users():
    global users
    users = []
    cur.execute("select * from fun_home.users")
    for x in cur.fetchall():
        users.append(x)


def refresh():
    global con, cur, tables, columns, vals
    tables = []
    columns = []
    vals = []
    cur.execute("SHOW TABLES from fun_home")
    for x in cur.fetchall():
        tables.append(x[0])

    for tab in tables:
        tab_cols = []
        tab_vals = []
        cur.execute("SHOW COLUMNS FROM fun_home." + str(tab))
        for col in cur.fetchall():
            tab_cols.append(col[0])
        columns.append(tab_cols)
        cur.execute("SELECT * FROM fun_home." + str(tab))
        for v in cur.fetchall():
            tab_vals.append(v)
        vals.append(tab_vals)


def win(_con, _cur, admin=False):
    global con, cur, tables, columns, vals, collection
    proc = subprocess.Popen([sys.executable, 'redis_server.py'], shell=True,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    r = redis.Redis(db=0)
    con = _con
    cur = _cur
    refresh()
    refresh_select()
    refresh_cert()
    if admin:
        refresh_users()
    tab1_layout = [[sg.Table(values=vals[tables.index('филиалы')], expand_x=True, num_rows=20,
                             headings=columns[tables.index('филиалы')], key='филиалы', enable_events=True)]]
    tab2_layout = [[sg.Table(values=vals[tables.index('представители')], expand_x=True, num_rows=20,
                             headings=columns[tables.index('представители')], key='представители', enable_events=True)]]
    tab3_layout = [[sg.Table(values=vals[tables.index('усопшие')], auto_size_columns=False, num_rows=20,
                             col_widths=[10, 10, 8, 10, 10, 12, 10, 7, 7, 5], expand_x=True,
                             headings=columns[tables.index('усопшие')], key='усопшие', enable_events=True)]]
    tab4_layout = [[sg.Table(values=vals[tables.index('сотрудники')], expand_x=True, num_rows=20,
                             headings=columns[tables.index('сотрудники')], key='сотрудники', enable_events=True)]]
    tab5_layout = [[sg.Table(values=vals[tables.index('должности')], expand_x=True, num_rows=20,
                             headings=columns[tables.index('должности')], key='должности', enable_events=True)]]
    tab6_layout = [[sg.Table(values=vals[tables.index('сотрудники_должности')], expand_x=True, num_rows=20,
                             headings=columns[tables.index('сотрудники_должности')], key='сотрудники_должности',
                             enable_events=True)]]
    tab7_layout = [[sg.Table(values=vals[tables.index('ритуалы')], expand_x=True, num_rows=20,
                             headings=columns[tables.index('ритуалы')], key='ритуалы', enable_events=True)]]
    tab8_layout = [[sg.Table(values=vals[tables.index('журнал_ритуалов')], expand_x=True, num_rows=20,
                             headings=columns[tables.index('журнал_ритуалов')], key='журнал_ритуалов',
                             enable_events=True)]]
    tab9_layout = [[sg.Table(values=vals[tables.index('товары')], expand_x=True, num_rows=20,
                             headings=columns[tables.index('товары')], key='товары', enable_events=True),
                    sg.Image(size=(96, 103), key='image')]]
    tab10_layout = [[sg.Table(values=vals[tables.index('журнал_товаров')], expand_x=True, num_rows=20,
                              headings=columns[tables.index('журнал_товаров')], key='журнал_товаров',
                              enable_events=True)]]
    tables_layout = [
        [sg.TabGroup([[sg.Tab('Филиалы', tab1_layout),
                       sg.Tab('Представители', tab2_layout),
                       sg.Tab('Усопшие', tab3_layout),
                       sg.Tab('Сотрудники', tab4_layout),
                       sg.Tab('Должности', tab5_layout),
                       sg.Tab('Сотрудники_Должности', tab6_layout),
                       sg.Tab('Ритуалы', tab7_layout),
                       sg.Tab('Журнал_ритуалов', tab8_layout),
                       sg.Tab('Товары', tab9_layout),
                       sg.Tab('Журнал_товаров', tab10_layout)]], key='tables')],
        [sg.Button('Добавить запись', visible=admin),
         sg.Button('Изменить запись', visible=admin),
         sg.Button('Удалить запись', visible=admin)]
    ]
    sel1_layout = [
        [sg.Text('Количество усопших по представителям')],
        [sg.Table(values=view_vals[0], expand_x=True, num_rows=20,
                  headings=view_columns[0], key='первый', enable_events=True)]
    ]
    sel2_layout = [
        [sg.Text('Количество усопших по филиалам')],
        [sg.Table(values=view_vals[1], expand_x=True, num_rows=20,
                  headings=view_columns[1], key='второй', enable_events=True)]
    ]
    sel3_layout = [
        [sg.Text('Все товары для представителя')],
        [sg.Table(values=view_vals[2], expand_x=True, expand_y=True,
                  headings=view_columns[2], key='третий', enable_events=True),
         sg.Image(size=(96, 103), key='sel3_img')],
        [sg.Button('Представитель', key='sel3_but')]
    ]
    sel4_layout = [
        [sg.Text('Все ритуалы для представителя')],
        [sg.Table(values=view_vals[3], expand_x=True, expand_y=True,
                  headings=view_columns[3], key='четвертый', enable_events=True)],
        [sg.Button('Представитель', key='sel4_but')]
    ]
    sel5_layout = [
        [sg.Text('Все ритуалы для усопшего')],
        [sg.Table(values=view_vals[4], expand_x=True, expand_y=True,
                  headings=view_columns[4], key='пятый', enable_events=True)],
        [sg.Button('Усопший', key='sel5_but')]
    ]
    sel6_layout = [
        [sg.Text('Все сотрудники, выполнявшие ритуалы для усопшего')],
        [sg.Table(values=view_vals[5], expand_x=True, expand_y=True,
                  headings=view_columns[5], key='шестой', enable_events=True)],
        [sg.Button('Усопший', key='sel6_but')]
    ]
    sel7_layout = [
        [sg.Text('Все усопшие, для которых сотрудник выполнял ритуалы')],
        [sg.Table(values=view_vals[6], auto_size_columns=False, expand_y=True,
                  col_widths=[16, 10, 10, 12, 10, 13, 13, 13],
                  headings=view_columns[6], key='седьмой', enable_events=True)],
        [sg.Button('Сотрудник', key='sel7_but')]
    ]
    sel8_layout = [
        [sg.Text('Все должности для сотрудника')],
        [sg.Table(values=view_vals[7], expand_x=True, expand_y=True,
                  headings=view_columns[7], key='восьмой', enable_events=True)],
        [sg.Button('Сотрудник', key='sel8_but')]
    ]
    sel9_layout = [
        [sg.Text('Все сотрудники для должности')],
        [sg.Table(values=view_vals[8], expand_x=True, expand_y=True,
                  headings=view_columns[8], key='девятый', enable_events=True)],
        [sg.Button('Должность', key='sel9_but')]
    ]
    sel10_layout = [
        [sg.Text('Количество поступивших успоших по дням')],
        [sg.Table(values=view_vals[9], expand_x=True, expand_y=True,
                  headings=view_columns[9], key='ltcznsq', enable_events=True)]
    ]
    select_layout = [
        [sg.TabGroup([[sg.Tab('Первый', sel1_layout),
                       sg.Tab('Второй', sel2_layout),
                       sg.Tab('Третий', sel3_layout),
                       sg.Tab('Четвертый', sel4_layout),
                       sg.Tab('Пятый', sel5_layout),
                       sg.Tab('Шестой', sel6_layout),
                       sg.Tab('Седьмой', sel7_layout),
                       sg.Tab('Восьмой', sel8_layout),
                       sg.Tab('Девятый', sel9_layout),
                       sg.Tab('Десятый', sel10_layout)
                       ]], key='select')]
    ]

    death_layout = [
        [sg.Table(values=prev_certs, headings=['Усопший_id', 'ФИО', 'Дата смерти'],
                  expand_x=True, num_rows=20, key='death', enable_events=True),
         sg.Multiline(key='cert', disabled=True, expand_y=True, expand_x=True)],
        [sg.Button('Добавить свидетельство'), sg.Button('Изменить свидетельство'), sg.Button('Удалить свидетельство')]

    ]
    admin_layout = [
        [sg.Table(values=users, headings=['Пользователь', 'Роль'], expand_x=True, num_rows=20, key='users')],
        [sg.Button('Добавить пользователя'), sg.Button('Изменить пользователя'), sg.Button('Удалить пользователя')]
    ]

    layout = [
        [sg.TabGroup([[
            sg.Tab('Таблицы', tables_layout),
            sg.Tab('Свидетельства о смерти', death_layout),
            sg.Tab('Тематические запросы', select_layout),
            sg.Tab('Администрирование', admin_layout, visible=admin),
        ]])],
        [sg.Button('Выход')]]

    window = sg.Window('Похоронное бюро', layout)

    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event == 'Выход':
            break

        elif event == 'death':
            cert = certs[values['death'][0]]
            _id = cert.get('_id')
            name = cert.get('ФИО')
            citizenship = cert.get('Гражданство')
            dt_birth = cert.get('Дата рождения')
            place_birth = [cert.get('Место рождения').get('Город'),
                           cert.get('Место рождения').get('Регион')]
            dt_death = cert.get('Дата смерти')
            dt_act = cert.get('Дата акта')
            numb_act = cert.get('Номер акта')
            place_death = [cert.get('Место смерти').get('Город'),
                           cert.get('Место смерти').get('Регион'),
                           cert.get('Место смерти').get('Страна')]
            reg = cert.get('ЗАГС')
            dt_issue = cert.get('Дата выдачи')

            window['cert'].update('')
            window['cert'].print('СВИДЕТЕЛЬСТВО О СМЕРТИ', justification='c')
            window['cert'].print()
            window['cert'].print(name, justification='c')
            window['cert'].print(citizenship, justification='c')
            window['cert'].print()
            window['cert'].print('Дата рождения: ', dt_birth, justification='c')
            window['cert'].print()
            window['cert'].print('Место рождения: ', place_birth[0], justification='c')
            window['cert'].print(place_birth[1], justification='c')
            window['cert'].print()
            window['cert'].print('Умер(ла): ', dt_death, justification='c')
            window['cert'].print('о чем: ', dt_act, justification='c')
            window['cert'].print('составлена запись акта о смерти №: ', numb_act, justification='c')
            window['cert'].print()
            window['cert'].print('Место смерти: ', place_death[0], justification='c')
            window['cert'].print(place_death[1], justification='c')
            window['cert'].print(place_death[2], justification='c')
            window['cert'].print()
            window['cert'].print('Место государственной регистрации: ', reg, justification='c')
            window['cert'].print('Дата выдачи: ', dt_issue, justification='c')

        elif event == 'Добавить свидетельство' or event == 'Изменить свидетельство':
            val_usop = vals[tables.index('усопшие')]
            col_usop = columns[tables.index('усопшие')]
            cert = None
            ch = False
            if event == 'Изменить свидетельство':
                ch = True
                try:
                    cert = certs[values['death'][0]]
                except IndexError:
                    sg.popup_error("Свидетельство для изменения не выбрано")
                    continue
            try:
                cert = cr.ch_cert(val_usop, col_usop, cert, ch)
            except TypeError:
                continue
            try:
                collection.delete_one({"_id": cert.get('_id')})
            except AttributeError:
                continue
            collection.insert_one(cert)
            refresh_cert()
            window['death'].update(values=prev_certs)

        elif event == 'Удалить свидетельство':
            try:
                cert = certs[values['death'][0]]
            except IndexError:
                sg.popup_error("Свидетельство для удаления не выбрано")
                continue
            if sg.popup_ok_cancel('Вы уверены, что хотите удалить эту запись?') != 'OK':
                continue
            try:
                collection.delete_one({"_id": cert.get('_id')})
            except AttributeError:
                continue
            refresh_cert()
            window['death'].update(values=prev_certs)

        elif event == 'Добавить пользователя' or event == 'Изменить пользователя':
            user = None
            role = None
            ch = False
            if event == 'Изменить пользователя':
                try:
                    user, role = users[values['users'][0]][0], users[values['users'][0]][1]
                except IndexError:
                    sg.popup_error("Пользователь для изменения не выбран")
                    continue
                if user == 'root':
                    sg.popup_error("Изменение пользователя root невозможно")
                    continue
                else:
                    ch = True
            sql1, sql2 = cr.ch_role(user, role, ch)
            cur.execute(sql1)
            cur.execute(sql2)
            cur.execute("FLUSH PRIVILEGES")
            con.commit()
            refresh_users()
            window['users'].update(values=users)

        elif event == 'Удалить пользователя':
            try:
                user, role = users[values['users'][0]][0], users[values['users'][0]][1]
            except IndexError:
                sg.popup_error("Пользователь для удаления не выбран")
                continue
            if user == 'root':
                sg.popup_error("Удаление пользователя root невозможно")
                continue
            if sg.popup_ok_cancel('Вы уверены, что хотите удалить эту запись?') != 'OK':
                continue
            try:
                cur.execute("drop user '" + user + "'@'localhost'")
            except Error as e:
                sg.popup_error(e)
                continue
            con.commit()
            refresh_users()
            window['users'].update(values=users)

        elif event == 'товары':
            key = vals[tables.index('товары')][values['товары'][0]][3]
            if key != b'':
                image = r.get(key)
                im = cr.get_img_data(image)
            else:
                im = None
            window['image'].update(data=im)

        elif event == 'Добавить запись' or event == 'Изменить запись':
            sql = None
            val = None
            row = None
            ch = False
            tab = values['tables'].lower()
            if event == 'Изменить запись':
                ch = True
                try:
                    row = vals[tables.index(tab)][values[tab][0]]
                except IndexError:
                    sg.popup_error("Запись для изменения не выбрана")
                    continue

            if tab == 'филиалы':
                sql, val = cr.ch_fil(row, ch)
            elif tab == 'представители':
                sql, val = cr.ch_pred(row, ch)
            elif tab == 'усопшие':
                val_fil = vals[tables.index('филиалы')]
                col_fil = columns[tables.index('филиалы')]
                val_pred = vals[tables.index('представители')]
                col_pred = columns[tables.index('представители')]
                sql, val = cr.ch_usop(val_fil, col_fil, val_pred, col_pred, row, ch)
            elif tab == 'сотрудники':
                sql, val = cr.ch_emp(row, ch)
            elif tab == 'должности':
                sql, val = cr.ch_post(row, ch)
            elif tab == 'сотрудники_должности':
                val_emp = vals[tables.index('сотрудники')]
                col_emp = columns[tables.index('сотрудники')]
                val_post = vals[tables.index('должности')]
                col_post = columns[tables.index('должности')]
                sql, val = cr.ch_emp_post(val_emp, col_emp, val_post, col_post, row, ch)
            elif tab == 'ритуалы':
                sql, val = cr.ch_rit(row, ch)
            elif tab == 'журнал_ритуалов':
                val_rit = vals[tables.index('ритуалы')]
                col_rit = columns[tables.index('ритуалы')]
                val_emp = vals[tables.index('сотрудники')]
                col_emp = columns[tables.index('сотрудники')]
                val_pred = vals[tables.index('представители')]
                col_pred = columns[tables.index('представители')]
                val_usop = vals[tables.index('усопшие')]
                col_usop = columns[tables.index('усопшие')]
                sql, val = cr.ch_jour_rit(val_rit, col_rit, val_emp, col_emp,
                                          val_pred, col_pred, val_usop, col_usop, row, ch)
            elif tab == 'товары':
                sql, val, image, key = cr.ch_god(r, row, ch)
                if key is not None and image is not None:
                    r.mset({key: image})
            elif tab == 'журнал_товаров':
                val_god = vals[tables.index('товары')]
                col_god = columns[tables.index('товары')]
                val_emp = vals[tables.index('сотрудники')]
                col_emp = columns[tables.index('сотрудники')]
                val_pred = vals[tables.index('представители')]
                col_pred = columns[tables.index('представители')]
                sql, val = cr.ch_jour_god(val_god, col_god, val_emp, col_emp, val_pred, col_pred, row, ch)

            try:
                cur.execute(sql, val)
                con.commit()
                refresh()
                refresh_select()
                window[tab].update(values=vals[tables.index(tab)])
                if tab == 'усопшие':
                    _id = None
                    if event == 'Изменить запись':
                        _id = int(row[0])
                    else:
                        cur.execute('select max(усопший_id) from усопшие')
                        for u in cur.fetchall():
                            _id = int(u[0])
                    collection.update_one({
                        '_id': _id
                    }, {
                        '$set': {
                            'ФИО': val[2],
                            'Дата рождения': val[3],
                            'Дата Смерти': val[4]
                        }
                    }, upsert=False)
                    refresh_cert()
                    window['death'].update(values=prev_certs)
            except Error as e:
                sg.popup_error(e)

        elif event == 'Удалить запись':
            tab = values['tables'].lower()
            col = columns[tables.index(tab)][0]
            try:
                _id = vals[tables.index(tab)][values[tab][0]][0]
            except IndexError:
                sg.popup_error("Запись для удаления не выбрана")
                continue
            if sg.popup_ok_cancel('Вы уверены, что хотите удалить эту запись?') != 'OK':
                continue
            try:
                cur.execute("delete from fun_home." + str(tab) + " where " + str(col) + " = " + str(_id))
            except Error as e:
                sg.popup_error(e)
                continue
            con.commit()
            refresh()
            refresh_select()
            window[tab].update(values=vals[tables.index(tab)])
            if tab == 'усопшие':
                collection.delete_one({"_id": int(_id)})
                refresh_cert()
                window['death'].update(values=prev_certs)

        elif event == 'sel3_but':
            val_new = []
            val_pred = vals[tables.index('представители')]
            col_pred = columns[tables.index('представители')]
            _id = cr.sel_row(val_pred, col_pred, 'Представитель')
            for x in view_vals[2]:
                if x[0] == _id:
                    val_new.append(x)
            window['третий'].update(values=val_new)

        elif event == 'третий':
            key = view_vals[2][values['третий'][0]][4]
            if key != b'':
                image = r.get(key)
                im = cr.get_img_data(image)
            else:
                im = None
            window['sel3_img'].update(data=im)

        elif event == 'sel4_but':
            val_new = []
            val_pred = vals[tables.index('представители')]
            col_pred = columns[tables.index('представители')]
            _id = cr.sel_row(val_pred, col_pred, 'Представитель')
            for x in view_vals[3]:
                if x[0] == _id:
                    val_new.append(x)
            window['четвертый'].update(values=val_new)

        elif event == 'sel5_but':
            val_new = []
            val_pred = vals[tables.index('усопшие')]
            col_pred = columns[tables.index('усопшие')]
            _id = cr.sel_row(val_pred, col_pred, 'Усопший')
            for x in view_vals[4]:
                if x[0] == _id:
                    val_new.append(x)
            window['пятый'].update(values=val_new)

        elif event == 'sel6_but':
            val_new = []
            val_pred = vals[tables.index('усопшие')]
            col_pred = columns[tables.index('усопшие')]
            _id = cr.sel_row(val_pred, col_pred, 'Усопший')
            for x in view_vals[5]:
                if x[0] == _id:
                    val_new.append(x)
            window['шестой'].update(values=val_new)

        elif event == 'sel7_but':
            val_new = []
            val_pred = vals[tables.index('сотрудники')]
            col_pred = columns[tables.index('сотрудники')]
            _id = cr.sel_row(val_pred, col_pred, 'Сотрудник')
            for x in view_vals[6]:
                if x[0] == _id:
                    val_new.append(x)
            window['седьмой'].update(values=val_new)

        elif event == 'sel8_but':
            val_new = []
            val_pred = vals[tables.index('сотрудники')]
            col_pred = columns[tables.index('сотрудники')]
            _id = cr.sel_row(val_pred, col_pred, 'Сотрудник')
            for x in view_vals[7]:
                if x[0] == _id:
                    val_new.append(x)
            window['восьмой'].update(values=val_new)

        elif event == 'sel9_but':
            val_new = []
            val_pred = vals[tables.index('должности')]
            col_pred = columns[tables.index('должности')]
            _id = cr.sel_row(val_pred, col_pred, 'Должность')
            for x in view_vals[8]:
                if x[0] == _id:
                    val_new.append(x)
            window['девятый'].update(values=val_new)

    window.close()
    r.bgsave(schedule=False)
    try:
        proc.wait(timeout=0)
    except subprocess.TimeoutExpired:
        kill(proc.pid)

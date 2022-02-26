import PySimpleGUI as sg
import hashlib
from io import BytesIO
from PIL import Image


def get_img_data(img, maxsize=(96, 103)):
    img = Image.open(BytesIO(img))
    img.thumbnail(maxsize)
    bio = BytesIO()
    img.save(bio, format="PNG")
    del img
    return bio.getvalue()


def hash_key(ind):
    h = hashlib.blake2b(digest_size=16)
    h.update(ind)
    key = h.hexdigest()
    return key


def sel_row(val, col, name):
    _id = 0
    layout = [
        [sg.Table(values=val, expand_x=True, num_rows=20,
                  headings=col, key='tab', enable_events=True)],
        [sg.Button('Выбрать'), sg.Button('Назад')]
    ]

    window = sg.Window(name, layout)

    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event == 'Назад':
            break
        elif event == 'Выбрать':
            _id = val[values['tab'][0]][0]
            break

    window.close()
    return _id


def ch_cert(val_usop, col_usop, cert, ch):
    cur_usop = None
    _id = ''
    citizenship = ''
    place_birth = ['', '']
    dt_act = ''
    numb_act = ''
    place_death = ['', '', '']
    reg = ''
    dt_issue = ''
    if cert is not None:
        _id = cert.get('_id')
        citizenship = cert.get('Гражданство')
        place_birth = [cert.get('Место рождения').get('Город'),
                       cert.get('Место рождения').get('Регион')]
        dt_act = cert.get('Дата акта')
        numb_act = cert.get('Номер акта')
        place_death = [cert.get('Место смерти').get('Город'),
                       cert.get('Место смерти').get('Регион'),
                       cert.get('Место смерти').get('Страна')]
        reg = cert.get('ЗАГС')
        dt_issue = cert.get('Дата выдачи')
        for usop in val_usop:
            if usop[0] == _id:
                cur_usop = usop
                break
    layout = [
        [sg.Text('Усопший_id', size=(15, 1), visible=not ch),
         sg.Input(key='usop_id', size=(30, 1), visible=not ch, default_text=str(_id)),
         sg.Button('Усопшие', visible=not ch)],
        [sg.Text('Гражданство', size=(15, 1)),
         sg.Input(key='citizenship', size=(30, 1), default_text=citizenship)],
        [sg.Text('Город рождения', size=(15, 1)),
         sg.Input(key='city_birth', size=(30, 1), default_text=place_birth[0])],
        [sg.Text('Регион рождения', size=(15, 1)),
         sg.Input(key='region_birth', size=(30, 1), default_text=place_birth[1])],
        [sg.CalendarButton('Дата акта', target='dt_act', key='cal_dt_act', format='%Y-%m-%d', size=(15, 1)),
         sg.Input(key='dt_act', size=(30, 1), default_text=dt_act)],
        [sg.Text('Номер акта', size=(15, 1)),
         sg.Input(key='numb_act', size=(30, 1), default_text=numb_act)],
        [sg.Text('Город смерти', size=(15, 1)),
         sg.Input(key='city_death', size=(30, 1), default_text=place_death[0])],
        [sg.Text('Регион смерти', size=(15, 1)),
         sg.Input(key='region_death', size=(30, 1), default_text=place_death[1])],
        [sg.Text('Страна смерти', size=(15, 1)),
         sg.Input(key='country_death', size=(30, 1), default_text=place_death[2])],
        [sg.Text('ЗАГС', size=(15, 1)),
         sg.Input(key='reg', size=(30, 1), default_text=reg)],
        [sg.CalendarButton('Дата выдачи', target='dt_issue', key='cal_dt_issue', format='%Y-%m-%d', size=(15, 1)),
         sg.Input(key='dt_issue', size=(30, 1), default_text=dt_issue)],
        [sg.Button('Добавить', visible=not ch), sg.Button('Сохранить', visible=ch), sg.Button('Назад')]
    ]

    window = sg.Window('Свидетельство о смерти', layout)

    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event == 'Назад':
            break
        elif event == 'Усопшие':
            window['usop_id'].update(value=sel_row(val_usop, col_usop, event))
        elif event == 'Добавить' or event == 'Сохранить':
            if not ch:
                for usop in val_usop:
                    try:
                        if usop[0] == int(values['usop_id']):
                            cur_usop = usop
                            break
                    except ValueError:
                        sg.popup_error('Усопший не выбран')
                        break
            else:
                pass
            cert = {
                '_id': cur_usop[0],
                "ФИО": cur_usop[3],
                "Гражданство": values['citizenship'],
                "Дата рождения": str(cur_usop[4]),
                "Место рождения": {
                    "Город": values['city_birth'],
                    "Регион": values['region_birth']
                },
                "Дата смерти": str(cur_usop[5]),
                "Дата акта": str(values['dt_act']),
                "Номер акта": str(values['numb_act']),
                "Место смерти": {
                    "Город": values['city_death'],
                    "Регион": values['region_death'],
                    "Страна": values['country_death']
                },
                "ЗАГС": values['reg'],
                "Дата выдачи": str(values['dt_issue'])
            }
            break

    window.close()
    return cert


def ch_role(user, role, ch):
    sql1 = None
    sql2 = None
    layout = [
        [sg.Text('Имя пользователя', size=(15, 1), visible=not ch),
         sg.Input(key='user', size=(30, 1), visible=not ch)],
        [sg.Text('Пароль', size=(15, 1), visible=not ch),
         sg.Input(key='pass', size=(30, 1), password_char='*', visible=not ch)],
        [sg.Text('Роль', size=(15, 1)), sg.Combo(['Админ', 'Чтение'], key='role',
                                                 size=(30, 1), default_value=role, readonly=True)],
        [sg.Button('Добавить', visible=not ch), sg.Button('Сохранить', visible=ch), sg.Button('Назад')]
    ]

    window = sg.Window(user, layout)

    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event == 'Назад':
            break
        elif event == 'Добавить' or event == 'Сохранить':
            if ch:
                sql1 = "REVOKE ALL PRIVILEGES ON *.* FROM '" + user + "'@'localhost'"
                if values['role'] == 'Админ':
                    sql2 = "GRANT ALL PRIVILEGES ON * . * TO '" + user + "'@'localhost'"
                elif values['role'] == 'Чтение':
                    sql2 = "GRANT SELECT ON * . * TO '" + user + "'@'localhost'"
            else:
                sql1 = "CREATE USER '" + values['user'] + "'@'localhost' IDENTIFIED BY '" + values['pass'] + "'"
                if values['role'] == 'Админ':
                    sql2 = "GRANT ALL PRIVILEGES ON * . * TO '" + values['user'] + "'@'localhost'"
                elif values['role'] == 'Чтение':
                    sql2 = "GRANT SELECT ON * . * TO '" + values['user'] + "'@'localhost'"
            break

    window.close()
    return sql1, sql2


def ch_fil(row, ch):
    if row is None:
        row = ['', '', '', '']
    sql = None
    val = None
    layout = [
        [sg.Text('Наименование', size=(15, 1)), sg.Input(key='fil_name', size=(30, 1), default_text=row[1])],
        [sg.Text('Адрес', size=(15, 1)), sg.Input(key='fil_ad', size=(30, 1), default_text=row[2])],
        [sg.Text('Телефон', size=(15, 1)), sg.Input(key='fil_ph', size=(30, 1), default_text=row[3])],
        [sg.Button('Добавить', visible=not ch), sg.Button('Сохранить', visible=ch), sg.Button('Назад')]
    ]

    window = sg.Window('Филиал', layout)

    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event == 'Назад':
            break
        elif event == 'Добавить' or event == 'Сохранить':
            if ch:
                sql = "UPDATE ФИЛИАЛЫ SET наименование = %s, адрес = %s, телефон = %s WHERE филиал_id = %s"
                val = (values['fil_name'], values['fil_ad'], values['fil_ph'], row[0])
            else:
                sql = "INSERT INTO ФИЛИАЛЫ (Наименование, Адрес, Телефон) VALUES (%s, %s, %s)"
                val = (values['fil_name'], values['fil_ad'], values['fil_ph'])
            break

    window.close()
    return sql, val


def ch_pred(row, ch):
    if row is None:
        row = ['', '', '', '', '']
    sql = None
    val = None
    layout = [
        [sg.Text('ФИО', size=(15, 1)), sg.Input(key='pred_name', size=(30, 1), default_text=row[1])],
        [sg.CalendarButton('Дата рождения', target='pred_birth', key='cal_birth', format='%Y-%m-%d', size=(15, 1)),
         sg.Input(key='pred_birth', size=(30, 1), default_text=row[2])],
        [sg.Text('Адрес', size=(15, 1)), sg.Input(key='pred_ad', size=(30, 1), default_text=row[3])],
        [sg.Text('Телефон', size=(15, 1)), sg.Input(key='pred_ph', size=(30, 1), default_text=row[4])],
        [sg.Button('Добавить', visible=not ch), sg.Button('Сохранить', visible=ch), sg.Button('Назад')]
    ]

    window = sg.Window('Представитель', layout)

    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event == 'Назад':
            break
        elif event == 'Добавить' or event == 'Сохранить':
            if ch:
                sql = "UPDATE ПРЕДСТАВИТЕЛИ SET ФИО = %s, Дата_рожд = %s, Адрес = %s, Телефон = %s WHERE пред_id = %s"
                val = (values['pred_name'], values['pred_birth'], values['pred_ad'], values['pred_ph'], row[0])
            else:
                sql = "INSERT INTO ПРЕДСТАВИТЕЛИ (ФИО, Дата_рожд, Адрес, Телефон) VALUES (%s, %s, %s, %s)"
                val = (values['pred_name'], values['pred_birth'], values['pred_ad'], values['pred_ph'])
            break

    window.close()
    return sql, val


def ch_usop(val_fil, col_fil, val_pred, col_pred, row, ch):
    if row is None:
        row = ['', '', '', '', '', '', '', '', '', '']
    sql = None
    val = None
    layout = [
        [sg.Text('Филиал_id', size=(15, 1)), sg.Input(key='fil_id', size=(30, 1), default_text=row[1]),
         sg.Button('Филиалы')],
        [sg.Text('Пред_id', size=(15, 1)), sg.Input(key='pred_id', size=(30, 1), default_text=row[2]),
         sg.Button('Представители')],
        [sg.Text('ФИО', size=(15, 1)), sg.Input(key='usop_name', size=(30, 1), default_text=row[3])],
        [sg.CalendarButton('Дата рождения', target='usop_birth',
                           key='cal_birth', format='%Y-%m-%d', size=(15, 1)),
         sg.Input(key='usop_birth', size=(30, 1), default_text=row[4])],
        [sg.CalendarButton('Дата смерти', target='usop_death',
                           key='cal_death', format='%Y-%m-%d', size=(15, 1)),
         sg.Input(key='usop_death', size=(30, 1), default_text=row[5])],
        [sg.CalendarButton('Дата поступление', target='usop_post',
                           key='cal_post', format='%Y-%m-%d', size=(15, 1)),
         sg.Input(key='usop_post', size=(30, 1), default_text=row[6])],
        [sg.Text('Длина', size=(15, 1)), sg.Input(key='usop_len', size=(30, 1), default_text=row[7])],
        [sg.Text('Ширина', size=(15, 1)), sg.Input(key='usop_width', size=(30, 1), default_text=row[8])],
        [sg.Text('Вес', size=(15, 1)), sg.Input(key='usop_weight', size=(30, 1), default_text=row[9])],
        [sg.Button('Добавить', visible=not ch), sg.Button('Сохранить', visible=ch), sg.Button('Назад')]
    ]

    window = sg.Window('Усопший', layout)

    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event == 'Назад':
            break

        elif event == 'Филиалы':
            window['fil_id'].update(value=sel_row(val_fil, col_fil, event))

        elif event == 'Представители':
            window['pred_id'].update(value=sel_row(val_pred, col_pred, event))

        elif event == 'Добавить' or event == 'Сохранить':
            if ch:
                sql = "UPDATE УСОПШИЕ SET Филиал_id = %s, Пред_id = %s, ФИО = %s, Дата_рожд = %s, " \
                      "Дата_смерти = %s, Дата_пост = %s, Длина = %s, ширина = %s, вес = %s WHERE усопший_id = %s"
                val = (values['fil_id'], values['pred_id'], values['usop_name'],
                       values['usop_birth'], values['usop_death'], values['usop_post'],
                       values['usop_len'], values['usop_width'], values['usop_weight'], row[0])
            else:
                sql = "INSERT INTO УСОПШИЕ (Филиал_id, Пред_id, ФИО, Дата_рожд, " \
                      "Дата_смерти, Дата_пост, Длина, ширина, вес) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
                val = (values['fil_id'], values['pred_id'], values['usop_name'],
                       values['usop_birth'], values['usop_death'], values['usop_post'],
                       values['usop_len'], values['usop_width'], values['usop_weight'])
            break

    window.close()
    return sql, val


def ch_emp(row, ch):
    if row is None:
        row = ['', '', '', '', '']
    sql = None
    val = None
    layout = [
        [sg.Text('ФИО', size=(15, 1)), sg.Input(key='emp_name', size=(30, 1), default_text=row[1])],
        [sg.CalendarButton('Дата рождения', target='emp_birth', key='cal_birth', format='%Y-%m-%d', size=(15, 1)),
         sg.Input(key='emp_birth', size=(30, 1), default_text=row[2])],
        [sg.Text('Адрес', size=(15, 1)), sg.Input(key='emp_ad', size=(30, 1), default_text=row[3])],
        [sg.Text('Телефон', size=(15, 1)), sg.Input(key='emp_ph', size=(30, 1), default_text=row[4])],
        [sg.Button('Добавить', visible=not ch), sg.Button('Сохранить', visible=ch), sg.Button('Назад')]
    ]

    window = sg.Window('Сотрудник', layout)

    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event == 'Назад':
            break
        elif event == 'Добавить' or event == 'Сохранить':
            if ch:
                sql = "UPDATE СОТРУДНИКИ SET ФИО = %s, Дата_рожд = %s, Адрес = %s, Телефон = %s WHERE сотрудник_id = %s"
                val = (values['emp_name'], values['emp_birth'], values['emp_ad'], values['emp_ph'], row[0])
            else:
                sql = "INSERT INTO СОТРУДНИКИ (ФИО, Дата_рожд, Адрес, Телефон) VALUES (%s, %s, %s, %s)"
                val = (values['emp_name'], values['emp_birth'], values['emp_ad'], values['emp_ph'])
            break

    window.close()
    return sql, val


def ch_post(row, ch):
    if row is None:
        row = ['', '', '', '']
    sql = None
    val = None
    layout = [
        [sg.Text('Наименование', size=(15, 1)), sg.Input(key='emp_name', size=(30, 1), default_text=row[1])],
        [sg.Text('Зарплата', size=(15, 1)), sg.Input(key='emp_sal', size=(30, 1), default_text=row[2])],
        [sg.Text('Требование ВО', size=(15, 1)), sg.Input(key='emp_he', size=(30, 1), default_text=row[3])],
        [sg.Button('Добавить', visible=not ch), sg.Button('Сохранить', visible=ch), sg.Button('Назад')]
    ]

    window = sg.Window('Должность', layout)

    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event == 'Назад':
            break
        elif event == 'Добавить' or event == 'Сохранить':
            if ch:
                sql = "UPDATE ДОЛЖНОСТИ SET наименование = %s, зарплата = %s, требование_во = %s " \
                      "WHERE должность_id = %s"
                val = (values['emp_name'], values['emp_sal'], values['emp_he'], row[0])
            else:
                sql = "INSERT INTO ДОЛЖНОСТИ (Наименование, Зарплата, Требование_ВО) VALUES (%s, %s, %s)"
                val = (values['emp_name'], values['emp_sal'], values['emp_he'])
            break

    window.close()
    return sql, val


def ch_emp_post(val_emp, col_emp, val_post, col_post, row, ch):
    if row is None:
        row = ['', '', '', '']
    sql = None
    val = None
    layout = [
        [sg.Text('Сотрудник_id', size=(15, 1)), sg.Input(key='emp_id', size=(30, 1), default_text=row[1]),
         sg.Button('Сотрудники')],
        [sg.Text('Должность_id', size=(15, 1)), sg.Input(key='post_id', size=(30, 1), default_text=row[2]),
         sg.Button('Должности')],
        [sg.Text('Опыт', size=(15, 1)), sg.Input(key='exp', size=(30, 1), default_text=row[3])],
        [sg.Button('Добавить', visible=not ch), sg.Button('Сохранить', visible=ch), sg.Button('Назад')]
    ]

    window = sg.Window('Сотрудник_должность', layout)

    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event == 'Назад':
            break

        elif event == 'Сотрудники':
            window['emp_id'].update(value=sel_row(val_emp, col_emp, event))

        elif event == 'Должности':
            window['post_id'].update(value=sel_row(val_post, col_post, event))

        elif event == 'Добавить' or event == 'Сохранить':
            if ch:
                sql = "UPDATE СОТРУДНИКИ_ДОЛЖНОСТИ SET Сотрудник_id = %s, Должность_id = %s, Опыт = %s " \
                      "WHERE ID = %s"
                val = (values['emp_id'], values['post_id'], values['exp'], row[0])
            else:
                sql = "INSERT INTO СОТРУДНИКИ_ДОЛЖНОСТИ (Сотрудник_id, Должность_id, Опыт) VALUES (%s, %s, %s)"
                val = (values['emp_id'], values['post_id'], values['exp'])
            break

    window.close()
    return sql, val


def ch_rit(row, ch):
    if row is None:
        row = ['', '', '']
    sql = None
    val = None
    layout = [
        [sg.Text('Наименование', size=(15, 1)), sg.Input(key='rit_name', size=(30, 1), default_text=row[1])],
        [sg.Text('Стоимость', size=(15, 1)), sg.Input(key='rit_price', size=(30, 1), default_text=row[2])],
        [sg.Button('Добавить', visible=not ch), sg.Button('Сохранить', visible=ch), sg.Button('Назад')]
    ]

    window = sg.Window('Ритуал', layout)

    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event == 'Назад':
            break
        elif event == 'Добавить' or event == 'Сохранить':
            if ch:
                sql = "UPDATE РИТУАЛЫ SET наименование = %s, стоимость = %s WHERE ритуал_id = %s"
                val = (values['rit_name'], values['rit_price'], row[0])
            else:
                sql = "INSERT INTO РИТУАЛЫ (Наименование, Стоимость) VALUES (%s, %s)"
                val = (values['rit_name'], values['rit_price'])
            break

    window.close()
    return sql, val


def ch_jour_rit(val_rit, col_rit, val_emp, col_emp, val_pred, col_pred, val_usop, col_usop, row, ch):
    if row is None:
        row = ['', '', '', '', '', '']
    sql = None
    val = None
    layout = [
        [sg.Text('Ритуал_id', size=(15, 1)), sg.Input(key='rit_id', size=(30, 1), default_text=row[1]),
         sg.Button('Ритуалы')],
        [sg.Text('Сотрудник_id', size=(15, 1)), sg.Input(key='emp_id', size=(30, 1), default_text=row[2]),
         sg.Button('Сотрудники')],
        [sg.Text('Пред_id', size=(15, 1)), sg.Input(key='pred_id', size=(30, 1), default_text=row[3]),
         sg.Button('Представители')],
        [sg.Text('Усопший_id', size=(15, 1)), sg.Input(key='usop_id', size=(30, 1), default_text=row[4]),
         sg.Button('Усопшие')],
        [sg.CalendarButton('Дата продажи', target='dt_sel', key='cal_dt_sel', format='%Y-%m-%d', size=(15, 1)),
         sg.Input(key='dt_sel', size=(30, 1), default_text=row[5])],
        [sg.Button('Добавить', visible=not ch), sg.Button('Сохранить', visible=ch), sg.Button('Назад')]
    ]

    window = sg.Window('Сотрудник_должность', layout)

    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event == 'Назад':
            break

        elif event == 'Ритуалы':
            window['rit_id'].update(value=sel_row(val_rit, col_rit, event))

        elif event == 'Сотрудники':
            window['emp_id'].update(value=sel_row(val_emp, col_emp, event))

        elif event == 'Представители':
            window['pred_id'].update(value=sel_row(val_pred, col_pred, event))

        elif event == 'Усопшие':
            window['usop_id'].update(value=sel_row(val_usop, col_usop, event))

        elif event == 'Добавить' or event == 'Сохранить':
            if ch:
                sql = "UPDATE ЖУРНАЛ_РИТУАЛОВ SET Ритуал_id = %s, Сотрудник_id = %s, Пред_id = %s, Усопший_id = %s, " \
                      "Дата_продажи = %s WHERE запись_id = %s"
                val = (values['rit_id'], values['emp_id'], values['pred_id'],
                       values['usop_id'], values['dt_sel'], row[0])
            else:
                sql = "INSERT INTO ЖУРНАЛ_РИТУАЛОВ (Ритуал_id, Сотрудник_id, Пред_id, Усопший_id, " \
                      "Дата_продажи) VALUES (%s, %s, %s, %s, %s)"
                val = (values['rit_id'], values['emp_id'], values['pred_id'],
                       values['usop_id'], values['dt_sel'])
            break

    window.close()
    return sql, val


def ch_god(r, row, ch):
    if row is None:
        row = ['', '', '', '']
    sql = None
    val = None
    image = None
    key = None
    if row[3] != b'' and ch:
        image = get_img_data(r.get(row[3]))
    layout = [
        [sg.Column([
            [sg.Text('Наименование', size=(15, 1))],
            [sg.Text('Стоимость', size=(15, 1))],
            [sg.Checkbox('', key='ch', default=True, enable_events=True),
             sg.FileBrowse('Изображение', file_types=(("Image Files", "*.jpg *.png *.BMP"),), size=(15, 1),
                           initial_folder='D:/', target='img', key='filebrowse', enable_events=True)]],
            element_justification='l'),
         sg.Column([[sg.Input(key='god_name', size=(40, 1), default_text=row[1])],
                    [sg.Input(key='god_price', size=(40, 1), default_text=row[2])],
                    [sg.In(default_text=row[3], size=(40, 1), key='img',
                           enable_events=True, visible=True, readonly=True)]], element_justification='l'),
         sg.Column([[sg.Image(size=(96, 103), key='image', data=image)]],
                   element_justification='l')],
        [sg.Button('Добавить', visible=not ch), sg.Button('Сохранить', visible=ch), sg.Button('Назад')]
    ]

    window = sg.Window('Товар', layout)

    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event == 'Назад':
            image = None
            key = None
            break
        if event == 'ch':
            window['filebrowse'].update(visible=values['ch'])
            if not values['ch']:
                window['img'].update(value='')
                window['image'].update(data=None)
        elif event == 'img' and values['ch']:
            try:
                image = open(values['img'], 'rb').read()
                key = hash_key(image)
                window['img'].update(value=key)

                im = get_img_data(image)
                window['image'].update(data=im)
            except FileNotFoundError:
                pass
        elif event == 'Добавить' or event == 'Сохранить':
            if ch:
                sql = "UPDATE ТОВАРЫ SET наименование = %s, стоимость = %s, изображение = %s WHERE товар_id = %s"
                val = (values['god_name'], values['god_price'], values['img'], row[0])
            else:
                sql = "INSERT ТОВАРЫ (Наименование, Стоимость, Изображение) VALUES (%s, %s, %s)"
                val = (values['god_name'], values['god_price'], values['img'])
            break

    window.close()
    return sql, val, image, key


def ch_jour_god(val_god, col_god, val_emp, col_emp, val_pred, col_pred, row, ch):
    if row is None:
        row = ['', '', '', '', '']
    sql = None
    val = None
    layout = [
        [sg.Text('Товар_id', size=(15, 1)), sg.Input(key='god_id', size=(30, 1), default_text=row[1]),
         sg.Button('Товары')],
        [sg.Text('Сотрудник_id', size=(15, 1)), sg.Input(key='emp_id', size=(30, 1), default_text=row[2]),
         sg.Button('Сотрудники')],
        [sg.Text('Пред_id', size=(15, 1)), sg.Input(key='pred_id', size=(30, 1), default_text=row[3]),
         sg.Button('Представители')],
        [sg.CalendarButton('Дата продажи', target='dt_sel', key='cal_dt_sel', format='%Y-%m-%d', size=(15, 1)),
         sg.Input(key='dt_sel', size=(30, 1), default_text=row[4])],
        [sg.Button('Добавить', visible=not ch), sg.Button('Сохранить', visible=ch), sg.Button('Назад')]
    ]

    window = sg.Window('Сотрудник_должность', layout)

    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event == 'Назад':
            break

        elif event == 'Товары':
            window['god_id'].update(value=sel_row(val_god, col_god, event))

        elif event == 'Сотрудники':
            window['emp_id'].update(value=sel_row(val_emp, col_emp, event))

        elif event == 'Представители':
            window['pred_id'].update(value=sel_row(val_pred, col_pred, event))

        elif event == 'Добавить' or event == 'Сохранить':
            if ch:
                sql = "UPDATE ЖУРНАЛ_ТОВАРОВ SET Товар_id = %s, Сотрудник_id = %s, Пред_id = %s, " \
                      "Дата_продажи = %s WHERE запись_id = %s"
                val = (values['god_id'], values['emp_id'], values['pred_id'], values['dt_sel'], row[0])
            else:
                sql = "INSERT INTO ЖУРНАЛ_ТОВАРОВ (Товар_id, Сотрудник_id, Пред_id, " \
                      "Дата_продажи) VALUES (%s, %s, %s, %s)"
                val = (values['god_id'], values['emp_id'], values['pred_id'], values['dt_sel'])
            break

    window.close()
    return sql, val

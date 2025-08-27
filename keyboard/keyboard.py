from aiogram.types import KeyboardButton, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

def template(*buttons:str,contact:int=None,location:int=None,poll:int=None,placeholder:str=None,size:tuple[int]=None):
    kb=ReplyKeyboardBuilder()
    for index, value in enumerate(buttons,start=0):
        if index==contact:
            kb.add(KeyboardButton(text=value,request_contact=True))
        elif index==location:
            kb.add(KeyboardButton(text=value,request_location=True))
        elif index==poll:
            kb.add(KeyboardButton(text=value,request_poll=True))
        else:
            kb.add(KeyboardButton(text=value))
    return kb.adjust(*size).as_markup(resize_keyboard=True,input_field_placeholder=placeholder)

def cart_inline(*,content:list[str],el:str):
    kb=InlineKeyboardBuilder()
    if len(content)==1:
            kb.add(InlineKeyboardButton(text='➖',callback_data=f'minus_{el}'),InlineKeyboardButton(text='➕',callback_data=f'plus_{el}'))
            kb.row(InlineKeyboardButton(text='Make Order',callback_data='ok'),InlineKeyboardButton(text='Menu',callback_data='menu'))
            return kb.as_markup(input_field_placeholder='Click an option')
    count=1
    for item in content:
        if item.split(' ')[0]==el.split(' ')[0]:
            if count==1:
                kb.add(InlineKeyboardButton(text='➖',callback_data=f'minus_{el}'),
                    InlineKeyboardButton(text='➕',callback_data=f'plus_{el}'),
                    InlineKeyboardButton(text='➡️',callback_data=f'shift_right_{el}'))
            elif count==len(content):
                kb.add(InlineKeyboardButton(text='⬅️',callback_data=f'shift_left_{el}'),
                       InlineKeyboardButton(text='➖',callback_data=f'minus_{el}'),
                       InlineKeyboardButton(text='➕',callback_data=f'plus_{el}'))
            else:
                kb.add(InlineKeyboardButton(text='⬅️',callback_data=f'shift_left_{el}'),
                    InlineKeyboardButton(text='➖',callback_data=f'minus_{el}'),
                    InlineKeyboardButton(text='➕',callback_data=f'plus_{el}'),
                    InlineKeyboardButton(text='➡️',callback_data=f'shift_right_{el}'))
            kb.row(InlineKeyboardButton(text='Make Order',callback_data='ok'),InlineKeyboardButton(text='Menu',callback_data='menu'))
            break
        count+=1
    return kb.as_markup(input_field_placeholder='Click an option')
    
def template_inline(items,id):
    kb=InlineKeyboardBuilder()
    if len(items)==1:
        kb.row(InlineKeyboardButton(text='Add to Cart',callback_data=f'add_{id}'))
        kb.row(InlineKeyboardButton(text='Cart and Order',callback_data='cart'),
            InlineKeyboardButton(text='Back',callback_data=f'to_family_{items[0].category}'),InlineKeyboardButton(text='Menu',callback_data='menu'))
        return kb.as_markup(input_field_placeholder='Click an option')
    count=1
    for item in items:
        if item.id==id:
            if count==1:
                kb.row(InlineKeyboardButton(text='Add to Cart',callback_data=f'add_{id}'),
                    InlineKeyboardButton(text='➡️',callback_data=f'right_{id}'))
            elif count==len(items):
                kb.row(InlineKeyboardButton(text='⬅️',callback_data=f'left_{id}'),
                    InlineKeyboardButton(text='Add to Cart',callback_data=f'add_{id}'))
            else:
                kb.row(InlineKeyboardButton(text='⬅️',callback_data=f'left_{id}'),
                    InlineKeyboardButton(text='Add to Cart',callback_data=f'add_{id}'),
                    InlineKeyboardButton(text='➡️',callback_data=f'right_{id}'))
            kb.row(InlineKeyboardButton(text='Cart and Order',callback_data='cart'),
           		InlineKeyboardButton(text='Back',callback_data=f'to_family_{item.category}'), InlineKeyboardButton(text='Menu',callback_data='menu'))
            break
        count+=1
    return kb.as_markup(input_field_placeholder='Click an option')

def dest_kb(dests):
    kb=InlineKeyboardBuilder()
    for dest in dests:
        if dest.room=='':
            kb.row(InlineKeyboardButton(text=f'{dest.country.capitalize()}, {dest.town.capitalize()}, {dest.street.capitalize()}, {dest.house}',
                callback_data=f'dest__{dest.country}_{dest.town}_{dest.street}_{dest.house}'))
        else:
            kb.row(InlineKeyboardButton(text=f'{dest.country.capitalize()}, {dest.town.capitalize()}, {dest.street.capitalize()}, {dest.house}, {dest.room}',
                callback_data=f'dest__{dest.country}_{dest.town}_{dest.street}_{dest.house}_{dest.room}'))
    kb.row(InlineKeyboardButton(text='Add address',callback_data='address'),InlineKeyboardButton(text='Cancel',callback_data='cancel'))
    return kb.as_markup(input_field_placeholder='Click an option')

def dest_countries_kb(dests):
    kb=InlineKeyboardBuilder()
    countries=[]
    for dest in dests:
        if dest.country not in countries:
            countries.append(dest.country)
            kb.row(InlineKeyboardButton(text=f'{dest.country.capitalize()}',callback_data=f'dest_country_{dest.country}'))
    kb.row(InlineKeyboardButton(text='Cancel',callback_data='cancel'))
    return kb.as_markup(input_field_placeholder='Click an option')

def dest_towns_kb(dests):
    kb=InlineKeyboardBuilder()
    towns=[]
    for dest in dests:
        if dest.town not in towns:
            towns.append(dest.town)
            kb.row(InlineKeyboardButton(text=f'{dest.town.capitalize()}',callback_data=f'dest_town_{dest.town}'))
    kb.row(InlineKeyboardButton(text='Cancel',callback_data='cancel'))
    return kb.as_markup(input_field_placeholder='Click an option')

def cafe_kb(cafes):
    kb=InlineKeyboardBuilder()
    for cafe in cafes:
        kb.row(InlineKeyboardButton(text=f'{cafe.country.capitalize()}, {cafe.town.capitalize()}, {cafe.street.capitalize()}, {cafe.house.capitalize()}',
         callback_data=f'cafe__{cafe.country}_{cafe.town}_{cafe.street}_{cafe.house}'))
    kb.row(InlineKeyboardButton(text='Cancel',callback_data='cancel'))
    return kb.as_markup(resize_keyboard=True,input_field_placeholder='Click an option')

def cafe_countries_kb(cafes):
    kb=InlineKeyboardBuilder()
    countries=[]
    for cafe in cafes:
        if cafe.country not in countries:
            countries.append(cafe.country)
            kb.row(InlineKeyboardButton(text=f'{cafe.country.capitalize()}',callback_data=f'cafe_country_{cafe.country}'))
    kb.row(InlineKeyboardButton(text='Cancel',callback_data='cancel'))
    return kb.as_markup(input_field_placeholder='Click an option')

def cafe_towns_kb(cafes):
    kb=InlineKeyboardBuilder()
    towns=[]
    for cafe in cafes:
        if cafe.town not in towns:
            towns.append(cafe.town)
            kb.row(InlineKeyboardButton(text=f'{cafe.town.capitalize()}',callback_data=f'cafe_town_{cafe.town}'))
    kb.row(InlineKeyboardButton(text='Cancel',callback_data='cancel'))
    return kb.as_markup(input_field_placeholder='Click an option')

def families_kb():
    kb=InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text='Food',callback_data='food'),InlineKeyboardButton(text='Beverage',callback_data='beverage'))
    kb.row(InlineKeyboardButton(text='Cart and Order',callback_data='cart'),InlineKeyboardButton(text='About',callback_data='about'),
        InlineKeyboardButton(text='Feedback',callback_data='feedback'))
    return kb.as_markup(input_field_placeholder='Click an option')

def categories_kb(categories,id:int):
    kb=InlineKeyboardBuilder()
    if len(categories)==1:
        kb.row(InlineKeyboardButton(text=f'{categories[0].title.capitalize()}',callback_data=f'category_{id}')),
        kb.row(InlineKeyboardButton(text='Cart and Order',callback_data='cart'),InlineKeyboardButton(text='Menu',callback_data='menu'))
        return kb.as_markup(input_field_placeholder='Click an option')
    count=1
    for category in categories:
        if category.id==id:
            if count==1:
                kb.row(InlineKeyboardButton(text=f'{category.title.capitalize()}',callback_data=f'category_{id}'),
                    InlineKeyboardButton(text='➡️',callback_data=f'offset_right_{id}'))
            elif count==len(categories):
                kb.row(InlineKeyboardButton(text='⬅️',callback_data=f'offset_left_{id}'),
                    InlineKeyboardButton(text=f'{category.title.capitalize()}',callback_data=f'category_{id}'))
            else:
                kb.row(InlineKeyboardButton(text='⬅️',callback_data=f'offset_left_{id}'),
                    InlineKeyboardButton(text=f'{category.title.capitalize()}',callback_data=f'category_{id}'),
                    InlineKeyboardButton(text='➡️',callback_data=f'offset_right_{id}'))
            kb.row(InlineKeyboardButton(text='Cart and Order',callback_data='cart'),InlineKeyboardButton(text='Menu',callback_data='menu'))
            break
        count+=1
    return kb.as_markup(input_field_placeholder='Click an option')
    
def confirm_kb():
    kb=InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text='Confirm and pay',callback_data='pay'),InlineKeyboardButton(text='Cancel',callback_data='cancel'))
    return kb.as_markup(input_field_placeholder='Click an option')

def phone_kb():
    kb=InlineKeyboardBuilder()
    return kb.row(InlineKeyboardButton(text='Cancel',callback_data='cancel')).as_markup(input_field_placeholder='Provide phone number')
    
def phones_kb(phones):
    kb=InlineKeyboardBuilder()
    for phone in phones:
        kb.row(InlineKeyboardButton(text=f'{phone.number}',callback_data=f'phone_{phone.number}'))
    kb.row(InlineKeyboardButton(text='Add phone',callback_data='another_phone'),InlineKeyboardButton(text='Cancel',callback_data='cancel'))
    return kb.as_markup(input_field_placeholder='Provide phone number')
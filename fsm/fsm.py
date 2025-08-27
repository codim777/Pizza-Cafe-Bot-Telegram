from aiogram.fsm.state import State, StatesGroup

class Post(StatesGroup):
    option=State()
    
class Post_category(StatesGroup):
    title=State()
    belong=State()
    image=State()
    finish=State()
    
class Post_item(StatesGroup):
    category=State()
    name=State()
    details=State()
    image=State()
    price=State()
    finish=State()
    
class Post_cafe(StatesGroup):
    cafe=State()
    finish=State()
    
class Update(StatesGroup):
    option=State()
    
class Update_category(StatesGroup):
    title=State()
    prop=State()
    value=State()
    finish=State()
    
class Update_item(StatesGroup):
    category=State()
    name=State()
    prop=State()
    value=State()
    finish=State()
    
class Update_cafe(StatesGroup):
    cafe=State()
    prop=State()
    value=State()
    finish=State()
    
class Delete(StatesGroup):
    option=State()
    
class Delete_category(StatesGroup):
    title=State()
    finish=State()
    
class Delete_item(StatesGroup):
    category=State()
    name=State()
    finish=State()
    
class Delete_cafe(StatesGroup):
    cafe=State()
    finish=State()
    
class Delete_order(StatesGroup):
    id=State()
    finish=State()
    
class Menu(StatesGroup):
    belong=State()
    category=State()
    finish=State()
    feedback=State()
    
class Order(StatesGroup):
    cart=State()
    delivery=State()
    dest=State()
    country=State()
    town=State()
    street=State()
    house=State()
    room=State()
    finish=State()
    cafe=State()
    phone=State()
    paid=State()

class Post_locale(StatesGroup):
    locale=State()
    finish=State()
    
class Delete_locale(StatesGroup):
    locale=State()
    finish=State()
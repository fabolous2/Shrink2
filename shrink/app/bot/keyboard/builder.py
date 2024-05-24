from aiogram.utils.keyboard import InlineKeyboardBuilder

def inline_builder(
        text: list and str,
        callback_data: str and list,
        sizes: int and list[int]=2,
        **kwargs
):
    builder=InlineKeyboardBuilder()
    if isinstance(text,str):
        text = [text]
    if isinstance(callback_data,str):
        callback_data = [callback_data]
    if isinstance(sizes,int):
        sizes = [sizes]

    [
        builder.button(text=txt,callback_data=cb)
        for txt,cb in zip(text,callback_data)
    ]
    builder.adjust(*sizes)
    return builder.as_markup(**kwargs)
db_list = [
    {'audio_id': 'CQACAgIAAxkBAAIHUmXtz7AvjO7tg5FDf6k0apLGG3XxAAIYQQACJmRwS_3nhGQFrT2xNAQ', 'audio_name': 'blonde(prod. artem1kz + zestymain) 145.mp3', 'size': 2297173, 'user_id': 5297779345, 'audio_index': 0},
    {'audio_id': 'CQACAgIAAxkBAAIHVGXtz7B5Py63h2DcLZiaIG3i5Yx7AAIaQQACJmRwSzbeboEdV060NAQ', 'audio_name': 'new_message_tone.mp3', 'size': 50684, 'user_id': 5297779345, 'audio_index': 0},
    {'audio_id': 'CQACAgIAAxkBAAIHU2Xtz7DyGdKdS2tKl1Q4lEO-f9-YAAIZQQACJmRwSz1wxl31A8d0NAQ', 'audio_name': 'new_message_notice.mp3', 'size': 34271, 'user_id': 5297779345, 'audio_index': 1},
    {'audio_id': 'CQACAgIAAxkBAAIHU2Xtz7DyGdKdS2tKl1Q4lEO-f9-YAAIZQQACJmRwSz1wxl31A8d0NAQ', 'audio_name': 'new_message_notice.mp3', 'size': 34271, 'user_id': 5297779345, 'audio_index': 1}
]

audio_list = [
    {'audio_id': 'CQACAgIAAxkBAAIHUmXtz7AvjO7tg5FDf6k0apLGG3XxAAIYQQACJmRwS_3nhGQFrT2xNAQ', 'audio_name': 'blonde(prod. artem1kz + zestymain) 145.mp3', 'size': 2297173, 'user_id': 5297779345, 'audio_index': 0},
    {'audio_id': 'CQACAgIAAxkBAAIHVGXtz7B5Py63h2DcLZiaIG3i5Yx7AAIaQQACJmRwSzbeboEdV060NAQ', 'audio_name': 'new_message_tone.mp3', 'size': 50684, 'user_id': 5297779345, 'audio_index': 0},
    {'audio_id': 'CQACAgIAAxkBAAIHU2Xtz7DyGdKdS2tKl1Q4lEO-f9-YAAIZQQACJmRwSz1wxl31A8d0NAQ', 'audio_name': 'new_message_notice.mp3', 'size': 34271, 'user_id': 5297779345, 'audio_index': 0},
    {'audio_id': 'CQACAgIAAxkBAAIHU2Xtz7DyGdKdS2tKl1Q4lEO-f9-YAAIZQQACJmRwSz1wxl31A8d0NAQ', 'audio_name': 'new_message_notice.mp3', 'size': 34271, 'user_id': 5297779345, 'audio_index': 0},
    {'audio_id': 'CQACAgIAAxkBAAIHU2Xtz7DyGdKdS2tKl1Q4lEO-f9-YAAIZQQACJmRwSz1wxl31A8d0NAQ', 'audio_name': 'new_message_notice.mp3', 'size': 34271, 'user_id': 5297779345, 'audio_index': 0},
    {'audio_id': 'CQACAgIAAxkBAAIHU2Xtz7DyGdKdS2tKl1Q4lEO-f9-YAAIZQQACJmRwSz1wxl31A8d0NAQ', 'audio_name': 'new_message_notice.mp3', 'size': 34271, 'user_id': 5297779345, 'audio_index': 0},
    {'audio_id': 'CQACAgIAAxkBAAIHU2Xtz7DyGdKdS2tKl1Q4lEO-f9-YAAIZQQACJmRwSz1wxl31A8d0NAQ', 'audio_name': 'new_message_notice.mp3', 'size': 34271, 'user_id': 5297779345, 'audio_index': 0}
]


def generate_album_indexes(audio_list: list[dict], amount: int) -> None:
    last_index = db_list[-1]['audio_index']
    
    count = 0
    amount_left = amount - 2
    for i in range(len(audio_list)):
        
        if amount_left == 0:
            temp = amount +  last_index
            audio_list[i]['audio_index'] = temp
            count += 1
            amount_left -=1
        
        elif amount_left > 0 :
            temp = last_index
            audio_list[i]['audio_index'] = temp
            count += 1
            amount_left = amount
    
generate_album_indexes(audio_list, 2)


for audio in audio_list:
    print(audio['audio_index'])
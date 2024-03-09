import redis
import json

import datetime

from app.config import settings
from app import crud, db, schemas

#redisのboard用のgroups, eventsを更新する
def update_redis(db_session, redis_db):
    #団体、イベント情報の取得と追加
    groups = crud.get_all_groups_public(db_session)
    groups_serializable = []

    for g in groups:
        events_serializable = []

        groups_serializable.append(schemas.Group.from_orm(g).dict())

        events=crud.get_all_events(db_session,g.id)
        for e in events:
            events_serializable.append(schemas.EventDBOutput_fromEvent(schemas.Event.from_orm(e)).dict())             

        redis_db.set('board_events:' + g.id, json.dumps(events_serializable))

    redis_db.set('board_groups', json.dumps(groups_serializable))
    return 1 #成功

#mainから呼ばれる関数
def update():
    try:
        db_session = db.SessionLocal()
        redis_db = redis.Redis(host=settings.redis_host , port=6379, db=0, decode_responses=True)
    except:
        return 'DBへの接続に失敗しました' #失敗

    #last_board_update : 最後にboard用の情報を更新した時間
    last_board_update_time = redis_db.get('last_board_update')
    now = datetime.datetime.now()
    if(last_board_update_time):
        #datetimeオブジェクトにstringから変換
        last_board_update = datetime.datetime.strptime(last_board_update_time, '"%Y-%m-%d %H:%M:%S.%f"')

        difference = now - last_board_update
        #一分間のずれがあるかを判定
        if (difference > datetime.timedelta(minutes=1)):
            redis_db.set('last_board_update', json.dumps(now, default=str))
            if(update_redis(db_session, redis_db)):
                return '新しく情報を更新しました'
            else:
                return '新しく情報を更新することに失敗しました'
        else:
            return '前回の更新は' + last_board_update_time
    else:
        redis_db.set('last_board_update', json.dumps(now, default=str))
        if(update_redis(db_session, redis_db)):
            return '新しく情報を登録しました'
        else:
            return '新しい情報の登録に失敗しました'
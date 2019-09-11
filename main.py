import os
import datetime

import tornado.ioloop
import tornado.web
from tornado.options import parse_command_line, define, options

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, String, Integer, Date, Enum, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import or_, and_, all_, any_

define("host", default="0.0.0.0", help="主机地址", type=str)
define("port", default=8000, help="主机端口", type=int)

engine = create_engine('mysql+pymysql://z:123321@localhost:3306/exam')
Base = declarative_base(bind=engine)
Session = sessionmaker(bind=engine)

session = Session()


class User(Base):
    __tablename__ = 'student'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(32), unique=True)
    sex = Column(Enum('男', '女'))
    city = Column(String(32))
    description = Column(Text)
    birthday = Column(Date, default=datetime.date(1995, 1, 1))
    only_child = Column(Integer)


q = session.query(User)


class GetHandler(tornado.web.RequestHandler):
    def get(self):
        menu = ["序号", "姓名", "性别", "住址", "注释", "出生日期", "是否为独生子女"]
        mes = []
        s = self.get_argument('s', '')
        if s == '':
            user = q.filter()
            for u in user:
                if u.only_child == 1:
                    u_only_child = '是'
                else:
                    u_only_child = '否'
                mes.append((u.id, u.name, u.sex, u.city, u.description, u.birthday, u_only_child))
            self.render('search.html', menu=menu, user=mes)
        else:
            user = q.filter(or_(User.id == s, User.name == s, User.city == s, User.sex == s))
            for u in user:
                if u.only_child == 1:
                    u_only_child = '是'
                else:
                    u_only_child = '否'
                mes.append((u.id, u.name, u.sex, u.city, u.description, u.birthday, u_only_child))
            self.render('search.html', menu=menu, user=mes)


class PostHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('mod.html')

    def post(self):
        id = self.get_argument('id')
        name = self.get_argument('name')
        sex = self.get_argument('sex')
        city = self.get_argument('city')
        description = self.get_argument('description')
        birthday = self.get_argument('birthday')
        only_child = self.get_argument('only_child')
        q.filter(User.id == id).update(
            {"name": name, "sex": sex, "city": city, "description": description, "birthday": birthday,
             "only_child": only_child})
        session.commit()

        self.redirect('/')   # 重定向跳转


def make_app():
    routes = [
        (r'/', GetHandler),
        (r'/post', PostHandler)
    ]
    base_dir = os.path.join(os.path.dirname(__file__), "templates")
    static_dir = os.path.join(os.path.dirname(__file__), 'statics')
    return tornado.web.Application(
        routes,
        template_path=base_dir,  # 模版路路径
        static_path=static_dir,  # 静态文文件路路径
        autoreload=True
    )


if __name__ == "__main__":
    app = make_app()
    app.listen(options.port, options.host)

    loop = tornado.ioloop.IOLoop.current()
    loop.start()

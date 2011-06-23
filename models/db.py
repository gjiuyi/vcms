# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

db = DAL('sqlite://vcms.sqlite')    # used at developing stage
#db = DAL('sqlite://vcms1.sqlite')    # used at developing stage
#db = DAL('mysql://vinfo1:v_info1121@localhost/vcms')
#db = DAL('mysql://root:v_study9@localhost/vinfo')    #to be deleted

#from gluon.tools import Auth, Crud
from gluon.tools import *
auth = Auth(globals(), db)
auth.define_tables()
crud = Crud(globals(), db)


db.define_table('article',
    Field('title'),
    Field('date', 'date', default=request.now.date()),
    #Field('date', 'datetime', default=request.now),    # miliseconds will cause error, not yet solved
    Field('modified', 'datetime', default=request.now, update=request.now),
    Field('content', 'text'),
    Field('url'),
    Field('categories', 'list:reference category'),
    Field('post_tags', 'list:reference post_tag'),
    #Field('tags', 'list:reference tag'),    #to be deleted
    format='%(title)s')

#to be deleted
#db.define_table('tag',
#    Field('name'),
#    Field('taxonomy'),
#    format='%(name)s')
    
db.define_table('category',
    Field('name'),
    Field('importance', 'integer', default=999),
    format='%(name)s')
    
db.define_table('post_tag',
    Field('name'),
    Field('importance', 'integer', default=999),
    format='%(name)s')
    
db.article.title.requires = IS_NOT_EMPTY()
db.article.date.requires = IS_NOT_EMPTY()
db.article.modified.readable = db.article.modified.writable = False
db.article.content.requires = IS_NOT_EMPTY()
#db.article.url.requires = IS_NOT_EMPTY()
db.article.categories.requires = IS_IN_DB(db, db.category.id, '%(name)s', multiple=True)
db.article.post_tags.requires = IS_IN_DB(db, db.post_tag.id, '%(name)s', multiple=True)
#db.article.tags.requires = IS_IN_DB(db, db.tag.id, '%(name)s', multiple=True)    #to be deleted

db.category.name.requires = IS_NOT_EMPTY()
db.category.importance.requires = IS_NOT_EMPTY()

db.post_tag.name.requires = IS_NOT_EMPTY()
db.post_tag.importance.requires = IS_NOT_EMPTY()

#to be deleted
#db.tag.name.requires = IS_NOT_EMPTY()
#db.tag.taxonomy.requires = IS_IN_SET(['category', 'post_tag'])

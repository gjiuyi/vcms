#-*- coding: utf-8 -*-

"""CMS administration panel"""

T.force('en-en')
#T.force('zh-cn')

def user():
    return dict(form=auth())

#@auth.requires_login()
#@auth.requires(auth.user_id==1)
@auth.requires_membership('admin')
def index():
    """List all the documents to be displayed"""
    
    articles = db().select(db.article.ALL, orderby=~db.article.date|~db.article.modified)
    response.title = 'Articles list'
    return dict(articles=articles)
    
@auth.requires_membership('admin')
def new():
    """Create a new article"""
    
    form = crud.create(db.article, next=URL('index'))
    form.element('textarea')['_cols']=120
    form.element('textarea')['_rows']=20
    response.title = T('Add article')
    return dict(form=form)

@auth.requires_membership('admin')
def edit():
    """Edit an existing article"""
    
    article = db.article(request.args(0)) or redirect(URL('index'))
    form = crud.update(db.article, article, next=URL('index'))
    form.element('textarea')['_cols']=120
    form.element('textarea')['_rows']=20
    #form = crud.update(db.article, article, next=URL('edit', args=request.args))
    response.title = T('Edit article - %(title)s', dict(title=article.title))
    return dict(form=form)
    
@auth.requires_membership('admin')
def delete():
    """Delete an existing article"""
    
    deleted_article = db.article(request.args(0)) or redirect(URL('index'))
    db(db.article.id==request.args(0)).delete()
    response.title = T('Delete article - %(title)s', dict(title=deleted_article.title))
    return dict(article=deleted_article)
    
@auth.requires_login()
def search():
    """Search an existing article"""
    
    form = FORM(INPUT(_id='keyword'), _name='keyword', _onkeyup="ajax('bg_find', ['keyword'], 'target');")
    response.title = T('Search articles')
    return dict(form=form, target_div=DIV(_id='target'))
    
def bg_find():
    """An ajax callback that returns a <ul> of links to existing articles"""
    
    pattern = '%' + request.vars.keywords.lower() + '%'
    articles = db(db.article.title.lower().like(pattern)).select(orderby=db.article.title)
    items = [A(article.title, _href=URL('show', args=article.id)) for article in articles]
    return UL(*items).xml()
    
@auth.requires_membership('admin')
def edit_tags():
    """Edit categories or post tags"""
    
    # taxonomy should be category or post_tag
    try:
        taxonomy = request.get_vars['taxonomy']
    except:
        redirect(URL('index'))
    
    # action should be list or edit
    try:
        action = request.get_vars['action']
    except:
        request.vars['action'] = action = 'list'
    
    tags = form = {}
    
    if 'post_tag' in taxonomy:
        form = {'1': taxonomy}
    
    if taxonomy == 'category':
        if action == 'list':
            response.title = T('Categories')
            tags = db().select(db.category.ALL, orderby=db.category.importance|db.category.name)
            #tags = db(db.tag.taxonomy==taxonomy).select(db.tag.ALL, orderby=db.tag.name)    #to be deleted
            form = crud.create(db.category, next=URL('edit_tags', vars=dict(taxonomy=taxonomy)))
            #form = crud.create(db.tag, next=URL('edit_tags', vars=dict(taxonomy=taxonomy)))
        elif action == 'edit':
            response.title = T('Edit Category')
            try:
                tag_id = request.get_vars['tag_id']
            except:
                redirect(URL('edit_tags', vars=dict(taxonomy=taxonomy)))
            tag = db.category(tag_id) or redirect(URL('edit_tags', vars=dict(taxonomy=taxonomy)))
            #tag = db.tag(tag_id) or redirect(URL('edit_tags', vars=dict(taxonomy=taxonomy)))    #to be deleted
            form = crud.update(db.category, tag, next=URL('edit_tags', vars=dict(taxonomy=taxonomy)))
            #form = crud.update(db.tag, tag, next=URL('edit_tags', vars=dict(taxonomy=taxonomy)))    #to be deleted
    elif taxonomy == 'post_tag':
        if action == 'list':
            response.title = T('Post Tags')
            tags = db().select(db.post_tag.ALL, orderby=db.post_tag.importance|db.post_tag.name)
            #tags = db(db.tag.taxonomy==taxonomy).select(db.tag.ALL, orderby=db.tag.name)    #to be deleted
            form = crud.create(db.post_tag, next=URL('edit_tags', vars=dict(taxonomy=taxonomy)))
            #form = crud.create(db.tag, next=URL('edit_tags', vars=dict(taxonomy=taxonomy)))
        elif action == 'edit':
            response.title = T('Edit Tag')
            try:
                tag_id = request.get_vars['tag_id']
            except:
                redirect(URL('edit_tags', vars=dict(taxonomy=taxonomy)))
            tag = db.post_tag(tag_id) or redirect(URL('eidt_tags', vars=dict(taxonomy=taxonomy)))
            #tag = db.tag(tag_id) or redirect(URL('edit_tags', vars=dict(taxonomy=taxonomy)))    #to be deleted
            form = crud.update(db.post_tag, tag, next=URL('edit_tags', vars=dict(taxonomy=taxonomy)))
            #form = crud.update(db.tag, tag, next=URL('edit_tags', vars=dict(taxonomy=taxonomy)))    #to be deleted
    return dict(taxonomy=taxonomy, tags=tags, form=form)

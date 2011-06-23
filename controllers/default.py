#-*- coding: utf-8 -*-

"""Frontend of VCMS, whose main function is viewing articles by date, by categories, or by post_tags."""

categories = db().select(db.category.ALL, orderby=db.category.importance|db.category.name)
post_tags = db().select(db.post_tag.ALL, orderby=db.post_tag.importance|db.post_tag.name)
#categories = db().select(db.category.ALL, orderby=db.category.name)
#post_tags = db().select(db.post_tag.ALL, orderby=db.post_tag.name)


def index():
    """Home page which displays the article list"""
    
    articles = db().select(db.article.ALL, orderby=~db.article.date|~db.article.modified)
    response.title = T('微学考试资讯')
    return dict(articles=articles, categories=categories, post_tags=post_tags)

def user():
    return dict(form=auth())

def list():
    """Display the article list by category or by post tag"""
    
    try:
        category = request.get_vars['category']
        name = db.category(category).name or redirect(URL('index'))
    except:
        category = ''
        
    try:
        post_tag = request.get_vars['post_tag']
        name = db.post_tag(post_tag).name or redirect(URL('index'))
    except:
        post_tag = ''
        
    if category != '':
        articles = db(db.article.categories.contains(category)).select(db.article.ALL, orderby=db.article.date)
        response.title = T('微学') + name + T('考试资讯')
    elif post_tag != '':
        articles = db(db.article.post_tags.contains(post_tag)).select(db.article.ALL, orderby=db.article.date)
        response.title = name + T('相关考试资讯')
    else:
        redirect(URL('index'))
        
    return dict(articles=articles, categories=categories, post_tags=post_tags)

def show():
    """Display a specific article"""

    #article = db(db.article.id==request.args(0)).select().first()
    article = db.article(request.args(0)) or redirect(URL('index'))
    cur_categories = []
    cur_post_tags = []
    keywords = []
    if article.categories:
        for category_id in article.categories:
            try:
                category = {'name': db.category(category_id).name, 'id': category_id}
                cur_categories.append(category)
                keywords.append(category['name'])
            except:
                pass
    if article.post_tags:
        for post_tag_id in article.post_tags:
            try:
                post_tag = {'name': db.post_tag(post_tag_id).name, 'id': post_tag_id}
                cur_post_tags.append(post_tag)
                keywords.append(post_tag['name'])
            except:
                pass
    response.title = article.title
    response.meta.description = article.title
    response.meta.keywords = ', '.join(keywords)
    return dict(article=article, categories=categories, post_tags=post_tags, 
        cur_categories=cur_categories, cur_post_tags=cur_post_tags)
    
def news():
    """Output RSS feeds"""

    import datetime
    articles = db().select(db.article.ALL, orderby=~db.article.date)
    return dict(
        title = '微学公务员考试资讯',
        link = 'http://www.htexam.net/soft/',
        description = '最新最权威的公务员考试资讯',
        created_on = request.now,
        items = [
            dict(
                title = article.title,
                link = 'http://%s%s' % (request.env.http_host, URL('show', extension=False, args=article.id)),
                description = article.content,
                created_on = datetime.date.isoformat(article.date)
            ) for article in articles
        ]
    )

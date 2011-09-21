#-*- coding: utf-8 -*-

"""Frontend of VCMS, whose main function is viewing articles by date, by categories, or by post_tags."""

categories = db().select(db.category.ALL, orderby=db.category.importance|db.category.name)
post_tags = db().select(db.post_tag.ALL, orderby=db.post_tag.importance|db.post_tag.name)
#categories = db().select(db.category.ALL, orderby=db.category.name)
#post_tags = db().select(db.post_tag.ALL, orderby=db.post_tag.name)


def index():
    """Home page which displays the article list"""
    
    # get total num of articles
    all_articles = db().select(db.article.ALL, orderby=~db.article.date|~db.article.modified)
    record_num = len(all_articles)

    try:    # get page num
        page_num = int(request.get_vars['page']) - 1
    except:    # default page 0
        page_num = 0
    try:    # get items num per page
        items_per_page = request.get_vars['items']
    except:    # default 50 items per page
        items_per_page = 50
    
    # if error page num specified, the last page will be displayed
    page_count = int(round(record_num * 1.0 / items_per_page))
    # in fact, round(2.08) will get 2 not 3
    if record_num * 1.0 / items_per_page > page_count:
        page_count += 1
    if page_num > page_count -1:
        page_num = page_count - 1

    if page_num > page_count -1:
        page_num = page_count - 1

    start = page_num * items_per_page
    end = (page_num + 1) * items_per_page + 1
    limitby = (start, end)
    articles = db().select(
        db.article.ALL,
        limitby=limitby,
        orderby=~db.article.date|~db.article.modified
    )

    response.title = T('微学考试资讯')
    return dict(
        articles=articles, 
        categories=categories, 
        post_tags=post_tags,
        record_num=record_num,
        page=page_num+1,
        max_page=page_count
    )

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
        articles = db(db.article.categories.contains(category)).select(db.article.ALL, 
            orderby=~db.article.date|~db.article.modified)
        response.title = T('微学') + name + T('考试资讯')
    elif post_tag != '':
        articles = db(db.article.post_tags.contains(post_tag)).select(db.article.ALL, 
            orderby=~db.article.date|~db.article.modified)
        response.title = name + T('相关考试资讯')
    else:
        redirect(URL('index'))
    record_num = len(articles)

    try:    # get page num
        page_num = int(request.get_vars['page']) - 1
    except:    # default page 0
        page_num = 0
    try:    # get items num per page
        items_per_page = request.get_vars['items']
    except:    # default 50 items per page
        items_per_page = 50
    
    # if error page num specified, the last page will be displayed
    page_count = int(round(record_num * 1.0 / items_per_page))
    # in fact, round(2.08) will get 2 not 3
    if record_num * 1.0 / items_per_page > page_count:
        page_count += 1
    if page_num > page_count -1:
        page_num = page_count - 1

    start = page_num * items_per_page
    end = (page_num + 1) * items_per_page + 1
    limitby = (start, end)
    articles = db().select(db.article.ALL, limitby=limitby)

    if category != '':
        articles = db(
            db.article.categories.contains(category)).select(db.article.ALL,
            limitby=limitby,
            orderby=~db.article.date|~db.article.modified
        )
    elif post_tag != '':
        articles = db(
            db.article.post_tags.contains(post_tag)).select(db.article.ALL, 
            limitby=limitby,
            orderby=~db.article.date|~db.article.modified
        )

    return dict(
        articles=articles,
        categories=categories,
        post_tags=post_tags,
        category_id=category,
        post_tag_id=post_tag,
        record_num=record_num,
        page = page_num + 1,
        max_page = page_count
    )

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
    #articles = db().select(db.article.ALL, orderby=~db.article.date)
    
    try:
        category = request.get_vars['category']    # the category id of news you want to get, stored as string
    except:
        category = ''
    try:
        post_tag = request.get_vars['post_tag']    # the post tag id of news you want to get, stored as string
    except:
        post_tag = ''
    try:
        num = int(request.get_vars['num'])    # the number of news you want to get
    except:
        num = 0
    try:
        format = request.get_vars['format']
    except:
        format = 'rss'

    def get_articles(category='', post_tag='', num=0):
        """get the news with specified category and num"""
        
        if category == '' and post_tag == '':
            if num == 0:
                articles = db().select(db.article.ALL, orderby=~db.article.date)
            else:
                articles = db().select(db.article.ALL, orderby=~db.article.date, limitby=(0, num))
        elif category != '':
            if num == 0:
                articles = db(db.article.categories.contains(category)).select(db.article.ALL, orderby=~db.article.date)
            else:
                articles = db(db.article.categories.contains(category)).select(db.article.ALL, orderby=~db.article.date, limitby=(0, num))
        elif post_tag != '':
            if num == 0:
                articles = db(db.article.post_tags.contains(post_tag)).select(db.article.ALL, orderby=~db.article.date)
            else:
                articles = db(db.article.post_tags.contains(post_tag)).select(db.article.ALL, orderby=~db.article.date, limitby=(0, num))            
        return articles
        
    articles = get_articles(category, post_tag, num)
            
    if format == 'rss':
        import rfc822
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
                    #created_on = datetime.date.isoformat(article.date)
                    #modify the format of created_on to satisfy RFC822
                    #to validate: http://www.feedvalidator.org
                    created_on = rfc822.formatdate(rfc822.mktime_tz(rfc822.parsedate_tz(datetime.datetime(article.date.year, article.date.month, article.date.day, 8, 0, 0).strftime('%a, %d %b %Y %H:%M:%S'))))
                ) for article in articles
            ]
        )
    elif format == 'json':
        # usage: https://example.com/vcms/default/news.json?num=2&category=5&format=json
        return dict(
            items = [dict(
                title = article.title,
                link = 'http://%s%s' % (request.env.http_host, URL('show', extension=False, args=article.id)),
                created_on = datetime.date.isoformat(article.date)
            ) for article in articles]
        )

def app():
    """Baidu Open App
    
    http://vcms.vstudy.cn/app?type=iframe
    http://vcms.vstudy.cn/app?type=normal
    """
    
    try:
        type = request.get_vars['type']
    except:
        type = 'normal'
    
    response.title = '公务员考试资讯'
          
    all = db().select(db.article.ALL, \
            orderby=~db.article.date|~db.article.modified, \
            limitby=[0, 18])
    gwy = db(db.article.categories.contains('1')).select(db.article.ALL, \
            orderby=~db.article.date|~db.article.modified, \
            limitby=[0,6])
    sydw = db(db.article.categories.contains('12')).select(db.article.ALL, \
            orderby=~db.article.date|~db.article.modified, \
            limitby=[0,6])
    zhaojiao = db(db.article.categories.contains('5')).select(db.article.ALL, \
            orderby=~db.article.date|~db.article.modified, \
            limitby=[0,6])
    zhaojing = db(db.article.categories.contains('11')).select(db.article.ALL, \
            orderby=~db.article.date|~db.article.modified, \
            limitby=[0,6])
    articles = [all, gwy, sydw, zhaojiao, zhaojing]
        
    return dict(type=type, articles=articles)

def monitor():

    return dict()

def query():
    """list article urls, query by exam date, etc."""

    try:
        exam_date = request.get_vars['exam_date']
    except:
        exam_date = ''

    if exam_date != '':
        articles = db(db.article.exam_date==exam_date).select(orderby=~db.article.date|~db.article.modified)
    else:
        articles = []

    return dict(
        exam_date = exam_date,
        articles = articles
    )

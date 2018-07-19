import re


def columnify(name):
    # "[Some] _ Article's Title--"
    # "[some] _ article's title--"
    s = name.lower()

    # "[some] _ article's_title--"
    # "[some]___article's_title__"
    s = re.sub('\W', '_', s)

    # "some___articles_title__"
    # "some_articles_title_"
    s = re.sub('_+', '_', s)

    # "_some_article_name_"
    # "some_article_name"
    s = re.sub('(\b_|_\b)', '', s)

    return s

APP_NAME = 'posts'
OBJECT_RELATED_URL_PARAMS = {
    # name_url:(object:orm_name)
    'slug': ('group', 'slug',),
    'post_id': ('post', 'id',),
    'username': ('user', 'username',),
}

CONFIG_TEST_URLS = {
    # name : [url{param}, template, redirect_url]
    'index': ['/', 'posts/index.html'],
    'group_list': ['/group/{slug}/', 'posts/group_list.html'],
    'profile': ['/profile/{username}/', 'posts/profile.html'],
    'post_create': ['/create/', 'posts/create_post.html', '/auth/login/'],
    'post_detail': ['/posts/{post_id}/', 'posts/post_detail.html'],
    'post_edit': [
        '/posts/{post_id}/edit/', 'posts/create_post.html',
        '/posts/{post_id}/'],
}

PAGINATOR_TEST_PAGES = ('group_list', 'profile', 'index',)
UNEXISTING_URL = '/unexisting/'
AUTHORISATION_PAGES_CASES = ('post_create', 'post_edit',)
POST_APPEAR_ON_PAGES = ('group_list', 'profile', 'index',)
PAGE_SHOW_CORRECT_CONTEXT = ('group_list', 'profile', 'index',)
PAGES_USES_CREATE_TEMPLATE = ('post_create', 'post_edit',)
PAGES_SHOW_SINGLE_POST = ('post_detail',)

def source_view_processor(request):
    view_name = request.resolver_match.view_name

    if view_name == 'search-books':
        source_view = 'BookSearchView'

    elif view_name == 'author-show-books':
        source_view = 'ShowAuthorBooksView'

    elif view_name == 'show-all-books':
        source_view = 'BookListView'

    elif view_name == 'user_reading_list':
        source_view = 'UserReadingListView'

    else:
        source_view = None

    return {'source_view': source_view}
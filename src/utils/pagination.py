"""
Pagination utility functions.
"""
import math


def generate_pagination_html(current_page, total_pages, per_page, total_chords, search=""):
    """Generate HTML for pagination navigation."""
    if total_pages <= 1:
        return ""
    
    # Build query string for search
    search_param = f"&search={search}" if search.strip() else ""
    
    html = f'''
    <div class="pagination-info">
        Showing page {current_page} of {total_pages} 
        ({per_page} chords per page, {total_chords} total)
    </div>
    <div class="pagination">
    '''
    
    # Previous button
    if current_page > 1:
        html += f'<a href="/?page={current_page - 1}&per_page={per_page}{search_param}" class="pagination-btn">« Previous</a>'
    else:
        html += '<span class="pagination-btn disabled">« Previous</span>'
    
    # Page numbers
    start_page = max(1, current_page - 2)
    end_page = min(total_pages, current_page + 2)
    
    if start_page > 1:
        html += f'<a href="/?page=1&per_page={per_page}{search_param}" class="pagination-btn">1</a>'
        if start_page > 2:
            html += '<span class="pagination-ellipsis">...</span>'
    
    for page_num in range(start_page, end_page + 1):
        if page_num == current_page:
            html += f'<span class="pagination-btn active">{page_num}</span>'
        else:
            html += f'<a href="/?page={page_num}&per_page={per_page}{search_param}" class="pagination-btn">{page_num}</a>'
    
    if end_page < total_pages:
        if end_page < total_pages - 1:
            html += '<span class="pagination-ellipsis">...</span>'
        html += f'<a href="/?page={total_pages}&per_page={per_page}{search_param}" class="pagination-btn">{total_pages}</a>'
    
    # Next button
    if current_page < total_pages:
        html += f'<a href="/?page={current_page + 1}&per_page={per_page}{search_param}" class="pagination-btn">Next »</a>'
    else:
        html += '<span class="pagination-btn disabled">Next »</span>'
    
    # Per-page selector
    html += f'''
    </div>
    <div class="per-page-selector">
        Show: 
        <a href="/?page=1&per_page=12{search_param}" class="{'active' if per_page == 12 else ''}">12</a>
        <a href="/?page=1&per_page=24{search_param}" class="{'active' if per_page == 24 else ''}">24</a>
        <a href="/?page=1&per_page=48{search_param}" class="{'active' if per_page == 48 else ''}">48</a>
        <a href="/?page=1&per_page=100{search_param}" class="{'active' if per_page == 100 else ''}">100</a>
        per page
    </div>
    '''
    
    return html


def calculate_pagination(page, per_page, total_items):
    """Calculate pagination parameters."""
    total_pages = math.ceil(total_items / per_page) if total_items > 0 else 1
    start_index = (page - 1) * per_page
    end_index = start_index + per_page
    
    return {
        'total_pages': total_pages,
        'start_index': start_index,
        'end_index': end_index
    }
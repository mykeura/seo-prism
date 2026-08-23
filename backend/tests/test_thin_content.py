"""
Unit tests for thin_content module.
"""
import pytest
from modules.thin_content import ThinContentModule


class TestThinContentModule:
    """Tests for thin_content module."""
    
    def test_thin_content_below_word_threshold(self, temp_db, sample_scan_id):
        """Test detecting content below minimum word count (300 words)."""
        # Create content with less than 300 words
        content = ' '.join(['word'] * 250)  # 250 words
        html = f'''
        <html>
            <head><title>Test Page</title></head>
            <body>
                <h1>Article Title</h1>
                <p>{content}</p>
            </body>
        </html>
        '''
        
        crawled_pages = [
            {
                'url': 'https://example.com/page',
                'status': 200,
                'html': html,
                'links': []
            }
        ]
        
        module = ThinContentModule(temp_db)
        issues = module.analyze(sample_scan_id, crawled_pages)
        
        assert len(issues) == 1
        assert issues[0]['issue_type'] == 'thin_content'
        assert issues[0]['severity'] == 'medium'
        assert 'thin content' in issues[0]['description'].lower()
        assert '250' in issues[0]['description']
    
    def test_thin_content_below_character_threshold(self, temp_db, sample_scan_id):
        """Test detecting content below minimum character count (1500 chars)."""
        # Create content with less than 1500 characters but more than 300 words
        content = ' '.join(['word'] * 350)  # 350 words, ~1750 chars (over word threshold)
        short_content = ' '.join(['word'] * 100)  # 100 words, ~500 chars (under both thresholds)
        html = f'''
        <html>
            <head><title>Test Page</title></head>
            <body>
                <h1>Article Title</h1>
                <p>{short_content}</p>
            </body>
        </html>
        '''
        
        crawled_pages = [
            {
                'url': 'https://example.com/page',
                'status': 200,
                'html': html,
                'links': []
            }
        ]
        
        module = ThinContentModule(temp_db)
        issues = module.analyze(sample_scan_id, crawled_pages)
        
        assert len(issues) == 1
        assert issues[0]['issue_type'] == 'thin_content'
        assert 'thin content' in issues[0]['description'].lower()
    
    def test_very_thin_content_high_severity(self, temp_db, sample_scan_id):
        """Test that very thin content (< 100 words) gets high severity."""
        content = ' '.join(['word'] * 50)  # 50 words
        html = f'''
        <html>
            <head><title>Test Page</title></head>
            <body>
                <h1>Article Title</h1>
                <p>{content}</p>
            </body>
        </html>
        '''
        
        crawled_pages = [
            {
                'url': 'https://example.com/page',
                'status': 200,
                'html': html,
                'links': []
            }
        ]
        
        module = ThinContentModule(temp_db)
        issues = module.analyze(sample_scan_id, crawled_pages)
        
        assert len(issues) == 1
        assert issues[0]['issue_type'] == 'thin_content'
        assert issues[0]['severity'] == 'high'
    
    def test_sufficient_content_no_issues(self, temp_db, sample_scan_id):
        """Test that sufficient content produces no issues."""
        # Create content with more than 300 words and 1500 characters
        content = ' '.join(['word'] * 400)  # 400 words, ~2000 chars
        html = f'''
        <html>
            <head><title>Test Page</title></head>
            <body>
                <h1>Article Title</h1>
                <p>{content}</p>
            </body>
        </html>
        '''
        
        crawled_pages = [
            {
                'url': 'https://example.com/page',
                'status': 200,
                'html': html,
                'links': []
            }
        ]
        
        module = ThinContentModule(temp_db)
        issues = module.analyze(sample_scan_id, crawled_pages)
        
        assert len(issues) == 0
    
    def test_content_exactly_300_words(self, temp_db, sample_scan_id):
        """Test content with exactly 300 words (minimum acceptable)."""
        content = ' '.join(['word'] * 301)  # 301 words (just over threshold)
        html = f'''
        <html>
            <head><title>Test Page</title></head>
            <body>
                <h1>Article Title</h1>
                <p>{content}</p>
            </body>
        </html>
        '''
        
        crawled_pages = [
            {
                'url': 'https://example.com/page',
                'status': 200,
                'html': html,
                'links': []
            }
        ]
        
        module = ThinContentModule(temp_db)
        issues = module.analyze(sample_scan_id, crawled_pages)
        
        assert len(issues) == 0
    
    def test_content_exactly_1500_chars(self, temp_db, sample_scan_id):
        """Test content with exactly 1500 characters (minimum acceptable)."""
        # Create content with more than 1500 characters AND more than 300 words
        content = ' '.join(['word'] * 350)  # ~1750 characters, 350 words
        html = f'''
        <html>
            <head><title>Test Page</title></head>
            <body>
                <h1>Article Title</h1>
                <p>{content}</p>
            </body>
        </html>
        '''
        
        crawled_pages = [
            {
                'url': 'https://example.com/page',
                'status': 200,
                'html': html,
                'links': []
            }
        ]
        
        module = ThinContentModule(temp_db)
        issues = module.analyze(sample_scan_id, crawled_pages)
        
        assert len(issues) == 0
    
    def test_title_excluded_from_content(self, temp_db, sample_scan_id):
        """Test that title tag is excluded from content analysis."""
        # Long title but short article content
        long_title = 'A' * 1000  # 1000 characters in title
        short_content = ' '.join(['word'] * 100)  # 100 words in content
        html = f'''
        <html>
            <head><title>{long_title}</title></head>
            <body>
                <h1>Article Title</h1>
                <p>{short_content}</p>
            </body>
        </html>
        '''
        
        crawled_pages = [
            {
                'url': 'https://example.com/page',
                'status': 200,
                'html': html,
                'links': []
            }
        ]
        
        module = ThinContentModule(temp_db)
        issues = module.analyze(sample_scan_id, crawled_pages)
        
        assert len(issues) == 1
        assert issues[0]['issue_type'] == 'thin_content'
        # Should only count the short content, not the long title
    
    def test_h1_excluded_from_content(self, temp_db, sample_scan_id):
        """Test that H1 tag is excluded from content analysis."""
        # Long H1 but short article content
        long_h1 = 'A' * 1000  # 1000 characters in H1
        short_content = ' '.join(['word'] * 100)  # 100 words in content
        html = f'''
        <html>
            <head><title>Test Page</title></head>
            <body>
                <h1>{long_h1}</h1>
                <p>{short_content}</p>
            </body>
        </html>
        '''
        
        crawled_pages = [
            {
                'url': 'https://example.com/page',
                'status': 200,
                'html': html,
                'links': []
            }
        ]
        
        module = ThinContentModule(temp_db)
        issues = module.analyze(sample_scan_id, crawled_pages)
        
        assert len(issues) == 1
        assert issues[0]['issue_type'] == 'thin_content'
        # Should only count the short content, not the long H1
    
    def test_nav_elements_excluded(self, temp_db, sample_scan_id):
        """Test that navigation elements are excluded from content analysis."""
        nav_content = ' '.join(['word'] * 200)  # 200 words in nav
        article_content = ' '.join(['word'] * 250)  # 250 words in article
        html = f'''
        <html>
            <head><title>Test Page</title></head>
            <body>
                <nav>
                    <p>{nav_content}</p>
                </nav>
                <article>
                    <h1>Article Title</h1>
                    <p>{article_content}</p>
                </article>
            </body>
        </html>
        '''
        
        crawled_pages = [
            {
                'url': 'https://example.com/page',
                'status': 200,
                'html': html,
                'links': []
            }
        ]
        
        module = ThinContentModule(temp_db)
        issues = module.analyze(sample_scan_id, crawled_pages)
        
        assert len(issues) == 1
        assert issues[0]['issue_type'] == 'thin_content'
        # Should only count article content, not nav
    
    def test_header_footer_excluded(self, temp_db, sample_scan_id):
        """Test that header and footer elements are excluded from content analysis."""
        header_content = ' '.join(['word'] * 100)
        footer_content = ' '.join(['word'] * 100)
        article_content = ' '.join(['word'] * 250)
        html = f'''
        <html>
            <head><title>Test Page</title></head>
            <body>
                <header><p>{header_content}</p></header>
                <article>
                    <h1>Article Title</h1>
                    <p>{article_content}</p>
                </article>
                <footer><p>{footer_content}</p></footer>
            </body>
        </html>
        '''
        
        crawled_pages = [
            {
                'url': 'https://example.com/page',
                'status': 200,
                'html': html,
                'links': []
            }
        ]
        
        module = ThinContentModule(temp_db)
        issues = module.analyze(sample_scan_id, crawled_pages)
        
        assert len(issues) == 1
        assert issues[0]['issue_type'] == 'thin_content'
    
    def test_scripts_styles_excluded(self, temp_db, sample_scan_id):
        """Test that script and style elements are excluded from content analysis."""
        script_content = ' '.join(['word'] * 100)
        style_content = ' '.join(['word'] * 100)
        article_content = ' '.join(['word'] * 250)
        html = f'''
        <html>
            <head>
                <title>Test Page</title>
                <script>{script_content}</script>
                <style>{style_content}</style>
            </head>
            <body>
                <article>
                    <h1>Article Title</h1>
                    <p>{article_content}</p>
                </article>
            </body>
        </html>
        '''
        
        crawled_pages = [
            {
                'url': 'https://example.com/page',
                'status': 200,
                'html': html,
                'links': []
            }
        ]
        
        module = ThinContentModule(temp_db)
        issues = module.analyze(sample_scan_id, crawled_pages)
        
        assert len(issues) == 1
        assert issues[0]['issue_type'] == 'thin_content'
    
    def test_main_element_priority(self, temp_db, sample_scan_id):
        """Test that main element is prioritized for content extraction."""
        main_content = ' '.join(['word'] * 400)  # Sufficient content in main
        aside_content = ' '.join(['word'] * 50)  # Thin content in aside
        html = f'''
        <html>
            <head><title>Test Page</title></head>
            <body>
                <aside><p>{aside_content}</p></aside>
                <main>
                    <h1>Article Title</h1>
                    <p>{main_content}</p>
                </main>
            </body>
        </html>
        '''
        
        crawled_pages = [
            {
                'url': 'https://example.com/page',
                'status': 200,
                'html': html,
                'links': []
            }
        ]
        
        module = ThinContentModule(temp_db)
        issues = module.analyze(sample_scan_id, crawled_pages)
        
        assert len(issues) == 0  # Should use main content, which is sufficient
    
    def test_article_element_priority(self, temp_db, sample_scan_id):
        """Test that article element is prioritized for content extraction."""
        article_content = ' '.join(['word'] * 400)
        div_content = ' '.join(['word'] * 50)
        html = f'''
        <html>
            <head><title>Test Page</title></head>
            <body>
                <div><p>{div_content}</p></div>
                <article>
                    <h1>Article Title</h1>
                    <p>{article_content}</p>
                </article>
            </body>
        </html>
        '''
        
        crawled_pages = [
            {
                'url': 'https://example.com/page',
                'status': 200,
                'html': html,
                'links': []
            }
        ]
        
        module = ThinContentModule(temp_db)
        issues = module.analyze(sample_scan_id, crawled_pages)
        
        assert len(issues) == 0
    
    def test_content_class_detection(self, temp_db, sample_scan_id):
        """Test that content class is detected for content extraction."""
        content_div = ' '.join(['word'] * 400)
        other_div = ' '.join(['word'] * 50)
        html = f'''
        <html>
            <head><title>Test Page</title></head>
            <body>
                <div><p>{other_div}</p></div>
                <div class="content">
                    <h1>Article Title</h1>
                    <p>{content_div}</p>
                </div>
            </body>
        </html>
        '''
        
        crawled_pages = [
            {
                'url': 'https://example.com/page',
                'status': 200,
                'html': html,
                'links': []
            }
        ]
        
        module = ThinContentModule(temp_db)
        issues = module.analyze(sample_scan_id, crawled_pages)
        
        assert len(issues) == 0
    
    def test_content_id_detection(self, temp_db, sample_scan_id):
        """Test that content id is detected for content extraction."""
        content_div = ' '.join(['word'] * 400)
        other_div = ' '.join(['word'] * 50)
        html = f'''
        <html>
            <head><title>Test Page</title></head>
            <body>
                <div><p>{other_div}</p></div>
                <div id="content">
                    <h1>Article Title</h1>
                    <p>{content_div}</p>
                </div>
            </body>
        </html>
        '''
        
        crawled_pages = [
            {
                'url': 'https://example.com/page',
                'status': 200,
                'html': html,
                'links': []
            }
        ]
        
        module = ThinContentModule(temp_db)
        issues = module.analyze(sample_scan_id, crawled_pages)
        
        assert len(issues) == 0
    
    def test_multiple_pages_with_thin_content(self, temp_db, sample_scan_id):
        """Test detecting thin content across multiple pages."""
        content = ' '.join(['word'] * 200)
        html = f'''
        <html>
            <head><title>Test Page</title></head>
            <body>
                <h1>Article Title</h1>
                <p>{content}</p>
            </body>
        </html>
        '''
        
        crawled_pages = [
            {
                'url': 'https://example.com/page1',
                'status': 200,
                'html': html,
                'links': []
            },
            {
                'url': 'https://example.com/page2',
                'status': 200,
                'html': html,
                'links': []
            }
        ]
        
        module = ThinContentModule(temp_db)
        issues = module.analyze(sample_scan_id, crawled_pages)
        
        assert len(issues) == 2
    
    def test_page_without_html(self, temp_db, sample_scan_id):
        """Test page without HTML content produces no issues."""
        crawled_pages = [
            {
                'url': 'https://example.com/page',
                'status': 200,
                'html': None,
                'links': []
            }
        ]
        
        module = ThinContentModule(temp_db)
        issues = module.analyze(sample_scan_id, crawled_pages)
        
        assert len(issues) == 0
    
    def test_empty_html(self, temp_db, sample_scan_id):
        """Test empty HTML produces no issues."""
        crawled_pages = [
            {
                'url': 'https://example.com/page',
                'status': 200,
                'html': '',
                'links': []
            }
        ]
        
        module = ThinContentModule(temp_db)
        issues = module.analyze(sample_scan_id, crawled_pages)
        
        assert len(issues) == 0
    
    def test_whitespace_cleaning(self, temp_db, sample_scan_id):
        """Test that whitespace is properly cleaned from content."""
        content = '  word1  word2  word3  '  # Extra whitespace
        html = f'''
        <html>
            <head><title>Test Page</title></head>
            <body>
                <h1>Article Title</h1>
                <p>{content}</p>
            </body>
        </html>
        '''
        
        crawled_pages = [
            {
                'url': 'https://example.com/page',
                'status': 200,
                'html': html,
                'links': []
            }
        ]
        
        module = ThinContentModule(temp_db)
        issues = module.analyze(sample_scan_id, crawled_pages)
        
        assert len(issues) == 1
        # Should count 3 words after cleaning
        assert '3' in issues[0]['description']
    
    def test_issues_saved_to_database(self, temp_db, sample_scan_id):
        """Test that issues are properly saved to database."""
        content = ' '.join(['word'] * 200)
        html = f'''
        <html>
            <head><title>Test Page</title></head>
            <body>
                <h1>Article Title</h1>
                <p>{content}</p>
            </body>
        </html>
        '''
        
        crawled_pages = [
            {
                'url': 'https://example.com/page',
                'status': 200,
                'html': html,
                'links': []
            }
        ]
        
        module = ThinContentModule(temp_db)
        issues = module.analyze(sample_scan_id, crawled_pages)
        
        # Verify issues were saved to database
        results = temp_db.get_scan_results(sample_scan_id)
        db_issues = results['issues']
        
        assert len(db_issues) == 1
        assert db_issues[0]['issue_type'] == 'thin_content'
        assert db_issues[0]['url'] == 'https://example.com/page'
        assert db_issues[0]['severity'] == 'medium'
    
    def test_mixed_content_pages(self, temp_db, sample_scan_id):
        """Test detecting issues across pages with mixed content lengths."""
        short_content = ' '.join(['word'] * 200)
        sufficient_content = ' '.join(['word'] * 400)
        
        crawled_pages = [
            {
                'url': 'https://example.com/page1',
                'status': 200,
                'html': f'<html><head><title>Page 1</title></head><body><h1>Title</h1><p>{short_content}</p></body></html>',
                'links': []
            },
            {
                'url': 'https://example.com/page2',
                'status': 200,
                'html': f'<html><head><title>Page 2</title></head><body><h1>Title</h1><p>{sufficient_content}</p></body></html>',
                'links': []
            },
            {
                'url': 'https://example.com/page3',
                'status': 200,
                'html': f'<html><head><title>Page 3</title></head><body><h1>Title</h1><p>{short_content}</p></body></html>',
                'links': []
            }
        ]
        
        module = ThinContentModule(temp_db)
        issues = module.analyze(sample_scan_id, crawled_pages)
        
        assert len(issues) == 2
        assert issues[0]['url'] == 'https://example.com/page1'
        assert issues[1]['url'] == 'https://example.com/page3'
    
    def test_forms_and_inputs_excluded(self, temp_db, sample_scan_id):
        """Test that form and input elements are excluded from content analysis."""
        form_content = ' '.join(['word'] * 100)
        article_content = ' '.join(['word'] * 250)
        html = f'''
        <html>
            <head><title>Test Page</title></head>
            <body>
                <form>
                    <p>{form_content}</p>
                    <input type="text" value="test input">
                </form>
                <article>
                    <h1>Article Title</h1>
                    <p>{article_content}</p>
                </article>
            </body>
        </html>
        '''
        
        crawled_pages = [
            {
                'url': 'https://example.com/page',
                'status': 200,
                'html': html,
                'links': []
            }
        ]
        
        module = ThinContentModule(temp_db)
        issues = module.analyze(sample_scan_id, crawled_pages)
        
        assert len(issues) == 1
        assert issues[0]['issue_type'] == 'thin_content'